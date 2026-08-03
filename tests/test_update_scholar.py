import unittest
from urllib.error import HTTPError

from scripts import update_scholar


VALID_PROFILE_HTML = b"""
<html>
  <head><meta name="description" content="Cited by 42"></head>
  <body>
    <table>
      <tr class="gsc_a_tr">
        <td><a class="gsc_a_at" href="/citations?view_op=view_citation&amp;user=test">A Test Paper</a></td>
        <td><a class="gsc_a_ac">7</a></td>
        <td><span class="gsc_a_h">2026</span></td>
      </tr>
    </table>
  </body>
</html>
"""


class FakeResponse:
    def __init__(self, payload):
        self.payload = payload

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback):
        return False

    def read(self):
        return self.payload


class FetchProfileTests(unittest.TestCase):
    def test_uses_translate_fallback_when_direct_scholar_is_forbidden(self):
        requested_urls = []

        def fake_urlopen(request, timeout):
            requested_urls.append(request.full_url)
            if request.full_url == update_scholar.PROFILE_URL:
                raise HTTPError(request.full_url, 403, "Forbidden", {}, None)
            return FakeResponse(VALID_PROFILE_HTML)

        parser = update_scholar.fetch_profile(opener=fake_urlopen)

        self.assertEqual([paper["title"] for paper in parser.rows], ["A Test Paper"])
        self.assertEqual(requested_urls, list(update_scholar.FETCH_URLS))

    def test_canonicalizes_translate_proxy_publication_links(self):
        translated_html = b"""
        <tr class="gsc_a_tr">
          <a class="gsc_a_at" href="https://scholar-google-com.translate.goog/citations?view_op=view_citation&amp;user=test&amp;_x_tr_sl=auto&amp;_x_tr_tl=en">A Test Paper</a>
        </tr>
        """
        parser = update_scholar.ScholarParser()

        parser.feed(translated_html.decode())

        scholar_url = parser.rows[0]["scholar_url"]
        self.assertTrue(scholar_url.startswith("https://scholar.google.com/citations?"))
        self.assertNotIn("_x_tr_", scholar_url)


if __name__ == "__main__":
    unittest.main()
