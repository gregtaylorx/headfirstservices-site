#!/usr/bin/env python3
"""Generate per-app legal + help pages for headfirstservices.com.

For every app in APPS this writes, under /<slug>/:
  privacy/index.html        Privacy Policy (standalone, this app only)
  terms/index.html          Terms of Service (standalone, this app only)
  support/index.html        Support / contact
  faq/index.html            FAQ  (skipped when the app has a hand-written FAQ,
                            e.g. /visastay/faq/, or no FAQ content yet)
  delete-account/index.html How to delete the account (or, for ChewPaca, why
                            there is none)
plus any extra pages an app defines (ZoneLink: delete-data/).

Run from the site root:  python tools/build_app_pages.py
Edit the content here, not the generated HTML.
"""
import html, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPDATED = "November 14, 2026"
COMPANY = "HeadFirstServices LLC"
PRIVACY_EMAIL = "privacy@headfirstservices.com"

# --------------------------------------------------------------------------
# Shared clauses
# --------------------------------------------------------------------------

PROCESSORS = {
    "supabase": ('<a href="https://supabase.com/privacy" target="_blank" rel="noopener">Supabase Inc.</a>',
                 "Database and sign-in", "Your account and the data you create in the app", "United States (AWS US East)"),
    "revenuecat": ('<a href="https://www.revenuecat.com/privacy" target="_blank" rel="noopener">RevenueCat Inc.</a>',
                   "Purchase management", "App store purchase receipts and Pro status", "United States"),
    "resend": ('<a href="https://resend.com/legal/privacy-policy" target="_blank" rel="noopener">Resend Inc.</a>',
               "Email delivery", "Recipient email addresses and email content", "United States"),
    "google": ('<a href="https://policies.google.com/privacy" target="_blank" rel="noopener">Google LLC</a>',
               "Sign in with Google", "Your email address (only if you choose Google sign-in)", "United States"),
    "apple": ('<a href="https://www.apple.com/legal/privacy/" target="_blank" rel="noopener">Apple Inc.</a>',
              "Sign in with Apple", "Your email address or Apple relay address (only if you choose Apple sign-in)", "United States"),
    "fcm": ('<a href="https://firebase.google.com/support/privacy" target="_blank" rel="noopener">Google LLC (Firebase Cloud Messaging)</a>',
            "Push notifications on Android", "Device push token and notification content", "United States"),
    "apns": ('<a href="https://www.apple.com/legal/privacy/" target="_blank" rel="noopener">Apple Inc. (Apple Push Notification service)</a>',
             "Push notifications on iPhone", "Device push token and notification content", "United States"),
    "openmeteo": ('<a href="https://open-meteo.com/en/terms" target="_blank" rel="noopener">Open-Meteo</a>',
                  "Weather forecasts", "Destination coordinates only (no personal identifiers)", "European Union"),
}

ACCOUNT_BLOCK = (
    "<h3>Account information</h3>"
    "<p>When you create an account you provide your <strong>email address</strong> and a <strong>password</strong> "
    "(stored as a salted hash — we never see it in plain text), or you sign in with <strong>Apple</strong> or "
    "<strong>Google</strong>, in which case we receive your email address from that provider. A unique user ID is "
    "generated and associated with your data. {name} has its own separate account, even if you use the same email "
    "address in our other apps.</p>"
)

BIOMETRIC_BLOCK = (
    "<h3>Biometric lock (optional)</h3>"
    "<p>If you turn on biometric app lock, authentication is handled entirely by your device's operating system "
    "(Face ID or fingerprint). <strong>We never receive, transmit, or store any biometric data</strong> — the app only "
    "stores a yes/no setting on your device.</p>"
)

NO_TRACKING_BLOCK = (
    "<h3>Device and usage data</h3>"
    "<p>We do not collect analytics, crash reports, advertising identifiers, or behavioral tracking data, and the app "
    "contains no third-party analytics or advertising SDK.</p>"
)

PAYMENT_BLOCK = (
    "<h3>Purchases</h3>"
    "<p>Purchases are processed by the Apple App Store or Google Play, with <strong>RevenueCat</strong> managing your "
    "Pro status. We receive only whether Pro is active. Your payment card details are never sent to or stored by us.</p>"
)


def privacy_common_tail(a):
    """Sections after the processor table, shared by every account-based app."""
    return f"""
<h2>5. Data Retention</h2>
<p>Your data is kept for as long as your account exists. When you delete your account, all personal data associated
with it is permanently deleted from our systems within <strong>7 days</strong>, except where retention is required by
applicable law. Anonymized, non-identifiable aggregates may be kept indefinitely.</p>

<h2>6. Your Rights</h2>
<p>Depending on where you live, you may have the right to:</p>
<ul>
  <li><strong>Access</strong> — request a copy of the data we hold about you</li>
  <li><strong>Correction</strong> — ask us to correct inaccurate data</li>
  <li><strong>Erasure</strong> — delete your account and all associated data</li>
  <li><strong>Portability</strong> — export your data in a machine-readable format (in the app: Profile → Export My Data)</li>
  <li><strong>Restriction / objection</strong> — ask us to limit or stop processing your data in certain circumstances</li>
  <li><strong>Withdraw consent</strong> — where processing is based on consent (for example, email notifications), turn it off at any time in the app</li>
</ul>
<p>To exercise any of these rights, email <a href="mailto:{PRIVACY_EMAIL}">{PRIVACY_EMAIL}</a>. We will respond
within 30 days. If you are in the European Economic Area or the UK, you can also lodge a complaint with your local
data protection authority.</p>

<h2>7. Deleting Your Account and Data</h2>
{a['privacy_deletion']}
<p>Deleting your {a['name']} account does not affect accounts in our other apps — each app keeps its own separate data.
Full instructions: <a href="/{a['slug']}/delete-account/">Delete your {a['name']} account</a>.</p>

<h2>8. Data Breach Notification</h2>
<p>If a personal data breach is likely to put your rights and freedoms at risk, we will notify the relevant supervisory
authority within <strong>72 hours</strong> of becoming aware of it where the law requires, notify affected users
without undue delay by email at the address on their account, and describe what happened, the data affected, the likely
consequences, and what we are doing about it.</p>

<h2>9. International Data Transfers</h2>
<p>Your data is stored on servers in the <strong>United States</strong>. If you are in the European Economic Area or
the UK, this is a transfer of personal data outside your region, covered by Standard Contractual Clauses (SCCs)
incorporated into our agreements with our processors.</p>

<h2>10. Children's Privacy</h2>
<p>{a['name']} is not directed to children under 13 (or 16 in the EEA). We do not knowingly collect personal data from
children. If you believe a child has given us personal data, contact <a href="mailto:{PRIVACY_EMAIL}">{PRIVACY_EMAIL}</a>
and we will delete it promptly.</p>

<h2>11. Security</h2>
<p>We use industry-standard security measures, including encryption in transit (TLS 1.2+) and at rest, row-level
security on every database table so you can only access your own data, and bcrypt password hashing. No method of
transmission over the internet is 100% secure, but we take reasonable precautions to protect your information.</p>

<h2>12. Changes to This Policy</h2>
<p>When we update this policy we will change the "Last updated" date above. For material changes, we will notify you
by email or in-app notice at least 14 days before the change takes effect. Continuing to use {a['name']} after that
date means you accept the updated policy.</p>

<h2>13. Contact</h2>
<p>{COMPANY} — Washington State, USA<br>
Email: <a href="mailto:{PRIVACY_EMAIL}">{PRIVACY_EMAIL}</a></p>
"""


def processor_table(keys):
    rows = "\n".join(
        f"  <tr><td>{PROCESSORS[k][0]}</td><td>{PROCESSORS[k][1]}</td><td>{PROCESSORS[k][2]}</td><td>{PROCESSORS[k][3]}</td></tr>"
        for k in keys)
    return ('<div class="legal-table"><table>\n  <tr><th>Processor</th><th>Purpose</th><th>Data shared</th><th>Location</th></tr>\n'
            + rows + "\n</table></div>")


def privacy_account_app(a):
    return f"""
<p>This Privacy Policy explains how {COMPANY} ("we", "us", "our") handles your information in <strong>{a['name']}</strong>
— {a['tagline_lc']}. It covers {a['name']} only; each of our apps has its own policy and its own separate database.</p>

<h2>1. Information We Collect</h2>
{ACCOUNT_BLOCK.format(name=a['name'])}
{a['privacy_collect']}
{BIOMETRIC_BLOCK if a.get('biometric') else ''}
{NO_TRACKING_BLOCK}
{PAYMENT_BLOCK}

<h2>2. How We Use Your Information</h2>
<ul>
{a['privacy_use']}
  <li>To keep track of whether Pro is active on your account</li>
  <li>To let you export or delete your data</li>
  <li>To comply with legal obligations</li>
</ul>
<p>We do not use your data for advertising or profiling, and we never sell it.</p>

<h2>3. Who Can See Your Data</h2>
{a['privacy_visibility']}

<h2>4. Service Providers (Processors)</h2>
<p>We use the following service providers to run {a['name']}. Each is bound by a Data Processing Agreement where
required. No other third parties receive your personal data.</p>
{processor_table(a['processors'])}
{a.get('privacy_processor_note', '')}
{privacy_common_tail(a)}
"""


def terms_account_app(a):
    return f"""
<p>These Terms of Service ("Terms") govern your use of <strong>{a['name']}</strong>, a mobile app operated by
{COMPANY} ("we", "us", "our"). By downloading, installing, or using {a['name']}, you agree to these Terms. If you do
not agree, do not use the app.</p>

<h2>1. Eligibility</h2>
<p>You must be at least 13 years old (or 16 in the European Economic Area) to use {a['name']}. If you are under 18, a
parent or legal guardian must review and agree to these Terms on your behalf.</p>

<h2>2. Your Account</h2>
<p>You need an account to use {a['name']}. You are responsible for keeping your sign-in details confidential and for
all activity under your account. Tell us immediately at <a href="mailto:{PRIVACY_EMAIL}">{PRIVACY_EMAIL}</a> if you
suspect unauthorized access. You may not create accounts by automated means or under false pretenses. We may suspend
or terminate accounts that violate these Terms.</p>

<h2>3. Free and Pro</h2>
{a['terms_tiers']}
<p>Free limits are set at our discretion and may change, but we will not reduce them in a way that deletes data you
have already created.</p>

<h2>4. Purchases and Billing</h2>
{a['terms_billing']}
<ul>
  <li>All purchases are processed by the Apple App Store or Google Play and are subject to their terms.</li>
  <li><strong>Refunds</strong> are handled by the relevant app store under its refund policy. We do not issue refunds directly.</li>
  <li>A lifetime or one-time purchase unlocks Pro in {a['name']} only, not in our other apps, unless clearly stated at the time of purchase.</li>
</ul>

<h2>5. {a['terms_disclaimer_title']}</h2>
{a['terms_disclaimer']}

<h2>6. Acceptable Use</h2>
<p>You agree not to:</p>
<ul>
  <li>Use {a['name']} for any unlawful purpose or in violation of any applicable law or regulation</li>
  <li>Attempt to gain unauthorized access to any part of the app, our servers, or connected systems</li>
  <li>Reverse engineer, decompile, or disassemble any part of the app</li>
  <li>Use the app to transmit spam, malware, or harmful code</li>
  <li>Scrape, harvest, or systematically extract data from the app</li>
  <li>Impersonate another person or create accounts for others without their consent</li>
  <li>Use the app in any way that could damage, disable, or impair our services</li>
</ul>

<h2>7. Intellectual Property</h2>
<p>{a['name']}, including its content, design, code, trademarks, and branding, is owned by {COMPANY} and protected by
intellectual property laws. Nothing in these Terms gives you any right to use our trademarks or branding.</p>
<p>Your data ({a['your_data']}) remains yours. You give us a limited license to process it solely to provide the
service to you.</p>

{shared_terms_tail(a, survive="7, 9, 10, 11, and 12")}
"""


def shared_terms_tail(a, survive):
    return f"""
<h2>8. Availability and Changes</h2>
<p>We aim to keep {a['name']} available at all times but do not guarantee uninterrupted access. We may update, modify,
or discontinue features with reasonable notice. For material changes that reduce functionality you have paid for, we
will give at least 30 days' notice and a pro-rated refund option where applicable.</p>

<h2>9. Disclaimers</h2>
<p>{a['name'].upper()} IS PROVIDED "AS IS" AND "AS AVAILABLE" WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR IMPLIED,
INCLUDING BUT NOT LIMITED TO WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, ACCURACY, OR
NON-INFRINGEMENT. We do not warrant that the app will be error-free, uninterrupted, or free of viruses or other harmful
components.</p>

<h2>10. Limitation of Liability</h2>
<p>TO THE MAXIMUM EXTENT PERMITTED BY APPLICABLE LAW, {COMPANY.upper()} SHALL NOT BE LIABLE FOR ANY INDIRECT, INCIDENTAL,
SPECIAL, CONSEQUENTIAL, OR PUNITIVE DAMAGES, INCLUDING BUT NOT LIMITED TO LOSS OF PROFITS, DATA, OR GOODWILL, ARISING OUT
OF OR IN CONNECTION WITH YOUR USE OF {a['name'].upper()}.</p>
<p>Our total liability to you for any claim arising from these Terms or your use of {a['name']} shall not exceed the
amount you paid us in the 12 months before the claim, or USD $10, whichever is greater. Some jurisdictions do not allow
certain liability exclusions; in those jurisdictions our liability is limited to the maximum extent permitted by law.</p>

<h2>11. Indemnification</h2>
<p>You agree to indemnify and hold harmless {COMPANY}, its officers, and employees from any claims, losses, or expenses
(including reasonable legal fees) arising from your use of {a['name']} in violation of these Terms or any applicable
law.</p>

<h2>12. Governing Law and Disputes</h2>
<p>These Terms are governed by the laws of the <strong>State of Washington, USA</strong>, without regard to its
conflict-of-law provisions. Any dispute arising from these Terms that cannot be resolved informally shall be submitted
to binding arbitration in Washington State under the rules of the American Arbitration Association, except that either
party may seek injunctive relief in a court of competent jurisdiction. Nothing in these Terms limits any rights you
have under the mandatory consumer protection laws of the country where you live.</p>

<h2>13. Termination</h2>
<p>{a['terms_termination']}</p>
<p>We may suspend or terminate your access immediately if you materially breach these Terms, with or without prior
notice. Upon termination, your right to use {a['name']} ends. Sections {survive} survive termination.</p>

<h2>14. Changes to These Terms</h2>
<p>We may update these Terms from time to time. We will notify you of material changes by email or in-app notice at
least 14 days before they take effect. Continuing to use {a['name']} after that date means you accept the updated
Terms.</p>

<h2>15. Contact</h2>
<p>{COMPANY} — Washington State, USA<br>
Email: <a href="mailto:{PRIVACY_EMAIL}">{PRIVACY_EMAIL}</a> · Support: <a href="mailto:{a['support_email']}">{a['support_email']}</a></p>
<p>Privacy: see the <a href="/{a['slug']}/privacy/">{a['name']} Privacy Policy</a>.</p>
"""


# --------------------------------------------------------------------------
# Per-app content
# --------------------------------------------------------------------------

STORE = {
    "visastay": ("https://play.google.com/store/apps/details?id=com.digitalnomadessentials.digital_nomad_essentials",
                 "https://apps.apple.com/us/app/visastay/id6776447080"),
    "zonelink": ("https://play.google.com/store/apps/details?id=com.digitalnomadessentials.zonelink",
                 "https://apps.apple.com/us/app/zonelink/id6794818466"),
    "chewpaca": ("https://play.google.com/store/apps/details?id=com.headfirstservices.chewpaca",
                 "https://apps.apple.com/us/app/chewpaca/id6799393365"),
}

APPS = []

# ---------------- VisaStay ----------------
APPS.append(dict(
    slug="visastay", name="VisaStay", tagline_lc="a visa day and tax residency tracker for frequent travelers",
    suite="Part of the Outbound Suite by HeadFirst Services.", released=True,
    support_email="support@headfirstservices.com", biometric=True, own_faq=True,
    processors=["supabase", "resend", "revenuecat", "fcm", "apns", "google", "apple"],
    privacy_collect="""
<h3>Profile information</h3>
<p>Your <strong>passport nationality</strong> and <strong>home currency</strong>, used to work out visa rules and show
amounts. Never sold or shared with advertisers.</p>
<h3>Trips and visas</h3>
<p>Trips you create: destination country, city, start and end dates, the passport used for entry, visa type or program,
and optional notes. Visas you save in My Visas: visa type, country, and dates. Destinations you star.</p>
<h3>Notifications and emails</h3>
<p>If you turn on push or email notifications, we store your alert rules (for example, days before a visa expires),
whether you want the monthly digest, and your device's push token.</p>
<h3>Additional alert recipients</h3>
<p>If you choose to send alert emails to someone else (for example a partner, accountant, or employer), we store the
email address you enter and send that person only the alerts you set up. They are not signed up for anything else, and
you can remove them at any time in the app. Please only add people who are happy to receive these emails.</p>
<h3>Visa info reports</h3>
<p>If you use "Report a visa info change", we receive what you write, the country it concerns, and your account email
so we can follow up.</p>
<h3>Location and photos</h3>
<p>VisaStay does not use your location. Shareable trip cards use a photo you pick for that card only; the app never
gets access to your photo library and the photo is not uploaded.</p>""",
    privacy_use="""  <li>To calculate visa days, Schengen 90/180 windows, and tax residency day counts</li>
  <li>To send the push notifications and emails you set up (visa expiry, passport expiry, tax residency, Schengen alerts, monthly digest), to you and to anyone you add</li>
  <li>To send account emails such as sign-up confirmation and password reset</li>
  <li>To review visa info reports you send</li>""",
    privacy_visibility="""<p>Your trips and visas are visible only to your account. Alert emails go only to you and
to the recipients you add.</p>""",
    privacy_deletion="""<p>Delete your account in the app at <strong>Profile → Delete Account</strong>. If you can't use
the app, email <a href="mailto:privacy@headfirstservices.com">privacy@headfirstservices.com</a> from the address on
your account and we will permanently delete your account and all associated data within 7 days.</p>""",
    terms_tiers="""<p>VisaStay has a free plan and a paid <strong>Pro</strong> plan. Free includes unlimited travel
history, up to 5 active trips, visa day tracking, the Schengen calculator, push notifications, and offline use. Pro
adds unlimited trips, email alerts (to you and anyone you add), "Where next?", the monthly digest, the Tax Year view,
and CSV + PDF export. New accounts get a 14-day Pro trial. What each plan includes is shown in the app and may change
over time with reasonable notice.</p>""",
    terms_billing="""<p>Pro is available as a monthly subscription, an annual subscription, or the one-time Founder
Lifetime Pass. Prices are shown in the app and on the store before you buy.</p>
<ul>
  <li><strong>Subscriptions renew automatically</strong> at the end of each period unless canceled at least 24 hours before renewal.</li>
  <li><strong>Cancel</strong> in your app store account (iPhone: Settings → your name → Subscriptions; Android: Google Play → Payments &amp; subscriptions → Subscriptions). Canceling stops future charges but does not refund the current period.</li>
  <li>For subscriptions, price changes are communicated at least 30 days in advance.</li>
</ul>""",
    terms_disclaimer_title="Visa, Travel, and Tax Information",
    terms_disclaimer="""<p><strong>Important:</strong> visa rules, entry requirements, and permitted stays change often.
VisaStay gives general guidance only and may not reflect the latest rules. Always confirm entry requirements with the
official embassy, consulate, or immigration authority of your destination before you travel. VisaStay is an
independent app and is not affiliated with, endorsed by, or operated by any government or immigration authority. It
is not legal advice.</p>
<p>Tax residency information (including 183-day or similar thresholds) is general guidance only. Tax residency rules
vary by country — including day-count thresholds, fiscal years, and facts-and-circumstances tests — and we do not
guarantee accuracy for any jurisdiction. It is not tax advice; consult a qualified tax professional before relying on
it.</p>
<p>We maintain visa data on a best-efforts basis. If you spot an error, use "Report a visa info change" in the app or
email <a href="mailto:support@headfirstservices.com">support@headfirstservices.com</a>. We are not liable for any
consequences of relying on information in the app.</p>""",
    your_data="trips, visas, notes, and settings",
    terms_termination="You may stop using VisaStay at any time and delete your account in the app at Profile → Delete Account.",
    delete_steps=["Open VisaStay and go to <strong>Profile</strong>.", "Tap <strong>Delete Account</strong> and confirm."],
    delete_what="your account and sign-in, your profile (email, passport nationality, home currency), all trips, saved visas, starred destinations, alert recipients, and notification settings",
    support_topics=[
        ("I forgot my password", "On the sign-in screen, tap <strong>Forgot password?</strong> and follow the link we email you. It opens straight in the app."),
        ("I bought Pro but the app shows Free", "Go to <strong>Profile → Restore Purchases</strong> while signed in to the same App Store or Google Play account you bought with."),
        ("Cancel a subscription", "Subscriptions are managed by your app store: on iPhone, Settings → your name → Subscriptions; on Android, Google Play → Payments &amp; subscriptions → Subscriptions. The Founder Lifetime Pass never renews."),
        ("A visa rule looks wrong", "Use <strong>Report a visa info change</strong> in the app. Every report is checked against official sources. See our <a href=\"/visastay/sources/\">sources</a>."),
        ("I'm not getting alerts", "Check that notifications are allowed for VisaStay in your phone's settings, and that the alert is turned on in the app. Email alerts and extra recipients need Pro."),
        ("Get a copy of my data", "Go to <strong>Profile → Export My Data</strong>. Pro also has CSV and PDF export of your trips."),
    ],
))

# ---------------- ZoneLink ----------------
APPS.append(dict(
    slug="zonelink", name="ZoneLink", tagline_lc="a visual, sleep-aware time-zone planner",
    suite="Part of the Outbound Suite by HeadFirst Services.", released=True,
    support_email="support@headfirstservices.com", biometric=True,
    processors=["supabase", "revenuecat", "google", "apple"],
    privacy_collect="""
<h3>Favorites and zones</h3>
<p>Favorites you save (name and color) and the entries in each one: a label you choose — such as a person's name,
team, or city — plus a time zone and optional work and sleep hours. The zones on your Home workbench.</p>
<p><strong>If you add another person</strong> (for example, a colleague's name and time zone), you are giving us
limited information about them on your behalf. Only the label and time zone you enter are stored; we do not verify or
enrich it, and only your account can see it.</p>
<h3>Jet lag tracking</h3>
<p>If you use jet lag tracking, we store the time zones you traveled from and to, your arrival time, and your device's
last time zone. ZoneLink reads your phone's time zone setting only — <strong>it never uses your location or
GPS</strong>. You can turn tracking off in Profile → Travel.</p>""",
    privacy_use="""  <li>To show your zones, rank the best times to meet, and warn you about daylight saving changes</li>
  <li>To sync your Favorites across your devices</li>
  <li>To send account emails such as sign-up confirmation and password reset</li>""",
    privacy_visibility="""<p>Your Favorites and zones are visible only to your account. When you share a best-time
card, you choose where it goes; the card is an image created on your phone.</p>""",
    privacy_deletion="""<p>Delete your account in the app at <strong>Profile → Delete Account</strong>. It is deleted
immediately. If you can't use the app, email <a href="mailto:privacy@headfirstservices.com">privacy@headfirstservices.com</a>
and we will permanently delete your account and all associated data within 7 days.</p>
<p>You can also delete individual Favorites or zones without deleting your account. They disappear from the app
immediately, but for sync reliability the record is kept on our servers, marked as deleted, and never shown or used
again. Deleting your account removes everything permanently. See <a href="/zonelink/delete-data/">Delete ZoneLink
data</a>.</p>""",
    terms_tiers="""<p>ZoneLink has a permanent free plan and a paid <strong>Pro</strong> upgrade. Free includes up to 5
zones, sleep/work banding, DST alerts, ranked best times to meet, the shareable overlap card, jet lag tracking,
biometric lock, and one home-screen widget. Pro adds unlimited zones and unlimited saved Favorites. New accounts get 14
days of Pro to try, after which the account moves to the free plan — nothing is locked.</p>""",
    terms_billing="""<p>ZoneLink Pro is a <strong>single one-time purchase</strong> — not a subscription, and it never
renews. The price is shown in the app and on the store before you buy.</p>""",
    terms_disclaimer_title="Time Zone Information",
    terms_disclaimer="""<p>ZoneLink uses the standard IANA time zone database to calculate local times and daylight
saving changes. Governments sometimes change time zone rules at short notice, so we cannot guarantee every time is
correct. Double-check important times — especially around daylight saving changes — before relying on them. We are
not liable for missed or mistimed meetings.</p>""",
    your_data="Favorites, zones, and settings",
    terms_termination="You may stop using ZoneLink at any time and delete your account in the app at Profile → Delete Account.",
    delete_steps=["Open ZoneLink and go to <strong>Profile</strong>.", "Tap <strong>Delete Account</strong> and confirm."],
    delete_what="your account and sign-in, all Favorites and zones, jet lag details, and settings — immediately and permanently",
    delete_extra='<p>Want to remove only some data and keep your account? See <a href="/zonelink/delete-data/">Delete ZoneLink data</a>.</p>',
    faq_json="../../gregtaylorx.github.io/zonelink-faq.json",
    support_topics=[
        ("I forgot my password", "On the sign-in screen, tap <strong>Forgot password?</strong> and follow the link we email you."),
        ("I bought Pro but the app shows Free", "Go to <strong>Profile → Restore Purchases</strong> while signed in to the same App Store or Google Play account you bought with."),
        ("My widget stopped updating", "Open ZoneLink and view the Favorite the widget shows — that refreshes the widget's data."),
        ("A time or DST change looks wrong", "Email us the zone and the date. ZoneLink follows the official IANA time zone data, so we can check whether a rule changed."),
        ("Get a copy of my data", "Go to <strong>Profile → Export My Data</strong>."),
    ],
))

# ---------------- TripGear ----------------
APPS.append(dict(
    slug="tripgear", name="TripGear", tagline_lc="weather-aware packing lists that learn from every trip",
    suite="Part of the Outbound Suite by HeadFirst Services. Coming to the App Store and Google Play.", released=False,
    support_email="support@headfirstservices.com", biometric=False,
    processors=["supabase", "revenuecat", "openmeteo", "google", "apple"],
    privacy_collect="""
<h3>Packing data</h3>
<p>Packing lists you create: destinations, travel dates, trip purpose, transport type, bag type, activities, and the
items on each list with their status (packed / used / not used / wish I'd brought). Templates, favorite items, bag
profiles, outfits, and notes you save. Post-trip debriefs you submit, used to improve your future lists — within your
account only.</p>
<h3>Location</h3>
<p>TripGear does not use your device location. To get a forecast, it sends the coordinates of the destination you
chose to our weather provider.</p>""",
    privacy_use="""  <li>To build your packing lists and adjust them to the weather, your trip, and your past debriefs</li>
  <li>To share a list with the travel partners you choose</li>
  <li>To send account emails such as sign-up confirmation and password reset</li>""",
    privacy_visibility="""<p>Your lists are visible only to your account, unless you share a list — then the people you
share it with can see that list.</p>""",
    privacy_deletion="""<p>Delete your account in the app at <strong>Profile → Delete Account</strong>. If you can't use
the app, email <a href="mailto:privacy@headfirstservices.com">privacy@headfirstservices.com</a> and we will permanently
delete your account and all associated data within 7 days.</p>""",
    terms_tiers="""<p>TripGear has a free plan and a paid <strong>Pro</strong> plan. Free lets you build complete lists
up to the limit shown in the app. Pro adds unlimited lists, templates and bag profiles, laundry and re-wear planning,
shared lists, and learning from your post-trip debriefs. What each plan includes is shown in the app and may change
over time with reasonable notice.</p>""",
    terms_billing="""<p>Pro is available as a subscription (monthly or annual) or as a one-time lifetime purchase.
Prices are shown in the app and on the store before you buy.</p>
<ul>
  <li><strong>Subscriptions renew automatically</strong> at the end of each period unless canceled at least 24 hours before renewal.</li>
  <li><strong>Cancel</strong> in your app store account (iPhone: Settings → your name → Subscriptions; Android: Google Play → Payments &amp; subscriptions → Subscriptions). Canceling stops future charges but does not refund the current period.</li>
  <li>For subscriptions, price changes are communicated at least 30 days in advance.</li>
</ul>""",
    terms_disclaimer_title="Packing Suggestions and Weather",
    terms_disclaimer="""<p>TripGear's packing suggestions are generated automatically from the information you provide
and from weather forecasts or past weather data, which can be wrong. They are recommendations only. Check airline and
border rules for restricted items yourself. We are not responsible for items left behind, lost, confiscated, or
unsuitable for your trip.</p>""",
    your_data="lists, items, templates, and notes",
    terms_termination="You may stop using TripGear at any time and delete your account in the app at Profile → Delete Account.",
    delete_steps=["Open TripGear and go to <strong>Profile</strong>.", "Tap <strong>Delete Account</strong> and confirm twice."],
    delete_what="your account and sign-in, all packing lists and items, templates, favorite items, bag profiles, and post-trip debriefs",
    faq_items=[
        ("TripGear", [
            ("What is TripGear?", "A packing list app that builds your list from where you're going, the weather forecast, how you're traveling, and what you'll be doing — then learns from what you actually used after each trip."),
            ("When is it available?", "TripGear is in testing now and is coming to both the App Store and Google Play."),
            ("Does it work for trips with several stops?", "Yes. Add every leg; each destination gets its own weather, and the list merges them."),
            ("How far ahead can it check the weather?", "Live forecasts cover about 16 days ahead. For trips further out, TripGear uses last year's weather for the same dates."),
            ("Does it work offline?", "Yes. Saved lists stay available without a signal."),
        ]),
        ("Pro and your data", [
            ("Is TripGear free?", "Yes — you can build complete lists for free. Pro adds unlimited lists, templates and bag profiles, laundry and re-wear planning, shared lists, and learning from your post-trip debriefs."),
            ("What is a debrief?", "After a trip, a 30-second check-in records what you used, never touched, or wished you'd brought. Pro uses it to drop unused items and add forgotten ones next time."),
            ("Does TripGear use my location?", "No. It uses only the destinations you enter, to fetch their weather."),
            ("How do I delete my account?", 'Profile → Delete Account in the app. Full details: <a href="/tripgear/delete-account/">Delete your TripGear account</a>.'),
        ]),
    ],
    support_topics=[
        ("I forgot my password", "On the sign-in screen, tap <strong>Forgot password?</strong> and follow the link we email you. It opens straight in the app."),
        ("I bought Pro but the app shows Free", "Go to <strong>Profile → Restore Purchases</strong> while signed in to the same App Store or Google Play account you bought with."),
        ("Get a copy of my data", "Go to <strong>Profile → Export My Data</strong>."),
    ],
))

# ---------------- CostSync (draft, unreleased) ----------------
APPS.append(dict(
    slug="costsync", name="CostSync", tagline_lc="trip-based, multi-currency travel spending",
    suite="Part of the Outbound Suite by HeadFirst Services. Coming to the App Store and Google Play.", released=False,
    draft=True, support_email="support@headfirstservices.com", biometric=True,
    processors=["supabase", "revenuecat", "google", "apple"],
    privacy_collect="""
<h3>Profile information</h3>
<p>Optional home currency, locale, tax country, and preferred expense categories.</p>
<h3>Trips and expenses</h3>
<p>Trips you create (name, countries, cities, dates, purpose, default currency) and the expenses in them: amount,
currency, exchange rate, converted amount, category, merchant, date and time, payment method, optional notes and
location. Receipt images and details read from them, budgets, and wallet balances you set.</p>""",
    privacy_use="""  <li>To organize and convert your travel spending and show trip totals, budgets, and breakdowns</li>
  <li>To send account emails such as sign-up confirmation and password reset</li>""",
    privacy_visibility="""<p>Your trips and expenses are visible only to your account unless you choose to share a
trip with someone.</p>""",
    privacy_processor_note="<p><em>Before release we will add any exchange-rate or email provider CostSync uses.</em></p>",
    privacy_deletion="""<p>Delete your account in the app at <strong>Profile → Delete Account</strong>. If you can't use
the app, email <a href="mailto:privacy@headfirstservices.com">privacy@headfirstservices.com</a> and we will permanently
delete your account and all associated data within 7 days.</p>""",
    terms_tiers="""<p>CostSync will have a free plan and a paid <strong>Pro</strong> plan. What each plan includes will
be shown in the app.</p>""",
    terms_billing="""<p>Pro pricing and billing terms will be shown in the app and on the store before you buy.
Subscriptions, if offered, renew automatically unless canceled at least 24 hours before renewal, and are managed in
your app store account.</p>""",
    terms_disclaimer_title="Currency and Financial Information",
    terms_disclaimer="""<p>Exchange rates and converted amounts are estimates and may differ from what your bank or card
provider actually charged. CostSync is a record-keeping tool, not financial, accounting, or tax advice. Check figures
against your statements before relying on them.</p>""",
    your_data="trips, expenses, receipts, and notes",
    terms_termination="You may stop using CostSync at any time and delete your account in the app at Profile → Delete Account.",
    delete_steps=["Open CostSync and go to <strong>Profile</strong>.", "Tap <strong>Delete Account</strong> and confirm."],
    delete_what="your account and sign-in, all trips, expenses, receipts, budgets, and wallets",
    support_topics=[
        ("When is CostSync available?", "CostSync is in development and is coming to both the App Store and Google Play."),
    ],
))

# ---------------- ChewPaca (no account) ----------------
APPS.append(dict(
    slug="chewpaca", name="ChewPaca", tagline_lc="an app that helps children learn to chew with their mouths closed",
    suite="An app for families by HeadFirst Services.", released=True, no_account=True,
    support_email="ChewPaca@HeadFirstServices.com",
))

# ChewPaca pages are written out in full below (no account, no server).
CHEWPACA_PRIVACY = """
<p class="legal-lede"><strong>ChewPaca collects no data. We never receive anything about you or your child.</strong></p>
<p>There is no account, no sign-in, and no server of ours for anything to be sent to. The camera is used to recognize
chewing as it happens, and those images are discarded immediately — video is never recorded and never stored,
anywhere.</p>
<p>Your child's name and progress are saved on your phone. Your phone may copy that to your own iCloud or Google account
as part of its normal backups, the same as it does for your other apps. That copy belongs to you and sits in your
account; we have no access to it and no way to ask for it. More on this below.</p>

<h2>Who this is for</h2>
<p>ChewPaca helps parents teach children to chew with their mouths closed. It is bought and set up by a parent or
caregiver, and used by a child under their supervision. Because children use it, we designed it to collect nothing at
all rather than to collect carefully.</p>

<h2>The camera</h2>
<p>During a practice session, the phone's front camera looks at your child's face and works out whether they are
chewing with their lips closed. All of that happens on the device itself, using software built into the app.</p>
<p>Each frame is examined and then thrown away. Nothing is written to storage, nothing is uploaded, and no image ever
reaches us or any third party. We could not look at your child even if we wanted to — there is nowhere for that video to
go.</p>
<p>The app asks for camera permission the first time it needs it. You can withdraw permission at any time in your device
settings; the app will then stop being able to run a practice session.</p>

<h2>The microphone</h2>
<p>ChewPaca does not use the microphone. It never asks for microphone permission and never listens to audio.</p>

<h2>What is stored on your device</h2>
<p>The app keeps a small amount of information on your phone so your child's progress survives closing the app:</p>
<div class="legal-table"><table>
  <tr><th>What</th><th>Why</th></tr>
  <tr><td>The name or nickname you type for your child, and an age range</td><td>So the app can address them and pace practice sensibly</td></tr>
  <tr><td>Practice history — rounds, tokens earned, rewards swapped, and the animals your child has chosen and named</td><td>To show progress and keep the reward system working</td></tr>
  <tr><td>Your settings and, if you set one, a parent PIN</td><td>To remember your preferences</td></tr>
</table></div>
<p>We never receive any of it. Deleting the app deletes it from your phone.</p>

<h2>Phone backups</h2>
<p>We want to be precise here, because it would be easy to overclaim.</p>
<p>iPhones and Android phones back up installed apps' data to the owner's iCloud or Google account automatically.
ChewPaca is an ordinary app, so unless you have turned that off, the information in the table above may be included —
your child's name, their practice history, their badges, and the animals in their barn.</p>
<p>That backup is yours, not ours. It goes to your account, under your control, protected by your own password. We are
not a party to it, cannot access it, and could not retrieve it if asked. No video or audio is ever included, because
none is ever stored in the first place.</p>
<p>If you would rather it were not backed up at all, both platforms let you exclude individual apps:</p>
<ul>
  <li><strong>iPhone:</strong> Settings → your name → iCloud → Manage Account Storage → Backups → this device → switch off ChewPaca</li>
  <li><strong>Android:</strong> Settings → Google → Backup → App data</li>
</ul>
<p>You can still move to a new phone using the export and import feature in ChewPaca's own settings, which does not
involve either company.</p>

<h2>Analytics, advertising and tracking</h2>
<p>There are none. ChewPaca contains no analytics, no advertising, no tracking pixels, and no third-party software
development kits that collect data about you or your child. We do not know how many times you have opened the app.</p>

<h2>Purchases</h2>
<p>If you buy anything in ChewPaca, the purchase is handled entirely by Apple's App Store or Google Play. The store
tells the app on your device that the purchase went through, so it can unlock what you paid for. Nothing about you or
the purchase is sent to us; the stores give us only overall sales totals, never who bought.</p>

<h2>Moving to a new device</h2>
<p>Because nothing is stored on a server, progress does not sync automatically. If you move to a new phone, the app can
export your child's progress to a file that you choose where to send. That file contains the information listed above.
It goes wherever you send it and nowhere else — it never passes through us.</p>

<h2>Children's privacy</h2>
<p>ChewPaca is designed to be used by children. We do not knowingly collect any personal information from anyone, of any
age, because we do not collect personal information at all. There is no account to create, no profile to build, no
message to send, and no way for a child to communicate with anyone through the app. The only link out of the app is the
support email address in Settings. Purchases are made through Apple or Google, which ask the account holder to
confirm.</p>

<h2>Your rights</h2>
<p>Laws such as the GDPR and COPPA give you rights to see, correct, and delete data held about you. In our case there is
nothing to exercise those rights against, because we hold nothing. All information lives on your device and is fully
under your control — deleting the app erases it completely.</p>

<h2>Changes to this policy</h2>
<p>If ChewPaca ever changes in a way that affects this policy, we will update this page and change the date at the top.
If a future version were ever to collect anything, we would say so plainly and ask you first.</p>

<h2>If you email us</h2>
<p>Emailing support is the only way we ever receive anything from you, and it is entirely your choice. We use your email
address and message only to help you and to improve ChewPaca. We never add you to a mailing list, and we never share or
sell your email. Please don't include your child's full name, photos, videos, or health details — we don't need them to
help.</p>

<h2>Contact</h2>
<p>Questions about privacy: <a href="mailto:privacy@headfirstservices.com">privacy@headfirstservices.com</a><br>
Help with the app: <a href="mailto:ChewPaca@HeadFirstServices.com">ChewPaca@HeadFirstServices.com</a></p>
<p>ChewPaca is made by HeadFirstServices LLC, Washington State, USA.</p>
"""

CHEWPACA_TERMS_HEAD = f"""
<p>These Terms of Service ("Terms") govern your use of <strong>ChewPaca</strong>, a mobile app operated by {COMPANY}
("we", "us", "our"). By downloading, installing, or using ChewPaca, you agree to these Terms. If you do not agree, do
not use the app.</p>

<h2>1. Who Can Use ChewPaca</h2>
<p>ChewPaca is meant to be downloaded, set up, and purchased by a parent or legal guardian, and used by their child
under adult supervision. By setting it up you confirm you are an adult with authority to agree to these Terms for your
family.</p>

<h2>2. No Account</h2>
<p>ChewPaca has no account and no sign-in. Everything the app saves stays on your device (see the
<a href="/chewpaca/privacy/">Privacy Policy</a>). You are responsible for your device and, if you choose, for keeping
a backup of the export file the app can create.</p>

<h2>3. Free Use and the Unlock</h2>
<p>You can try a full practice-to-reward cycle for each child for free. After that, a <strong>single one-time
purchase</strong> unlocks ChewPaca for every child on that store account — it is not a subscription and never renews.
The price is shown in the app and on the store before you buy. On the App Store it supports Family Sharing.</p>

<h2>4. Purchases and Refunds</h2>
<ul>
  <li>The purchase is processed by the Apple App Store or Google Play and is subject to their terms.</li>
  <li><strong>Refunds</strong> are handled by the relevant app store under its refund policy. We do not issue refunds directly.</li>
  <li>To restore the unlock on a new phone, use <strong>Settings → Purchases</strong> in the app.</li>
</ul>

<h2>5. Not Medical Advice</h2>
<p><strong>ChewPaca is not a medical, dental, feeding, or swallowing assessment</strong>, and it does not diagnose or
treat anything. Some children find closed-mouth chewing genuinely hard because of blocked nasal breathing, enlarged
tonsils or adenoids, allergies, or oral-motor differences, which practice will not fix. If your child has pain while
chewing, coughs or chokes during meals, or usually breathes through their mouth, stop and talk to your pediatrician,
dentist, or an ENT. Supervise your child during meals at all times, and place the phone where it cannot fall into food
or be handled by your child.</p>

<h2>6. Acceptable Use</h2>
<p>You agree not to reverse engineer, decompile, or disassemble ChewPaca, use it for any unlawful purpose, or use it in
a way that could damage or impair it.</p>

<h2>7. Intellectual Property</h2>
<p>ChewPaca, including its characters, artwork, sounds, design, code, trademarks, and branding, is owned by {COMPANY} or
used under license (sound credits are listed on the <a href="/chewpaca/support/#credits">support page</a>), and is
protected by intellectual property laws. Your child's progress data remains yours.</p>
"""

CHEWPACA_FAQ = [
    ("Getting set up", [
        ("Where should I put the phone?", "Propped up, facing your child, roughly at the far side of their plate — about an arm's length away (20–28 in / 50–70 cm). It needs to see their face, so put it somewhere it will not get knocked. A cheap phone stand helps; leaning it against a glass works too. Your child should never hold the phone. If it gets picked up or moved, the app pauses rather than guessing."),
        ("It says the camera cannot see a face", "Usually one of three things: the phone is too far away, the room is too dim, or your child is looking down at their plate. Move the phone closer, add light, and angle it slightly upward toward their face."),
        ("Does it use the microphone?", "No. ChewPaca only uses the camera, and never records it."),
    ]),
    ("Running a session", [
        ("How long should we practice?", "One meal a day, at least for the first week. That is not a limitation we added to be annoying — practicing a little and often works considerably better than drilling, and pushing harder tends to turn mealtimes into a struggle."),
        ("Nothing happened when my child chewed with their mouth open", "That is deliberate. ChewPaca only ever responds to success. When your child keeps chewing with their lips closed, their alpaca or horse chews along and footprints appear, one by one. When they do not, nothing happens at all — no buzzer, no red mark, no tally. Children learn this skill faster from being caught doing it right than from being corrected doing it wrong."),
        ("What do I actually do during the meal?", "Not much, and that is the point. At the end of each round the app prompts you with one short sentence to say out loud — something specific like \"I noticed your lips stayed together while you chewed.\" That sentence is the part that teaches. The animal holds your child's attention; your praise is what makes the habit stick."),
        ("How do I stop a session?", "Press and hold the ✕ in the corner for about a second. It takes a deliberate hold so a stray finger cannot end the meal."),
    ]),
    ("The animals", [
        ("Alpaca or horse?", "Either. When you set up a child, choose an alpaca or a horse and pick its look — coat color, and for an alpaca a scarf and backpack, or for a horse an optional white blaze and a saddle and bedroll in colors of your choice. Give it a name, or tap <strong>Surprise me</strong>."),
        ("What happens when a reward is delivered?", "Your child's animal walks off to the barn, and they choose a new one — alpaca or horse, any look. Every animal stays in the barn for good. Tap an animal there to watch its walk again; tap its name to rename it."),
        ("Can my child use ChewPaca without the animal on screen?", "Yes. On the home screen, switch <strong>Alpaca</strong> (or <strong>Horse</strong>) off for a plain progress ring with green lines instead. For ages 11–13 this is the default, and either way your child can switch it themselves."),
        ("What is the sound at the end of each round?", "A soft hum from the alpaca, or a quiet nicker from the horse. It is your cue to say something, because you probably can't see the screen from across the table. Turn it off with the <strong>Sound</strong> button on the home screen."),
        ("Can my child start practice on their own?", "Yes. If you set a parent PIN in Settings, your child can still start a session and switch the animal or sound on and off. The PIN is only asked for Settings, bonus tokens, confirming a reward was delivered, adding a child, and practicing beyond the daily limit. Bonus tokens always need a grown-up: without a PIN, the app asks a quick grown-up question instead."),
    ]),
    ("Tokens and rewards", [
        ("How do tokens work?", "A good round earns a token. A few tokens swap for a real-world reward you agreed on beforehand — choosing the bedtime story, picking the music in the car, ten extra minutes before bed. Tokens are never taken away. Once earned, they are earned, even after a bad meal."),
        ("Why are the rewards not candy?", "Tying food to the lesson tends to turn mealtimes into a negotiation, which is the opposite of what we are going for. Attention, choice, and a small activity work better and cost nothing."),
        ("How do stages, rounds and tokens work?", "Practice has four stages: Learning, Practicing, Maintaining and Fading out. Every good round earns one token — that never changes. As the habit forms, a reward takes more tokens: 3, then 5, then 8, then 10. Rounds also get longer, from 20 seconds up to 90, depending on your child's age and stage. A new price only applies after the reward your child is currently saving for, and rounds only lengthen once a reward is earned at the new stage, so the goal never moves midway. Moving up a stage takes a minimum number of meals and days plus a steady success rate. Two hard meals in a row pause progress for a few meals; mostly hard recent meals step practice back one stage with shorter rounds. That is normal, not failure. Learning never steps back. In Fading out, log meals where your child chewed well with no app. Two logged app-free meals plus a good run suggest graduating — the aim is for your child not to need the app at all."),
    ]),
    ("Privacy and devices", [
        ("Does anything leave my phone?", "Nothing goes to us — there is no ChewPaca server, no account, and no analytics, and video is never recorded. Your phone's own iCloud or Google backup may include the app's saved progress, like every other app; see the <a href=\"/chewpaca/privacy/\">Privacy Policy</a> for how to switch that off."),
        ("Moving to a new phone", "Because nothing is stored on a server, progress does not sync by itself. In Settings you can export your child's progress to a file and import it on the new device. Restore your unlock in Settings → Purchases."),
    ]),
]

# --------------------------------------------------------------------------
# Page shell
# --------------------------------------------------------------------------

def nav(a):
    return f"""<nav class="site-nav">
  <div class="container">
    <a class="brand-mark" href="/">
      <span class="mono">HF</span>
      HeadFirst Services
    </a>
    <div class="nav-links">
      <a href="/{a['slug']}/">{a['name']}</a>
      <a href="/{a['slug']}/faq/">FAQ</a>
      <a href="/{a['slug']}/support/" class="nav-cta">Support</a>
    </div>
  </div>
</nav>"""


def footer(a):
    extra = '\n          <li><a href="/zonelink/delete-data/">Delete Data</a></li>' if a['slug'] == 'zonelink' else ''
    del_label = "Your Data" if a.get('no_account') else "Delete Account"
    return f"""<footer class="site-footer">
  <div class="container">
    <div class="footer-grid">
      <div>
        <h4>{a['name']}</h4>
        <p style="color:var(--color-text-muted); font-size:14px; max-width:32ch;">{a['suite']}</p>
      </div>
      <div>
        <h4>Help</h4>
        <ul>
          <li><a href="/{a['slug']}/">Overview</a></li>
          <li><a href="/{a['slug']}/faq/">FAQ</a></li>
          <li><a href="/{a['slug']}/support/">Support</a></li>
        </ul>
      </div>
      <div>
        <h4>Legal</h4>
        <ul>
          <li><a href="/{a['slug']}/privacy/">Privacy Policy</a></li>
          <li><a href="/{a['slug']}/terms/">Terms of Service</a></li>
          <li><a href="/{a['slug']}/delete-account/">{del_label}</a></li>{extra}
        </ul>
      </div>
      <div>
        <h4>Contact</h4>
        <ul>
          <li><a href="mailto:{a['support_email']}">{a['support_email']}</a></li>
          <li><a href="/">HeadFirst Services</a></li>
        </ul>
      </div>
    </div>
    <div class="footer-bottom">
      <span>&copy; 2026 HeadFirst Services. All rights reserved.</span>
    </div>
  </div>
</footer>"""


def page(a, sub, title, eyebrow, h1, lede, body, desc, jsonld=None):
    url = f"https://headfirstservices.com/{a['slug']}/{sub}/"
    robots = '\n<meta name="robots" content="noindex">' if a.get('draft') else ''
    draft = ('<div class="note-box" style="margin-bottom:24px;"><strong>Draft.</strong> CostSync has not been released yet. '
             'This page will be finalized before launch.</div>\n') if a.get('draft') else ''
    ld = f'\n<script type="application/ld+json">\n{json.dumps(jsonld, ensure_ascii=False, indent=1)}\n</script>' if jsonld else ''
    lede_html = f'\n    <p class="lede">{lede}</p>' if lede else ''
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(desc)}">
<link rel="canonical" href="{url}">{robots}
<link rel="stylesheet" href="/assets/css/style.css">
<meta property="og:type" content="website">
<meta property="og:title" content="{html.escape(title)}">
<meta property="og:description" content="{html.escape(desc)}">
<meta property="og:url" content="{url}">{ld}
</head>
<body>

{nav(a)}

<section class="hero">
  <div class="container">
    <a class="back-link" href="/{a['slug']}/">← {a['name']}</a>
    <span class="eyebrow">{eyebrow}</span>
    <h1>{h1}</h1>{lede_html}
  </div>
</section>

<section style="padding-top:0;">
  <div class="container legal">
{draft}{body}
  </div>
</section>

{footer(a)}

</body>
</html>
"""


def faq_html(sections):
    out = []
    first = True
    for i, (cat, items) in enumerate(sections):
        style = '' if i == 0 else ' style="margin-top:32px;"'
        out.append(f'<p class="category-label"{style}>{cat}</p>')
        for q, ans in items:
            op = ' open' if first else ''
            first = False
            out.append(f'<details class="faq-item"{op}>\n  <summary><h3 style="display:inline;">{q}</h3></summary>\n  <p>{ans}</p>\n</details>')
    return "\n".join(out)


def faq_jsonld(sections):
    return {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": re.sub(r"<[^>]+>", "", ans)}}
        for _, items in sections for q, ans in items]}


def zonelink_faq_sections(path):
    p = os.path.join(ROOT, path)
    if not os.path.exists(p):
        sys.exit(f"ZoneLink FAQ source not found: {p}")
    d = json.load(open(p, encoding="utf-8"))
    def esc(t):
        return html.escape(t).replace("\n", "<br>")
    return [(s["title"], [(esc(i["q"]), esc(i["a"])) for i in s["items"]]) for s in d["sections"]]


def support_body(a):
    topics = "\n".join(
        f'<details class="faq-item"{" open" if i == 0 else ""}>\n  <summary><h3 style="display:inline;">{q}</h3></summary>\n  <p>{ans}</p>\n</details>'
        for i, (q, ans) in enumerate(a.get('support_topics', [])))
    stores = ''
    if a['slug'] in STORE:
        play, ios = STORE[a['slug']]
        stores = f'''
<h2>Get the app</h2>
<div class="store-badges">
  <a class="store-badge" href="{play}" target="_blank" rel="noopener">▶ Google Play</a>
  <a class="store-badge" href="{ios}" target="_blank" rel="noopener">🍎 App Store</a>
</div>'''
    return f"""
<h2>Contact us</h2>
<p>Email <a href="mailto:{a['support_email']}?subject={a['name']}%20support">{a['support_email']}</a>. Tell us what
happened, what phone you're using, and what you expected instead. We usually reply within two business days.</p>
<p>Privacy questions: <a href="mailto:{PRIVACY_EMAIL}">{PRIVACY_EMAIL}</a>.</p>

<h2>Common questions</h2>
{topics}
<p style="margin-top:16px;">More answers in the <a href="/{a['slug']}/faq/">{a['name']} FAQ</a>.</p>

<h2>Your account and data</h2>
<ul>
  <li><a href="/{a['slug']}/delete-account/">Delete your {a['name']} account</a></li>
  <li><a href="/{a['slug']}/privacy/">Privacy Policy</a></li>
  <li><a href="/{a['slug']}/terms/">Terms of Service</a></li>
</ul>
{stores}
"""


def chewpaca_support_body(a):
    play, ios = STORE['chewpaca']
    return f"""
<h2>Contact us</h2>
<p>Email <a href="mailto:ChewPaca@HeadFirstServices.com?subject=ChewPaca%20support">ChewPaca@HeadFirstServices.com</a>
and tell us what happened, what phone you're using, and what you expected instead. Please don't include your child's
full name, photos, videos, or health details — we don't need them to help. Privacy questions:
<a href="mailto:{PRIVACY_EMAIL}">{PRIVACY_EMAIL}</a>.</p>

<h2>Quick fixes</h2>
<details class="faq-item" open>
  <summary><h3 style="display:inline;">The camera cannot see a face</h3></summary>
  <p>Move the phone closer (about an arm's length), add light, and angle it slightly upward toward your child's face.
  Make sure camera permission is allowed for ChewPaca in your phone's settings.</p>
</details>
<details class="faq-item">
  <summary><h3 style="display:inline;">I bought the unlock but it's locked again</h3></summary>
  <p>Open <strong>Settings → Purchases</strong> and restore, signed in to the same App Store or Google Play account you
  bought with.</p>
</details>
<details class="faq-item">
  <summary><h3 style="display:inline;">Moving to a new phone</h3></summary>
  <p>Export your child's progress in Settings, import it on the new phone, then restore your unlock in Settings →
  Purchases.</p>
</details>
<p style="margin-top:16px;">More answers in the <a href="/chewpaca/faq/">ChewPaca FAQ</a>.</p>

<h2>When to stop and ask someone</h2>
<p>Some children physically cannot chew with their mouth closed. Blocked nasal breathing, enlarged tonsils or adenoids,
allergies, a deviated septum, or oral-motor differences can all make it genuinely hard or uncomfortable. Practicing
will not fix any of those.</p>
<p>If your child has pain while chewing, coughs or chokes during meals, struggles with certain textures, or usually
breathes through their mouth, mention what you have noticed to your pediatrician, dentist, or an ENT before continuing.
If there is little change after a couple of weeks of regular practice, ChewPaca shows this list again as a reminder
before the next session.</p>
<p><strong>ChewPaca is not a medical, dental, feeding, or swallowing assessment.</strong> Stop and seek advice from an
appropriate clinician if you have concerns.</p>

<h2>Why we don't say "nothing ever leaves your phone"</h2>
<p>It would be a better line, and plenty of apps use it. We think it would be slightly untrue, so here is the precise
version. <strong>Nothing goes to us</strong> — there is no ChewPaca server, no account system, no analytics, and no way
to receive your child's name, their progress, or a single frame of video. But your phone backs up its apps: unless you
have turned that off, iOS copies app data to your iCloud and Android copies it to your Google account — ChewPaca
included. That backup holds your child's name or nickname, an age range, their practice history and badges, in your
account, under your password. It never contains video or audio. To exclude it, see the
<a href="/chewpaca/privacy/">Privacy Policy</a>.</p>

<h2 id="credits">Sound credits</h2>
<p>Horse sounds from <a href="https://freesound.org" target="_blank" rel="noopener">freesound.org</a>, trimmed and
level-adjusted for the app:</p>
<ul>
  <li>“Horse Whinny 1.wav” by GoodListener — <a href="https://freesound.org/s/322445/" target="_blank" rel="noopener">freesound.org/s/322445</a> — licensed <a href="https://creativecommons.org/licenses/by/4.0/" target="_blank" rel="noopener">CC BY 4.0</a>.</li>
  <li>“horse neigh shortened.wav” by shadoWisp — <a href="https://freesound.org/s/269571/" target="_blank" rel="noopener">freesound.org/s/269571</a> — CC0.</li>
  <li>“Renill de cavall / Horse Neigh” by Salsero_classic — <a href="https://freesound.org/s/826753/" target="_blank" rel="noopener">freesound.org/s/826753</a> — CC0.</li>
</ul>

<h2>Get the app</h2>
<div class="store-badges">
  <a class="store-badge" href="{play}" target="_blank" rel="noopener">▶ Google Play</a>
  <a class="store-badge" href="{ios}" target="_blank" rel="noopener">🍎 App Store</a>
</div>
"""


def delete_body(a):
    if a.get('no_account'):
        return """
<p><strong>ChewPaca has no account, so there is nothing to delete on our side.</strong> We never receive your child's
name, progress, or any video — there is no ChewPaca server.</p>
<h2>Delete ChewPaca's data from your phone</h2>
<ul>
  <li><strong>Remove everything:</strong> uninstall ChewPaca. All of its data on the phone is erased.</li>
  <li><strong>Phone backups:</strong> your iCloud or Google backup may hold a copy of the app's data. To remove it, see
  <a href="/chewpaca/privacy/">Phone backups in the Privacy Policy</a>.</li>
</ul>
<p>Questions? <a href="mailto:privacy@headfirstservices.com">privacy@headfirstservices.com</a></p>
"""
    steps = "\n".join(f"  <li>{s}</li>" for s in a['delete_steps'])
    subj = f"Delete%20my%20{a['name']}%20account"
    body = f"Please%20delete%20my%20{a['name']}%20account%20and%20all%20associated%20data.%0A%0AEmail%20address%20on%20the%20account%3A%20"
    return f"""
<p>{a['name']} has its own account, separate from our other apps. Deleting it never affects your accounts in other
HeadFirst Services apps.</p>

<h2>Fastest: delete in the app</h2>
<ol>
{steps}
</ol>
<p>This deletes {a['delete_what']}.</p>
{a.get('delete_extra', '')}
<h2>Can't use the app? Email us</h2>
<p>Email <a href="mailto:{PRIVACY_EMAIL}">{PRIVACY_EMAIL}</a> from the address on your account (or tell us that
address). We will permanently delete your account and all associated data within <strong>7 days</strong> and confirm by
email.</p>
<p><a class="btn btn-primary" href="mailto:{PRIVACY_EMAIL}?subject={subj}&amp;body={body}">Request account deletion</a></p>

<h2>Before you delete</h2>
<ul>
  <li>Want a copy first? Use <strong>Profile → Export My Data</strong> in the app.</li>
  <li>Deleting your account does not cancel an app store subscription. Cancel it in your App Store or Google Play account
  so you aren't charged again.</li>
</ul>
<p>More detail: <a href="/{a['slug']}/privacy/">{a['name']} Privacy Policy</a>.</p>
"""


ZONELINK_DELETE_DATA = """
<p>You can delete some of your ZoneLink data without deleting your account, or delete everything at once.</p>

<h2>Favorites and the zones in them</h2>
<p>To remove a zone, tap the trash icon next to it. To remove a whole Favorite, open its settings (the gear icon in
History) and tap <strong>Delete favorite</strong>. Either one disappears from the app immediately.</p>
<div class="note-box"><strong>Retention:</strong> so your devices stay in sync, a deleted Favorite or zone is marked as
deleted on our servers rather than erased right away. It is never shown, returned to the app, or used for anything
after you delete it. Deleting your account (below) erases it permanently and immediately.</div>

<h2>Jet lag tracking</h2>
<p>Go to <strong>Profile → Travel</strong> and turn off jet lag tracking to stop ZoneLink asking when your device's
time zone changes. ZoneLink never uses your location for this. Any jet lag details already saved are erased when you
delete your account.</p>

<h2>Get a copy first</h2>
<p>Go to <strong>Profile → Export My Data</strong> to download everything ZoneLink holds about you.</p>

<h2>Everything (full account deletion)</h2>
<p>To permanently delete your ZoneLink account and all of its data, immediately and with nothing retained:</p>
<p><a class="btn btn-primary" href="/zonelink/delete-account/">Delete my account</a></p>
<p>Questions about your data? <a href="mailto:privacy@headfirstservices.com">privacy@headfirstservices.com</a></p>
"""

# --------------------------------------------------------------------------

def write(path, text):
    full = os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    return path


def build():
    written = []
    for a in APPS:
        s, n = a['slug'], a['name']
        upd = f'<p class="legal-updated">Last updated: {UPDATED}</p>'
        # Privacy
        if a.get('no_account'):
            pbody = CHEWPACA_PRIVACY
        else:
            pbody = privacy_account_app(a)
        written.append(write(f"{s}/privacy/index.html", page(a, "privacy", f"{n} Privacy Policy", "Privacy",
                       f"{n} Privacy Policy", None, upd + pbody, f"How {n} handles your information.")))
        # Terms
        if a.get('no_account'):
            tbody = CHEWPACA_TERMS_HEAD + shared_terms_tail(dict(a, terms_termination="You may stop using ChewPaca at any time by uninstalling it, which erases all of its data from your phone."), survive="7, 9, 10, 11, and 12")
        else:
            tbody = terms_account_app(a)
        written.append(write(f"{s}/terms/index.html", page(a, "terms", f"{n} Terms of Service", "Terms",
                       f"{n} Terms of Service", None, upd + tbody, f"Terms of Service for {n}.")))
        # Support
        sbody = chewpaca_support_body(a) if s == 'chewpaca' else support_body(a)
        written.append(write(f"{s}/support/index.html", page(a, "support", f"{n} Support", "Support",
                       f"{n} support", f"Help with {n}, and how to reach us.", sbody, f"Get help with {n}.")))
        # Delete account
        dtitle = "Your ChewPaca data" if a.get('no_account') else f"Delete your {n} account"
        written.append(write(f"{s}/delete-account/index.html", page(a, "delete-account", f"{dtitle} — {n}",
                       "Your data", dtitle, None, delete_body(a), f"How to delete your {n} account and data.")))
        # FAQ
        sections = None
        if s == 'chewpaca':
            sections = CHEWPACA_FAQ
        elif a.get('faq_json'):
            sections = zonelink_faq_sections(a['faq_json'])
        elif a.get('faq_items'):
            sections = a['faq_items']
        if sections and not a.get('own_faq'):
            written.append(write(f"{s}/faq/index.html", page(a, "faq", f"{n} FAQ", "FAQ", f"{n} frequently asked questions",
                           None, faq_html(sections) + f'\n<p style="margin-top:32px;">Still stuck? <a href="/{s}/support/">Contact support</a>.</p>',
                           f"Answers to common questions about {n}.", jsonld=faq_jsonld(sections))))
        elif not sections and not a.get('own_faq'):
            written.append(write(f"{s}/faq/index.html", page(a, "faq", f"{n} FAQ", "FAQ", f"{n} FAQ", None,
                           f'<p>{n} is in development and is coming to both the App Store and Google Play. Answers to common questions will appear here at launch.</p>\n<p>Questions now? <a href="/{s}/support/">Contact us</a>.</p>',
                           f"{n} FAQ.")))
        if s == 'zonelink':
            written.append(write("zonelink/delete-data/index.html", page(a, "delete-data", "Delete ZoneLink data", "Your data",
                           "Delete your ZoneLink data", None, ZONELINK_DELETE_DATA, "Delete some or all of your ZoneLink data.")))
    return written


def build_hub():
    rows = []
    for a in APPS:
        if a.get('draft'):
            continue
        s, n = a['slug'], a['name']
        dl = "Your data" if a.get('no_account') else "Delete account"
        status = "" if a.get('released') else ' <span class="status-pill status-soon">Coming soon</span>'
        rows.append(f"""<div class="card">
  <h3><a href="/{s}/">{n}</a>{status}</h3>
  <ul>
    <li><a href="/{s}/privacy/">Privacy Policy</a></li>
    <li><a href="/{s}/terms/">Terms of Service</a></li>
    <li><a href="/{s}/support/">Support</a></li>
    <li><a href="/{s}/faq/">FAQ</a></li>
    <li><a href="/{s}/delete-account/">{dl}</a></li>
  </ul>
</div>""")
    body = ('<p>Each HeadFirst Services app has its own privacy policy, terms, and account. Choose your app:</p>\n'
            '<div class="grid grid-3">\n' + "\n".join(rows) + '\n</div>\n'
            '<p style="margin-top:32px;">Privacy questions: <a href="mailto:privacy@headfirstservices.com">privacy@headfirstservices.com</a> · '
            'Support: <a href="mailto:support@headfirstservices.com">support@headfirstservices.com</a></p>')
    hub_app = dict(slug="", name="HeadFirst Services", suite="Mobile app development studio.", support_email="support@headfirstservices.com")
    out = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Legal and support — HeadFirst Services</title>
<meta name="description" content="Privacy policies, terms, support, and account deletion for every HeadFirst Services app.">
<link rel="canonical" href="https://headfirstservices.com/legal/">
<link rel="stylesheet" href="/assets/css/style.css">
</head>
<body>

<nav class="site-nav">
  <div class="container">
    <a class="brand-mark" href="/">
      <span class="mono">HF</span>
      HeadFirst Services
    </a>
    <div class="nav-links">
      <a href="/#products">Apps</a>
      <a href="mailto:support@headfirstservices.com" class="nav-cta">Contact</a>
    </div>
  </div>
</nav>

<section class="hero">
  <div class="container">
    <a class="back-link" href="/">← HeadFirst Services</a>
    <span class="eyebrow">Legal and support</span>
    <h1>Privacy, terms, and support by app</h1>
  </div>
</section>

<section style="padding-top:0;">
  <div class="container">
{body}
  </div>
</section>

<footer class="site-footer">
  <div class="container">
    <div class="footer-bottom">
      <span>&copy; 2026 HeadFirst Services. All rights reserved.</span>
      <span>support@headfirstservices.com</span>
    </div>
  </div>
</footer>

</body>
</html>
"""
    return write("legal/index.html", out)


if __name__ == "__main__":
    for w in build():
        print(w)
    print(build_hub())
