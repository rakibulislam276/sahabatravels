#!/usr/bin/env python3
"""
Sahaba Travels — static site builder.

Run from the project root:   python3 _build/build.py

It reads _build/packages.json and:
  1. generates /packages/<slug>.html (one itinerary page per package)
  2. generates /packages/index.html (all packages)
  3. refreshes the shared header, footer and package cards inside index.html
     (between <!-- BUILD:name --> ... <!-- /BUILD:name --> markers)
  4. writes sitemap.xml

No third-party dependencies. The _build folder is ignored by GitHub Pages (Jekyll skips "_" folders).
"""
from __future__ import annotations

import html
import json
import re
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = json.loads((ROOT / "_build" / "packages.json").read_text(encoding="utf-8"))
PACKAGES = DATA["packages"]
BY_SLUG = {p["slug"]: p for p in PACKAGES}

SITE = "https://sahabatravels.com"
TODAY = date.today().isoformat()
BRAND = "Sahaba Travels & Forex"
LEGAL = "Sahaba Travels and Forex Private Limited"
CIN = "U79110MH2025PTC441982"
PHONE1, PHONE1_TEL = "+91 97690 47633", "+919769047633"
PHONE2, PHONE2_TEL = "+91 90820 17919", "+919082017919"
WA = "919769047633"
EMAIL = "info@sahabatravels.com"
DIRECTOR_URL = "https://www.linkedin.com/in/khan-faisal-7564a543"
DEV_URL = "https://www.linkedin.com/in/rakibulislamsalafi"
FACEBOOK = "https://www.facebook.com/p/Sahaba-Travels-and-Forex-Pvt-Ltd-61576299080446/"
INSTAGRAM = "https://www.instagram.com/sahabatravels/"
LINKEDIN = "https://www.linkedin.com/company/sahaba-travels-and-forex/"
LEGAL_PAGES = [("terms-and-conditions.html", "legal.terms", "Terms &amp; Conditions"), ("privacy-policy.html", "legal.privacy", "Privacy Policy"),
               ("cancellation-refund-policy.html", "legal.refund", "Cancellation &amp; Refund Policy"), ("feedback.html", "legal.feedback", "Feedback")]

e = html.escape

# ---------------------------------------------------------------- launch gate
# Until this moment (IST) every page sends visitors to coming-soon.html; after it the site shows normally.
# After launch day set LAUNCH_AT = "" and rebuild to remove the gate completely.
# Preview the real site early: open any page with ?preview  (turn off with ?preview=off).
LAUNCH_AT = "2026-10-16T12:00:00+05:30"


def gate(base: str) -> str:
    if not LAUNCH_AT:
        return ""
    target = f"{base}coming-soon.html"
    return (
        "<script>(function(){var L=Date.parse('" + LAUNCH_AT + "'),q=location.search;"
        "function g(k){try{return localStorage.getItem(k)}catch(e){return null}}"
        "function p(k,v){try{v?localStorage.setItem(k,v):localStorage.removeItem(k)}catch(e){}}"
        "var off=/[?&]preview=off(&|$)/.test(q),pv=!off&&/[?&]preview(=|&|$)/.test(q);"
        "if(off)p('st-preview');if(pv)p('st-preview','1');"
        "if(Date.now()<L&&!pv&&!g('st-preview')&&!g('st-live'))location.replace('" + target + "');})();</script>"
    )

# group -> (label, anchor id on packages page, heading, filter kind)
GROUPS = {
    "umrah": ("Hajj & Umrah", "umrah", "Umrah &amp; Hajj Packages"),
    "family": ("Family Packages", "family", "Family Packages"),
    "honeymoon": ("Honeymoon Packages", "honeymoon", "Honeymoon Packages"),
    "religious": ("Religious Travel", "religious", "Religious Travel Packages"),
}
KIND = {"umrah": "pilgrimage", "family": "family", "honeymoon": "honeymoon", "religious": "religious"}
FEATURED = [p for p in PACKAGES if p.get("featured")]


def img(pid: str, w: int = 800, h: int | None = None, q: int = 75) -> str:
    crop = f"&h={h}" if h else ""
    return f"https://images.unsplash.com/{pid}?auto=format&fit=crop&w={w}{crop}&q={q}"


def srcset(pid: str, widths=(480, 800, 1200), ratio: float | None = None) -> str:
    out = []
    for w in widths:
        h = int(w * ratio) if ratio else None
        out.append(f"{img(pid, w, h)} {w}w")
    return ", ".join(out)


def inr(n: int) -> str:
    s = str(n)
    if len(s) <= 3:
        return "₹" + s
    head, tail = s[:-3], s[-3:]
    head = re.sub(r"(\d)(?=(\d\d)+$)", r"\1,", head)
    return f"₹{head},{tail}"


def duration(p) -> str:
    return f"{p['nights']} Nights / {p['days']} Days"


def wa_link(text: str) -> str:
    from urllib.parse import quote
    return f"https://wa.me/{WA}?text={quote(text)}"


# ---------------------------------------------------------------- header / footer
NAV = [
    ("home", "nav.home", "Home", "#home"),
    ("about", "nav.about", "About Us", "#about"),
    ("services", "nav.services", "Services", "#services"),
    ("visa", "nav.visa", "Visa", "visa.html"),
    ("packages", "nav.packages", "Packages", "#packages"),
    ("hajj-umrah", "nav.hajj", "Hajj & Umrah", "#hajj-umrah"),
    ("forex", "nav.forex", "Forex", "#forex"),
    ("contact", "nav.contact", "Contact Us", "#contact"),
]

LANGS = [("en", "English", "EN"), ("hi", "हिन्दी", "HI"), ("gu", "ગુજરાતી", "GU"), ("mr", "मराठी", "MR"), ("ur", "اردو", "UR")]


def header(base: str, active: str = "home") -> str:
    home = base or "./"
    links = []
    mlinks = []
    for key, i18n, label, frag in NAV:
        href = (base + frag) if base else frag
        if key == "packages" and base:
            href = base + "packages/"
        cur = ' aria-current="page"' if key == active else ""
        cls = ' class="active"' if key == active else ""
        links.append(f'<li><a href="{href}"{cls}{cur} data-i18n="{i18n}">{label}</a></li>')
        mlinks.append(f'<li><a href="{href}" class="mobile-link" data-i18n="{i18n}">{label}</a></li>')
    lang_items = "\n".join(
        f'            <li><button type="button" role="menuitemradio" aria-checked="{"true" if c == "en" else "false"}" data-lang="{c}" lang="{c}"><span class="lang-code">{s}</span> {n}</button></li>'
        for c, n, s in LANGS
    )
    return f'''<a class="skip-link" href="#main" data-i18n="a11y.skip">Skip to main content</a>

<div class="topbar">
  <div class="container topbar-inner">
    <ul class="topbar-links">
      <li><a href="tel:{PHONE1_TEL}"><i class="fas fa-phone" aria-hidden="true"></i> {PHONE1}</a></li>
      <li class="hide-sm"><a href="tel:{PHONE2_TEL}"><i class="fas fa-phone" aria-hidden="true"></i> {PHONE2}</a></li>
      <li class="hide-md"><a href="mailto:{EMAIL}"><i class="fas fa-envelope" aria-hidden="true"></i> {EMAIL}</a></li>
    </ul>
    <p class="topbar-hours hide-md"><i class="fas fa-clock" aria-hidden="true"></i> <span data-i18n="top.hours">Mon–Fri 10 AM–9 PM · Sat 10 AM–6 PM · Sun Closed</span></p>
  </div>
</div>

<header class="navbar" id="navbar">
  <div class="container navbar-inner">
    <a href="{home}" class="logo" aria-label="{BRAND} — home">
      <span class="logo-mark"><img src="{base}assets/img/emblem.webp" width="48" height="48" alt="" decoding="async"></span>
      <span class="logo-text">
        <span class="logo-name">Sahaba Travels</span>
        <span class="logo-sub">Travel &amp; Forex Services</span>
      </span>
    </a>

    <nav class="nav-links" aria-label="Primary">
      <ul>
        {"".join(links)}
      </ul>
    </nav>

    <div class="nav-tools">
      <div class="lang-switch">
        <button type="button" class="icon-btn" id="langBtn" aria-haspopup="menu" aria-expanded="false" aria-controls="langMenu" aria-label="Change language" data-i18n-attr="aria-label:a11y.lang">
          <i class="fas fa-language" aria-hidden="true"></i><span class="lang-current" id="langCurrent">EN</span>
        </button>
        <ul class="lang-menu" id="langMenu" role="menu" hidden>
{lang_items}
        </ul>
      </div>
      <button type="button" class="icon-btn" id="themeBtn" aria-label="Switch to dark theme" data-i18n-attr="aria-label:a11y.theme">
        <i class="fas fa-moon theme-icon-dark" aria-hidden="true"></i><i class="fas fa-sun theme-icon-light" aria-hidden="true"></i>
      </button>
      <a href="tel:{PHONE1_TEL}" class="btn btn-primary nav-call"><i class="fas fa-phone" aria-hidden="true"></i><span data-i18n="cta.call">Call Now</span></a>
      <button type="button" class="hamburger" id="hamburger" aria-label="Open menu" aria-expanded="false" aria-controls="mobileMenu">
        <span></span><span></span><span></span>
      </button>
    </div>
  </div>
</header>

<div class="mobile-menu" id="mobileMenu" aria-hidden="true">
  <div class="mobile-menu-head">
    <span class="logo-name">Sahaba Travels</span>
    <button type="button" class="mobile-close" id="mobileClose" aria-label="Close menu"><i class="fas fa-xmark" aria-hidden="true"></i></button>
  </div>
  <nav aria-label="Mobile">
    <ul>
      {"".join(mlinks)}
    </ul>
  </nav>
  <div class="mobile-contact">
    <a href="tel:{PHONE1_TEL}"><i class="fas fa-phone" aria-hidden="true"></i> {PHONE1}</a>
    <a href="tel:{PHONE2_TEL}"><i class="fas fa-phone" aria-hidden="true"></i> {PHONE2}</a>
    <a href="mailto:{EMAIL}"><i class="fas fa-envelope" aria-hidden="true"></i> {EMAIL}</a>
  </div>
</div>'''


def footer(base: str) -> str:
    def h(frag):
        return (base + frag) if base else frag
    legal_links = "".join(f' <span class="sep" aria-hidden="true">|</span> <a href="{base}{href}" data-i18n="{key}">{label}</a>' for href, key, label in LEGAL_PAGES)
    pkg_links = "\n".join(
        f'          <li><a href="{base}packages/{p["slug"]}.html">{e(p["title"])}</a></li>' for p in FEATURED[:7]
    )
    return f'''<footer class="site-footer">
  <div class="container">
    <div class="footer-grid">
      <div class="footer-brand">
        <a href="{base or './'}" class="logo logo-footer" aria-label="{BRAND} — home">
          <span class="logo-mark"><img src="{base}assets/img/emblem.webp" width="48" height="48" alt="" loading="lazy" decoding="async"></span>
          <span class="logo-text"><span class="logo-name">Sahaba Travels</span><span class="logo-sub">Travel &amp; Forex Services</span></span>
        </a>
        <p class="footer-desc" data-i18n="footer.desc">Mumbai’s trusted travel partner for Hajj &amp; Umrah, international and domestic holiday packages, and foreign exchange. Travel with trust · Exchange with confidence.</p>
        <p class="footer-legal"><strong>{LEGAL}</strong><br>CIN: {CIN}</p>
        <div class="footer-social">
          <a href="{FACEBOOK}" target="_blank" rel="noopener" aria-label="Facebook"><i class="fab fa-facebook-f" aria-hidden="true"></i></a>
          <a href="{INSTAGRAM}" target="_blank" rel="noopener" aria-label="Instagram"><i class="fab fa-instagram" aria-hidden="true"></i></a>
          <a href="{LINKEDIN}" target="_blank" rel="noopener" aria-label="LinkedIn"><i class="fab fa-linkedin-in" aria-hidden="true"></i></a>
          <a href="https://wa.me/{WA}" target="_blank" rel="noopener" aria-label="WhatsApp"><i class="fab fa-whatsapp" aria-hidden="true"></i></a>
          <a href="mailto:{EMAIL}" aria-label="Email"><i class="fas fa-envelope" aria-hidden="true"></i></a>
          <a href="tel:{PHONE1_TEL}" aria-label="Call"><i class="fas fa-phone" aria-hidden="true"></i></a>
        </div>
      </div>
      <nav class="footer-col" aria-label="Quick links">
        <h2 data-i18n="footer.quick">Quick Links</h2>
        <ul>
          <li><a href="{h('#home')}" data-i18n="nav.home">Home</a></li>
          <li><a href="{h('#about')}" data-i18n="nav.about">About Us</a></li>
          <li><a href="{h('#services')}" data-i18n="nav.services">Services</a></li>
          <li><a href="{base}visa.html" data-i18n="nav.visa">Visa</a></li>
          <li><a href="{base}packages/" data-i18n="nav.packages">Packages</a></li>
          <li><a href="{h('#hajj-umrah')}" data-i18n="nav.hajj">Hajj &amp; Umrah</a></li>
          <li><a href="{h('#forex')}" data-i18n="nav.forex">Forex</a></li>
          <li><a href="{h('#faq')}" data-i18n="nav.faq">FAQs</a></li>
          <li><a href="{h('#contact')}" data-i18n="nav.contact">Contact Us</a></li>
        </ul>
      </nav>
      <nav class="footer-col" aria-label="Popular packages">
        <h2 data-i18n="footer.popular">Popular Packages</h2>
        <ul>
{pkg_links}
        </ul>
      </nav>
      <div class="footer-col">
        <h2 data-i18n="footer.contact">Contact Info</h2>
        <address>
          <p class="footer-contact-item"><i class="fas fa-location-dot" aria-hidden="true"></i><span>Shop No. 2, Arsiwala Building, Dimtimkar Road, Nagpada, Mumbai – 400008</span></p>
          <p class="footer-contact-item"><i class="fas fa-phone" aria-hidden="true"></i><span><a href="tel:{PHONE1_TEL}">{PHONE1}</a><br><a href="tel:{PHONE2_TEL}">{PHONE2}</a></span></p>
          <p class="footer-contact-item"><i class="fas fa-envelope" aria-hidden="true"></i><span><a href="mailto:{EMAIL}">{EMAIL}</a></span></p>
          <p class="footer-contact-item"><i class="fas fa-clock" aria-hidden="true"></i><span data-i18n-html="footer.hours">Mon–Fri: 10 AM – 9 PM<br>Sat: 10 AM – 6 PM · Sun: Closed</span></p>
        </address>
      </div>
    </div>
    <div class="footer-bottom">
      <p class="footer-copy">© <span data-year>2026</span> {LEGAL}. <span data-i18n="footer.rights">All rights reserved.</span>{legal_links}</p>
      <p>Designed and Developed by <a href="{DEV_URL}" target="_blank" rel="noopener">Rakibul Islam Salafi</a></p>
    </div>
  </div>
</footer>

<div class="float-stack">
  <a href="https://wa.me/{WA}?text=Hello%20Sahaba%20Travels!%20I%E2%80%99d%20like%20to%20enquire%20about%20your%20services." class="float-btn float-wa" target="_blank" rel="noopener" aria-label="Chat with us on WhatsApp">
    <span class="float-label" data-i18n="fab.wa">Chat on WhatsApp</span><i class="fab fa-whatsapp" aria-hidden="true"></i>
  </a>
  <a href="tel:{PHONE1_TEL}" class="float-btn float-call" aria-label="Call {PHONE1}">
    <span class="float-label"><span data-i18n="fab.call">Call us</span> · {PHONE1}</span><i class="fas fa-phone-volume" aria-hidden="true"></i>
  </a>
</div>
<button type="button" class="back-to-top" id="backToTop" aria-label="Back to top"><i class="fas fa-arrow-up" aria-hidden="true"></i></button>
<div class="toast" id="toast" role="status" aria-live="polite"></div>

<dialog class="flyer" id="flyer" aria-labelledby="flyer-title">
  <button type="button" class="flyer-close" data-close-flyer aria-label="Close"><i class="fas fa-xmark" aria-hidden="true"></i></button>
  <div class="flyer-media">
    <img src="https://images.unsplash.com/photo-1693590614566-1d3ea9ef32f7?auto=format&amp;fit=crop&amp;w=640&amp;h=820&amp;q=70" width="640" height="820" alt="The Kaaba in Masjid al-Haram" loading="lazy" decoding="async">
    <span class="flyer-stamp"><strong data-i18n="fly.stamp1">Hajj 2027</strong><small data-i18n="fly.stamp2">Registrations open</small></span>
  </div>
  <div class="flyer-body">
    <img class="flyer-logo" src="{base}assets/img/logo.webp" width="120" height="91" alt="Sahaba Travels &amp; Forex" loading="lazy">
    <p class="flyer-tag" data-i18n="fly.tag">Welcome to Sahaba Travels</p>
    <h2 id="flyer-title" data-i18n-html="fly.h">Your next journey <span>starts here</span></h2>
    <ul class="flyer-offers">
      <li><i class="fas fa-kaaba" aria-hidden="true"></i><span><strong data-i18n="fly.o1">Umrah packages</strong> <em data-i18n="fly.o1d">from ₹75,000 · 15 days</em></span></li>
      <li><i class="fas fa-moon" aria-hidden="true"></i><span><strong data-i18n="fly.o2">Hajj 2027</strong> <em data-i18n="fly.o2d">21, 35 &amp; 40-day packages</em></span></li>
      <li><i class="fas fa-umbrella-beach" aria-hidden="true"></i><span><strong data-i18n="fly.o3">Holidays</strong> <em data-i18n="fly.o3d">from ₹10,490 · Kashmir, Dubai, Bali &amp; more</em></span></li>
      <li><i class="fas fa-money-bill-transfer" aria-hidden="true"></i><span><strong data-i18n="fly.o4">Forex</strong> <em data-i18n="fly.o4d">live rates &amp; doorstep delivery</em></span></li>
    </ul>
    <div class="flyer-actions">
      <a href="https://wa.me/{WA}?text=Hello%20Sahaba%20Travels%2C%20I%20saw%20your%20offers%20on%20the%20website.%20Please%20share%20details." class="btn btn-wa" target="_blank" rel="noopener" data-close-flyer><i class="fab fa-whatsapp" aria-hidden="true"></i><span data-i18n="fly.wa">WhatsApp us</span></a>
      <a href="{base}packages/" class="btn btn-primary" data-close-flyer><span data-i18n="fly.view">View packages</span><i class="fas fa-arrow-right" aria-hidden="true"></i></a>
    </div>
    <p class="flyer-contact"><i class="fas fa-phone" aria-hidden="true"></i> <a href="tel:{PHONE1_TEL}">{PHONE1}</a> · <a href="tel:{PHONE2_TEL}">{PHONE2}</a></p>
  </div>
</dialog>'''


# ---------------------------------------------------------------- cards
def card(p, base: str, delay: int = 0, heading: str = "h3") -> str:
    url = f"{base}packages/{p['slug']}.html"
    badge = f'<span class="package-badge" data-i18n="pkg.popular">{e(p["badge"])}</span>' if p.get("badge") else ""
    kind = KIND[p["group"]]
    featured = " featured" if p.get("badge") else ""
    style = f' style="--delay:{delay * 0.08:.2f}s"' if delay else ""
    return f'''<article class="package-card reveal{featured}" data-kind="{kind}"{style}>
  {badge}
  <a class="package-img" href="{url}" tabindex="-1" aria-hidden="true">
    <img src="{img(p['image'], 640, 420)}" srcset="{srcset(p['image'], (400, 640, 960), 0.656)}" sizes="(max-width: 640px) 100vw, (max-width: 1024px) 50vw, 33vw" width="640" height="420" alt="{e(p['imageAlt'])}" loading="lazy" decoding="async">
    <span class="package-price"><span class="amount">{inr(p['price'])}</span><small data-i18n="pkg.pp">per person</small></span>
  </a>
  <div class="package-body">
    <p class="package-category">{e(p['category'])}</p>
    <{heading} class="package-title"><a href="{url}">{e(p['title'])}</a></{heading}>
    <ul class="package-meta">
      <li><i class="fas fa-clock" aria-hidden="true"></i> {duration(p)}</li>
      <li><i class="fas fa-users" aria-hidden="true"></i> {e(p['pax'])}</li>
      <li><i class="fas fa-location-dot" aria-hidden="true"></i> {e(p.get("duration_note") or " – ".join(p['cities'][:4]))}</li>
    </ul>
    <p class="package-desc">{e(p['summary'])}</p>
    <div class="package-actions">
      <a href="{base}#contact" class="btn btn-primary btn-sm" data-plan="{e(p['title'])}"><i class="fas fa-paper-plane" aria-hidden="true"></i><span data-i18n="pkg.plan">Plan Your Trip</span></a>
      <a href="{url}" class="btn btn-outline btn-sm"><i class="fas fa-route" aria-hidden="true"></i><span data-i18n="pkg.view">View Itinerary</span></a>
    </div>
  </div>
</article>'''


# ---------------------------------------------------------------- package page
def jsonld(obj) -> str:
    return '<script type="application/ld+json">' + json.dumps(obj, ensure_ascii=False, separators=(",", ":")) + "</script>"


def head(title, desc, canonical, base, og_image, extra_ld: list, lang="en") -> str:
    return f'''<!DOCTYPE html>
<html lang="{lang}" dir="ltr">
<head>
  <meta charset="UTF-8">
  {gate(base)}
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
  <title>{e(title)}</title>
  <meta name="description" content="{e(desc)}">
  <meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1">
  <link rel="canonical" href="{canonical}">
  <meta name="author" content="{LEGAL}">
  <meta name="geo.region" content="IN-MH">
  <meta name="geo.placename" content="Nagpada, Mumbai">
  <meta name="geo.position" content="18.9686;72.8283">
  <meta name="ICBM" content="18.9686, 72.8283">
  <meta name="theme-color" content="#13235b">
  <meta property="og:type" content="website">
  <meta property="og:site_name" content="{BRAND}">
  <meta property="og:locale" content="en_IN">
  <meta property="og:title" content="{e(title)}">
  <meta property="og:description" content="{e(desc)}">
  <meta property="og:url" content="{canonical}">
  <meta property="og:image" content="{og_image}">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{e(title)}">
  <meta name="twitter:description" content="{e(desc)}">
  <meta name="twitter:image" content="{og_image}">
  <link rel="icon" href="{base}favicon.ico" sizes="any">
  <link rel="icon" type="image/png" sizes="32x32" href="{base}assets/img/icon-32.png">
  <link rel="apple-touch-icon" href="{base}assets/img/apple-touch-icon.png">
  <link rel="manifest" href="{base}site.webmanifest">
  <script>try{{var t=localStorage.getItem('st-theme');document.documentElement.dataset.theme=t||(matchMedia('(prefers-color-scheme: dark)').matches?'dark':'light');}}catch(_){{}}</script>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link rel="preconnect" href="https://images.unsplash.com">
  <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,500;0,600;0,700;1,500&amp;family=DM+Sans:opsz,wght@9..40,400;9..40,500;9..40,600;9..40,700&amp;family=Poppins:wght@500;700&amp;display=swap">
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css" crossorigin="anonymous" referrerpolicy="no-referrer">
  <link rel="stylesheet" href="{base}css/style.css">
  {"".join(jsonld(x) for x in extra_ld)}
</head>'''


ICON_FALLBACK = {"shopping-bag": "bag-shopping"}


def package_page(p) -> str:
    base = "../"
    url = f"{SITE}/packages/{p['slug']}.html"
    title = f"{p['title']} – {duration(p)} Itinerary & Price | {BRAND}"
    desc = f"{p['title']}: {duration(p)} covering {', '.join(p['cities'])}. Day-wise itinerary, inclusions, hotels and price from {inr(p['price'])} {p['priceNote']}. Book with Sahaba Travels, Nagpada, Mumbai."
    group_label = GROUPS[p["group"]][0]
    group_href = f"./#{GROUPS[p['group']][1]}"

    ld_trip = {
        "@context": "https://schema.org",
        "@type": "TouristTrip",
        "name": p["title"],
        "description": p["overview"],
        "url": url,
        "image": [img(p["image"], 1200)] + [img(g[0], 1200) for g in p["gallery"]],
        "touristType": "Pilgrims" if p["group"] == "umrah" else "Leisure travellers",
        "itinerary": {
            "@type": "ItemList",
            "numberOfItems": len(p["itinerary"]),
            "itemListElement": [
                {"@type": "ListItem", "position": i + 1, "item": {"@type": "TouristAttraction", "name": d["title"], "description": d["text"]}}
                for i, d in enumerate(p["itinerary"])
            ],
        },
        "offers": {
            "@type": "Offer",
            "price": p["price"],
            "priceCurrency": "INR",
            "availability": "https://schema.org/InStock",
            "url": url,
            "description": p["priceNote"],
        },
        "provider": {"@id": f"{SITE}/#organization"},
    }
    ld_bc = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{SITE}/"},
            {"@type": "ListItem", "position": 2, "name": "Packages", "item": f"{SITE}/packages/"},
            {"@type": "ListItem", "position": 3, "name": p["title"], "item": url},
        ],
    }
    ld_faq = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in p["faqs"]],
    }
    ld_org = {"@context": "https://schema.org", "@type": "TravelAgency", "@id": f"{SITE}/#organization", "name": BRAND, "legalName": LEGAL, "url": f"{SITE}/", "telephone": PHONE1_TEL, "email": EMAIL,
              "address": {"@type": "PostalAddress", "streetAddress": "Shop No. 2, Arsiwala Building, Dimtimkar Road, Nagpada", "addressLocality": "Mumbai", "addressRegion": "Maharashtra", "postalCode": "400008", "addressCountry": "IN"}}

    gallery = "\n".join(
        f'<button type="button" class="gallery-item" data-full="{img(g[0], 1600)}" data-alt="{e(g[1])}" aria-label="Enlarge photo: {e(g[1])}"><img src="{img(g[0], 600, 420)}" srcset="{srcset(g[0], (400, 600, 900), 0.7)}" sizes="(max-width: 640px) 50vw, 25vw" width="600" height="420" alt="{e(g[1])}" loading="lazy" decoding="async"></button>'
        for g in p["gallery"]
    )
    route = '<i class="fas fa-arrow-right-long" aria-hidden="true"></i>'.join(f"<span>{e(c)}</span>" for c in p["cities"])
    highlights = "\n".join(f'<li><i class="fas fa-circle-check" aria-hidden="true"></i>{e(h)}</li>' for h in p["highlights"])

    days = []
    n = 0
    for i, d in enumerate(p["itinerary"]):
        m = re.match(r"^Days? ([\d–-]+) · (.*)$", d["title"])
        if m:
            label, ttl = m.group(1), m.group(2)
        else:
            n_label = i + 1
            label, ttl = str(n_label), d["title"]
        items = "".join(
            f'<li><i class="fas fa-{ICON_FALLBACK.get(ic, ic)}" aria-hidden="true"></i>{e(t)}</li>' for ic, t in d["items"]
        )
        tags = []
        if d.get("meals"):
            tags.append(f'<span class="tag"><i class="fas fa-utensils" aria-hidden="true"></i> <span data-i18n="it.meals">Meals</span>: {e(d["meals"])}</span>')
        if d.get("stay"):
            tags.append(f'<span class="tag"><i class="fas fa-bed" aria-hidden="true"></i> <span data-i18n="it.stay">Overnight</span>: {e(d["stay"])}</span>')
        days.append(f'''<li class="day">
  <details{" open" if i == 0 else ""}>
    <summary>
      <span class="day-badge"><small data-i18n="it.day">Day</small> {e(label)}</span>
      <span class="day-title">{e(ttl)}</span>
      <i class="fas fa-chevron-down day-chevron" aria-hidden="true"></i>
    </summary>
    <div class="day-body">
      <p>{e(d["text"])}</p>
      <ul class="day-items">{items}</ul>
      <div class="day-tags">{"".join(tags)}</div>
    </div>
  </details>
</li>''')
    days_html = "\n".join(days)

    inc = "\n".join(f'<li><i class="fas fa-check" aria-hidden="true"></i>{e(x)}</li>' for x in p["inclusions"])
    exc = "\n".join(f'<li><i class="fas fa-xmark" aria-hidden="true"></i>{e(x)}</li>' for x in p["exclusions"])
    hotels = "\n".join(f"<tr><th scope=\"row\">{e(c)}</th><td>{e(hh)}</td></tr>" for c, hh in p["hotels"])
    faqs = "\n".join(
        f'<details class="faq-item" name="faq-pkg"><summary>{e(q)}<i class="fas fa-plus" aria-hidden="true"></i></summary><p>{e(a)}</p></details>' for q, a in p["faqs"]
    )
    related = [x for x in PACKAGES if x["slug"] != p["slug"] and x["group"] == p["group"]][:3]
    if len(related) < 3:
        related += [x for x in PACKAGES if x["slug"] != p["slug"] and x not in related][: 3 - len(related)]
    related_html = "\n".join(card(r, base, i) for i, r in enumerate(related))

    share_text = f"{p['title']} – {duration(p)} from {inr(p['price'])} | Sahaba Travels"
    from urllib.parse import quote
    q_url, q_text = quote(url, safe=""), quote(share_text, safe="")
    enquiry_msg = f"Hello Sahaba Travels, I'm interested in the {p['title']} ({duration(p)}). Please share availability and price."

    return f'''{head(title, desc, url, base, img(p["image"], 1200, 630), [ld_org, ld_trip, ld_bc, ld_faq])}
<body class="page-package">
<!-- BUILD:header -->
{header(base, "packages")}
<!-- /BUILD:header -->

<main id="main">
  <section class="pkg-hero">
    <picture class="pkg-hero-bg">
      <img src="{img(p['image'], 1600, 900)}" srcset="{srcset(p['image'], (800, 1200, 1600, 2000), 0.5625)}" sizes="100vw" width="1600" height="900" alt="{e(p['imageAlt'])}" fetchpriority="high" decoding="async">
    </picture>
    <div class="container pkg-hero-inner">
      <nav class="breadcrumb" aria-label="Breadcrumb">
        <ol>
          <li><a href="../" data-i18n="nav.home">Home</a></li>
          <li><a href="{group_href}">{group_label}</a></li>
          <li aria-current="page">{e(p['title'])}</li>
        </ol>
      </nav>
      <p class="pkg-category">{e(p['category'])}</p>
      <h1>{e(p['title'])}</h1>
      <ul class="pkg-pills">
        <li><i class="fas fa-clock" aria-hidden="true"></i> {duration(p)}</li>
        <li><i class="fas fa-location-dot" aria-hidden="true"></i> {e(", ".join(p['cities']))}</li>
        <li><i class="fas fa-users" aria-hidden="true"></i> {e(p['pax'])}</li>
        <li><i class="fas fa-calendar" aria-hidden="true"></i> {e(p['bestTime'])}</li>
      </ul>
    </div>
  </section>

  <nav class="pkg-tabs" aria-label="Package sections">
    <div class="container">
      <ul>
        <li><a href="#overview" data-i18n="it.overview">Overview</a></li>
        <li><a href="#itinerary" data-i18n="it.itinerary">Itinerary</a></li>
        <li><a href="#inclusions" data-i18n="it.inclusions">Inclusions</a></li>
        <li><a href="#hotels" data-i18n="it.hotels">Hotels</a></li>
        <li><a href="#faqs" data-i18n="it.faqs">FAQs</a></li>
      </ul>
    </div>
  </nav>

  <div class="container pkg-layout">
    <div class="pkg-main">
      <section id="overview" class="pkg-section">
        <h2 data-i18n="it.overview">Overview</h2>
        <p class="lead">{e(p['overview'])}</p>
        <div class="pkg-route" aria-label="Route">{route}</div>
        <h3 data-i18n="it.highlights">Tour Highlights</h3>
        <ul class="check-list">{highlights}</ul>
        <div class="pkg-gallery">{gallery}</div>
      </section>

      <section id="itinerary" class="pkg-section">
        <div class="section-head-row">
          <h2 data-i18n="it.dayWise">Day-wise Itinerary</h2>
          <button type="button" class="btn-link" id="toggleDays" data-i18n="it.expand">Expand all</button>
        </div>
        <ol class="timeline">
{days_html}
        </ol>

        <div class="share-bar" aria-label="Share this itinerary">
          <p class="share-title" data-i18n="it.share">Share this itinerary</p>
          <div class="share-buttons">
            <a class="share-btn share-wa" href="https://wa.me/?text={q_text}%20{q_url}" target="_blank" rel="noopener"><i class="fab fa-whatsapp" aria-hidden="true"></i><span>WhatsApp</span></a>
            <a class="share-btn share-mail" href="mailto:?subject={q_text}&amp;body={quote('Have a look at this itinerary: ', safe='')}{q_url}"><i class="fas fa-envelope" aria-hidden="true"></i><span data-i18n="it.email">Email</span></a>
            <button type="button" class="share-btn share-pdf" data-action="print"><i class="fas fa-file-pdf" aria-hidden="true"></i><span data-i18n="it.pdf">View PDF</span></button>
            <button type="button" class="share-btn share-copy" data-action="copy" data-url="{url}"><i class="fas fa-link" aria-hidden="true"></i><span data-i18n="it.copy">Copy Link</span></button>
            <a class="share-btn share-fb" href="https://www.facebook.com/sharer/sharer.php?u={q_url}" target="_blank" rel="noopener"><i class="fab fa-facebook-f" aria-hidden="true"></i><span>Facebook</span></a>
            <a class="share-btn share-x" href="https://twitter.com/intent/tweet?text={q_text}&amp;url={q_url}" target="_blank" rel="noopener"><i class="fab fa-x-twitter" aria-hidden="true"></i><span>X</span></a>
            <a class="share-btn share-tg" href="https://t.me/share/url?url={q_url}&amp;text={q_text}" target="_blank" rel="noopener"><i class="fab fa-telegram" aria-hidden="true"></i><span>Telegram</span></a>
            <button type="button" class="share-btn share-native" data-action="share" data-title="{e(share_text)}" data-url="{url}" hidden><i class="fas fa-share-nodes" aria-hidden="true"></i><span data-i18n="it.more">More</span></button>
          </div>
        </div>
      </section>

      <section id="inclusions" class="pkg-section">
        <h2 data-i18n="it.incExc">Inclusions &amp; Exclusions</h2>
        <div class="inc-grid">
          <div class="inc-box inc-yes"><h3 data-i18n="it.inclusions">Inclusions</h3><ul>{inc}</ul></div>
          <div class="inc-box inc-no"><h3 data-i18n="it.exclusions">Exclusions</h3><ul>{exc}</ul></div>
        </div>
      </section>

      <section id="hotels" class="pkg-section">
        <h2 data-i18n="it.hotelsTitle">Hotels (or similar)</h2>
        <div class="table-wrap"><table class="hotel-table"><thead><tr><th scope="col" data-i18n="it.city">City</th><th scope="col" data-i18n="it.hotel">Hotel / Category</th></tr></thead><tbody>{hotels}</tbody></table></div>
        <div class="note-box">
          <h3 data-i18n="it.notes">Good to know</h3>
          <ul>
            <li>Prices are per person and subject to availability at the time of booking; they can change with airfare, hotel rates, taxes and exchange rates.</li>
            <li>Hotels named are indicative; a hotel of the same category may be provided.</li>
            <li>The order of sightseeing may change due to weather, local conditions or timings.</li>
            <li>A valid passport (minimum 6 months’ validity) is required for international travel.</li>
          </ul>
        </div>
      </section>

      <section id="faqs" class="pkg-section">
        <h2 data-i18n="it.faqs">FAQs</h2>
        <div class="faq-list">{faqs}</div>
      </section>
    </div>

    <aside class="pkg-aside" aria-label="Book this package">
      <div class="price-card">
        <p class="price-from" data-i18n="it.from">Starting from</p>
        <p class="price-amount">{inr(p['price'])}</p>
        <p class="price-note">{e(p['priceNote'])}</p>
        <ul class="price-facts">
          <li><i class="fas fa-clock" aria-hidden="true"></i> {duration(p)}</li>
          <li><i class="fas fa-globe" aria-hidden="true"></i> {e(p['country'])}</li>
        </ul>
        <div class="price-actions">
          <a href="#enquire" class="btn btn-primary" data-plan="{e(p['title'])}"><i class="fas fa-paper-plane" aria-hidden="true"></i><span data-i18n="pkg.plan">Plan Your Trip</span></a>
          <a href="{wa_link(enquiry_msg)}" class="btn btn-wa" target="_blank" rel="noopener"><i class="fab fa-whatsapp" aria-hidden="true"></i><span>WhatsApp</span></a>
          <a href="tel:{PHONE1_TEL}" class="btn btn-outline"><i class="fas fa-phone" aria-hidden="true"></i><span>{PHONE1}</span></a>
        </div>
      </div>

      <form class="enquiry-form" id="enquire" data-form="enquiry" novalidate>
        <h2 data-i18n="it.enquire">Quick Enquiry</h2>
        <input type="hidden" name="package" value="{e(p['title'])}">
        <input type="text" name="_gotcha" class="hp" tabindex="-1" autocomplete="off" aria-hidden="true">
        <div class="field"><label for="eq-name" data-i18n="form.name">Full Name</label><input id="eq-name" name="name" type="text" autocomplete="name" required></div>
        <div class="field"><label for="eq-phone" data-i18n="form.phone">Phone / WhatsApp</label><input id="eq-phone" name="phone" type="tel" autocomplete="tel" inputmode="tel" pattern="[0-9+()\\s-]{{8,}}" required></div>
        <div class="field"><label for="eq-date" data-i18n="form.date">Travel Month</label><input id="eq-date" name="travel_date" type="month"></div>
        <div class="field"><label for="eq-pax" data-i18n="form.pax">Travellers</label><input id="eq-pax" name="travellers" type="number" min="1" max="99" value="2"></div>
        <button type="submit" class="btn btn-primary btn-block"><i class="fas fa-paper-plane" aria-hidden="true"></i><span data-i18n="form.send">Send Enquiry</span></button>
        <p class="form-status" role="status" aria-live="polite"></p>
      </form>
    </aside>
  </div>

  <section class="related">
    <div class="container">
      <h2 class="section-title" data-i18n-html="it.related">You may also <span>like</span></h2>
      <div class="packages-grid">
{related_html}
      </div>
    </div>
  </section>

  <dialog class="lightbox" id="lightbox" aria-label="Photo viewer">
    <button type="button" class="lightbox-close" aria-label="Close"><i class="fas fa-xmark" aria-hidden="true"></i></button>
    <img src="" alt="" width="1600" height="1067">
  </dialog>

  <div class="print-footer" aria-hidden="true">
    <img src="../assets/img/logo.webp" width="160" height="122" alt="">
    <p><strong>{LEGAL}</strong> · CIN {CIN}<br>Shop No. 2, Arsiwala Building, Dimtimkar Road, Nagpada, Mumbai – 400008<br>{PHONE1} · {PHONE2} · {EMAIL} · sahabatravels.com</p>
  </div>
</main>

<!-- BUILD:footer -->
{footer(base)}
<!-- /BUILD:footer -->
<script src="../js/i18n.js" defer></script>
<script src="../js/main.js" defer></script>
</body>
</html>
'''


def packages_index() -> str:
    base = "../"
    url = f"{SITE}/packages/"
    title = f"Tour Packages from Mumbai – Holidays, Umrah & Hajj | {BRAND}"
    desc = f"All {len(PACKAGES)} Sahaba Travels packages from Mumbai — Umrah & Hajj, family holidays, honeymoon trips and religious tours (Kashmir, Kerala, Dubai, Turkey, Thailand, Bali, Vietnam, Char Dham and more) with day-wise itineraries."
    ld_list = {
        "@context": "https://schema.org",
        "@type": "ItemList",
        "name": "Sahaba Travels packages",
        "itemListElement": [{"@type": "ListItem", "position": i + 1, "url": f"{SITE}/packages/{p['slug']}.html", "name": p["title"]} for i, p in enumerate(PACKAGES)],
    }
    sections = []
    for g, (label, anchor, heading) in GROUPS.items():
        items = [p for p in PACKAGES if p["group"] == g]
        cards = "\n".join(card(p, base, i % 3) for i, p in enumerate(items))
        sections.append(f'''<section class="section pk-group" id="{anchor}" aria-labelledby="h-{anchor}">
    <div class="container">
      <header class="section-header reveal">
        <p class="section-tag">{len(items)} packages</p>
        <h2 class="section-title" id="h-{anchor}">{heading}</h2>
      </header>
      <div class="packages-grid">
{cards}
      </div>
    </div>
  </section>''')
    chips = "".join(f'<a class="chip" href="#{a}">{l}</a>' for l, a, _ in GROUPS.values())
    return f'''{head(title, desc, url, base, img(PACKAGES[0]["image"], 1200, 630), [ld_list])}
<body class="page-packages">
<!-- BUILD:header -->
{header(base, "packages")}
<!-- /BUILD:header -->
<main id="main">
  <section class="page-hero">
    <picture class="pkg-hero-bg"><img src="{img('photo-1488085061387-422e29b40080', 1600, 600)}" width="1600" height="600" alt="View of the sky from an aeroplane window at golden hour" fetchpriority="high" decoding="async"></picture>
    <div class="container pkg-hero-inner">
      <nav class="breadcrumb" aria-label="Breadcrumb"><ol><li><a href="../" data-i18n="nav.home">Home</a></li><li aria-current="page" data-i18n="nav.packages">Packages</li></ol></nav>
      <h1 data-i18n="pk.title">All Tour Packages</h1>
      <p class="pkg-lead" data-i18n="pk.sub">Holidays, Umrah and Hajj from Mumbai — every package with a full day-wise itinerary.</p>
      <nav class="chip-nav" aria-label="Package categories">{chips}</nav>
    </div>
  </section>
  {"".join(sections)}
</main>
<!-- BUILD:footer -->
{footer(base)}
<!-- /BUILD:footer -->
<script src="../js/i18n.js" defer></script>
<script src="../js/main.js" defer></script>
</body>
</html>
'''


def simple_page(slug, title, desc, h1, lead, body, hero_img, ld=None, body_class="page-legal", active=""):
    base = "./"
    url = f"{SITE}/{slug}"
    bc = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{SITE}/"},
        {"@type": "ListItem", "position": 2, "name": re.sub("<[^>]+>", "", h1).replace("&amp;", "&"), "item": url}]}
    page_ld = {"@context": "https://schema.org", "@type": "WebPage", "name": re.sub("<[^>]+>", "", h1).replace("&amp;", "&"), "url": url, "description": desc,
               "isPartOf": {"@id": f"{SITE}/#website"}, "publisher": {"@id": f"{SITE}/#organization"}}
    return f'''{head(title, desc, url, base, f"{SITE}/assets/img/og-image.jpg", [bc, page_ld] + (ld or []))}
<body class="{body_class}">
<!-- BUILD:header -->
{header(base, active)}
<!-- /BUILD:header -->
<main id="main">
  <section class="page-hero page-hero-sm">
    <picture class="pkg-hero-bg"><img src="{img(hero_img, 1600, 500)}" width="1600" height="500" alt="" fetchpriority="high" decoding="async"></picture>
    <div class="container pkg-hero-inner">
      <nav class="breadcrumb" aria-label="Breadcrumb"><ol><li><a href="./" data-i18n="nav.home">Home</a></li><li aria-current="page">{h1}</li></ol></nav>
      <h1>{h1}</h1>
      <p class="pkg-lead">{lead}</p>
    </div>
  </section>
  {body}
</main>
<!-- BUILD:footer -->
{footer(base)}
<!-- /BUILD:footer -->
<script src="js/i18n.js" defer></script>
<script src="js/main.js" defer></script>
</body>
</html>
'''


def legal_page(slug, h1, desc, html_body, hero_img):
    from legal_content import UPDATED
    toc = "".join(f'<li><a href="#{i}">{t}</a></li>' for i, t in re.findall(r'<h2 id="([^"]+)">(.*?)</h2>', html_body))
    body = f'''<section class="section legal">
    <div class="container legal-layout">
      <aside class="legal-toc" aria-label="On this page"><p class="legal-toc-title">On this page</p><ol>{toc}</ol></aside>
      <article class="legal-body">
        <p class="legal-updated"><i class="fas fa-calendar-check" aria-hidden="true"></i> Last updated: {UPDATED}</p>
        {html_body}
        <div class="legal-contact">
          <h2>Questions?</h2>
          <p><strong>{LEGAL}</strong> · CIN {CIN}<br>Shop No. 2, Arsiwala Building, Dimtimkar Road, Nagpada, Mumbai – 400008<br>
          <a href="tel:{PHONE1_TEL}">{PHONE1}</a> · <a href="tel:{PHONE2_TEL}">{PHONE2}</a> · <a href="mailto:{EMAIL}">{EMAIL}</a></p>
          <div class="btn-row"><a class="btn btn-wa btn-sm" href="https://wa.me/{WA}" target="_blank" rel="noopener"><i class="fab fa-whatsapp" aria-hidden="true"></i><span>WhatsApp us</span></a>
          <button type="button" class="btn btn-outline btn-sm" data-action="print"><i class="fas fa-print" aria-hidden="true"></i><span>Print / Save PDF</span></button></div>
        </div>
      </article>
    </div>
  </section>'''
    return simple_page(slug, f"{re.sub('<[^>]+>', '', h1).replace('&amp;', '&')} | {BRAND}", desc, h1, desc, body, hero_img)


def feedback_page():
    groups = []
    for g, (label, _a, _h) in GROUPS.items():
        opts = "".join(f"<option>{e(p['title'])}</option>" for p in PACKAGES if p["group"] == g)
        groups.append(f'<optgroup label="{label}">{opts}</optgroup>')
    groups.append('<optgroup label="Services"><option>Air tickets</option><option>Hotel booking</option><option>Visa assistance</option><option>Forex / currency exchange</option><option>Cruise</option><option>Customized travel</option><option>Other</option></optgroup>')
    def rating(name, legend, required=False):
        labels = ["Poor", "Fair", "Good", "Very good", "Excellent"]
        stars = "".join(
            f'<input type="radio" id="{name}-{n}" name="{name}" value="{n}/5 – {labels[n-1]}"{" required" if required and n == 5 else ""}><label for="{name}-{n}" title="{labels[n-1]}"><i class="fas fa-star" aria-hidden="true"></i><span class="sr-only">{n} – {labels[n-1]}</span></label>'
            for n in range(5, 0, -1))
        return f'<fieldset class="rating-field"><legend>{legend}{" *" if required else ""}</legend><div class="stars-input">{stars}</div></fieldset>'
    body = f'''<section class="section feedback">
    <div class="container feedback-layout">
      <form class="feedback-card" id="feedbackForm" data-form="feedback" data-subject="Customer feedback" novalidate>
        <input type="text" name="_gotcha" class="hp" tabindex="-1" autocomplete="off" aria-hidden="true">
        <h2>Tell us about your trip</h2>
        <p class="muted">Fields marked * are required. When you press submit, WhatsApp opens with your feedback ready to send to our team.</p>
        <div class="cf-grid">
          <div class="field"><label for="fb-name">Full Name *</label><input id="fb-name" name="Name" type="text" autocomplete="name" required></div>
          <div class="field"><label for="fb-phone">Phone / WhatsApp *</label><input id="fb-phone" name="Phone" type="tel" autocomplete="tel" inputmode="tel" pattern="[0-9+()\\s-]{{8,}}" required></div>
          <div class="field"><label for="fb-email">Email</label><input id="fb-email" name="Email" type="email" autocomplete="email"></div>
          <div class="field"><label for="fb-city">City</label><input id="fb-city" name="City" type="text" autocomplete="address-level2"></div>
          <div class="field cf-full"><label for="fb-pkg">Package / service used *</label><select id="fb-pkg" name="Package or service" required><option value="">Select…</option>{"".join(groups)}</select></div>
          <div class="field"><label for="fb-date">Travel month</label><input id="fb-date" name="Travel month" type="month"></div>
          <div class="field"><label for="fb-ref">Booking reference (optional)</label><input id="fb-ref" name="Booking reference" type="text"></div>
        </div>
        <div class="rating-grid">
          {rating("Overall_experience", "Overall experience", True)}
          {rating("Booking_and_communication", "Booking &amp; communication")}
          {rating("Hotels_and_accommodation", "Hotels &amp; accommodation")}
          {rating("Transport_and_transfers", "Transport &amp; transfers")}
          {rating("Guide_or_group_leader", "Guide / group leader")}
          {rating("Value_for_money", "Value for money")}
        </div>
        <fieldset class="choice-field"><legend>Would you recommend Sahaba Travels to family &amp; friends? *</legend>
          <label><input type="radio" name="Would recommend" value="Yes" required> Yes</label>
          <label><input type="radio" name="Would recommend" value="Maybe"> Maybe</label>
          <label><input type="radio" name="Would recommend" value="No"> No</label>
        </fieldset>
        <div class="field"><label for="fb-liked">What did you like most?</label><textarea id="fb-liked" name="Liked most" rows="3"></textarea></div>
        <div class="field"><label for="fb-improve">What can we improve?</label><textarea id="fb-improve" name="Can improve" rows="3"></textarea></div>
        <label class="check-line"><input type="checkbox" name="May publish as testimonial" value="Yes"> You may publish my feedback (first name and city only) as a testimonial.</label>
        <button type="submit" class="btn btn-wa btn-block"><i class="fab fa-whatsapp" aria-hidden="true"></i><span>Submit feedback on WhatsApp</span></button>
        <p class="form-status" role="status" aria-live="polite"></p>
      </form>
      <aside class="feedback-aside">
        <div class="feedback-note">
          <i class="fas fa-heart" aria-hidden="true"></i>
          <h2>Your words help us serve every pilgrim and traveller better.</h2>
          <p>Every message is read by our management team. If something went wrong, we want to make it right — please include your phone number and booking details.</p>
        </div>
        <div class="feedback-note alt">
          <i class="fab fa-google" aria-hidden="true"></i>
          <h2>Happy with your trip?</h2>
          <p>A quick Google review helps other families find a travel partner they can trust.</p>
          <a class="btn btn-primary btn-sm" href="https://www.google.com/maps/search/?api=1&amp;query=Sahaba+Travels+and+Forex+Nagpada+Mumbai" target="_blank" rel="noopener"><i class="fas fa-star" aria-hidden="true"></i><span>Review us on Google</span></a>
        </div>
        <div class="feedback-note">
          <i class="fas fa-headset" aria-hidden="true"></i>
          <h2>Need help right now?</h2>
          <p><a href="tel:{PHONE1_TEL}">{PHONE1}</a><br><a href="tel:{PHONE2_TEL}">{PHONE2}</a><br><a href="mailto:{EMAIL}">{EMAIL}</a></p>
        </div>
      </aside>
    </div>
  </section>'''
    return simple_page("feedback.html", f"Feedback | {BRAND}", "Share feedback about your Umrah, Hajj, holiday, visa or forex experience with Sahaba Travels and Forex, Nagpada, Mumbai.",
                       "Feedback", "Travelled with us? Tell us how it went — your feedback reaches our team directly on WhatsApp.", body, "photo-1545132147-d037e6c54cfd", body_class="page-feedback")


def visa_page():
    import visa_content as V
    from urllib.parse import quote
    chips = [("all", "All", "vf.all")] + [(k, v, f"vf.{k}") for k, v in V.TYPE_LABEL.items()]
    chip_html = "".join(
        f'<button type="button" class="chip{" active" if k == "all" else ""}" data-visa-filter="{k}" aria-pressed="{"true" if k == "all" else "false"}" data-i18n="{key}">{label}</button>'
        for k, label, key in chips)
    cards = []
    for country, flag, typ, proc, stay, note in V.VISAS:
        wa = f"https://wa.me/{WA}?text=" + quote(f"Hello Sahaba Travels, I need a {country} visa. Please share the documents and fees.")
        cards.append(f'''<article class="visa-card" data-type="{typ}" data-name="{e(country.lower())}">
          <div class="visa-card-head">
            <img src="https://flagcdn.com/w80/{flag}.png" srcset="https://flagcdn.com/w160/{flag}.png 2x" width="44" height="30" alt="" loading="lazy" decoding="async">
            <h3>{e(country)}</h3>
            <span class="visa-tag tag-{typ}">{V.TYPE_LABEL[typ]}</span>
          </div>
          <dl class="visa-facts">
            <div><dt><i class="fas fa-clock" aria-hidden="true"></i> <span data-i18n="vc.proc">Processing</span></dt><dd>{e(proc)}</dd></div>
            <div><dt><i class="fas fa-calendar-days" aria-hidden="true"></i> <span data-i18n="vc.stay">Stay</span></dt><dd>{e(stay)}</dd></div>
          </dl>
          <p class="visa-note">{e(note)}</p>
          <div class="service-actions">
            <a href="#visa-apply" class="service-link" data-visa="{e(country)}"><span data-i18n="vc.apply">Apply now</span> <i class="fas fa-arrow-right" aria-hidden="true"></i></a>
            <span class="service-quick">
              <a href="{wa}" class="quick-btn quick-wa" target="_blank" rel="noopener" aria-label="WhatsApp about {e(country)} visa"><i class="fab fa-whatsapp" aria-hidden="true"></i></a>
              <a href="tel:{PHONE1_TEL}" class="quick-btn quick-call" aria-label="Call about {e(country)} visa"><i class="fas fa-phone" aria-hidden="true"></i></a>
            </span>
          </div>
        </article>''')
    countries = "".join(f"<option>{e(c)}</option>" for c, *_ in sorted(V.VISAS, key=lambda x: x[0])) + "<option>Other</option>"
    vtypes = "".join(f"<option>{t}</option>" for t in V.VISA_TYPES)
    docs = "".join(f'<li><span class="feature-icon"><i class="fas fa-{ic}" aria-hidden="true"></i></span><div><h3>{t}</h3><p>{d}</p></div></li>' for ic, t, d in V.DOCS)
    faqs = "".join(f'<details class="faq-item" name="faq-visa"><summary>{e(q)}<i class="fas fa-plus" aria-hidden="true"></i></summary><p>{e(a)}</p></details>' for q, a in V.FAQS)
    ld_service = {"@context": "https://schema.org", "@type": "Service", "name": "Visa assistance", "serviceType": "Visa application assistance",
                  "provider": {"@id": f"{SITE}/#organization"}, "areaServed": {"@type": "City", "name": "Mumbai"},
                  "description": f"Visa assistance from Nagpada, Mumbai for {len(V.VISAS)} destinations including UAE, Saudi Arabia, Schengen, UK, USA, Canada and Asia.",
                  "hasOfferCatalog": {"@type": "OfferCatalog", "name": "Visa destinations", "itemListElement": [
                      {"@type": "Offer", "itemOffered": {"@type": "Service", "name": f"{c} visa"}} for c, *_ in V.VISAS]}}
    ld_faq = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in V.FAQS]}
    body = f'''<section class="visa-trust">
    <div class="container">
      <ul class="visa-trust-list">
        <li><i class="fas fa-earth-asia" aria-hidden="true"></i><strong>{len(V.VISAS)}+</strong> <span data-i18n="vt.1">destinations</span></li>
        <li><i class="fas fa-list-check" aria-hidden="true"></i><span data-i18n="vt.2">Country-wise document checklist</span></li>
        <li><i class="fas fa-building-columns" aria-hidden="true"></i><span data-i18n="vt.3">Embassy &amp; VFS filing support</span></li>
        <li><i class="fas fa-truck-fast" aria-hidden="true"></i><span data-i18n="vt.4">Doorstep pickup in Mumbai</span></li>
      </ul>
    </div>
  </section>

  <section class="section visa-dest" id="destinations" aria-labelledby="dest-title">
    <div class="container">
      <header class="section-header reveal">
        <p class="section-tag" data-i18n="vd.tag">Visa Destinations</p>
        <h2 class="section-title" id="dest-title" data-i18n-html="vd.h">Popular <span>visa destinations</span></h2>
        <p class="section-subtitle" data-i18n="vd.desc">Typical processing times for Indian passport holders. Rules change often — we confirm the latest requirements and fees before you apply.</p>
      </header>
      <div class="visa-tools">
        <div class="filter-bar" role="group" aria-label="Filter by visa type">{chip_html}</div>
        <label class="visa-search"><i class="fas fa-magnifying-glass" aria-hidden="true"></i><span class="sr-only">Search country</span><input type="search" id="visaSearch" placeholder="Search country…" data-i18n-attr="placeholder:vd.search" autocomplete="off"></label>
      </div>
      <p class="visa-count" id="visaCount" aria-live="polite">{len(V.VISAS)} destinations</p>
      <div class="visa-grid" id="visaGrid">
{chr(10).join(cards)}
      </div>
      <div class="visa-empty" id="visaEmpty" hidden>
        <p data-i18n="vd.none">No destination found — we still help with most countries.</p>
        <button type="button" class="btn btn-outline btn-sm" id="visaClear" data-i18n="vd.clear">Clear search</button>
        <a href="#visa-apply" class="btn btn-primary btn-sm" data-visa="Other" data-i18n="vd.ask">Ask about another country</a>
      </div>
    </div>
  </section>

  <section class="section visa-process" aria-labelledby="process-title">
    <div class="container">
      <header class="section-header reveal">
        <p class="section-tag" data-i18n="vp.tag">Simple Process</p>
        <h2 class="section-title" id="process-title" data-i18n-html="vp.h">How we get <span>your visa</span></h2>
      </header>
      <ol class="process-steps">
        <li class="reveal"><span class="process-n">1</span><i class="fas fa-pen-to-square" aria-hidden="true"></i><h3 data-i18n="vp.1">Share your plan</h3><p data-i18n="vp.1d">Tell us the destination, travel date and visa type.</p></li>
        <li class="reveal" style="--delay:.08s"><span class="process-n">2</span><i class="fas fa-folder-open" aria-hidden="true"></i><h3 data-i18n="vp.2">Get your checklist</h3><p data-i18n="vp.2d">We send a country-specific document list and the fees.</p></li>
        <li class="reveal" style="--delay:.16s"><span class="process-n">3</span><i class="fas fa-building-columns" aria-hidden="true"></i><h3 data-i18n="vp.3">We file your application</h3><p data-i18n="vp.3d">Forms, appointment and submission to the embassy or VFS.</p></li>
        <li class="reveal" style="--delay:.24s"><span class="process-n">4</span><i class="fas fa-passport" aria-hidden="true"></i><h3 data-i18n="vp.4">Visa delivered</h3><p data-i18n="vp.4d">By email for e-visas, or passport delivered in Mumbai.</p></li>
      </ol>
      <p class="center-cta"><a href="#visa-apply" class="btn btn-primary"><span data-i18n="vp.cta">Start your application</span><i class="fas fa-arrow-right" aria-hidden="true"></i></a></p>
    </div>
  </section>

  <section class="section visa-docs" aria-labelledby="docs-title">
    <div class="container">
      <header class="section-header reveal">
        <p class="section-tag" data-i18n="vdoc.tag">Documents</p>
        <h2 class="section-title" id="docs-title" data-i18n-html="vdoc.h">What you’ll <span>usually need</span></h2>
        <p class="section-subtitle" data-i18n="vdoc.desc">Exact requirements depend on the country and visa type — your checklist will be specific to you.</p>
      </header>
      <ul class="visa-docs-grid reveal">{docs}</ul>
    </div>
  </section>

  <section class="section visa-apply" id="visa-apply" aria-labelledby="apply-title">
    <div class="container visa-apply-grid">
      <form class="contact-form-card" id="visaForm" data-form="visa" data-subject="Visa enquiry" novalidate>
        <h2 id="apply-title" data-i18n="va.h">Start your visa application</h2>
        <p data-i18n="va.sub">Share a few details — our visa desk replies during office hours with your document checklist and fees.</p>
        <input type="text" name="_gotcha" class="hp" tabindex="-1" autocomplete="off" aria-hidden="true">
        <div class="cf-grid">
          <div class="field"><label for="va-first" data-i18n="form.first">First Name</label><input id="va-first" name="First_name" type="text" autocomplete="given-name" required></div>
          <div class="field"><label for="va-last" data-i18n="form.last">Last Name</label><input id="va-last" name="Last_name" type="text" autocomplete="family-name" required></div>
          <div class="field"><label for="va-phone" data-i18n="form.phone">Phone / WhatsApp</label><input id="va-phone" name="Mobile" type="tel" autocomplete="tel" inputmode="tel" pattern="[0-9+()\\s-]{{8,}}" required></div>
          <div class="field"><label for="va-email" data-i18n="form.email">Email Address</label><input id="va-email" name="Email" type="email" autocomplete="email"></div>
          <div class="field"><label for="va-country" data-i18n="va.country">Destination country</label><select id="va-country" name="Destination" required><option value="" data-i18n="va.select">Select country</option>{countries}</select></div>
          <div class="field"><label for="va-type" data-i18n="va.type">Visa type</label><select id="va-type" name="Visa_type">{vtypes}</select></div>
          <div class="field"><label for="va-pax" data-i18n="va.pax">Applicants</label><select id="va-pax" name="Applicants"><option>1</option><option>2</option><option>3</option><option>4</option><option>5</option><option>6+</option></select></div>
          <div class="field"><label for="va-date" data-i18n="va.date">Travel date</label><input id="va-date" name="Travel_date" type="date"></div>
          <fieldset class="choice-field cf-full"><legend data-i18n="va.contact">Preferred contact</legend>
            <label><input type="radio" name="Preferred_contact" value="WhatsApp" checked> WhatsApp</label>
            <label><input type="radio" name="Preferred_contact" value="Phone call"> <span data-i18n="va.call">Phone call</span></label>
            <label><input type="radio" name="Preferred_contact" value="Email"> Email</label>
          </fieldset>
          <div class="field cf-full"><label for="va-notes" data-i18n="va.notes">Additional notes</label><textarea id="va-notes" name="Notes" rows="3" placeholder="Previous visas, refusals, purpose of travel…"></textarea></div>
          <div class="cf-full">
            <button type="submit" class="btn btn-primary btn-block"><i class="fas fa-paper-plane" aria-hidden="true"></i> <span data-i18n="va.send">Submit visa enquiry</span></button>
            <p class="form-status" role="status" aria-live="polite"></p>
            <p class="visa-privacy"><i class="fas fa-lock" aria-hidden="true"></i> <span data-i18n="va.privacy">Your details are used only for your application.</span> <a href="privacy-policy.html" data-i18n="legal.privacy">Privacy Policy</a></p>
          </div>
        </div>
      </form>
      <aside class="feedback-aside">
        <div class="feedback-note alt">
          <i class="fas fa-headset" aria-hidden="true"></i>
          <h2 data-i18n="va.help">Need immediate help?</h2>
          <p data-i18n="va.helpd">Talk to our visa desk now.</p>
          <div class="btn-row">
            <a class="btn btn-primary btn-sm" href="tel:{PHONE1_TEL}"><i class="fas fa-phone" aria-hidden="true"></i><span>{PHONE1}</span></a>
            <a class="btn btn-outline btn-sm visa-alt-call" href="tel:{PHONE2_TEL}"><i class="fas fa-phone" aria-hidden="true"></i><span>{PHONE2}</span></a>
            <a class="btn btn-wa btn-sm" href="https://wa.me/{WA}?text={quote('Hello Sahaba Travels, I need help with a visa.')}" target="_blank" rel="noopener"><i class="fab fa-whatsapp" aria-hidden="true"></i><span>WhatsApp</span></a>
          </div>
        </div>
        <div class="feedback-note">
          <i class="fas fa-circle-info" aria-hidden="true"></i>
          <h2 data-i18n="va.noteh">Good to know</h2>
          <ul class="visa-notes">
            <li data-i18n="va.n1">Apply 3–4 weeks before travel; 6–8 weeks for the USA, UK and Schengen in peak season.</li>
            <li data-i18n="va.n2">The embassy decides every visa; no agent can guarantee approval.</li>
            <li data-i18n="va.n3">Embassy fees and service charges are non-refundable once filed.</li>
          </ul>
        </div>
      </aside>
    </div>
  </section>

  <section class="section faq" id="visa-faq" aria-labelledby="vfaq-title">
    <div class="container faq-grid">
      <header class="section-header align-start reveal">
        <p class="section-tag" data-i18n="faq.tag">FAQs</p>
        <h2 class="section-title" id="vfaq-title" data-i18n-html="vfaq.h">Visa questions, <span>answered</span></h2>
        <p class="section-subtitle">Destination list last reviewed: {V.UPDATED}. Visa rules for Indian passport holders change often; we confirm the current rule for your trip.</p>
      </header>
      <div class="faq-list reveal">{faqs}</div>
    </div>
  </section>'''
    return simple_page("visa.html", f"Visa Services in Mumbai – Dubai, Saudi, Schengen, UK, USA & {len(V.VISAS)}+ Countries | {BRAND}",
                       f"Visa assistance from Nagpada, Mumbai for {len(V.VISAS)}+ destinations — e-visas, sticker visas and visa on arrival. Document checklist, embassy filing and doorstep pickup. Call +91 97690 47633.",
                       "Visa Services", "Tourist, business, Umrah and visit visas for 45+ countries — document checklist, embassy filing and doorstep pickup in Mumbai.",
                       body, "photo-1655722725332-9925c96dd627", ld=[ld_service, ld_faq], body_class="page-visa", active="visa")


def replace_block(text: str, name: str, content: str) -> str:
    pat = re.compile(rf"(<!-- BUILD:{name} -->)(.*?)(<!-- /BUILD:{name} -->)", re.S)
    if not pat.search(text):
        raise SystemExit(f"marker BUILD:{name} missing in index.html")
    return pat.sub(lambda m: f"{m.group(1)}\n{content}\n{m.group(3)}", text)


def sitemap() -> str:
    urls = [(f"{SITE}/", "1.0", "weekly"), (f"{SITE}/packages/", "0.9", "weekly"), (f"{SITE}/visa.html", "0.9", "monthly")]
    urls += [(f"{SITE}/packages/{p['slug']}.html", "0.8", "monthly") for p in PACKAGES]
    urls += [(f"{SITE}/{href}", "0.3", "yearly") for href, _k, _l in LEGAL_PAGES]
    body = "\n".join(
        f"  <url><loc>{u}</loc><lastmod>{TODAY}</lastmod><changefreq>{c}</changefreq><priority>{pr}</priority></url>" for u, pr, c in urls
    )
    return f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{body}\n</urlset>\n'


def llms() -> str:
    lines = [
        "# Sahaba Travels & Forex", "",
        f"> {LEGAL} (CIN {CIN}) is a travel agency and foreign-exchange office in Nagpada, Mumbai, India, offering Umrah and Hajj packages, family and honeymoon holidays, religious tours, visa assistance, flights, hotels and currency exchange.", "",
        "## Key facts",
        f"- Legal name: {LEGAL}", f"- CIN: {CIN} (ROC Mumbai, incorporated 4 March 2025)",
        f"- Director: Khan Faisal — {DIRECTOR_URL}",
        "- Address: Shop No. 2, Arsiwala Building, Dimtimkar Road, Nagpada, Mumbai – 400008, Maharashtra, India",
        f"- Phone / WhatsApp: {PHONE1}, {PHONE2}", f"- Email: {EMAIL}",
        "- Hours (IST): Monday–Friday 10:00 AM–9:00 PM; Saturday 10:00 AM–6:00 PM; Sunday closed",
        "- Languages: English, Hindi, Urdu, Marathi, Gujarati", "",
        "## Pages",
        f"- [All packages]({SITE}/packages/)", f"- [Visa services — 45+ destinations]({SITE}/visa.html)", f"- [Umrah & Hajj]({SITE}/#hajj-umrah)", f"- [Forex rates]({SITE}/#forex)", f"- [FAQs]({SITE}/#faq)", f"- [Contact]({SITE}/#contact)",
    ]
    for g, (label, _a, _h) in GROUPS.items():
        lines += ["", f"## {label}"]
        for p in (x for x in PACKAGES if x["group"] == g):
            lines.append(f"- [{p['title']}]({SITE}/packages/{p['slug']}.html): {p['nights']}N/{p['days']}D, {' – '.join(p['cities'])}; from {inr(p['price'])} {p['priceNote']}.")
    return "\n".join(lines) + "\n"


def forex_fallback() -> str:
    """Read data/forex-rates.xlsx with the standard library and write data/forex-rates.js.
    The site reads the Excel file directly; this JS copy is only a fallback (e.g. when the
    page is opened from disk with file://, where browsers block reading the .xlsx)."""
    import zipfile
    import xml.etree.ElementTree as ET
    ns = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
    path = ROOT / "data" / "forex-rates.xlsx"
    with zipfile.ZipFile(path) as z:
        shared = []
        if "xl/sharedStrings.xml" in z.namelist():
            for si in ET.fromstring(z.read("xl/sharedStrings.xml")).findall("m:si", ns):
                shared.append("".join(t.text or "" for t in si.iter(f"{{{ns['m']}}}t")))
        sheet = ET.fromstring(z.read("xl/worksheets/sheet1.xml"))
    rows = []
    for r in sheet.iter(f"{{{ns['m']}}}row"):
        vals = {}
        for c in r.findall("m:c", ns):
            col = re.match(r"[A-Z]+", c.get("r")).group(0)
            v = c.find("m:v", ns)
            isv = c.find("m:is", ns)
            if c.get("t") == "s" and v is not None:
                vals[col] = shared[int(v.text)]
            elif isv is not None:
                vals[col] = "".join(t.text or "" for t in isv.iter(f"{{{ns['m']}}}t"))
            elif v is not None:
                vals[col] = v.text
        rows.append(vals)
    head = {k: (v or "").lower() for k, v in rows[0].items()}
    col = lambda word: next((k for k, v in head.items() if word in v), None)
    c_code, c_sell, c_upd = col("code"), col("sell"), col("updated")
    sell, updated = {}, ""
    for r in rows[1:]:
        code = (r.get(c_code) or "").strip().upper()
        try:
            val = float(r.get(c_sell))
        except (TypeError, ValueError):
            continue
        if re.fullmatch(r"[A-Z]{3}", code) and val > 0:
            sell[code] = val
        updated = updated or (r.get(c_upd) or "")
    data = {"sell": sell, "buy": {}, "updated": updated}
    return "/* Auto-generated from data/forex-rates.xlsx by _build/build.py — do not edit. */\nwindow.SAHABA_FX_FALLBACK = " + json.dumps(data) + ";\n"


def main():
    out = ROOT / "packages"
    out.mkdir(exist_ok=True)
    keep = {f"{p['slug']}.html" for p in PACKAGES} | {"index.html"}
    for old in out.glob("*.html"):
        if old.name not in keep:
            old.unlink()  # package removed from packages.json
    for p in PACKAGES:
        (out / f"{p['slug']}.html").write_text(package_page(p), encoding="utf-8")
    (out / "index.html").write_text(packages_index(), encoding="utf-8")

    idx_path = ROOT / "index.html"
    idx = idx_path.read_text(encoding="utf-8")
    idx = replace_block(idx, "gate", gate(""))
    idx = replace_block(idx, "header", header("", "home"))
    idx = replace_block(idx, "footer", footer(""))
    holiday = [p for p in FEATURED if p["group"] != "umrah"]
    umrah = [p for p in PACKAGES if p["group"] == "umrah"]
    idx = replace_block(idx, "holiday-cards", "\n".join(card(p, "", i % 3) for i, p in enumerate(holiday)))
    idx = replace_block(idx, "umrah-cards", "\n".join(card(p, "", i) for i, p in enumerate(umrah)))
    idx_path.write_text(idx, encoding="utf-8")

    import sys
    sys.path.insert(0, str(ROOT / "_build"))
    import legal_content as L
    (ROOT / "terms-and-conditions.html").write_text(legal_page("terms-and-conditions.html", "Terms &amp; Conditions",
        "Terms and conditions for bookings with Sahaba Travels and Forex Pvt. Ltd. — packages, Umrah & Hajj, flights, visas and forex.", L.TERMS, "photo-1581553673739-c4906b5d0de8"), encoding="utf-8")
    (ROOT / "privacy-policy.html").write_text(legal_page("privacy-policy.html", "Privacy Policy",
        "How Sahaba Travels and Forex Pvt. Ltd. collects, uses and protects your personal data under India’s DPDP Act, 2023.", L.PRIVACY, "photo-1553697388-94e804e2f0f6"), encoding="utf-8")
    (ROOT / "cancellation-refund-policy.html").write_text(legal_page("cancellation-refund-policy.html", "Cancellation &amp; Refund Policy",
        "Cancellation charges, change requests and refund timelines for holidays, Umrah, Hajj, flights, hotels, visas and forex at Sahaba Travels.", L.REFUND, "photo-1436491865332-7a61a109cc05"), encoding="utf-8")
    (ROOT / "feedback.html").write_text(feedback_page(), encoding="utf-8")
    (ROOT / "visa.html").write_text(visa_page(), encoding="utf-8")
    (ROOT / "sitemap.xml").write_text(sitemap(), encoding="utf-8")
    (ROOT / "llms.txt").write_text(llms(), encoding="utf-8")
    (ROOT / "data" / "forex-rates.js").write_text(forex_fallback(), encoding="utf-8")
    print(f"Built {len(PACKAGES)} package pages + packages/index.html, refreshed index.html and sitemap.xml")


if __name__ == "__main__":
    main()
