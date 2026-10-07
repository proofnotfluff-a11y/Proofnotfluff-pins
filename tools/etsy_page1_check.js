// ProofNotFluff BUYER EVIDENCE check for one Etsy search results page (ledger BUYER EVIDENCE GATE, Oct 7, 2026).
// Run it with the browser's javascript tool on a signed-out https://www.etsy.com/search?q=<phrase> page after it
// loads (one page load, counted toward the run's Etsy page cap). It reads only what the page shows; it clicks nothing.
//
// Listing age comes from the listing id: Etsy ids rise over time, about 575,000 a day in Oct 2026
// (anchor 4590270056 = Oct 7, 2026 07:54 UTC, our own listing #23). Ids under 4,000,000,000 come from before
// Etsy's 2025 id jump and are years old; they show as "old" and always count as older than 180 days.
//
// Verdict:
//   FLOOD   when 40% or more of the page-1 organic (non-ad) listings are under 60 days old: sellers are piling
//           in faster than buyers prove demand. Fail.
//   PROOF   when at least 3 page-1 organic listings carry a buyer badge ("Bestseller", "Popular now") or at
//           least 5 are older than 180 days (they survived because they sell). Needed to pass.
//   ENTRY   when at least 2 page-1 organic listings are under 180 days old: a new listing can still reach page 1.
//   PASS = PROOF and ENTRY and not FLOOD. Anything else is FAIL. Record the whole result on the idea as
//   buyerProof, and say in the idea why our product is different from the badged listings on page 1.
(() => {
  const ANCHOR_ID = 4590270056, ANCHOR_MS = Date.parse("2026-10-07T07:54:00Z"), PER_DAY = 575000;
  const OURS = (window.PNF_OURS || []).map(String);
  const now = Date.now();
  const ageDays = id => id < 4e9 ? 9999 : Math.round((ANCHOR_ID - id) / PER_DAY + (now - ANCHOR_MS) / 864e5);
  const seen = new Set(), rows = [];
  for (const c of document.querySelectorAll("[data-listing-id]")) {
    const id = c.getAttribute("data-listing-id");
    if (!id || seen.has(id)) continue;
    seen.add(id);
    const t = c.innerText || "";
    const ad = /(^|\n|\s)Ad(\s|・|$)|Ad from shop|Ad by/.test(t);
    const badge = (t.match(/Bestseller|Popular now|Etsy's Pick|Star Seller/i) || [""])[0];
    const shop = (t.match(/From shop\s+([A-Za-z0-9]+)/) || [])[1] || "";
    const title = ((c.querySelector("h3,h2") || {}).innerText || "").trim().slice(0, 70);
    rows.push({ pos: rows.length + 1, id: +id, age: ageDays(+id), ad, badge, shop, title, ours: OURS.includes(id) });
  }
  const org = rows.filter(r => !r.ad);
  const n = org.length || 1;
  const under60 = org.filter(r => r.age < 60).length;
  const over180 = org.filter(r => r.age > 180).length;
  const badged = org.filter(r => r.badge).length;
  const flood = under60 / n >= 0.4;
  const proof = badged >= 3 || over180 >= 5;
  const under180 = org.filter(r => r.age < 180).length;
  const entry = under180 >= 2;
  const shops = new Set(org.map(r => r.shop).filter(Boolean)).size;
  return {
    phrase: new URLSearchParams(location.search).get("q"),
    checkedAt: new Date().toISOString(),
    signedIn: !/\bSign in\b/.test(document.body.innerText.slice(0, 400)),
    organic: org.length, ads: rows.length - org.length, shops,
    under60, under60Share: +(under60 / n).toFixed(2), over180, badged,
    under180, flood, proof, entry, verdict: proof && entry && !flood ? "PASS" : "FAIL",
    why: [flood ? `flood: ${under60} of ${org.length} organic listings are under 60 days old` : "",
          !proof ? `no buyer proof: ${badged} badged, ${over180} older than 180 days` : "",
          !entry ? `no entry: only ${under180} page-1 organic listings are under 180 days old` : ""].filter(Boolean).join("; "),
    ours: rows.filter(r => r.ours).map(r => ({ pos: r.pos, id: r.id, ad: r.ad })),
    top: org.slice(0, 12).map(r => `${r.pos}. ${r.age === 9999 ? "old" : r.age + "d"} ${r.badge ? "[" + r.badge + "] " : ""}${r.shop}: ${r.title}`),
  };
})()
