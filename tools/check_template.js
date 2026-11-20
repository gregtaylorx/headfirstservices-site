(function () {
  // Public (anon) Supabase key — safe to ship; only the rate-limited
  // get_visa_rule_public RPC is callable without an account.
  var API = 'https://aubnhaktbxapnhtwmcyj.supabase.co/rest/v1/rpc/get_visa_rule_public';
  var KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImF1Ym5oYWt0YnhhcG5odHdtY3lqIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Nzc4Njg4NDksImV4cCI6MjA5MzQ0NDg0OX0.Kg5v1Fm712sFxiSsNMPMnXrxGAFcCBwL2K8IKIwiSWU';

  var PASSPORTS = __PASSPORTS__;
  var DESTS = __DESTS__;
  var INFO_URLS = __INFO_URLS__;
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
