() => {
  const W = document.documentElement.clientWidth, out = [];
  for (const el of document.querySelectorAll("body *")) {
    const r = el.getBoundingClientRect();
    if (r.right > W + 0.5 && r.width > 0) {
      let p = el.parentElement, clipped = false;
      while (p) { const o = getComputedStyle(p).overflowX; if (o === "auto" || o === "hidden" || o === "scroll") { clipped = true; break; } p = p.parentElement; }
      if (!clipped) out.push(el.tagName + "." + (typeof el.className === "string" ? el.className : "") + "#" + el.id + " right=" + Math.round(r.right) + " w=" + Math.round(r.width) + " :: " + (el.textContent || "").trim().slice(0, 50));
    }
  }
  return "clientWidth=" + W + " scrollWidth=" + document.documentElement.scrollWidth + "\n" + out.slice(0, 40).join("\n");
}
