#!/usr/bin/env python3
"""Build the free SEO resource pages for CertTrack and Property Alerts USA.

Run: python3 docs/build.py   (writes HTML next to this file; GitHub Pages serves /docs)
"""
import os, json, html

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = "https://arshank1.github.io/certtrack-social"
UPDATED = "2026-10-01"

BRANDS = {
    "certtrack": {
        "name": "CertTrack", "url": "https://certtracksecure.com", "accent": "#1f388a", "accent2": "#ffb020",
        "cta_title": "Stop tracking expiration dates by hand",
        "cta_body": "CertTrack keeps every license, permit, certification and insurance policy in one place and alerts you before anything expires.",
        "cta_button": "See CertTrack",
    },
    "property-alerts": {
        "name": "Property Alerts USA", "url": "https://propertyalertsusa.com", "accent": "#0d4a3e", "accent2": "#7ee7b0",
        "cta_title": "Put your lease dates on autopilot",
        "cta_body": "Property Alerts USA scans your leases for renewal, option, inspection and insurance dates, then reminds you 30, 7 and 3 days before each one.",
        "cta_button": "See a sample digest",
        "cta_url": "https://propertyalertsusa.com/demo.html",
    },
}

PAGES = []

def page(brand, slug, title, description, body):
    PAGES.append(dict(brand=brand, slug=slug, title=title, description=description, body=body))

# ---------------------------------------------------------------- CertTrack
page("certtrack", "license-permit-expiration-tracker",
 "How to Track License and Permit Expiration Dates (Without a Spreadsheet)",
 "A practical system for tracking business licenses, permits, certifications and insurance policies so nothing expires unnoticed.",
 """
<p class="lead">Most businesses don't lose a license because they ignored it. They lose it because the renewal date lived in one person's head, an old email, or a spreadsheet nobody opened that month.</p>

<p>If your company holds more than a handful of licenses, permits, certifications and insurance policies, you need a system: one list, one owner per item, and reminders that arrive early enough to act. Here is how to set one up.</p>

<h2>1. Build one complete inventory</h2>
<p>Start by listing every document that has an expiration date. Most businesses undercount on the first pass, so check each category:</p>
<ul>
<li><strong>Business-level licenses:</strong> city or county business license, state contractor or professional license, seller's permit, health permit, liquor license.</li>
<li><strong>Operating permits:</strong> fire inspection certificates, occupancy permits, signage permits, elevator or boiler certificates, hazardous materials permits.</li>
<li><strong>Insurance:</strong> general liability, workers' compensation, commercial auto, professional liability, and the certificates of insurance (COIs) your clients ask for.</li>
<li><strong>Bonds:</strong> license bonds and surety bonds, which renew on their own schedule.</li>
<li><strong>People:</strong> employee licenses and certifications such as CPR, food handler cards, OSHA training, CDLs and trade certifications.</li>
<li><strong>Vehicles and equipment:</strong> registrations, inspections and DOT filings.</li>
</ul>
<p>For each item, record the document name, who or what it covers, the issuing agency, the expiration date, and where the current copy is stored.</p>

<h2>2. Give every item an owner</h2>
<p>A reminder sent to "everyone" is a reminder sent to no one. Assign one person to each renewal, plus a backup for when that person is on vacation or leaves the company.</p>

<h2>3. Work backward from the real deadline</h2>
<p>The expiration date is not the deadline. Many renewals need a fresh insurance certificate, continuing education hours, an inspection or a background check first, and agencies can take weeks to process paperwork. Set your first reminder far enough out to cover the slowest step:</p>
<table>
<tr><th>Item type</th><th>First reminder</th><th>Why</th></tr>
<tr><td>State licenses with education requirements</td><td>90 days</td><td>Courses and exams take time to schedule</td></tr>
<tr><td>Permits needing an inspection</td><td>60 days</td><td>Inspection slots fill up</td></tr>
<tr><td>Insurance policies and COIs</td><td>45 days</td><td>Quotes, underwriting and new certificates</td></tr>
<tr><td>Employee certifications</td><td>30 days</td><td>Classes are usually easy to book</td></tr>
</table>
<p>Then add a second and third reminder closer in, so a missed email doesn't become a missed renewal.</p>

<h2>4. Why spreadsheets and calendar reminders break down</h2>
<p>A spreadsheet works until it doesn't. Someone sorts a column wrong, the file lives on one laptop, or the person who built it leaves. Calendar reminders are better, but they are tied to one person's account and are easy to snooze and forget.</p>
<p>The warning sign is simple: if you can't answer "what expires in the next 60 days?" in under a minute, your system is fragile.</p>

<h2>5. Keep proof, not just dates</h2>
<p>Store a copy of each current document next to its date. When a client, inspector or insurer asks for proof, you want to send it in minutes, not search through email.</p>

<h2>6. Review monthly</h2>
<p>Put a 15-minute review on the calendar once a month. Look at everything expiring in the next 90 days, confirm each owner knows, and add any new licenses, hires or vehicles from the past month.</p>

<h2>A dedicated tracker does this for you</h2>
<p>Expiration-tracking software exists so this process runs without depending on memory. You enter each document once, and the system sends escalating reminders before every deadline to the people responsible.</p>
""")

page("certtrack", "coi-tracking-small-business",
 "Certificate of Insurance (COI) Tracking for Small Businesses",
 "What a certificate of insurance is, why clients ask for it, and a simple process to track COIs you give and COIs you collect.",
 """
<p class="lead">A certificate of insurance (COI) is a one-page summary proving that a business carries insurance. Clients, landlords and general contractors ask for them constantly, and an expired one can stall a job or a payment.</p>

<h2>What a COI shows</h2>
<p>A standard COI lists the insured business, the insurance company, the policy numbers, the types of coverage (often general liability, auto, workers' compensation and umbrella), the limits, and each policy's effective and expiration dates. It may also name a "certificate holder" and list additional insureds.</p>
<p>A COI is evidence of coverage at the moment it was issued. When the underlying policy renews or changes, the old certificate goes out of date.</p>

<h2>Two sides of COI tracking</h2>
<h3>COIs you provide</h3>
<p>If you are a contractor or vendor, your customers may require an up-to-date COI before you start work and again whenever your policies renew. Missing that update can mean being pulled off a site or having an invoice held.</p>
<h3>COIs you collect</h3>
<p>If you hire subcontractors or vendors, or manage a building, you probably require their COIs. If a vendor's coverage lapses and something goes wrong on your property, you may be the one exposed. Talk to your insurance broker or attorney about exactly what your contracts require.</p>

<h2>A simple COI tracking process</h2>
<ol>
<li><strong>List every party.</strong> One row per vendor or customer, with a contact who can send updated certificates.</li>
<li><strong>Record each policy's expiration date</strong>, not just the date the certificate was issued. One COI can carry several policies with different dates.</li>
<li><strong>Check requirements.</strong> Note the minimum limits and additional-insured wording your contracts require, and compare each certificate against them.</li>
<li><strong>Request renewals early.</strong> Ask for the updated certificate about 30 days before the earliest policy on it expires.</li>
<li><strong>Store the PDF</strong> next to the dates so you can produce it on request.</li>
<li><strong>Follow up on gaps.</strong> If a renewal hasn't arrived by the expiration date, escalate before the vendor's next job.</li>
</ol>

<h2>Common mistakes</h2>
<ul>
<li>Filing the certificate and never checking it again.</li>
<li>Tracking only general liability and missing a workers' compensation or auto policy that expires sooner.</li>
<li>Relying on vendors to send renewals without being asked.</li>
<li>Keeping COIs in one person's inbox.</li>
</ul>

<h2>Spreadsheet or software?</h2>
<p>With a handful of vendors, a carefully maintained spreadsheet can work. Once you are tracking dozens of certificates, each with several policy dates, automated reminders save hours and catch the lapses a spreadsheet misses.</p>
""")

page("certtrack", "california-contractor-license-renewal-checklist",
 "California Contractor License Renewal Checklist",
 "A checklist of what California contractors need to keep current: the two-year CSLB license term, the $25,000 bond, and workers' compensation proof.",
 """
<p class="lead">A California contractor license is only as good as the paperwork behind it. Here is a checklist of what has to stay current, based on the Contractors State License Board's published requirements.</p>

<p class="note">This is a general checklist, not legal advice. Confirm current requirements directly with the <a href="https://www.cslb.ca.gov/" rel="nofollow">CSLB</a>.</p>

<h2>The license itself</h2>
<p>According to the <a href="https://www.cslb.ca.gov/contractors/applicants/contractors_license/exam_application/Issuing_My_License.aspx" rel="nofollow">CSLB</a>, an initial license is issued for two years, running to the last day of the month it was issued. Active licenses then renew for two years at a time; inactive licenses can renew for four years.</p>
<ul class="check">
<li>Know your license's expiration date and put it somewhere more than one person can see.</li>
<li>Start the renewal well before that date so processing time doesn't leave you working on an expired license.</li>
<li>Make sure the business name, address and personnel on file are current.</li>
</ul>

<h2>The contractor's bond</h2>
<p>The CSLB requires a $25,000 contractor's bond (or a cashier's check deposit instead). A separate $25,000 bond of qualifying individual can apply to a Responsible Managing Officer or Employee, with some exemptions.</p>
<ul class="check">
<li>Track the bond's own renewal or continuation date with your surety.</li>
<li>Confirm the bond on file with the CSLB matches your current license.</li>
</ul>

<h2>Workers' compensation</h2>
<p>Contractors must keep proof of workers' compensation coverage on file with the CSLB, or file an exemption if they have no employees. Some classifications, including C-8, C-20, C-22, C-39 and C-61/D-49, cannot claim the exemption.</p>
<ul class="check">
<li>Track your workers' comp policy expiration and make sure the renewed certificate reaches the CSLB.</li>
<li>If you hire your first employee while exempt, get coverage in place first.</li>
</ul>

<h2>Everything else with a date on it</h2>
<ul class="check">
<li>General liability and commercial auto policies, plus the COIs your customers request.</li>
<li>City business licenses for each city you work in.</li>
<li>Job permits and inspections.</li>
<li>Employee certifications, such as safety training and equipment operator cards.</li>
<li>Vehicle registrations and any DOT requirements.</li>
</ul>

<h2>Make it someone's job</h2>
<p>Give each item an owner and get reminders at 90, 30 and 7 days out. The most expensive renewal is the one everyone assumed someone else was handling.</p>
""")

# ---------------------------------------------------------------- Property Alerts
page("property-alerts", "check-311-complaints-by-address",
 "How to Check 311 Complaints and City Activity for a Property Address",
 "Where to look up 311 service requests, code complaints and permit activity near a property in Los Angeles, New York, Chicago, San Francisco and Seattle.",
 """
<p class="lead">Neighbors file 311 requests about dumping, noise, graffiti and building conditions every day. That record is often public. Checking it regularly is one of the cheapest early-warning systems a property owner or manager has.</p>

<h2>What 311 and city data can tell you</h2>
<ul>
<li><strong>Service requests</strong> near your property: illegal dumping, graffiti, streetlights, encampments, abandoned vehicles.</li>
<li><strong>Code and building complaints</strong> that may lead to an inspection.</li>
<li><strong>Permit activity</strong> next door, such as construction that could affect tenants, parking or access.</li>
</ul>
<p>Public data can be delayed, incomplete or miscategorized. Treat it as a signal to look closer, not as an official finding. Always confirm with the city agency involved.</p>

<h2>Where to look in major cities</h2>
<table>
<tr><th>City</th><th>Where to start</th></tr>
<tr><td>Los Angeles</td><td>MyLA311 for service requests; the city open data portal (data.lacity.org) publishes 311 request data; LADBS handles building permits and code complaints, and the Los Angeles Housing Department handles rental housing code enforcement.</td></tr>
<tr><td>New York City</td><td>The NYC311 portal, and the 311 Service Requests dataset on NYC Open Data.</td></tr>
<tr><td>Chicago</td><td>CHI311, and the 311 Service Requests dataset on the Chicago Data Portal.</td></tr>
<tr><td>San Francisco</td><td>SF311, and 311 case data on DataSF.</td></tr>
<tr><td>Seattle</td><td>Find It, Fix It service requests, and the City of Seattle open data portal.</td></tr>
</table>

<h2>How to search by address</h2>
<ol>
<li>Open the city's open data portal and find the 311 or service request dataset.</li>
<li>Filter by street address, or by latitude and longitude within a small radius of your building.</li>
<li>Sort by date, newest first, and look at the last 30 to 90 days.</li>
<li>Note the request type, status and how far it is from your property.</li>
<li>Repeat for the building permit dataset to see construction nearby.</li>
</ol>

<h2>What to do with what you find</h2>
<ul>
<li><strong>Something on your own parcel:</strong> look into it right away, before it becomes a notice or a tenant complaint.</li>
<li><strong>Repeated requests nearby:</strong> a pattern of dumping or graffiti on your block may call for cameras, lighting or a call to the council office.</li>
<li><strong>Permits next door:</strong> give tenants a heads-up about noise or parking.</li>
</ul>

<h2>The problem: nobody checks every morning</h2>
<p>Searching each portal by hand works for one building, once. Across a portfolio, it rarely happens consistently. That is why some owners use a monitoring service that checks these sources for them and sends one ranked summary.</p>
""")

page("property-alerts", "lease-renewal-checklist-landlords",
 "Lease Renewal Checklist for Landlords and Property Managers",
 "Every date inside a lease to track, from renewal options and notice deadlines to rent increases, inspections and insurance expirations.",
 """
<p class="lead">The lease end date is the obvious one. The dates that cause trouble are the ones buried inside the lease: notice windows, renewal options, escalations and insurance requirements.</p>

<h2>Dates to pull out of every lease</h2>
<table>
<tr><th>Date</th><th>Why it matters</th></tr>
<tr><td>Lease expiration</td><td>Plan the renewal or turnover in advance.</td></tr>
<tr><td>Notice deadline</td><td>Many leases and local laws require notice a set number of days before expiration or a rent change.</td></tr>
<tr><td>Renewal or extension option</td><td>Commercial leases often give the tenant a window to exercise an option. Know when it opens and closes.</td></tr>
<tr><td>Rent escalation dates</td><td>Scheduled increases are easy to miss if nobody is tracking them.</td></tr>
<tr><td>Tenant insurance expiration</td><td>If the lease requires renters or liability insurance, the policy can lapse mid-lease.</td></tr>
<tr><td>Inspection dates</td><td>Move-in, periodic and move-out inspections.</td></tr>
<tr><td>Security deposit deadlines</td><td>Local rules often set deadlines for returning or itemizing deposits.</td></tr>
</table>

<h2>90 days before expiration</h2>
<ul class="check">
<li>Decide whether you want to renew, and on what terms.</li>
<li>Check local rent control or just-cause rules that may limit increases or non-renewals.</li>
<li>Review the tenant's payment history and any open maintenance issues.</li>
</ul>

<h2>60 days before</h2>
<ul class="check">
<li>Send the renewal offer or required notice, following the method your lease and local law require.</li>
<li>Request an updated certificate of renters or liability insurance if required.</li>
</ul>

<h2>30 days before</h2>
<ul class="check">
<li>Follow up on unsigned renewals.</li>
<li>If the tenant is leaving, schedule the move-out inspection and start marketing the unit.</li>
</ul>

<h2>At signing</h2>
<ul class="check">
<li>Record every new date from the renewed lease right away.</li>
<li>Store the signed copy where your whole team can find it.</li>
</ul>

<p class="note">Notice periods and rent rules vary by state and city. This checklist is general information, not legal advice; check local requirements or ask a local attorney.</p>

<h2>Stop re-reading leases</h2>
<p>The slow part is reading each lease to find these dates. Tools that extract dates from a lease for you to confirm, then send reminders on a schedule, remove most of that manual work.</p>
""")

page("property-alerts", "tenant-insurance-tracking",
 "How to Track Tenant Insurance Expirations",
 "A simple process for collecting and tracking renters and commercial tenant insurance certificates so coverage doesn't lapse mid-lease.",
 """
<p class="lead">Requiring tenant insurance in the lease is the easy part. Knowing that the policy is still active eight months later is where most landlords lose track.</p>

<h2>Why it lapses</h2>
<p>Tenants buy a policy to get the keys, then let it lapse at renewal, switch carriers, or drop coverage to save money. Unless you ask, you usually won't find out until there is a claim.</p>

<h2>What to collect</h2>
<ul>
<li>The carrier name and policy number.</li>
<li>Policy effective and expiration dates.</li>
<li>Coverage limits, especially liability, compared with what the lease requires.</li>
<li>Whether you are listed as an additional insured or interested party, if the lease requires it. Being listed as an interested party often means the carrier notifies you of cancellation.</li>
<li>A copy of the declarations page or certificate.</li>
</ul>

<h2>A tracking process that holds up</h2>
<ol>
<li><strong>Collect proof at move-in</strong> and record the expiration date the same day.</li>
<li><strong>Request renewal proof 30 days before expiration.</strong> A short, friendly reminder works for most tenants.</li>
<li><strong>Follow up at expiration</strong> if nothing has arrived.</li>
<li><strong>Escalate per the lease</strong> if coverage still isn't shown, following your lease terms and local law.</li>
<li><strong>Repeat every year</strong> for the life of the lease.</li>
</ol>

<h2>Commercial tenants</h2>
<p>Commercial leases often require several policies, such as general liability, property and workers' compensation, each with its own expiration date. Track each policy separately, not just the certificate's issue date.</p>

<h2>Make it automatic</h2>
<p>Across a portfolio, tenant insurance dates add up fast. Pulling them from leases automatically and getting reminders before each one is the difference between a policy you know is active and one you hope is.</p>

<p class="note">This is general information, not legal or insurance advice. Confirm requirements with your attorney or insurance broker.</p>
""")

# ---------------------------------------------------------------- render
CSS = """
:root{--ink:#141821;--muted:#566070;--paper:#f7f5ef;--card:#ffffff;--line:#e3e0d6}
*{box-sizing:border-box}
body{margin:0;background:var(--paper);color:var(--ink);font:17px/1.65 -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,Roboto,sans-serif}
header{background:var(--accent);color:#fff;padding:14px 16px}
header .in{max-width:760px;margin:0 auto;display:flex;justify-content:space-between;align-items:center;gap:12px}
header a{color:#fff;text-decoration:none;font-weight:700}
header .go{background:var(--accent2);color:var(--accent);padding:7px 14px;border-radius:999px;font-size:14px;white-space:nowrap}
main{max-width:760px;margin:0 auto;padding:28px 16px 48px}
h1{font-size:clamp(28px,5vw,40px);line-height:1.15;margin:8px 0 12px}
h2{font-size:23px;margin:34px 0 8px}
h3{font-size:19px;margin:22px 0 6px}
.meta{color:var(--muted);font-size:14px}
.lead{font-size:19px}
a{color:var(--accent)}
table{width:100%;border-collapse:collapse;margin:14px 0;background:var(--card);font-size:15px;display:block;overflow-x:auto}
th,td{text-align:left;padding:10px 12px;border-bottom:1px solid var(--line);vertical-align:top}
th{background:#efece3}
ul.check{list-style:none;padding-left:0}
ul.check li{padding-left:30px;position:relative;margin:6px 0}
ul.check li:before{content:"";position:absolute;left:0;top:6px;width:16px;height:16px;border:2.5px solid var(--accent);border-radius:4px}
.note{background:#fff8e6;border-left:4px solid var(--accent2);padding:10px 14px;font-size:15px}
.cta{margin-top:40px;background:var(--accent);color:#fff;border-radius:16px;padding:24px}
.cta h2{margin-top:0;color:#fff}
.cta a{display:inline-block;margin-top:8px;background:var(--accent2);color:var(--accent);font-weight:700;padding:11px 20px;border-radius:999px;text-decoration:none}
.related{margin-top:32px}
footer{color:var(--muted);font-size:13px;text-align:center;padding:24px 16px}
.grid{display:grid;gap:14px}
.card{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:16px}
.card a{font-weight:700;text-decoration:none}
"""

def write(path, text):
    full = os.path.join(HERE, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    open(full, "w").write(text)

def render(p):
    b = BRANDS[p["brand"]]
    url = f"{BASE}/{p['brand']}/{p['slug']}.html"
    ld = {"@context": "https://schema.org", "@type": "Article", "headline": p["title"],
          "description": p["description"], "dateModified": UPDATED, "datePublished": UPDATED,
          "publisher": {"@type": "Organization", "name": b["name"], "url": b["url"]},
          "mainEntityOfPage": url}
    related = [q for q in PAGES if q["brand"] == p["brand"] and q["slug"] != p["slug"]]
    rel = "".join(f'<li><a href="{q["slug"]}.html">{html.escape(q["title"])}</a></li>' for q in related)
    cta_url = b.get("cta_url", b["url"])
    return f"""<!doctype html>
<html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(p['title'])} | {b['name']}</title>
<meta name="description" content="{html.escape(p['description'])}">
<link rel="canonical" href="{url}">
<meta property="og:type" content="article"><meta property="og:title" content="{html.escape(p['title'])}">
<meta property="og:description" content="{html.escape(p['description'])}"><meta property="og:url" content="{url}">
<script type="application/ld+json">{json.dumps(ld)}</script>
<style>:root{{--accent:{b['accent']};--accent2:{b['accent2']}}}{CSS}</style>
</head><body>
<header><div class="in"><a href="{b['url']}">{b['name']}</a><a class="go" href="{cta_url}">{b['cta_button']}</a></div></header>
<main>
<p class="meta">{b['name']} guides · Updated October 1, 2026</p>
<h1>{html.escape(p['title'])}</h1>
{p['body']}
<section class="cta"><h2>{b['cta_title']}</h2><p>{b['cta_body']}</p><a href="{cta_url}">{b['cta_button']} →</a></section>
<section class="related"><h2>More guides</h2><ul>{rel}</ul></section>
</main>
<footer>© 2026 {b['name']} · <a href="{b['url']}">{b['url'].replace('https://','')}</a></footer>
</body></html>"""

for p in PAGES:
    write(f"{p['brand']}/{p['slug']}.html", render(p))

# hub page
cards = ""
for key, b in BRANDS.items():
    items = "".join(f'<div class="card"><a href="{key}/{q["slug"]}.html">{html.escape(q["title"])}</a><p>{html.escape(q["description"])}</p></div>'
                    for q in PAGES if q["brand"] == key)
    cards += f'<h2><a href="{b["url"]}">{b["name"]}</a></h2><div class="grid">{items}</div>'
write("index.html", f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Compliance and Property Guides</title><meta name="description" content="Free guides on tracking licenses, permits, insurance certificates, lease dates and city activity.">
<link rel="canonical" href="{BASE}/"><style>:root{{--accent:#1f388a;--accent2:#ffb020}}{CSS}</style></head><body>
<main><h1>Free guides</h1><p class="lead">Practical checklists for keeping licenses, insurance and lease dates current.</p>{cards}</main></body></html>""")

urls = [f"{BASE}/"] + [f"{BASE}/{p['brand']}/{p['slug']}.html" for p in PAGES]
write("sitemap.xml", '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' +
      "".join(f"<url><loc>{u}</loc><lastmod>{UPDATED}</lastmod></url>\n" for u in urls) + "</urlset>\n")
write("robots.txt", f"User-agent: *\nAllow: /\nSitemap: {BASE}/sitemap.xml\n")
write(".nojekyll", "")
print(f"built {len(PAGES)} pages")
