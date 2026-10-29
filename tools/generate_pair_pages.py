#!/usr/bin/env python3
"""
Generates passport -> destination pages for the top destinations:
  /visastay/passports/<passport>/<dest>/index.html
Answers "Do <demonym> need a visa for <country>?" from the DB rule.

Data: tools/data/pairs.json (bridge supabase.sql_read of countries for PAIR_DESTS:
code, name, sz (schengen_zone), rules[{p,e,m,x,xd,me,n,cond}]), tools/passport_meta.json.
Official links: VisaStay app repo lib/app/utils/visa_info_urls.dart (VISASTAY_REPO env).
Also rewrites the passport-page sitemap block. Run after generate_passport_pages.py:
  DATA_DATE="October 2026" python3 tools/generate_pair_pages.py
"""
import json, os, re, html

TOOLS = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.abspath(os.path.join(TOOLS, ".."))
APP = os.environ.get("VISASTAY_REPO", os.path.join(SITE, "..", "..", "VisaStay"))
DATA_DATE = os.environ.get("DATA_DATE", "")
TODAY = os.environ.get("SITEMAP_DATE", "2026-10-29")

import generate_passport_pages as gp  # reuse template chrome, FREE_MOVEMENT, META

PAIR_DESTS = ["TH", "ID", "VN", "MY", "PH", "JP", "KR", "SG", "AE", "TR", "GE",
              "PT", "ES", "IT", "FR", "GB", "US", "MX", "CO", "BR"]
META = gp.META
dests = {d["code"]: d for d in json.load(open(os.path.join(TOOLS, "data", "pairs.json"), encoding="utf-8"))}

# official info URLs from the app
s = open(os.path.join(APP, "lib/app/utils/visa_info_urls.dart"), encoding="utf-8").read()
body = s[s.index("{", s.index("static const Map<String, String> _urls")):]
body = body[:body.index("};")]
URLS = {c: u for c, u in re.findall(r"'([A-Z]{2})'\s*:\s*'([^']+)'", body, re.S) if "wikipedia" not in u}

INTERNAL = re.compile(r"tier-?\d|source:|wikipedia|reclassif|modell?ed|audit|corrected|cross-?check|fetch|"
                      r"this session|verified 20|sherpa|visalist|embassies\.net|passport ?index|timatic|\bTODO\b|"
                      r"^\s*(eVisa|ETA|Visa)[^.;]*$", re.I)

T = gp.PAGE_TEMPLATE
NAV = T[T.index("<nav class=\"site-nav\">"):T.index("<section class=\"hero\">")]
FOOTER = T[T.index("<footer class=\"site-footer\">"):T.index("</footer>") + len("</footer>")]
E = html.escape


def cap(s): return s[:1].upper() + s[1:]


THE = {"United Kingdom", "United States", "United Arab Emirates", "Philippines", "Netherlands", "Czech Republic"}


def the(name): return f"the {name}" if name in THE else name


def answer(meta, country, r):
    dem, e = meta["demonym"], r["e"]
    if meta.get("_fm"):
        return ("No visa needed (freedom of movement)",
                f"No. {cap(dem)} have freedom of movement in {country} as EU/EEA/Swiss citizens, so no visa is needed and there is no fixed limit on visits. Longer stays may need local registration.",
                999)
    m = int(r["m"]) if (r.get("m") or "").isdigit() else 0
    stay = "with no fixed time limit" if m >= 999 else f"for up to {m} days"
    if e == "visa_exempt":
        short, a = "No visa needed", f"No. {cap(dem)} can enter {country} visa-free {stay}."
    elif e == "visa_on_arrival":
        short, a = "Visa on arrival", f"{cap(dem)} can get a visa on arrival in {country}, valid {stay}."
    elif e == "evisa":
        short, a = "eVisa required", f"Yes. {cap(dem)} need an eVisa, applied for online before travelling to {country}. It allows stays {stay}."
    elif e == "eta":
        short, a = "Travel authorisation required", f"No visa, but {dem} need an electronic travel authorisation before travelling to {country}. Stays are allowed {stay}."
    else:
        short, a = "Visa required", f"Yes. {cap(dem)} need a visa issued by an embassy or consulate of {country} before travelling."
    if e != "visa_required" and m < 999:
        if r.get("x") and r.get("xd"):
            a += f" The stay can be extended by up to {r['xd']} days."
        else:
            a += " An extension is not confirmed, so plan to leave within the permitted stay."
    return short, a, m


def page(pp, dc):
    meta, d = META[pp], dests[dc]
    r = next((x for x in d["rules"] if x["p"] == pp), None)
    if not r or pp == dc:
        return None
    country = the(d["name"])
    fm = pp in gp.FREE_MOVEMENT and dc in gp.FREE_MOVEMENT
    short, ans, m = answer(dict(meta, _fm=fm), country, r)
    schengen = d.get("sz") and pp not in gp.FREE_MOVEMENT
    extras = [t for t in [r.get("n")] + [c for c in (r.get("cond") or []) if isinstance(c, str)]
              if t and not INTERNAL.search(t)]
    url = f"https://headfirstservices.com/visastay/passports/{pp.lower()}/{dc.lower()}/"
    q1 = f"Do {meta['demonym']} need a visa for {country}?"
    faqs = [(q1, ans)]
    if schengen:
        faqs.append((f"Does the Schengen 90/180 rule apply to {meta['demonym']} in {country}?",
                     f"Yes. {country} is in the Schengen Area, so days spent there count toward the 90 days in any rolling 180-day period across the whole area."))
    faqs.append(("Is this legal advice?", "No. This is a planning reference, not legal or immigration advice. Always confirm current requirements with official government sources before you travel."))
    ld_faq = {"@context": "https://schema.org", "@type": "FAQPage",
              "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faqs]}
    ld_bc = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "VisaStay", "item": "https://headfirstservices.com/visastay/"},
        {"@type": "ListItem", "position": 2, "name": f"{meta['name']} Passport", "item": f"https://headfirstservices.com/visastay/passports/{pp.lower()}/"},
        {"@type": "ListItem", "position": 3, "name": country, "item": url}]}
    stay_txt = "No limit" if m >= 999 else (f"{m} days" if m and r["e"] != "visa_required" else "Set by your visa")
    ext_txt = "Not needed" if fm else (f"Yes, up to {r['xd']} days" if r.get("x") and r.get("xd") else "Not confirmed")
    rows = [("Entry", short), ("Maximum stay", stay_txt), ("Extension", ext_txt)]
    if r.get("me") == "true" and r["e"] != "visa_required":
        rows.append(("Multiple entries", "Allowed"))
    official = URLS.get(dc)
    others_d = " · ".join(f'<a href="/visastay/passports/{pp.lower()}/{x.lower()}/">{E(dests[x]["name"])}</a>'
                          for x in PAIR_DESTS if x != dc and x != pp and x in dests)
    others_p = " · ".join(f'<a href="/visastay/passports/{x.lower()}/{dc.lower()}/">{E(META[x]["name"])}</a>'
                          for x in ["US", "GB", "CA", "AU", "DE", "FR", "IN", "CN", "JP", "BR"] if x != pp and x != dc and x in META)
    title = f"Do {cap(meta['demonym'])} Need a Visa for {country}? {meta['name']} Passport Rules | VisaStay"
    desc = ans[:155]
    out = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{E(title)}</title>
<meta name="description" content="{E(desc)}">
<link rel="canonical" href="{url}">
<link rel="icon" href="/assets/img/visastay-icon.png">
<link rel="stylesheet" href="/assets/css/style.css">
<meta property="og:type" content="article">
<meta property="og:title" content="{E(q1)}">
<meta property="og:description" content="{E(desc)}">
<meta property="og:url" content="{url}">
<script type="application/ld+json">{json.dumps(ld_bc, ensure_ascii=False)}</script>
<script type="application/ld+json">{json.dumps(ld_faq, ensure_ascii=False)}</script>
</head>
<body>

{NAV}<section class="hero">
  <div class="container">
    <a class="back-link" href="/visastay/passports/{pp.lower()}/">← {E(meta['name'])} passport</a>
    <span class="eyebrow">{E(meta['flag'])} {E(meta['name'])} passport → {E(country)}</span>
    <h1>{E(q1)}</h1>
    <p class="lede">{E(ans)}</p>
  </div>
</section>

<section>
  <div class="container" style="max-width:820px;">
    <div style="overflow-x:auto;">
    <table style="width:100%; border-collapse:collapse; font-size:16px; margin-bottom:20px;">
      <tbody>
{chr(10).join(f'        <tr style="border-bottom:1px solid var(--color-border);"><th style="text-align:left; padding:10px 8px; width:40%;">{k}</th><td style="padding:10px 8px;">{E(v)}</td></tr>' for k, v in rows)}
      </tbody>
    </table>
    </div>
{''.join(f'    <p>{E(t)}</p>{chr(10)}' for t in extras)}{'    <div class="note-box" style="margin:20px 0;"><strong>Schengen:</strong> ' + E(country) + ' is in the Schengen Area. Days here count toward the 90 days in any rolling 180-day period across the whole area. <a href="/visastay/schengen-90-180-rule/">Read the guide →</a></div>' + chr(10) if schengen else ''}{f'    <p>Official information: <a href="{E(official)}" rel="nofollow noopener" target="_blank">{E(official)}</a></p>{chr(10)}' if official else ''}
    <div class="note-box" style="margin:24px 0;">
      {('Data last updated ' + DATA_DATE + '. ') if DATA_DATE else ''}Checked against official government immigration sources and reviewed on a rolling basis (<a href="/visastay/sources/">sources</a>). This is a planning reference, not legal or immigration advice. Entry rules change; confirm with official sources before you travel. VisaStay is independent and not affiliated with any government.
    </div>

    <div class="cta-banner" style="margin-top:24px;">
      <h2>Track your days in {E(country)} automatically</h2>
      <p>VisaStay counts your days per country, warns before your stay runs out, and handles the Schengen 90/180 rule for your passport.</p>
      <a href="/visastay/" class="btn btn-primary">See VisaStay →</a>
    </div>

    <h2>Other destinations for {E(meta['name'])} passport holders</h2>
    <p>{others_d}</p>
    <h2>Other passports visiting {E(country)}</h2>
    <p>{others_p}</p>
  </div>
</section>

{FOOTER}

</body>
</html>
"""
    os.makedirs(os.path.join(gp.OUT_ROOT, pp.lower(), dc.lower()), exist_ok=True)
    open(os.path.join(gp.OUT_ROOT, pp.lower(), dc.lower(), "index.html"), "w", encoding="utf-8").write(out)
    return url


def main():
    urls = []
    for pp in sorted(META):
        for dc in PAIR_DESTS:
            if dc in dests:
                u = page(pp, dc)
                if u: urls.append(u)
    # sitemap: replace all passport URLs (passport pages + pairs)
    sm = os.path.join(SITE, "sitemap.xml")
    x = open(sm, encoding="utf-8").read()
    x = re.sub(r"\s*<url>\s*<loc>https://headfirstservices.com/visastay/passports/.*?</url>", "", x, flags=re.S)
    def entry(u, pr): return f"  <url>\n    <loc>{u}</loc>\n    <lastmod>{TODAY}</lastmod>\n    <changefreq>monthly</changefreq>\n    <priority>{pr}</priority>\n  </url>\n"
    add = "".join(entry(f"https://headfirstservices.com/visastay/passports/{c.lower()}/", "0.6") for c in sorted(META))
    add += "".join(entry(u, "0.5") for u in urls)
    x = x.replace("</urlset>", add + "</urlset>")
    open(sm, "w", encoding="utf-8").write(x)
    print(f"OK   {len(urls)} pair pages; sitemap {x.count('<loc>')} URLs")


if __name__ == "__main__":
    main()
