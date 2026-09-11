from __future__ import annotations

import argparse
import difflib
import re
import subprocess
import sys
from html.parser import HTMLParser
from pathlib import Path
from typing import Dict, List, Sequence, Tuple


_TITLE_RE = re.compile(r'(<title\b[^>]*>)(.*?)(</title\s*>)', re.IGNORECASE | re.DOTALL)
_META_RE = re.compile(r'<meta\b[^>]*>', re.IGNORECASE | re.DOTALL)
_ATTR_RE = re.compile(r'([:\w-]+)\s*=\s*(["\'])(.*?)\2', re.IGNORECASE | re.DOTALL)
_CONTENT_RE = re.compile(r'(\bcontent\s*=\s*)(["\'])(.*?)\2', re.IGNORECASE | re.DOTALL)

BLOCKED_HTML = {'admin.html'}
GOOGLE_VERIFY_RE = re.compile(r'^google[0-9a-f]+\.html$', re.IGNORECASE)
INFRA_PATHS = {
    'tools/seo_publish_guard.py',
    'tests/test_seo_publish_guard.py',
    '.github/workflows/seo-safe-publish-ci.yml',
}


def _attrs(tag: str) -> Dict[str, str]:
    return {name.lower(): value for name, _quote, value in _ATTR_RE.findall(tag)}


def _description_tags(source: str) -> List[re.Match[str]]:
    result: List[re.Match[str]] = []
    for match in _META_RE.finditer(source):
        if _attrs(match.group(0)).get('name', '').strip().lower() == 'description':
            result.append(match)
    return result


def _metadata_neutral(source: str) -> str:
    title_matches = list(_TITLE_RE.finditer(source))
    descriptions = _description_tags(source)
    if len(title_matches) != 1:
        raise ValueError('expected exactly one <title> tag')
    if len(descriptions) != 1:
        raise ValueError('expected exactly one meta description tag')

    result = _TITLE_RE.sub(r'\1__SEO_TITLE__\3', source, count=1)
    description = _description_tags(result)[0]
    tag = description.group(0)
    content_matches = list(_CONTENT_RE.finditer(tag))
    if len(content_matches) != 1:
        raise ValueError('expected exactly one content attribute on meta description')
    content_match = content_matches[0]
    neutral_tag = tag[:content_match.start(3)] + '__SEO_DESCRIPTION__' + tag[content_match.end(3):]
    return result[:description.start()] + neutral_tag + result[description.end():]


class _Snapshot(HTMLParser):
    STRUCTURAL = {
        'body', 'header', 'nav', 'main', 'section', 'article', 'aside', 'footer',
        'div', 'form', 'ul', 'ol', 'li', 'table', 'thead', 'tbody', 'tr', 'td', 'th',
    }

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.canonicals: List[str] = []
        self.robots: List[str] = []
        self.stylesheets: List[str] = []
        self.scripts: List[Tuple[Tuple[Tuple[str, str], ...], str]] = []
        self.h1s: List[str] = []
        self.assets: List[Tuple[str, str, str]] = []
        self.structure: List[str] = []
        self._inside_body = False
        self._inside_h1 = False
        self._h1_parts: List[str] = []
        self._inside_script = False
        self._script_attrs: Tuple[Tuple[str, str], ...] = ()
        self._script_parts: List[str] = []

    @staticmethod
    def _map(attrs):
        return {str(k).lower(): '' if v is None else str(v) for k, v in attrs}

    def handle_starttag(self, tag, attrs):
        tag = tag.lower()
        amap = self._map(attrs)
        rel = {x.lower() for x in amap.get('rel', '').split()}
        if tag == 'body':
            self._inside_body = True
        if self._inside_body and tag in self.STRUCTURAL:
            self.structure.append(f'<{tag}>')
        if tag == 'link' and 'canonical' in rel:
            self.canonicals.append(amap.get('href', ''))
        if tag == 'link' and 'stylesheet' in rel:
            self.stylesheets.append(amap.get('href', ''))
        if tag == 'meta' and amap.get('name', '').lower() == 'robots':
            self.robots.append(amap.get('content', ''))
        if tag == 'script':
            self._inside_script = True
            self._script_attrs = tuple(sorted((str(k).lower(), '' if v is None else str(v)) for k, v in attrs))
            self._script_parts = []
        if tag == 'h1':
            self._inside_h1 = True
            self._h1_parts = []
        if tag in {'img', 'source', 'video', 'audio', 'iframe'}:
            for name in ('src', 'srcset', 'poster'):
                if name in amap:
                    self.assets.append((tag, name, amap[name]))

    def handle_endtag(self, tag):
        tag = tag.lower()
        if tag == 'h1' and self._inside_h1:
            self.h1s.append(' '.join(''.join(self._h1_parts).split()))
            self._inside_h1 = False
        if tag == 'script' and self._inside_script:
            self.scripts.append((self._script_attrs, ''.join(self._script_parts)))
            self._inside_script = False
        if self._inside_body and tag in self.STRUCTURAL:
            self.structure.append(f'</{tag}>')
        if tag == 'body':
            self._inside_body = False

    def handle_data(self, data):
        if self._inside_h1:
            self._h1_parts.append(data)
        if self._inside_script:
            self._script_parts.append(data)


def _snapshot(source: str) -> _Snapshot:
    parser = _Snapshot()
    parser.feed(source)
    parser.close()
    return parser


def _edit_chars(before: str, after: str) -> int:
    total = 0
    for opcode, i1, i2, j1, j2 in difflib.SequenceMatcher(a=before, b=after, autojunk=False).get_opcodes():
        if opcode != 'equal':
            total += max(i2 - i1, j2 - j1)
    return total


def validate_html_change(before: str, after: str, *, max_edit_chars: int = 1024) -> Dict[str, object]:
    violations: List[str] = []
    old = _snapshot(before)
    new = _snapshot(after)

    checks = (
        ('canonical_changed', old.canonicals, new.canonicals),
        ('robots_changed', old.robots, new.robots),
        ('stylesheet_changed', old.stylesheets, new.stylesheets),
        ('script_changed', old.scripts, new.scripts),
        ('h1_changed', old.h1s, new.h1s),
        ('body_structure_changed', old.structure, new.structure),
        ('asset_reference_changed', old.assets, new.assets),
    )
    for name, previous, current in checks:
        if previous != current:
            violations.append(name)

    try:
        if _metadata_neutral(before) != _metadata_neutral(after):
            violations.append('non_metadata_change')
    except ValueError as exc:
        violations.append(str(exc))

    edit_chars = _edit_chars(before, after)
    if edit_chars > max_edit_chars:
        violations.append('diff_budget_exceeded')

    return {
        'safe': not violations,
        'violations': sorted(set(violations)),
        'edit_chars': edit_chars,
        'max_edit_chars': max_edit_chars,
    }


def _is_public_root_html(path: str) -> bool:
    p = Path(path)
    if p.parent != Path('.') or p.suffix.lower() != '.html':
        return False
    name = p.name
    if name in BLOCKED_HTML or GOOGLE_VERIFY_RE.match(name):
        return False
    return True


def validate_changed_paths(paths: Sequence[str], *, allow_infrastructure: bool = False) -> Dict[str, object]:
    normalized = [str(Path(p).as_posix()) for p in paths if str(p).strip()]
    html_paths = [p for p in normalized if p.lower().endswith('.html')]
    extras = [p for p in normalized if p not in html_paths]

    violations: List[str] = []
    if len(html_paths) != 1:
        violations.append('expected_exactly_one_html')
    elif not _is_public_root_html(html_paths[0]):
        violations.append('html_path_not_allowed')

    if extras:
        if not allow_infrastructure or any(p not in INFRA_PATHS for p in extras):
            violations.append('non_html_change')

    return {'safe': not violations, 'violations': violations, 'html_paths': html_paths, 'extra_paths': extras}


def _git(*args: str) -> str:
    completed = subprocess.run(['git', *args], check=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return completed.stdout


def _changed_paths(base_ref: str, head_ref: str) -> List[str]:
    output = _git('diff', '--name-only', f'{base_ref}...{head_ref}')
    return [line.strip() for line in output.splitlines() if line.strip()]


def _show(ref: str, path: str) -> str:
    return _git('show', f'{ref}:{path}')


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description='SEO自动发布安全门禁 / SEO safe publish guard')
    parser.add_argument('--base-ref', required=True)
    parser.add_argument('--head-ref', default='HEAD')
    parser.add_argument('--allow-infrastructure', action='store_true')
    args = parser.parse_args(argv)

    paths = _changed_paths(args.base_ref, args.head_ref)
    path_result = validate_changed_paths(paths, allow_infrastructure=args.allow_infrastructure)
    if not path_result['safe']:
        print(f"BLOCKED paths: {path_result}")
        return 2

    html_path = path_result['html_paths'][0]
    before = _show(args.base_ref, html_path)
    after = _show(args.head_ref, html_path)
    result = validate_html_change(before, after)
    if not result['safe']:
        print(f"BLOCKED html: {html_path} {result}")
        return 3

    print(f"PASS SAFE_AUTO html={html_path} edit_chars={result['edit_chars']}")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
