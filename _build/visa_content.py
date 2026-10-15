"""Visa page data. Edit here, then run: python3 _build/build.py

Each destination: (country, flag code, type, typical processing, stay / validity, note)
type = "e-visa" | "sticker" | "on-arrival" | "visa-free"
Rules for Indian passport holders change often — review this list every few months.
"""

UPDATED = "October 2026"

VISAS = [
    # --- Middle East
    ("United Arab Emirates (Dubai)", "ae", "e-visa", "3–5 working days", "30 or 60 days", "Tourist e-visa; visa on arrival if you hold a valid US, UK or EU visa / residence."),
    ("Saudi Arabia", "sa", "e-visa", "1–3 working days", "Up to 90 days", "Umrah & tourist e-visa; Nusuk registration for Umrah."),
    ("Oman", "om", "e-visa", "3–5 working days", "Up to 30 days", "Tourist e-visa."),
    ("Qatar", "qa", "visa-free", "On arrival", "Up to 30 days", "Visa waiver with return ticket and hotel booking."),
    ("Bahrain", "bh", "e-visa", "3–5 working days", "Up to 14 / 30 days", "Tourist e-visa."),
    ("Jordan", "jo", "on-arrival", "On arrival", "Up to 30 days", "Visa on arrival; Jordan Pass recommended."),
    ("Egypt", "eg", "e-visa", "5–7 working days", "Up to 30 days", "Tourist e-visa."),
    ("Türkiye", "tr", "sticker", "10–15 working days", "Up to 30 days", "Sticker visa; e-visa if you hold a valid US, UK or Schengen visa."),
    ("Azerbaijan", "az", "e-visa", "3 working days", "Up to 30 days", "ASAN e-visa."),
    ("Georgia", "ge", "e-visa", "5–7 working days", "Up to 30 days", "Tourist e-visa."),
    ("Uzbekistan", "uz", "e-visa", "3 working days", "Up to 30 days", "Tourist e-visa."),
    # --- Asia
    ("Thailand", "th", "visa-free", "On arrival", "As per current exemption", "Visa exemption for Indian tourists — we confirm the latest rule before you fly."),
    ("Malaysia", "my", "visa-free", "On arrival", "Up to 30 days", "Visa-free entry; MDAC arrival card required."),
    ("Singapore", "sg", "e-visa", "3–5 working days", "Up to 30 days", "Tourist e-visa through an authorised agent."),
    ("Indonesia (Bali)", "id", "on-arrival", "On arrival / e-VOA", "Up to 30 days", "e-VOA online or visa on arrival; Bali tourist levy extra."),
    ("Vietnam", "vn", "e-visa", "3–5 working days", "Up to 90 days", "Single or multiple-entry e-visa."),
    ("Sri Lanka", "lk", "e-visa", "1–2 working days", "Up to 30 days", "ETA (electronic travel authorisation)."),
    ("Maldives", "mv", "visa-free", "On arrival", "Up to 30 days", "Free visa on arrival with hotel booking."),
    ("Nepal", "np", "visa-free", "No visa", "—", "No visa for Indians; carry passport or voter ID."),
    ("Bhutan", "bt", "visa-free", "Entry permit", "As per permit", "Entry permit on arrival; Sustainable Development Fee applies."),
    ("Cambodia", "kh", "e-visa", "3 working days", "Up to 30 days", "Tourist e-visa."),
    ("Philippines", "ph", "visa-free", "On arrival", "Up to 14 days", "Visa-free for short tourism stays; longer stays need a visa."),
    ("Japan", "jp", "e-visa", "5–7 working days", "Up to 90 days", "Japan eVISA, applied through an accredited agent."),
    ("South Korea", "kr", "sticker", "5–7 working days", "Up to 90 days", "Sticker visa through the visa centre."),
    ("China", "cn", "sticker", "4–7 working days", "As per visa", "Sticker visa with biometrics."),
    ("Hong Kong", "hk", "visa-free", "Online pre-registration", "Up to 14 days", "Free pre-arrival registration (PAR) online."),
    ("Taiwan", "tw", "e-visa", "5–7 working days", "Up to 30 days", "e-visa / online travel authorisation for eligible travellers."),
    ("Bangladesh", "bd", "sticker", "5–7 working days", "As per visa", "Sticker visa."),
    ("Kazakhstan", "kz", "visa-free", "On arrival", "Up to 14 days", "Visa-free for short stays."),
    # --- Europe
    ("Schengen (Europe)", "eu", "sticker", "15 working days", "Up to 90 days", "One visa for 29 European countries; biometrics at VFS / BLS."),
    ("France", "fr", "sticker", "15 working days", "Up to 90 days", "Schengen visa."),
    ("Switzerland", "ch", "sticker", "15 working days", "Up to 90 days", "Schengen visa."),
    ("Italy", "it", "sticker", "15 working days", "Up to 90 days", "Schengen visa."),
    ("Germany", "de", "sticker", "15 working days", "Up to 90 days", "Schengen visa."),
    ("Spain", "es", "sticker", "15 working days", "Up to 90 days", "Schengen visa."),
    ("Netherlands", "nl", "sticker", "15 working days", "Up to 90 days", "Schengen visa."),
    ("Greece", "gr", "sticker", "15 working days", "Up to 90 days", "Schengen visa."),
    ("United Kingdom", "gb", "sticker", "15 working days", "Up to 6 months", "Standard visitor visa; priority service available."),
    ("Russia", "ru", "e-visa", "4–7 days", "Up to 16 days", "Unified e-visa."),
    # --- Americas, Africa, Oceania
    ("United States", "us", "sticker", "Interview-based", "Up to 10 years (B1/B2)", "DS-160, fee and interview — wait times vary by city."),
    ("Canada", "ca", "sticker", "4–8 weeks", "Up to 10 years", "Visitor visa with biometrics."),
    ("Australia", "au", "e-visa", "15–30 days", "Up to 12 months", "Visitor visa (subclass 600), applied online."),
    ("New Zealand", "nz", "e-visa", "20–30 days", "Up to 9 months", "Visitor visa, applied online."),
    ("South Africa", "za", "sticker", "10–15 working days", "Up to 90 days", "Sticker visa through VFS."),
    ("Kenya", "ke", "e-visa", "3 working days", "Up to 90 days", "eTA (electronic travel authorisation)."),
    ("Tanzania", "tz", "e-visa", "5–10 working days", "Up to 90 days", "Tourist e-visa."),
    ("Morocco", "ma", "e-visa", "3–5 working days", "Up to 30 days", "e-visa if you hold a valid US, UK or Schengen visa; otherwise sticker."),
    ("Mauritius", "mu", "visa-free", "On arrival", "Up to 60 days", "Visa-free for tourists."),
    ("Seychelles", "sc", "visa-free", "On arrival", "Up to 30 days", "Visitor permit on arrival; online travel authorisation."),
]

TYPE_LABEL = {"e-visa": "e-Visa", "sticker": "Sticker visa", "on-arrival": "Visa on arrival", "visa-free": "Visa-free"}

VISA_TYPES = ["Tourist", "Business", "Umrah / Hajj", "Family / Visit", "Student", "Transit", "Work permit"]

FAQS = [
    ("Which visas does Sahaba Travels help with?", "Tourist, business, Umrah, family-visit, student and transit visas for 45+ destinations, including Dubai, Saudi Arabia, Schengen, the UK, the USA, Canada, Australia and Asia."),
    ("What documents are usually needed?", "A passport valid for at least 6 months with two blank pages, recent photos, bank statements for the last 3–6 months, income tax returns or salary slips, a cover letter, flight and hotel bookings, and travel insurance where required. We send a destination-specific checklist."),
    ("How long does a visa take?", "e-visas usually take 1–7 working days, Schengen and UK visas about 15 working days, and US visas depend on interview availability. Apply at least 3–4 weeks before travel; earlier in peak season."),
    ("Can Sahaba guarantee a visa?", "No agent can guarantee a visa; the decision is the embassy’s. We make sure your file is complete and correct, which gives you the best chance of approval."),
    ("Are visa fees refundable if the visa is refused?", "Embassy fees and service charges are non-refundable once an application is submitted, whatever the outcome. See our Cancellation & Refund Policy."),
    ("Do you offer doorstep document pickup in Mumbai?", "Yes. We can collect documents and deliver passports across Mumbai on request."),
]

DOCS = [
    ("passport", "Passport", "Valid 6+ months from return, 2 blank pages, old passports if any"),
    ("camera", "Photographs", "Recent photos to the embassy’s size and background rules"),
    ("building-columns", "Financials", "Bank statements (3–6 months), ITRs or salary slips"),
    ("file-lines", "Cover letter & forms", "Purpose of travel, itinerary and signed application form"),
    ("plane-departure", "Bookings", "Return flight reservation and hotel booking"),
    ("shield-heart", "Insurance", "Travel medical insurance (mandatory for Schengen)"),
]
