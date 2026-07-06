#!/usr/bin/env python3
"""
Generates static passport visa-requirement pages for the VisaStay site.

Single source of truth: tools/data/<CODE>.json (pulled fresh from Supabase
`countries.visa_rules_json` via the generate script's data-pull step) plus
tools/passport_meta.json (stable per-passport metadata: name/demonym/flag/
Schengen-subject flag).

To refresh a page after visa data changes in the DB:
  1. Re-pull tools/data/<CODE>.json from Supabase (countries table, filtered
     to that passport_code).
  2. Re-run this script: `python3 generate_passport_pages.py`
It regenerates every page found in tools/data/ from this one template --
no page is ever hand-edited directly.

Output: ../visastay/passports/<code-lowercase>/index.html
"""
import json
import os

TOOLS_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(TOOLS_DIR, "data")
SITE_DIR = os.path.abspath(os.path.join(TOOLS_DIR, ".."))
OUT_ROOT = os.path.join(SITE_DIR, "visastay", "passports")

with open(os.path.join(TOOLS_DIR, "passport_meta.json"), encoding="utf-8") as f:
    META = json.load(f)

ENTRY_LABELS = {
    "visa_exempt": "Visa-free",
    "eta": "eTA required",
    "evisa": "eVisa",
    "visa_on_arrival": "Visa on arrival",
    "visa_required": "Visa required",
}

PAGE_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>⟦TITLE⟧</title>
<meta name="description" content="⟦META_DESC⟧">
<link rel="canonical" href="⟦CANONICAL⟧">
<link rel="icon" href="/assets/img/visastay-icon.png">
<link rel="stylesheet" href="/assets/css/style.css">

<meta property="og:type" content="website">
<meta property="og:title" content="⟦OG_TITLE⟧">
<meta property="og:description" content="⟦OG_DESC⟧">
<meta property="og:url" content="⟦CANONICAL⟧">

<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "BreadcrumbList",
  "itemListElement": [
    { "@type": "ListItem", "position": 1, "name": "Home", "item": "https://headfirstservices.com/" },
    { "@type": "ListItem", "position": 2, "name": "VisaStay", "item": "https://headfirstservices.com/visastay/" },
    { "@type": "ListItem", "position": 3, "name": "Supported Passports", "item": "https://headfirstservices.com/visastay/supported-passports/" },
    { "@type": "ListItem", "position": 4, "name": "⟦NAME⟧ Passport", "item": "⟦CANONICAL⟧" }
  ]
}
</script>

<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "How many countries can ⟦DEMONYM⟧ visit visa-free?",
      "acceptedAnswer": { "@type": "Answer", "text": "⟦FAQ1_ANSWER⟧" }
    },
    {
      "@type": "Question",
      "name": "Does the Schengen 90/180-day rule apply to ⟦DEMONYM⟧?",
      "acceptedAnswer": { "@type": "Answer", "text": "⟦FAQ2_ANSWER⟧" }
    },
    {
      "@type": "Question",
      "name": "Is this visa information legal advice?",
      "acceptedAnswer": { "@type": "Answer", "text": "No. This page is a planning reference, not legal or immigration advice. Visa rules change, and you should always confirm current requirements with the relevant embassy or consulate before you travel." }
    }
  ]
}
</script>
</head>
<body>

<nav class="site-nav">
  <div class="container">
    <a class="brand-mark" href="/">
      <span class="mono">HF</span>
      HeadFirst Services
    </a>
    <div class="nav-links">
      <a href="/visastay/">VisaStay</a>
      <a href="/visastay/faq/">FAQ</a>
      <a href="/visastay/supported-passports/" class="nav-cta">All passports</a>
    </div>
  </div>
</nav>

<section class="hero">
  <div class="container">
    <a class="back-link" href="/visastay/supported-passports/">← Supported Passports</a>
    <span class="eyebrow">Passport Guide</span>
    <h1>⟦FLAG⟧ ⟦NAME⟧ passport visa requirements</h1>
    <p class="lede">Where ⟦DEMONYM⟧ can travel visa-free, get an eVisa, visa on arrival, or need a visa in advance — across all ⟦TOTAL⟧ destinations tracked in VisaStay.</p>
  </div>
</section>

<section>
  <div class="container" style="max-width:900px;">

    <p>⟦INTRO_PARAGRAPH⟧</p>

    <div class="grid grid-3" style="margin:20px 0;">
      <div class="card">
        <h3>⟦VISA_FREE_COUNT⟧</h3>
        <p>Visa-free destinations</p>
      </div>
      <div class="card">
        <h3>⟦EASY_COUNT⟧</h3>
        <p>Via eTA, eVisa, or visa on arrival</p>
      </div>
      <div class="card">
        <h3>⟦REQUIRED_COUNT⟧</h3>
        <p>Require a visa in advance</p>
      </div>
    </div>

    ⟦SCHENGEN_NOTE⟧

    <h2>Full destination list</h2>
    <p style="color:var(--color-text-muted); font-size:14px;">Search to filter by country name.</p>
    <input type="text" id="passport-filter" placeholder="Search destinations…" style="width:100%; max-width:360px; padding:10px 14px; margin-bottom:16px; border:1px solid var(--color-border); border-radius:8px; font-size:15px;">

    <div style="overflow-x:auto;">
    <table id="passport-table" style="width:100%; border-collapse:collapse; font-size:15px;">
      <thead>
        <tr style="text-align:left; border-bottom:2px solid var(--color-border);">
          <th style="padding:10px 8px;">Destination</th>
          <th style="padding:10px 8px;">Entry Type</th>
          <th style="padding:10px 8px;">Max Stay</th>
          <th style="padding:10px 8px;">Extension</th>
        </tr>
      </thead>
      <tbody>
⟦TABLE_ROWS⟧
      </tbody>
    </table>
    </div>

    <div class="note-box" style="margin:24px 0;">
      Visa rules are provided for planning purposes and are not legal or immigration advice. Entry requirements can change without notice — always confirm current requirements with the relevant embassy or consulate before you travel.
    </div>

    <h2>Common questions</h2>
    <div class="faq-item">
      <h3>How many countries can ⟦DEMONYM⟧ visit visa-free?</h3>
      <p>⟦FAQ1_ANSWER⟧</p>
    </div>
    <div class="faq-item">
      <h3>Does the Schengen 90/180-day rule apply to ⟦DEMONYM⟧?</h3>
      <p>⟦FAQ2_ANSWER⟧ <a href="/visastay/schengen-90-180-rule/">Read the full Schengen guide →</a></p>
    </div>
    <div class="faq-item">
      <h3>Is this visa information legal advice?</h3>
      <p>No. This page is a planning reference, not legal or immigration advice. Visa rules change, and you should always confirm current requirements with the relevant embassy or consulate before you travel.</p>
    </div>

    <div class="cta-banner" style="margin-top:24px;">
      <h2>Track every trip automatically</h2>
      <p>VisaStay calculates your exact visa-free days, Schengen window, and tax residency threshold per passport — no manual lookups.</p>
      <a href="/visastay/" class="btn btn-primary">See VisaStay →</a>
    </div>

    <p style="margin-top:24px; color:var(--color-text-muted); font-size:15px;">Related: see <a href="/visastay/supported-passports/">all supported passports</a>, or check the <a href="/visastay/faq/">full FAQ</a>.</p>

  </div>
</section>

<footer class="site-footer">
  <div class="container">
    <div class="footer-grid">
      <div>
        <h4>VisaStay</h4>
        <p style="color:var(--color-text-muted); font-size:14px; max-width:32ch;">Part of the Digital Nomad Essentials suite by HeadFirst Services.</p>
      </div>
      <div>
        <h4>Guides</h4>
        <ul>
          <li><a href="/visastay/faq/">FAQ</a></li>
          <li><a href="/visastay/schengen-90-180-rule/">Schengen 90/180 Rule</a></li>
          <li><a href="/visastay/tax-residency-183-day-rule/">Tax Residency (183-Day Rule)</a></li>
          <li><a href="/visastay/supported-passports/">Supported Passports</a></li>
        </ul>
      </div>
      <div>
        <h4>Suite</h4>
        <ul>
          <li><a href="/">HeadFirst Services</a></li>
          <li><a href="/packlite/">PackLite</a></li>
        </ul>
      </div>
      <div>
        <h4>Legal</h4>
        <ul>
          <li><a href="https://gregtaylorx.github.io/privacy.html">Privacy Policy</a></li>
          <li><a href="https://gregtaylorx.github.io/delete-account.html">Delete Account</a></li>
        </ul>
      </div>
    </div>
    <div class="footer-bottom">
      <span>&copy; 2026 HeadFirst Services. All rights reserved.</span>
      <span>support@headfirstservices.com</span>
    </div>
  </div>
</footer>

<script>
document.getElementById('passport-filter').addEventListener('input', function(e) {
  var q = e.target.value.toLowerCase();
  document.querySelectorAll('#passport-table tbody tr').forEach(function(row) {
    row.style.display = row.dataset.name.indexOf(q) === -1 ? 'none' : '';
  });
});
</script>

</body>
</html>
"""


def entry_label(e):
    return ENTRY_LABELS.get(e, e)


def build_row(dest):
    name = dest["n"]
    entry = dest["e"]
    m = dest.get("m")
    extendable = dest.get("x")
    xd = dest.get("xd")

    if entry == "visa_required" or not m or m == "0":
        stay = "—"
    else:
        stay = f"{m} days"

    if extendable:
        ext = f"Yes (+{xd} days)" if xd else "Yes"
    else:
        ext = "No"

    return (
        f'        <tr data-name="{name.lower()}" style="border-bottom:1px solid var(--color-border);">'
        f'<td style="padding:8px;">{name}</td>'
        f'<td style="padding:8px;">{entry_label(entry)}</td>'
        f'<td style="padding:8px;">{stay}</td>'
        f'<td style="padding:8px;">{ext}</td>'
        f'</tr>'
    )


def generate(code):
    meta = META.get(code)
    if not meta:
        print(f"SKIP {code}: no metadata in passport_meta.json")
        return

    with open(os.path.join(DATA_DIR, f"{code}.json"), encoding="utf-8") as f:
        destinations = json.load(f)

    # Exclude the passport's own home-country row (placeholder data, not a real destination)
    destinations = [d for d in destinations if d["c"] != code]
    destinations.sort(key=lambda d: d["n"])

    visa_free = sum(1 for d in destinations if d["e"] == "visa_exempt")
    easy = sum(1 for d in destinations if d["e"] in ("eta", "evisa", "visa_on_arrival"))
    required = sum(1 for d in destinations if d["e"] == "visa_required")
    total = len(destinations)

    name = meta["name"]
    demonym = meta["demonym"]
    flag = meta["flag"]
    schengen_subject = meta["schengen_subject"]
    slug = code.lower()
    canonical = f"https://headfirstservices.com/visastay/passports/{slug}/"

    intro = (
        f"VisaStay tracks visa requirements for {demonym} across {total} destinations worldwide. "
        f"Below is the full breakdown by entry type and maximum stay, plus the two rules that catch "
        f"long-term travelers most often: the Schengen 90/180-day window and the 183-day tax residency threshold."
    )

    faq1 = (
        f"Of the {total} destinations tracked in VisaStay, {visa_free} allow {demonym} to enter completely "
        f"visa-free. Another {easy} are accessible via a fast eTA, eVisa, or visa on arrival, and {required} "
        f"require a visa arranged in advance."
    )

    if schengen_subject:
        faq2 = (
            f"Yes. {demonym.capitalize()} are limited to 90 days within any rolling 180-day period across "
            f"the entire Schengen Area — it's not a per-country allowance."
        )
        schengen_note = (
            '<div class="note-box" style="margin:20px 0;">'
            f'<strong>Schengen travelers:</strong> {demonym} are subject to the 90/180-day rule across the whole '
            'Schengen Area, not per country. '
            '<a href="/visastay/schengen-90-180-rule/">Read the full guide →</a>'
            '</div>'
        )
    else:
        faq2 = (
            f"No. {demonym.capitalize()} have freedom-of-movement rights within the EU/EEA and Switzerland, "
            f"so the 90/180-day limit that applies to non-EU visitors does not apply here."
        )
        schengen_note = (
            '<div class="note-box" style="margin:20px 0;">'
            f'<strong>Schengen travelers:</strong> {demonym} are not subject to the 90/180-day rule within the '
            'EU/EEA/Switzerland thanks to freedom-of-movement rights. Traveling further afield still follows the '
            f'entry types listed below.'
            '</div>'
        )

    table_rows = "\n".join(build_row(d) for d in destinations)

    html = PAGE_TEMPLATE
    replacements = {
        "⟦TITLE⟧": f"{name} Passport Visa Requirements — Where Can {demonym.capitalize()} Travel Visa-Free? | VisaStay",
        "⟦META_DESC⟧": f"Full visa requirement breakdown for {demonym}: {visa_free} visa-free destinations, {easy} via eTA/eVisa/visa on arrival, and {required} requiring a visa in advance, across {total} countries.",
        "⟦CANONICAL⟧": canonical,
        "⟦OG_TITLE⟧": f"{name} Passport Visa Requirements | VisaStay",
        "⟦OG_DESC⟧": f"{visa_free} visa-free destinations, {easy} via eTA/eVisa/visa on arrival, {required} requiring a visa in advance.",
        "⟦NAME⟧": name,
        "⟦DEMONYM⟧": demonym,
        "⟦FLAG⟧": flag,
        "⟦TOTAL⟧": str(total),
        "⟦INTRO_PARAGRAPH⟧": intro,
        "⟦VISA_FREE_COUNT⟧": str(visa_free),
        "⟦EASY_COUNT⟧": str(easy),
        "⟦REQUIRED_COUNT⟧": str(required),
        "⟦SCHENGEN_NOTE⟧": schengen_note,
        "⟦TABLE_ROWS⟧": table_rows,
        "⟦FAQ1_ANSWER⟧": faq1,
        "⟦FAQ2_ANSWER⟧": faq2,
    }
    for token, value in replacements.items():
        html = html.replace(token, value)

    out_dir = os.path.join(OUT_ROOT, slug)
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "index.html")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"OK   {code} -> {out_path}  ({total} destinations, {visa_free} visa-free)")


def main():
    codes = sorted(
        fn[:-5] for fn in os.listdir(DATA_DIR) if fn.endswith(".json")
    )
    print(f"Found {len(codes)} passport data files: {', '.join(codes)}\n")
    for code in codes:
        generate(code)


if __name__ == "__main__":
    main()
