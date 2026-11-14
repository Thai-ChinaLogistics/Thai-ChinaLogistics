import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.check_visible_internal_tokens import check_html_text, check_public_pages


class VisibleInternalTokenTests(unittest.TestCase):
    def test_customer_visible_policy_identifiers_are_rejected(self):
        html = ('<html><head><script>let x="ALLOWED_INTERNAL_CODE";</script></head>'
                '<body><p>Requires FOOD_REVIEW_REQUIRED approval</p></body></html>')
        self.assertEqual(check_html_text(html), ['FOOD_REVIEW_REQUIRED'])

    def test_hidden_script_style_and_comments_are_not_customer_visible(self):
        html = ('<html><body><!-- COMMERCIAL_IMPORT -->'
                '<script>SEARCH_INTENT_ONLY</script>'
                '<style>.x{content:"SAFE_AUTO"}</style>'
                '<div>泰国寄中国需先审核货物和线路。</div></body></html>')
        self.assertEqual(check_html_text(html), [])

    def test_no_public_html_body_contains_internal_policy_markers(self):
        failures = check_public_pages(ROOT)
        self.assertEqual(failures, {}, str(failures))


if __name__ == '__main__':
    unittest.main()
