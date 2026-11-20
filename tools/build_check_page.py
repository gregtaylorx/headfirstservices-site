"""Builds /visastay/check/index.html from check_template.html.

Passport list from tools/passport_meta.json; official-info URLs from the
VisaStay app repo (visa_info_urls.dart) so the page stays in sync with
the app. Destination list = countries table (code, name). Re-run after adding
a passport or destination:  python tools/build_check_page.py
"""
import hashlib, json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.dirname(HERE)
APP = os.environ.get('VISASTAY_REPO', os.path.join(SITE, '..', '..', 'VisaStay'))

# Passports = tools/passport_meta.json (mirrors supported_passports in the DB;
# refreshed together with tools/data/ by the passport-pages data pull).
meta = json.load(open(os.path.join(HERE, 'passport_meta.json'), encoding='utf-8'))
pp = sorted([[c, m['name']] for c, m in meta.items()], key=lambda x: x[1])

s = open(os.path.join(APP, 'lib/app/utils/visa_info_urls.dart'), encoding='utf-8').read()
body = s[s.index('{', s.index('static const Map<String, String> _urls')):]
body = body[:body.index('};')]
urls = {c: u for c, u in re.findall(r"'([A-Z]{2})'\s*:\s*'([^']+)'", body, re.S) if 'wikipedia' not in u}

dests = json.load(open(os.path.join(HERE, 'data', 'destinations.json'), encoding='utf-8'))

# The page's script lives in its own file (visastay/check/check.js) so the
# site CSP can stay script-src 'self' with no inline scripts.
js = open(os.path.join(HERE, 'check_template.js'), encoding='utf-8').read()
js = (js.replace('__PASSPORTS__', json.dumps(pp, ensure_ascii=False))
        .replace('__DESTS__', json.dumps(dests, ensure_ascii=False))
        .replace('__INFO_URLS__', json.dumps(urls, ensure_ascii=False)))
ver = hashlib.sha256(js.encode('utf-8')).hexdigest()[:10]
t = open(os.path.join(HERE, 'check_template.html'), encoding='utf-8').read()
t = t.replace('__CHECK_JS_VER__', ver)
outdir = os.path.join(SITE, 'visastay', 'check')
os.makedirs(outdir, exist_ok=True)
open(os.path.join(outdir, 'check.js'), 'w', encoding='utf-8').write(js)
out = os.path.join(outdir, 'index.html')
open(out, 'w', encoding='utf-8').write(t)
print(f'passports={len(pp)} destinations={len(dests)} info_urls={len(urls)} -> {out} (+check.js v={ver})')
