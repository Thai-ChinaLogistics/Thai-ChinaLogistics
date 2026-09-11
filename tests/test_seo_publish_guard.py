import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))

from seo_publish_guard import validate_html_change, validate_changed_paths


BEFORE = '''<!doctype html>
<html><head>
<title>Old title</title>
<meta name="description" content="Old description">
<meta name="robots" content="index,follow">
<link rel="canonical" href="https://example.com/page.html">
<link rel="stylesheet" href="site.css">
<script src="site.js"></script>
</head><body><main><h1>Stable H1</h1><section><p>Body</p></section></main></body></html>
'''


class SeoPublishGuardTests(unittest.TestCase):
    def test_allows_metadata_only_change(self):
        after = BEFORE.replace('Old title', 'New title').replace('Old description', 'New description')
        result = validate_html_change(BEFORE, after)
        self.assertTrue(result['safe'])
        self.assertEqual(result['violations'], [])

    def test_blocks_canonical_change(self):
        after = BEFORE.replace('https://example.com/page.html', 'https://evil.example/page.html')
        result = validate_html_change(BEFORE, after)
        self.assertFalse(result['safe'])
        self.assertIn('canonical_changed', result['violations'])

    def test_blocks_h1_or_script_change(self):
        after = BEFORE.replace('Stable H1', 'Changed H1').replace('site.js', 'other.js')
        result = validate_html_change(BEFORE, after)
        self.assertFalse(result['safe'])
        self.assertIn('h1_changed', result['violations'])
        self.assertIn('script_changed', result['violations'])

    def test_blocks_body_structure_change(self):
        after = BEFORE.replace('<section><p>Body</p></section>', '<section><div><p>Body</p></div></section>')
        result = validate_html_change(BEFORE, after)
        self.assertFalse(result['safe'])
        self.assertIn('body_structure_changed', result['violations'])

    def test_changed_paths_allow_exactly_one_public_html(self):
        self.assertEqual(validate_changed_paths(['china-to-thailand.html'])['safe'], True)
        self.assertEqual(validate_changed_paths(['china-to-thailand.html', 'seo-pages.css'])['safe'], False)
        self.assertEqual(validate_changed_paths(['admin.html'])['safe'], False)
        self.assertEqual(validate_changed_paths(['google744716665e019d1a.html'])['safe'], False)
        self.assertEqual(validate_changed_paths(['folder/page.html'])['safe'], False)

    def test_bootstrap_mode_allows_only_guard_infrastructure_without_html(self):
        infrastructure = [
            '.github/workflows/seo-safe-publish-ci.yml',
            'tests/test_seo_publish_guard.py',
            'tools/seo_publish_guard.py',
        ]
        self.assertTrue(validate_changed_paths(infrastructure, allow_infrastructure=True)['safe'])
        self.assertFalse(validate_changed_paths(infrastructure + ['seo-pages.css'], allow_infrastructure=True)['safe'])


if __name__ == '__main__':
    unittest.main()
