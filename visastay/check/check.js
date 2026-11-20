(function () {
  // Public (anon) Supabase key — safe to ship; only the rate-limited
  // get_visa_rule_public RPC is callable without an account.
  var API = 'https://aubnhaktbxapnhtwmcyj.supabase.co/rest/v1/rpc/get_visa_rule_public';
  var KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImF1Ym5oYWt0YnhhcG5odHdtY3lqIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Nzc4Njg4NDksImV4cCI6MjA5MzQ0NDg0OX0.Kg5v1Fm712sFxiSsNMPMnXrxGAFcCBwL2K8IKIwiSWU';

  var PASSPORTS = [["DZ", "Algeria"], ["AR", "Argentina"], ["AU", "Australia"], ["AT", "Austria"], ["BH", "Bahrain"], ["BD", "Bangladesh"], ["BE", "Belgium"], ["BR", "Brazil"], ["CA", "Canada"], ["CL", "Chile"], ["CN", "China"], ["CO", "Colombia"], ["CZ", "Czech Republic"], ["CI", "Côte d'Ivoire"], ["EG", "Egypt"], ["FR", "France"], ["DE", "Germany"], ["GH", "Ghana"], ["HK", "Hong Kong"], ["IN", "India"], ["ID", "Indonesia"], ["IE", "Ireland"], ["IL", "Israel"], ["IT", "Italy"], ["JP", "Japan"], ["JO", "Jordan"], ["KZ", "Kazakhstan"], ["KE", "Kenya"], ["KW", "Kuwait"], ["MY", "Malaysia"], ["MX", "Mexico"], ["MA", "Morocco"], ["NL", "Netherlands"], ["NZ", "New Zealand"], ["NG", "Nigeria"], ["NO", "Norway"], ["OM", "Oman"], ["PK", "Pakistan"], ["PE", "Peru"], ["PH", "Philippines"], ["PL", "Poland"], ["PT", "Portugal"], ["QA", "Qatar"], ["RO", "Romania"], ["RU", "Russia"], ["SA", "Saudi Arabia"], ["RS", "Serbia"], ["SG", "Singapore"], ["ZA", "South Africa"], ["KR", "South Korea"], ["ES", "Spain"], ["LK", "Sri Lanka"], ["SE", "Sweden"], ["CH", "Switzerland"], ["TW", "Taiwan"], ["TJ", "Tajikistan"], ["TZ", "Tanzania"], ["TH", "Thailand"], ["TR", "Turkey (Türkiye)"], ["UA", "Ukraine"], ["AE", "United Arab Emirates"], ["GB", "United Kingdom"], ["US", "United States"], ["VN", "Vietnam"]];
  var DESTS = [["AF", "Afghanistan"], ["AL", "Albania"], ["DZ", "Algeria"], ["AD", "Andorra"], ["AO", "Angola"], ["AG", "Antigua and Barbuda"], ["AR", "Argentina"], ["AM", "Armenia"], ["AU", "Australia"], ["AT", "Austria"], ["AZ", "Azerbaijan"], ["BS", "Bahamas"], ["BH", "Bahrain"], ["BD", "Bangladesh"], ["BB", "Barbados"], ["BY", "Belarus"], ["BE", "Belgium"], ["BZ", "Belize"], ["BT", "Bhutan"], ["BO", "Bolivia"], ["BA", "Bosnia and Herzegovina"], ["BW", "Botswana"], ["BR", "Brazil"], ["BN", "Brunei"], ["BG", "Bulgaria"], ["BI", "Burundi"], ["KH", "Cambodia"], ["CM", "Cameroon"], ["CA", "Canada"], ["CV", "Cape Verde"], ["CL", "Chile"], ["CN", "China"], ["CO", "Colombia"], ["KM", "Comoros"], ["CR", "Costa Rica"], ["HR", "Croatia"], ["CU", "Cuba"], ["CW", "Curaçao"], ["CY", "Cyprus"], ["CZ", "Czech Republic"], ["CI", "Côte d'Ivoire"], ["CD", "DR Congo"], ["DK", "Denmark"], ["DJ", "Djibouti"], ["DM", "Dominica"], ["DO", "Dominican Republic"], ["TL", "East Timor"], ["EC", "Ecuador"], ["EG", "Egypt"], ["SV", "El Salvador"], ["GQ", "Equatorial Guinea"], ["ER", "Eritrea"], ["EE", "Estonia"], ["ET", "Ethiopia"], ["FJ", "Fiji"], ["FI", "Finland"], ["FR", "France"], ["GA", "Gabon"], ["GE", "Georgia"], ["DE", "Germany"], ["GH", "Ghana"], ["GR", "Greece"], ["GT", "Guatemala"], ["HN", "Honduras"], ["HK", "Hong Kong"], ["HU", "Hungary"], ["IS", "Iceland"], ["IN", "India"], ["ID", "Indonesia"], ["IR", "Iran"], ["IQ", "Iraq"], ["IE", "Ireland"], ["IL", "Israel"], ["IT", "Italy"], ["JM", "Jamaica"], ["JP", "Japan"], ["JO", "Jordan"], ["KZ", "Kazakhstan"], ["KE", "Kenya"], ["KW", "Kuwait"], ["KG", "Kyrgyzstan"], ["LA", "Laos"], ["LV", "Latvia"], ["LB", "Lebanon"], ["LY", "Libya"], ["LI", "Liechtenstein"], ["LT", "Lithuania"], ["LU", "Luxembourg"], ["MO", "Macau"], ["MG", "Madagascar"], ["MW", "Malawi"], ["MY", "Malaysia"], ["MV", "Maldives"], ["MT", "Malta"], ["MU", "Mauritius"], ["MX", "Mexico"], ["MD", "Moldova"], ["MN", "Mongolia"], ["ME", "Montenegro"], ["MA", "Morocco"], ["MZ", "Mozambique"], ["MM", "Myanmar"], ["NA", "Namibia"], ["NP", "Nepal"], ["NL", "Netherlands"], ["NZ", "New Zealand"], ["NI", "Nicaragua"], ["NG", "Nigeria"], ["MK", "North Macedonia"], ["NO", "Norway"], ["OM", "Oman"], ["PK", "Pakistan"], ["PA", "Panama"], ["PG", "Papua New Guinea"], ["PY", "Paraguay"], ["PE", "Peru"], ["PH", "Philippines"], ["PL", "Poland"], ["PT", "Portugal"], ["QA", "Qatar"], ["CG", "Republic of the Congo"], ["RO", "Romania"], ["RW", "Rwanda"], ["WS", "Samoa"], ["SA", "Saudi Arabia"], ["SN", "Senegal"], ["RS", "Serbia"], ["SC", "Seychelles"], ["SG", "Singapore"], ["SK", "Slovakia"], ["SI", "Slovenia"], ["SB", "Solomon Islands"], ["SO", "Somalia"], ["ZA", "South Africa"], ["KR", "South Korea"], ["SS", "South Sudan"], ["ES", "Spain"], ["LK", "Sri Lanka"], ["SD", "Sudan"], ["SE", "Sweden"], ["CH", "Switzerland"], ["SY", "Syria"], ["TW", "Taiwan"], ["TJ", "Tajikistan"], ["TZ", "Tanzania"], ["TH", "Thailand"], ["TO", "Tonga"], ["TT", "Trinidad and Tobago"], ["TN", "Tunisia"], ["TR", "Turkey (Türkiye)"], ["TM", "Turkmenistan"], ["UG", "Uganda"], ["UA", "Ukraine"], ["AE", "United Arab Emirates"], ["GB", "United Kingdom"], ["US", "United States"], ["UY", "Uruguay"], ["UZ", "Uzbekistan"], ["VU", "Vanuatu"], ["VE", "Venezuela"], ["VN", "Vietnam"], ["YE", "Yemen"], ["ZM", "Zambia"], ["ZW", "Zimbabwe"]];
  var INFO_URLS = {"GB": "https://www.gov.uk/check-uk-visa", "RS": "https://www.mfa.gov.rs/en/consular-affairs/entry-serbia/visa-information", "BA": "https://mvp.gov.ba/eng/", "AL": "https://e-albania.al/", "MK": "https://evisa.gov.mk/", "ME": "https://www.mfa.gov.me/en/ministry/consular-affairs/visa-regime", "MD": "https://www.evisa.gov.md/", "UA": "https://consul.mfa.gov.ua/", "BY": "https://mfa.gov.by/en/visa/", "IE": "https://www.irishimmigration.ie/", "TR": "https://www.evisa.gov.tr/", "AF": "https://eafghans.com/e-visa/", "TM": "https://migration.gov.tm/", "TH": "https://www.thaievisa.go.th/", "JP": "https://www.mofa.go.jp/j_info/visit/visa/index.html", "VN": "https://evisa.gov.vn/", "MY": "https://www.imi.gov.my/index.php/en/", "GE": "https://www.evisa.gov.ge/", "ID": "https://evisa.imigrasi.go.id/", "PH": "https://www.immigration.gov.ph/", "SG": "https://www.ica.gov.sg/enter-transit-depart/entering-singapore", "KH": "https://www.evisa.gov.kh/", "MM": "https://evisa.moip.gov.mm/", "NP": "https://www.immigration.gov.np/", "LK": "https://www.eta.gov.lk/", "UZ": "https://e-visa.gov.uz/", "AM": "https://evisa.mfa.am/", "NZ": "https://www.immigration.govt.nz/new-zealand-visas/visas/visa/visitor-visa", "KR": "https://www.visa.go.kr/", "TW": "https://www.boca.gov.tw/", "HK": "https://www.immd.gov.hk/eng/services/visas/", "MO": "https://www.fsm.gov.mo/psp/eng/TravelVisa.html", "MN": "https://evisa.mn/", "LA": "https://laoevisa.gov.la/", "BN": "https://www.immigration.gov.bn/", "TL": "https://migracao.gov.tl/", "BD": "https://visa.gov.bd/", "BT": "https://immi.gov.bt/", "AZ": "https://evisa.gov.az/", "KZ": "https://evisa.mfa.gov.kz/", "KG": "https://evisa.e-gov.kg/", "TJ": "https://evisa.tj/", "LB": "https://www.general-security.gov.lb/en", "YE": "https://yemenevisa.org/visas", "AE": "https://u.ae/en/information-and-services/visa-and-emirates-id/apply-for-a-visa", "QA": "https://www.moi.gov.qa/en/services/visas", "MV": "https://www.immigration.gov.mv/", "IN": "https://indianvisaonline.gov.in/evisa/tvoa.do", "SA": "https://visa.mofa.gov.sa/", "KW": "https://kuwaitvisa.moi.gov.kw/", "BH": "https://www.evisa.gov.bh/", "OM": "https://evisa.rop.gov.om/", "IQ": "https://evisa.iq/en", "JO": "https://eservices.moi.gov.jo/MOI_EVISA/", "IL": "https://israel-entry.piba.gov.il/", "PK": "https://visa.nadra.gov.pk/", "AO": "https://www.smevisa.gov.ao/", "BI": "https://migration.gov.bi/", "BW": "https://www.gov.bw/visa-applications/visa-application-visitors-visa", "CD": "https://evisa.gouv.cd/", "CG": "https://diplobrazza.net/", "CM": "https://www.evisacam.cm/", "DZ": "https://www.mfa.gov.dz/services-for-foreigners/entry-visa-to-algeria", "GQ": "https://egonline.vfsevisa.com/gnq/en", "LY": "https://evisa.gov.ly/", "SD": "https://eservice.passport.gov.sd/aliens/home", "SO": "https://etas.gov.so/", "SS": "https://www.evisa.gov.ss/", "TN": "https://www.diplomatie.gov.tn/", "KE": "https://www.etakenya.go.ke/", "TZ": "https://www.immigration.go.tz/", "ZA": "https://www.dha.gov.za/index.php/immigration-services/types-of-visas", "MU": "https://passport.govmu.org/passport/index.php/immigration-visas", "MA": "https://www.consulat.ma/en/visas", "EG": "https://www.visa2egypt.gov.eg/", "ET": "https://www.evisa.gov.et/", "RW": "https://www.migration.gov.rw/", "UG": "https://visas.immigration.go.ug/", "GH": "https://evisa.immigration.gov.gh/", "SN": "https://www.evisa.sn/", "CI": "https://snedai.com/", "NG": "https://immigration.gov.ng/", "MZ": "https://evisa.gov.mz/", "MW": "https://evisa.gov.mw/", "ZM": "https://eservices.zambiaimmigration.gov.zm/", "ZW": "https://www.evisa.gov.zw/", "NA": "https://www.home-affairs.gov.na/", "SC": "https://seychelles.govtas.com/", "CV": "https://ease.gov.cv/", "MG": "https://evisamada.gov.mg/", "DJ": "https://www.evisa.gouv.dj/", "GA": "https://evisa.dgdi.ga/", "SB": "https://immigration.gov.sb/", "VE": "https://saime.gob.ve/", "MX": "https://www.gob.mx/tramites/ficha/visa-para-extranjeros/INM207", "CO": "https://www.cancilleria.gov.co/tramites_servicios/visas", "CR": "https://www.migracion.go.cr/Paginas/Visas.aspx", "PA": "https://www.migracion.gob.pa/", "BR": "https://www.gov.br/mre/en/consular-services/visas", "AR": "https://www.migraciones.gov.ar/accesible/indexP.php", "CL": "https://serviciomigraciones.cl/", "PE": "https://www.migraciones.gob.pe/", "US": "https://travel.state.gov/content/travel/en/us-visas.html", "CA": "https://www.canada.ca/en/immigration-refugees-citizenship/services/visit-canada.html", "AU": "https://immi.homeaffairs.gov.au/", "EC": "https://www.cancilleria.gob.ec/visas/", "BO": "https://www.migracion.gob.bo/", "PY": "https://migraciones.gov.py/", "UY": "https://www.gub.uy/ministerio-interior/tramites-y-servicios/tramites/visa-turista", "GT": "https://igm.gob.gt/", "HN": "https://inm.gob.hn/", "NI": "https://www.migob.gob.ni/", "SV": "https://www.migracion.gob.sv/", "DO": "https://migracion.gob.do/", "JM": "https://www.immigration.gov.jm/", "BB": "https://immigration.gov.bb/", "BS": "https://www.immigration.gov.bs/", "TT": "https://www.immigration.gov.tt/", "FJ": "https://www.immigration.gov.fj/", "PG": "https://ica.gov.pg/", "VU": "https://immigration.gov.vu/", "TO": "https://www.revenue.gov.to/immigration-and-general-services", "WS": "https://mpmc.gov.ws/divisions/immigration/"};
  var SCHENGEN = ['AT','BE','HR','CZ','DK','EE','FI','FR','DE','GR','HU','IS','IT','LV','LI','LT','LU','MT','NL','NO','PL','PT','SK','SI','ES','SE','CH','BG','RO'];
  var FREE_MOVEMENT = ['AT','BE','CZ','DE','ES','FR','IE','IT','NL','PL','PT','RO','SE','NO','CH'];
  var EU_EEA = SCHENGEN.concat(['CY','IE']);
  var SCHENGEN_URL = 'https://home-affairs.ec.europa.eu/policies/schengen-borders-and-visa/visa-policy/applying-schengen-visa_en';
  var PLAY = 'https://play.google.com/store/apps/details?id=com.digitalnomadessentials.digital_nomad_essentials&referrer=';
  var IOS = 'https://apps.apple.com/us/app/visastay/id6776447080';

  var $p = document.getElementById('passport'), $d = document.getElementById('dest'),
      $e = document.getElementById('entry'), $go = document.getElementById('go'),
      $form = document.getElementById('checker'), $out = document.getElementById('result');

  function flag(cc) { return cc.replace(/./g, function (c) { return String.fromCodePoint(127397 + c.charCodeAt(0)); }); }
  function esc(s) { return String(s).replace(/[&<>"']/g, function (c) { return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]; }); }
  function opt(sel, code, name) { var o = document.createElement('option'); o.value = code; o.textContent = flag(code) + '  ' + name; sel.appendChild(o); }
  function nameOf(list, code) { for (var i = 0; i < list.length; i++) if (list[i][0] === code) return list[i][1]; return code; }

  var ph = document.createElement('option'); ph.value = ''; ph.textContent = 'Select passport…'; $p.appendChild(ph);
  PASSPORTS.forEach(function (x) { opt($p, x[0], x[1]); });
  var dh = document.createElement('option'); dh.value = ''; dh.textContent = 'Select destination…'; $d.appendChild(dh);
  DESTS.forEach(function (x) { opt($d, x[0], x[1]); });

  function iso(d) { return d.getFullYear() + '-' + String(d.getMonth() + 1).padStart(2, '0') + '-' + String(d.getDate()).padStart(2, '0'); }
  $e.value = iso(new Date());

  // Prefill: URL params first, then browser region for passport.
  var q = new URLSearchParams(location.search);
  var qp = (q.get('passport') || '').toUpperCase(), qd = (q.get('to') || '').toUpperCase(), qe = q.get('date');
  if (PASSPORTS.some(function (x) { return x[0] === qp; })) $p.value = qp;
  else {
    var reg = ((navigator.language || '').split('-')[1] || '').toUpperCase();
    if (PASSPORTS.some(function (x) { return x[0] === reg; })) $p.value = reg;
  }
  if (DESTS.some(function (x) { return x[0] === qd; })) $d.value = qd;
  if (qe && /^\d{4}-\d{2}-\d{2}$/.test(qe)) $e.value = qe;

  function fmt(d) { return d.toLocaleDateString(undefined, { day: 'numeric', month: 'short', year: 'numeric' }); }
  function addDays(isoStr, n) { var p = isoStr.split('-'); var d = new Date(+p[0], +p[1] - 1, +p[2]); d.setDate(d.getDate() + n); return d; }

  var LABEL = {
    visa_exempt: ['Visa-free', 'pill-free'],
    visa_on_arrival: ['Visa on arrival', 'pill-arrival'], voa: ['Visa on arrival', 'pill-arrival'],
    evisa: ['eVisa — apply online before travel', 'pill-online'],
    eta: ['Travel authorization (ETA) — apply online', 'pill-online'],
    visa_required: ['Visa required before travel', 'pill-required']
  };

  function storeLinks(pp, dd) {
    var ref = encodeURIComponent('utm_source=headfirstservices&utm_medium=web&utm_campaign=stay_checker&utm_content=result_' + pp + '_' + dd);
    return '<div class="store-badges">' +
      '<a class="store-badge" href="' + PLAY + ref + '" target="_blank" rel="noopener">▶ Get it on Google Play</a>' +
      '<a class="store-badge" href="' + IOS + '" target="_blank" rel="noopener">🍎 Download on the App Store</a></div>';
  }

  function render(pp, dd, entryIso, data) {
    var pName = nameOf(PASSPORTS, pp), dName = nameOf(DESTS, dd);
    var route = flag(pp) + ' ' + esc(pName) + ' passport → ' + flag(dd) + ' ' + esc(dName);
    var info = INFO_URLS[dd] || (SCHENGEN.indexOf(dd) >= 0 ? SCHENGEN_URL : null);
    var infoLink = info ? '<a href="' + esc(info) + '" target="_blank" rel="noopener">official visa information ↗</a>' : 'the destination\'s embassy or consulate';
    var rule = data && data.rule;
    var h = '<div class="result-card">';

    if (!rule) {
      h += '<p class="result-route">' + route + '</p>';
      h += '<p class="result-days" style="font-size:26px;">No rule on file for this combination</p>';
      h += '<p class="result-leave">Check ' + infoLink + ' before you travel.</p></div>';
      $out.innerHTML = h; return;
    }

    if (FREE_MOVEMENT.indexOf(pp) >= 0 && EU_EEA.indexOf(dd) >= 0) {
      h += '<div class="result-head"><div><p class="result-route">' + route + '</p>';
      h += '<p class="result-days" style="font-size:30px;">No visa needed</p>';
      h += '<p class="result-leave">EU/EEA/Swiss freedom of movement — no fixed short-stay limit. Longer stays may need local registration.</p></div>';
      h += '<span class="pill pill-free">Freedom of movement</span></div>';
      h += '<p class="result-meta">Planning information only — confirm with ' + infoLink + ' before you travel.</p>';
      h += '<div class="result-cta"><p><strong>Spending months abroad?</strong> VisaStay tracks your days per country for tax residency, too.</p>' + storeLinks(pp, dd) + '</div></div>';
      $out.innerHTML = h; return;
    }

    var type = LABEL[rule.entry_rule] || [String(rule.entry_rule).replace(/_/g, ' '), 'pill-online'];
    var days = rule.max_stay_per_entry || rule.visa_free_duration || rule.voa_duration || 0;
    var required = rule.entry_rule === 'visa_required';

    h += '<div class="result-head"><div>';
    h += '<p class="result-route">' + route + '</p>';
    if (required) {
      h += '<p class="result-days" style="font-size:30px;">Visa needed before you go</p>';
      h += '<p class="result-leave">Your allowed stay depends on the visa you are issued.</p>';
    } else if (days > 0) {
      var leave = addDays(entryIso, days - 1);
      h += '<p class="result-days">Up to ' + days + ' days</p>';
      h += '<p class="result-leave">Enter ' + fmt(addDays(entryIso, 0)) + ' → <strong>leave by ' + fmt(leave) + '</strong></p>';
    } else {
      h += '<p class="result-days" style="font-size:28px;">Stay length not published</p>';
    }
    h += '</div><span class="pill ' + type[1] + '">' + esc(type[0]) + '</span></div>';

    h += '<ul class="result-list">';
    if (!required && days > 0) h += '<li><strong>Max stay per entry</strong><span>' + days + ' days</span></li>';
    if (rule.extendable && rule.extension_days > 0) h += '<li><strong>Extension</strong><span>Extendable in-country by up to ' + rule.extension_days + ' days</span></li>';
    else if (!required) h += '<li><strong>Extension</strong><span>No in-country extension on file</span></li>';
    if (typeof rule.multiple_entries_allowed === 'boolean' && !required) h += '<li><strong>Entries</strong><span>' + (rule.multiple_entries_allowed ? 'Multiple entries allowed' : 'Single entry') + '</span></li>';
    (rule.conditions || []).forEach(function (c) { h += '<li><strong>Note</strong><span>' + esc(c) + '</span></li>'; });
    h += '</ul>';

    if (SCHENGEN.indexOf(dd) >= 0) {
      if (FREE_MOVEMENT.indexOf(pp) >= 0) {
        h += '<div class="result-note">EU/EEA/Swiss citizens have freedom of movement in the Schengen Area, so the 90/180-day limit doesn\'t apply to you. Longer stays may still need local registration.</div>';
      } else if (!required) {
        h += '<div class="result-note"><strong>Schengen 90/180 applies.</strong> Days in <em>any</em> Schengen country in the last 180 days count toward the same 90-day limit, so your real allowance may be lower than shown. <a href="/visastay/schengen-90-180-rule/">How the rule works</a>.</div>';
      }
    }

    h += '<p class="result-meta">Rule last reviewed ' + esc(data.last_updated || '—') + '. Planning information only — confirm with ' + infoLink + ' before you travel.</p>';

    h += '<div class="result-cta"><p>' + (required
      ? '<strong>Got your visa?</strong> Track your stay in VisaStay using your visa\'s dates and get a reminder before it ends.'
      : '<strong>Don\'t lose track of this date.</strong> Save this trip in VisaStay and get a reminder before your stay ends.') + '</p>' + storeLinks(pp, dd) + '</div>';
    h += '</div>';
    $out.innerHTML = h;
  }

  function lookup(pp, dd, entryIso) {
    $go.disabled = true; $go.textContent = 'Checking…';
    $out.innerHTML = '';
    fetch(API, {
      method: 'POST',
      headers: { 'apikey': KEY, 'Authorization': 'Bearer ' + KEY, 'Content-Type': 'application/json' },
      body: JSON.stringify({ p_destination: dd, p_passport: pp })
    }).then(function (r) {
      return r.json().then(function (j) { return { ok: r.ok, body: j }; });
    }).then(function (res) {
      if (!res.ok) {
        var msg = (res.body && res.body.message) || '';
        if (msg.indexOf('rate_limited') >= 0) throw new Error('You\'ve run a lot of checks in the last hour. Please try again a little later — or get unlimited checks in the app.');
        throw new Error('Something went wrong. Please try again.');
      }
      render(pp, dd, entryIso, res.body);
    }).catch(function (err) {
      $out.innerHTML = '<p class="err">' + esc(err.message && err.message.indexOf('Failed to fetch') < 0 ? err.message : 'Couldn\'t reach VisaStay. Check your connection and try again.') + '</p>';
    }).then(function () { $go.disabled = false; $go.textContent = 'Check my stay'; });
  }

  $form.addEventListener('submit', function (ev) {
    ev.preventDefault();
    var pp = $p.value, dd = $d.value, en = $e.value;
    if (!pp || !dd || !en) { $out.innerHTML = '<p class="err">Choose a passport, a destination and an entry date.</p>'; return; }
    if (pp === dd) { $out.innerHTML = '<div class="result-card"><p class="result-days" style="font-size:26px;">That\'s your own country</p><p class="result-leave">Citizens don\'t need a visa to enter their own country. Pick a different destination.</p></div>'; return; }
    var url = new URL(location.href);
    url.searchParams.set('passport', pp); url.searchParams.set('to', dd); url.searchParams.set('date', en);
    history.replaceState(null, '', url.toString());
    lookup(pp, dd, en);
  });

  if ($p.value && $d.value && qd) { document.getElementById('check').scrollIntoView(); }
  if ($p.value && $d.value && qd) $form.requestSubmit ? $form.requestSubmit() : $form.dispatchEvent(new Event('submit'));
})();
