"""Builds /visastay/check/index.html from check_template.html.

Passport list + official-info URLs are read from the VisaStay app repo
(country_constants.dart, visa_info_urls.dart) so the page stays in sync with
the app. Destination list = countries table (code, name). Re-run after adding
a passport or destination:  python tools/build_check_page.py
"""
import json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.dirname(HERE)
APP = os.environ.get('VISASTAY_REPO', os.path.join(SITE, '..', '..', 'VisaStay'))

src = open(os.path.join(APP, 'packages/core/lib/src/utils/country_constants.dart'), encoding='utf-8').read()
pp = re.findall(r"\('([A-Z]{2})', '([^']+)', '[^']*'\)", src.split('kSupportedPassports')[1].split('];')[0])
pp = sorted([[c, 'United Arab Emirates' if n == 'UAE' else n] for c, n in pp], key=lambda x: x[1])

s = open(os.path.join(APP, 'lib/app/utils/visa_info_urls.dart'), encoding='utf-8').read()
body = s[s.index('{', s.index('static const Map<String, String> _urls')):]
body = body[:body.index('};')]
urls = {c: u for c, u in re.findall(r"'([A-Z]{2})'\s*:\s*'([^']+)'", body, re.S) if 'wikipedia' not in u}

dests = json.load(open(os.path.join(HERE, 'data', 'destinations.json'), encoding='utf-8'))

t = open(os.path.join(HERE, 'check_template.html'), encoding='utf-8').read()
t = (t.replace('__PASSPORTS__', json.dumps(pp, ensure_ascii=False))
      .replace('__DESTS__', json.dumps(dests, ensure_ascii=False))
      .replace('__INFO_URLS__', json.dumps(urls, ensure_ascii=False)))
out = os.path.join(SITE, 'visastay', 'check', 'index.html')
os.makedirs(os.path.dirname(out), exist_ok=True)
open(out, 'w', encoding='utf-8').write(t)
print(f'passports={len(pp)} destinations={len(dests)} info_urls={len(urls)} -> {out}')
