# Sahaba Travels & Forex — website

Static site (HTML + CSS + vanilla JS). There's no build step to deploy: push to GitHub Pages and it's live.

## Structure
```
index.html              Home (hero, quick enquiry, about, director, packages, Hajj & Umrah, forex, reviews, FAQ, contact, map)
packages/               One page per package with a day-wise itinerary + packages/index.html (all packages)
css/style.css           All styles: light/dark theme tokens, responsive, RTL (Urdu), print/PDF
js/main.js              Theme, menu, tabs, filters, forms, share/PDF, lightbox, open-now badge  ← CONFIG at top
js/i18n.js              Language switcher: English (default), Hindi, Gujarati, Marathi, Urdu
js/forex.js             Live buy rates + sell rates from Excel + converter                         ← CONFIG at top
data/forex-rates.xlsx   YOUR SELL RATES: edit in Excel, commit, done
assets/img/             Logo, emblem, favicons, social share image
sitemap.xml, robots.txt, llms.txt, site.webmanifest, 404.html
_build/                 packages.json (all package content) + build.py (not published by GitHub Pages)
```

## Everyday updates
- **Forex sell rates:** open `data/forex-rates.xlsx`, change the yellow column, save, then commit and push. The rates in the file now are SAMPLES (market + 1.5%), so replace them with your real rates. Optionally run `python3 _build/build.py` too: it refreshes `data/forex-rates.js`, a backup copy that's used when the page is opened straight from your computer (browsers block reading the .xlsx from `file://`).
- **Packages:** edit `_build/packages.json`, then run `python3 _build/build.py`. It regenerates every package page, the home-page cards, the shared header/footer, `sitemap.xml` and `llms.txt`. Set `"group"` to `umrah`, `family`, `honeymoon` or `religious`. Add `"featured": true` to show a package on the home page. If you remove a package from the JSON, its page is deleted on the next build.
- **Visa page** (`visa.html`): destinations, processing times, notes, FAQs and documents live in `_build/visa_content.py`. Edit there, then run the build. Visa rules for Indian passports change often, so review the list every few months.
- **Office hours:** they appear in the top bar and footer (`_build/build.py`), the contact card and JSON-LD (`index.html`), the "Open now" badge (`js/main.js` → `closeAt`), the translations (`js/i18n.js` → `top.hours`, `footer.hours`), `llms()` in `build.py`, and the refund-policy contact line.
- **Policy pages** (Terms, Privacy, Cancellation & Refund): edit the text in `_build/legal_content.py`, then run the build. The Feedback page form sends straight to WhatsApp.
- **Welcome flyer:** each visitor sees it once (it's in the footer template in `_build/build.py`). To show a new offer to everyone again, change `FLYER_KEY = 'st-flyer-v1'` in `js/main.js` to `'st-flyer-v2'`.
- **Social links:** Facebook, Instagram and LinkedIn URLs are at the top of `_build/build.py` (`FACEBOOK`, `INSTAGRAM`, `LINKEDIN`).
- **Header/footer/contact details:** these are in `_build/build.py` (top constants + `header()`/`footer()`). Re-run the build afterwards.

## Launch day: coming-soon page and automatic switch

- `coming-soon.html` is the countdown page. Every page of the site starts with a small time check (added by the build, controlled by `LAUNCH_AT` in `_build/build.py`). Before **16 Oct 2026, 12:00 PM IST**, visitors are sent to the coming-soon page. From 12:00 the real site opens; nothing needs to be pushed at noon.
- The countdown uses the web server's clock, so phones set to the wrong time still switch on time. The "final call" 10-second countdown starts at 11:59:50. Anyone watching the page is taken to the new site automatically at 12:00.
- **Preview the real site before launch:** open `https://sahabatravels.com/?preview`. The browser remembers it, so every page opens normally. Turn it off with `?preview=off`.
- **After launch (from the next day):** set `LAUNCH_AT = ""` in `_build/build.py`, run the build, then commit and push. That removes the time check from every page. You can keep `coming-soon.html` or delete it.
- To change the launch time, edit **both** `LAUNCH_AT` in `_build/build.py` and `LAUNCH` at the bottom of `coming-soon.html`, then run the build.

## Upload to GitHub Pages
1. Create a repository (for example `sahabatravels`) and copy **everything inside this folder** to the repository root (with GitHub Desktop: drop the files into the cloned folder, then commit and push). `index.html` must be at the root.
2. On GitHub, go to **Settings → Pages → Build and deployment**, set Source to "Deploy from a branch", choose Branch `main` and folder `/ (root)`, then click Save.
3. **Custom domain:** the included `CNAME` file sets `sahabatravels.com`. At your domain registrar, add four A records for `@` (185.199.108.153, 185.199.109.153, 185.199.110.153, 185.199.111.153) and a CNAME record `www → <your-username>.github.io`. Once DNS resolves, tick **Enforce HTTPS**.
   If you're **not** using the domain yet, delete `CNAME` and the site will open at `https://<username>.github.io/<repo>/`. Everything uses relative links, so it works there too. Only the 404 page uses root links, so it looks right once the domain is connected.
4. Keep the `_build/` folder in the repo: GitHub Pages doesn't publish folders that start with `_`, and you need it for future package edits.

## Before going live (checklist)
1. **Form delivery:** create a free Formspree form and paste its URL in `js/main.js → CONFIG.formEndpoint`. Until you do, all forms open WhatsApp with the details pre-filled, so they still work.
2. **Google reviews:** put the Place ID in `CONFIG.googlePlaceId` so the "Write a review" button opens the review box directly. Replace the testimonial cards in `index.html` with real Google reviews.
3. **Director photo:** already added in `assets/img/director.webp` and `director.jpg`. To change it, replace both files and keep the same names.
4. **Map pin:** check the coordinates `18.9686, 72.8283` (in `<head>` meta and JSON-LD) against the exact shop location.
5. **HTTPS:** the current domain redirects HTTPS to HTTP. Turn on "Enforce HTTPS" in GitHub Pages settings, because every canonical URL is `https://`.
6. **Claims to verify:** "15K+ pilgrims", "18+ years", package prices, Hajj 2027 pricing, and the RBI/forex wording. The company was incorporated in March 2025, so make sure the "years" claim refers to the founders' experience.
7. **Cancellation slabs:** the % charges in the Cancellation & Refund Policy are a standard industry draft. Confirm them with the director before launch.
8. Submit `sitemap.xml` in Google Search Console and Bing Webmaster Tools, and link the Google Business Profile to the site.

Images are hotlinked from Unsplash (free licence, served by Unsplash's CDN with automatic WebP/AVIF). Flags come from flagcdn.com.
