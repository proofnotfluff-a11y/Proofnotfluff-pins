() => {
  const W = document.documentElement.clientWidth, out = [];
  for (const el of document.querySelectorAll("body *")) {
    const r = el.getBoundingClientRect();
    if (r.right > W + 0.5 && r.width > 0) {
      let p = el.parentElement, clip = "";
      while (p && p !== document.body) { const o = getComputedStyle(p).overflowX; if (o !== "visible") { clip = p.tagName + "." + (typeof p.className === "string" ? p.className : ""); break; } p = p.parentElement; }
      const cs = getComputedStyle(el);
      out.push((clip ? "[in " + clip + "] " : "[FREE] ") + el.tagName + "." + (typeof el.className === "string" ? el.className : "") + "#" + el.id + " pos=" + cs.position + " right=" + Math.round(r.right) + " w=" + Math.round(r.width) + " :: " + (el.textContent || "").trim().slice(0, 40));
    }
  }
  const bo = getComputedStyle(document.body).overflowX, ho = getComputedStyle(document.documentElement).overflowX;
  return "clientWidth=" + W + " scrollWidth=" + document.documentElement.scrollWidth + " body=" + bo + " html=" + ho + "\n" + out.filter(x => x.startsWith("[FREE]")).concat(out.filter(x => !x.startsWith("[FREE]"))).slice(0, 30).join("\n");
}
