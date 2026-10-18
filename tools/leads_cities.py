#!/usr/bin/env python3
"""Per-city settings for the construction cleaning leads products: the members' app (tools/leads_app.py) and the workbook
(tools/leads_xlsx.py) are one code base, and everything that differs by city lives here, so the Legal desk reads one file.

Chicago's values are the exact strings the Chicago product shipped with before this file existed (Oct 18, 2026), so its
app and workbook do not change. Austin's data disclaimer is the City of Austin's own text, word for word, from the Issued
Construction Permits dataset description (permits/austin/source-terms.txt); its terms page is the City of Austin Open Data
Terms of Use.

city(key) returns the settings; for_source(source) picks the city from a list's source block.
"""

CHICAGO = {
    "key": "chicago",
    "city": "Chicago", "state": "IL",
    "product": "Chicago Construction Cleaning Leads",
    "slug": "chicago-construction-cleaning-leads",
    "members": "chicago-leads-members",
    "freePage": "https://proofnotfluff.com/chicago-construction-cleaning-leads/",
    "csvPrefix": "chicago-leads",
    "storageKey": "pnf-ccl-v1",
    "center": [41.88, -87.66], "zoom": 11,
    "cityName": "City of Chicago",
    "records": "City of Chicago permit records",
    "sourceLabel": "City of Chicago Data Portal, Building Permits",
    "disclaimer": ("This site provides applications using data that has been modified for use from its original source, "
                   "www.cityofchicago.org, the official website of the City of Chicago. The City of Chicago makes no claims "
                   "as to the content, accuracy, timeliness, or completeness of any of the data provided at this site. The "
                   "data provided at this site is subject to change at any time. It is understood that the data provided at "
                   "this site is being used at one's own risk."),
    "termsLabel": "City of Chicago Data Terms of Use",
    "termsUrl": "https://www.chicago.gov/city/en/narr/foia/data_disclaimer.html",
    "record": "https://data.cityofchicago.org/resource/ydr8-5enu.json?permit_=",
    # areas, money, permits
    "area": "Community area", "areaLower": "community area", "areaAll": "All community areas", "areaPlural": "community areas",
    "cost": "Reported cost", "costLower": "reported cost", "costShort": "reported",
    "permit": "Permit", "permitLower": "permit",
    "types": ["New construction", "Renovation"],
    # stages: closest to a final clean first
    "stages": ["Partial occupancy approved", "Inspections under way", "Permit issued"],
    "stagesShort": ["Near finish", "Inspections", "Permit issued"],
    "stageLines": ["The City approved partial or temporary occupancy: part of the building is cleared for use, so the final clean is close.",
                   "City inspections have started. The final clean usually comes after the last inspections.",
                   "The permit is issued and work can start. The City has not logged inspections yet."],
    "nearMatch": ("OCCUPANCY PENDING", "PARTIAL OCCUPANCY"),
    "contacts": True,
    # the members' app footer and gate: the City's disclaimer word for word, then ours
    "legal": ("Public City of Chicago permit records, as of __ASOF__. This site provides applications using data that has been modified "
              "for use from its original source, www.cityofchicago.org, the official website of the City of Chicago. The City of Chicago "
              "makes no claims as to the content, accuracy, timeliness, or completeness of any of the data provided at this site. The data "
              "provided at this site is subject to change at any time. It is understood that the data provided at this site is being used "
              "at one's own risk. ProofNotFluff is not affiliated with or endorsed by the City of Chicago, and no builder listed has "
              "endorsed or works with ProofNotFluff. Builder contacts come from each builder's own website, not the City. You make your "
              "own calls and emails and are responsible for following the law when you do. Licensed to one business for its own "
              "prospecting; no reselling or republishing. Provided as is, without warranties of any kind, to the extent the law allows, and "
              "ProofNotFluff's total liability for any claim is limited to the amount you paid for the most recent month of your membership. "
              "Made with AI assistance. Read the full Terms of Use (also on the Terms tab of the Excel file)."),
    "notice": ("For general business information only. Projects appear because their permits are public City of Chicago "
               "records; no builder listed here has endorsed or works with ProofNotFluff, and a listing is not an "
               "invitation to bid. Reported cost is the figure the applicant filed for the permit, not a contract value. "
               "You make your own calls and emails, and you are responsible for following the law when you do. "
               "ProofNotFluff never contacts builders or anyone else on your behalf."),
    "termsVersion": "Version 2",
    # members' app words
    "gateSub": "Projects close to a final clean, the builder on each, and the builder's office phone or email where their own website lists one.",
    "nearEmpty": "No project has partial occupancy approved this week. Projects with inspections under way are the next closest.",
    "midWords": "with inspections under way",
    "totalWord": "total reported",
    "leaveList": "Projects leave the list when the City marks the permit complete, and builders leave with their projects.",
    "noGeo": "no map location in the City record",
}

AUSTIN_DISCLAIMER = (
    "Austin Development Services Data Disclaimer: 1. The data provided are for informational use only and may differ from official "
    "department data. 2. Austin Development Services’ database is continuously updated, so reports run at different times may produce "
    "different results. Care should be taken when comparing against other reports as different data collection methods and different "
    "data sources may have been used. 3. Austin Development Services does not assume any liability for any decision made or action "
    "taken or not taken by the recipient in reliance upon any information or data provided.")

AUSTIN = {
    "key": "austin",
    "city": "Austin", "state": "TX",
    "product": "Austin Construction Cleaning Leads",
    "slug": "austin-construction-cleaning-leads",
    "members": "austin-leads-members",
    "freePage": "https://proofnotfluff.com/austin-construction-cleaning-leads/",
    "csvPrefix": "austin-leads",
    "storageKey": "pnf-acl-v1",
    "center": [30.29, -97.74], "zoom": 11,
    "cityName": "City of Austin",
    "records": "City of Austin permit records",
    "sourceLabel": "City of Austin, Issued Construction Permits",
    "attribution": "City of Austin, Texas - data.austintexas.gov",
    "disclaimer": AUSTIN_DISCLAIMER,
    "termsLabel": "City of Austin Open Data Terms of Use",
    "termsUrl": "https://data.austintexas.gov/stories/s/ranj-cccq",
    "record": "https://data.austintexas.gov/resource/3syk-w9eu.json?masterpermitnum=",
    "area": "ZIP code", "areaLower": "ZIP code", "areaAll": "All ZIP codes", "areaPlural": "ZIP codes",
    "cost": "Valuation", "costLower": "valuation", "costShort": "in valuation",
    "permit": "Master permit", "permitLower": "master permit",
    "types": ["New construction", "Finish-out", "Remodel or addition"],
    "stages": ["Some permits finaled", "Work under way", "Permit issued"],
    "stagesShort": ["Near finish", "Under way", "Permit issued"],
    "stageLines": ["At least one of this project's building permits is marked Final by the City while others are still active, so parts of "
                   "the project are done and final cleans are under way or close.",
                   "The City has pushed a building permit's expiry date past the first 180 days, which it does when an inspection passes "
                   "or an extension is granted. The final clean usually comes after the last inspections.",
                   "The building permits are issued and work can start. The City has not extended or finaled any of them yet."],
    "nearMatch": ("SOME PERMITS FINALED",),
    "contacts": False,
    "legal": ("Public City of Austin permit records, as of __ASOF__. Source: City of Austin, Texas - data.austintexas.gov, used under the "
              "City of Austin Open Data Terms of Use and modified by ProofNotFluff (filtered, grouped into projects and shortened). "
              + AUSTIN_DISCLAIMER + " ProofNotFluff is not affiliated with or endorsed by the City of Austin, and no builder listed has "
              "endorsed or works with ProofNotFluff. You make your own calls and emails and are responsible for following the law when "
              "you do. Licensed to one business for its own prospecting; no reselling or republishing. Provided as is, without warranties "
              "of any kind, to the extent the law allows, and ProofNotFluff's total liability for any claim is limited to the amount you "
              "paid for the most recent month of your membership. Made with AI assistance. Read the full Terms of Use (also on the Terms "
              "tab of the Excel file)."),
    "notice": ("For general business information only. Projects appear because their building permits are public City of Austin "
               "records; no builder listed here has endorsed or works with ProofNotFluff, and a listing is not an invitation to bid. "
               "Valuation is the largest valuation filed on the project's City building permits, not a contract value or a budget. "
               "You make your own calls and emails, and you are responsible for following the law when you do. "
               "ProofNotFluff never contacts builders or anyone else on your behalf."),
    "termsVersion": "Version 1",
    "gateSub": "Open projects close to a final clean and the general contractor the City lists on each, from City of Austin permit records.",
    "nearEmpty": "No project has a building permit finaled this week. Projects with work under way are the next closest.",
    "midWords": "with work under way",
    "totalWord": "total valuation",
    "leaveList": "Projects leave the list when the City finals or closes all their building permits, and builders leave with their projects.",
    "noGeo": "no map location in the City record or from the Census geocoder",
}

CITIES = {"chicago": CHICAGO, "austin": AUSTIN}


def city(key):
    return CITIES[(key or "chicago").lower()]


def for_source(source):
    """The city of a list, read from its source block (Austin's names the City of Austin)."""
    s = " ".join(str((source or {}).get(k, "")) for k in ("name", "url"))
    return AUSTIN if "austin" in s.lower() else CHICAGO
