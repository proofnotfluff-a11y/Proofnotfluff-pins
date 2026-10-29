() => {
  const W = document.documentElement.clientWidth, out = [];
  for (const el of document.querySelectorAll("html *")) {
    const r = el.getBoundingClientRect(), cs = getComputedStyle(el);
    const sw = el.scrollWidth, cw = el.clientWidth;
    if (r.right > W + 0.5 || r.left > W || (sw > cw + 1 && cs.overflowX === "visible" && cw > 0)) {
      out.push(el.tagName + "." + (typeof el.className === "string" ? el.className : "") + "#" + el.id + " pos=" + cs.position + " L=" + Math.round(r.left) + " R=" + Math.round(r.right) + " w=" + Math.round(r.width) + " sw=" + sw + " cw=" + cw + " ovx=" + cs.overflowX + " :: " + (el.textContent || "").trim().slice(0, 40));
    }
  }
  return "clientWidth=" + W + " scrollWidth=" + document.documentElement.scrollWidth + " bodySW=" + document.body.scrollWidth + "\n" + out.slice(0, 40).join("\n");
}
