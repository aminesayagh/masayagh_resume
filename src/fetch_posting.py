#!/usr/bin/env python3
"""Read a job posting from its URL: title, company, description and location.

Usage: python3 src/fetch_posting.py URL

Most career sites (Greenhouse, Lever, Workday, Oracle, Ashby, many company sites) embed
a schema.org JobPosting block for search engines; this reads it. Pages that build it with
JavaScript are retried through headless Chrome. LinkedIn and some boards refuse automated
access: then paste the posting into src/new_job.py instead.
Also compares the job's location with template/default.json's contact location.
"""

import html
import html.parser
import json
import re
import shutil
import subprocess
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LD_JSON = re.compile(r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>', re.S | re.I)
# ponytail: only the codes seen so far; add a line when a posting shows a bare code.
COUNTRY_CODES = {"MA": "Morocco", "FR": "France", "US": "United States", "GB": "United Kingdom", "AE": "United Arab Emirates",
                 "SA": "Saudi Arabia", "DE": "Germany", "ES": "Spain", "NL": "Netherlands", "CA": "Canada", "SG": "Singapore"}


def download(url: str) -> str:
    request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (resume job-posting reader)",
                                                  "Accept-Language": "en-US,en;q=0.9"})
    with urllib.request.urlopen(request, timeout=20) as response:
        return response.read().decode(response.headers.get_content_charset() or "utf-8", "replace")


def render(url: str) -> str:
    browser = shutil.which("google-chrome")
    if browser is None:
        return ""
    result = subprocess.run([browser, "--headless", "--no-sandbox", "--disable-gpu", "--disable-dev-shm-usage",
                             "--virtual-time-budget=10000", "--dump-dom", url],
                            capture_output=True, text=True, timeout=60)
    return result.stdout


def find_posting(page: str) -> dict | None:
    def walk(node):
        if isinstance(node, list):
            for item in node:
                yield from walk(item)
        elif isinstance(node, dict):
            kind = node.get("@type")
            if kind == "JobPosting" or (isinstance(kind, list) and "JobPosting" in kind):
                yield node
            yield from walk(node.get("@graph", []))
    for block in LD_JSON.findall(page):
        try:
            found = next(walk(json.loads(html.unescape(block.strip()) if block.strip().startswith("&") else block)), None)
        except json.JSONDecodeError:
            continue
        if found:
            return found
    return None


class Microdata(html.parser.HTMLParser):
    """schema.org microdata (itemprop attributes), used by SAP SuccessFactors sites such as Capgemini.
    Keeps the first value of each property: <meta content> or the element's inner HTML."""
    VOID = {"meta", "br", "img", "input", "link", "hr"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.props, self.open = {}, []  # open: [prop, depth, parts] being captured

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        for capture in self.open:
            capture[2].append(self.get_starttag_text())
        prop = a.get("itemprop")
        if prop and "content" in a:
            self.props.setdefault(prop, a["content"])
        elif prop and "itemscope" not in a and tag not in self.VOID:
            self.open.append([prop, 0, []])
        if tag not in self.VOID:
            for capture in self.open:
                capture[1] += 1

    def handle_endtag(self, tag):
        if tag in self.VOID:
            return
        for capture in list(self.open):
            capture[1] -= 1
            if capture[1] == 0:
                self.open.remove(capture)
                self.props.setdefault(capture[0], "".join(capture[2]))
            else:
                capture[2].append(f"</{tag}>")

    def handle_data(self, data):
        for capture in self.open:
            capture[2].append(html.escape(data, quote=False))


def microdata_posting(page: str) -> dict | None:
    if 'schema.org/JobPosting' not in page:
        return None
    parser = Microdata()
    parser.feed(page)
    p = parser.props
    if not p.get("title"):
        return None
    return {"@type": "JobPosting", "title": to_text(p["title"]), "description": p.get("description", ""),
            "hiringOrganization": {"name": to_text(p.get("hiringOrganization", ""))},
            "jobLocation": {"address": {k: p[k] for k in ("streetAddress", "addressLocality", "addressCountry") if k in p}}}


def to_text(markup: str) -> str:
    markup = html.unescape(markup or "")
    markup = re.sub(r"(?i)<br\s*/?>|</(p|div|li|h[1-6]|ul|ol)>", "\n", markup)
    markup = re.sub(r"(?i)<li[^>]*>", "- ", markup)
    text = html.unescape(re.sub(r"<[^>]+>", "", markup))
    text = "\n".join(line.strip() for line in text.splitlines())
    text = re.sub(r"^- *\n\s*", "- ", text, flags=re.M)  # <li><p>text</p></li> left the bullet alone on its line
    return re.sub(r"\n\s*\n+", "\n\n", text).strip()


def locations(posting: dict) -> list[dict]:
    places = posting.get("jobLocation") or []
    out = []
    for place in places if isinstance(places, list) else [places]:
        address = place.get("address", {}) if isinstance(place, dict) else {}
        if isinstance(address, str):
            out.append({"city": address, "country": ""})
            continue
        country = address.get("addressCountry", "")
        country = country.get("name", "") if isinstance(country, dict) else country
        city = address.get("addressLocality", "")
        if not city and not country and address.get("streetAddress"):  # "Casablanca, MA"
            city, _, country = address["streetAddress"].rpartition(", ")
        out.append({"city": city, "country": COUNTRY_CODES.get(country, country)})
    return out


def compare_location(places: list[dict], remote: bool, mine: str) -> str:
    """'Casablanca, Morocco' vs the posting's places -> a one-line verdict."""
    city, _, country = (part.strip().casefold() for part in mine.rpartition(","))
    if not places:
        return "remote: check which countries it accepts" if remote else "unknown: the posting gives no location"
    if remote:
        return "remote, listed in " + compare_location(places, False, mine)
    if any(p["city"].casefold() == city for p in places):
        return "same city"
    if any(p["country"].casefold() == country for p in places):
        return "same country, different city"
    return "different country: check relocation or work authorization"


def greenhouse(url: str) -> dict | None:
    """Greenhouse boards no longer embed JobPosting data; their public API has the same fields."""
    match = re.search(r"greenhouse\.io/(?:embed/job_app\?for=)?([\w-]+)/jobs/(\d+)", url)
    if not match:
        return None
    job = json.loads(download(f"https://boards-api.greenhouse.io/v1/boards/{match[1]}/jobs/{match[2]}"))
    city, _, country = job.get("location", {}).get("name", "").rpartition(", ")
    return {"@type": "JobPosting", "title": job.get("title", ""), "description": job.get("content", ""),
            "hiringOrganization": {"name": job.get("company_name", match[1])},
            "jobLocation": {"address": {"addressLocality": city or country, "addressCountry": country if city else ""}}}


def oracle_hcm(url: str, page: str) -> dict | None:
    """Oracle Recruiting Cloud sites (careers.oracle.com and many other employers) load the job
    with JavaScript from <host>/hcmRestApi; the page names the host and the site number."""
    host = re.search(r"(https://[\w.-]+\.oraclecloud\.com)(?::443)?/hcm", page)
    site = re.search(r"siteNumber=(\w+)", page)
    job_id = re.search(r"/job/(\d+)", url)
    if not (host and site and job_id):
        return None
    api = (f"{host[1]}/hcmRestApi/resources/latest/recruitingCEJobRequisitionDetails?expand=all&onlyData=true"
           f"&finder=ById;Id=%22{job_id[1]}%22,siteNumber={site[1]}")
    items = json.loads(download(api)).get("items") or [{}]
    job = items[0]
    if not job.get("Title"):
        return None
    city, _, country = (job.get("PrimaryLocation") or "").rpartition(", ")
    # ponytail: company = the site's domain owner; fine for careers.oracle.com, override with --company elsewhere
    company = re.search(r"https://(?:[\w-]+\.)*?([\w-]+)\.\w+/", url)[1].title()
    body = "".join(job.get(k) or "" for k in ("ExternalDescriptionStr", "ExternalResponsibilitiesStr", "ExternalQualificationsStr"))
    return {"@type": "JobPosting", "title": job["Title"], "description": body, "hiringOrganization": {"name": company},
            "jobLocation": {"address": {"addressLocality": city.title(), "addressCountry": country}}}


def fetch(url: str) -> dict:
    if "linkedin.com/" in url and "_l=" not in url:  # local subdomains (ma.linkedin.com) answer in the local language
        url += ("&" if "?" in url else "?") + "_l=en_US"
    page = "" if "greenhouse.io/" in url else download(url)
    posting = greenhouse(url) or find_posting(page) or microdata_posting(page) or oracle_hcm(url, page) or find_posting(render(url))
    if posting is None:
        sys.exit(f"No job data found at {url} (the site may block automated access). Paste the posting into src/new_job.py instead.")
    org = posting.get("hiringOrganization") or {}
    places = locations(posting)
    remote = posting.get("jobLocationType") == "TELECOMMUTE"
    mine = json.loads((ROOT / "template" / "default.json").read_text(encoding="utf-8"))["contact"]["location"]
    where = "; ".join(", ".join(x for x in (p["city"], p["country"]) if x) for p in places) or ("Remote" if remote else "")
    return {"url": url, "title": html.unescape(posting.get("title", "")).strip(),
            "company": html.unescape(org.get("name", "") if isinstance(org, dict) else str(org)).strip(),
            "location": where, "location_match": compare_location(places, remote, mine),
            "description": to_text(posting.get("description", ""))}


_SAMPLE = '''<script type="application/ld+json">{"@type":"JobPosting","title":"Engineer",
"hiringOrganization":{"name":"Acme"},"description":"&lt;p&gt;Build &amp;amp; ship&lt;/p&gt;&lt;ul&gt;&lt;li&gt;APIs&lt;/li&gt;&lt;/ul&gt;",
"jobLocation":{"address":{"addressLocality":"Rabat","addressCountry":"MA"}}}</script>'''
assert find_posting(_SAMPLE)["title"] == "Engineer"
_MICRO = ('<div itemscope itemtype="http://schema.org/JobPosting"><span itemprop="title">Dev</span>'
          '<meta itemprop="hiringOrganization" content="Capgemini"><span itemprop="jobLocation" itemscope>'
          '<meta itemprop="streetAddress" content="Casablanca, MA"></span>'
          '<span itemprop="description"><p>Build <span>APIs</span></p><br><ul><li>Java</li></ul></span></div>')
assert microdata_posting(_MICRO)["title"] == "Dev"
assert to_text(microdata_posting(_MICRO)["description"]) == "Build APIs\n\n- Java"
assert compare_location(locations(microdata_posting(_MICRO)), False, "Casablanca, Morocco") == "same city"
assert to_text(find_posting(_SAMPLE)["description"]) == "Build & ship\n- APIs"
assert compare_location(locations(find_posting(_SAMPLE)), False, "Casablanca, Morocco") == "same country, different city"

if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    job = fetch(sys.argv[1])
    print(f"Title:    {job['title']}\nCompany:  {job['company']}\nLocation: {job['location'] or 'not given'} "
          f"({job['location_match']})\n\n{job['description']}")
