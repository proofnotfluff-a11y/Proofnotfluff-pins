/* ProofNotFluff site behaviors (store v2, Oct 24, 2026). Loaded with defer on every page; every part is optional:
   without this file every page still shows all of its content and every link still works.
   1. Header: slims and gets a frosted background once the page scrolls.
   2. Quick-find: press / or Ctrl/Cmd+K, or tap Search, to find any calculator, lead list or guide (assets/search.json,
      fetched only when the search first opens).
   3. Calculator catalog (/calculators/): instant search with synonyms and category chips.
   4. On-this-page bar: highlights the section in view on long pages (.otp).
   Motion lives in pnf.css and is off under prefers-reduced-motion. */
(function () {
  "use strict";
  var doc = document, root = doc.documentElement;
  var me = doc.currentScript || doc.querySelector('script[src*="pnf-ui.js"]');
  var base = me ? new URL("..", me.src).href : "/";   // the site root, from this file's own address

  function onReady(fn) { if (doc.readyState !== "loading") fn(); else doc.addEventListener("DOMContentLoaded", fn); }
  function href(s) { return /^https?:/.test(s) ? s : base + s; }
  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); }
  function norm(s) { return String(s || "").toLowerCase().replace(/[^a-z0-9+&$ ]+/g, " ").replace(/\s+/g, " ").trim(); }
  // every typed word must start some word of the entry (so "pres wash" finds pressure washing)
  function matches(hay, words) {
    if (!words.length) return true;
    var list = " " + hay;
    for (var i = 0; i < words.length; i++) if (list.indexOf(" " + words[i]) < 0) return false;
    return true;
  }

  onReady(function () {
    /* 1. header */
    var head = doc.querySelector("header.top");
    if (head) {
      var last = null;
      var tick = function () { var on = window.scrollY > 8; if (on !== last) { head.classList.toggle("scrolled", on); last = on; } };
      window.addEventListener("scroll", tick, { passive: true }); tick();
    }

    /* 2. quick-find */
    var btns = doc.querySelectorAll("[data-qf]");
    var dlg = null, input, list, status, index = null, items = [], sel = -1, opener = null;
    function load(cb) {
      if (index) return cb();
      fetch(base + "assets/search.json").then(function (r) { return r.json(); }).then(function (d) {
        index = d.map(function (x) { x.h = norm(x.t + " " + x.g + " " + x.d + " " + x.k); return x; }); cb();
      }).catch(function () { index = []; status.textContent = "Search could not load. Try the menu links instead."; });
    }
    function titleHits(x, words) { var tt = " " + norm(x.t), n = 0; words.forEach(function (w) { if (tt.indexOf(" " + w) >= 0) n++; }); return n; }
    function render() {
      var words = norm(input.value).split(" ").filter(Boolean);
      var order = { "Lead list": 0, "Calculator": 1, "Guide": 2, "Workbook": 3, "Page": 4 };
      items = (index || []).filter(function (x) { return matches(x.h, words); })
        .sort(function (a, b) {   // more typed words in the title first, then lists, calculators, guides
          return (titleHits(b, words) - titleHits(a, words)) || (order[a.g] - order[b.g]);
        }).slice(0, words.length ? 12 : 8);
      sel = items.length ? 0 : -1;
      list.innerHTML = items.map(function (x, i) {
        return '<li role="option" id="qf-o' + i + '"' + (i === sel ? ' aria-selected="true"' : "") + '><a href="' + esc(href(x.s)) + '" tabindex="-1">'
          + '<span class="qf-g">' + esc(x.g) + '</span><b>' + esc(x.t) + '</b><span class="qf-d">' + esc(x.d) + "</span></a></li>";
      }).join("");
      input.setAttribute("aria-activedescendant", sel >= 0 ? "qf-o" + sel : "");
      status.classList.toggle("qf-none", !items.length);
      status.textContent = items.length ? (words.length ? items.length + (items.length === 1 ? " match" : " matches") : "Popular") :
        "Nothing matches. Try a trade (cleaning, pest, junk), a platform (Amazon, Etsy) or a word like price or rate.";
    }
    function move(d) {
      if (!items.length) return;
      var old = list.children[sel]; if (old) old.removeAttribute("aria-selected");
      sel = (sel + d + items.length) % items.length;
      var li = list.children[sel]; li.setAttribute("aria-selected", "true"); li.scrollIntoView({ block: "nearest" });
      input.setAttribute("aria-activedescendant", "qf-o" + sel);
    }
    function build() {
      dlg = doc.createElement("dialog");
      dlg.className = "qf"; dlg.setAttribute("aria-label", "Search ProofNotFluff");
      dlg.innerHTML = '<div class="qf-box"><label class="qf-in"><span class="sr">Search calculators, lead lists and guides</span>'
        + '<svg aria-hidden="true" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></svg>'
        + '<input type="search" role="combobox" aria-expanded="true" aria-controls="qfList" aria-autocomplete="list" placeholder="Search calculators, lead lists, guides" autocomplete="off" enterkeyhint="go"></label>'
        + '<button type="button" class="qf-x" aria-label="Close search">Esc</button>'
        + '<p class="qf-s" aria-live="polite"></p><ul class="qf-list" id="qfList" role="listbox" aria-label="Results"></ul>'
        + '<p class="qf-foot"><span><kbd>&uarr;</kbd><kbd>&darr;</kbd> to move</span><span><kbd>Enter</kbd> to open</span></p></div>';
      doc.body.appendChild(dlg);
      input = dlg.querySelector("input"); list = dlg.querySelector(".qf-list"); status = dlg.querySelector(".qf-s");
      input.addEventListener("input", render);
      input.addEventListener("keydown", function (e) {
        if (e.key === "ArrowDown") { e.preventDefault(); move(1); }
        else if (e.key === "ArrowUp") { e.preventDefault(); move(-1); }
        else if (e.key === "Enter" && sel >= 0) { e.preventDefault(); location.href = href(items[sel].s); }
      });
      dlg.querySelector(".qf-x").addEventListener("click", function () { dlg.close(); });
      dlg.addEventListener("click", function (e) { if (e.target === dlg) dlg.close(); });
      dlg.addEventListener("close", function () { root.classList.remove("qf-open"); if (opener) opener.focus(); });
    }
    function open(from) {
      if (!dlg) build();
      opener = from || doc.activeElement;
      if (typeof dlg.showModal === "function") dlg.showModal(); else dlg.setAttribute("open", "");
      root.classList.add("qf-open");
      input.value = ""; input.focus();
      load(render);
    }
    btns.forEach(function (b) { b.hidden = false; b.addEventListener("click", function () { open(b); }); });
    if (btns.length) doc.addEventListener("keydown", function (e) {
      var t = e.target, typing = t && (t.tagName === "INPUT" || t.tagName === "TEXTAREA" || t.tagName === "SELECT" || t.isContentEditable);
      if (((e.key === "k" || e.key === "K") && (e.metaKey || e.ctrlKey)) || (e.key === "/" && !typing && !doc.getElementById("cxQ"))) {
        e.preventDefault(); open(null);
      }
    });

    /* 3. calculator catalog */
    var q = doc.getElementById("cxQ");
    if (q) {
      var bar = doc.getElementById("cxBar"), all = doc.getElementById("cxAll"), empty = doc.getElementById("cxEmpty"), count = doc.getElementById("cxCount");
      var chips = [].slice.call(doc.querySelectorAll(".cx-chip")), cards = [].slice.call(doc.querySelectorAll("#cxAll .cx-group .cx-item"));
      var groups = [].slice.call(doc.querySelectorAll("#cxAll .cx-group")), start = doc.querySelector(".cx-start");
      var g = "", total = cards.length;
      bar.hidden = false;
      var run = function () {
        var words = norm(q.value).split(" ").filter(Boolean), n = 0;
        cards.forEach(function (c) { var ok = (!g || c.dataset.g === g) && matches(norm(c.dataset.k), words); c.hidden = !ok; if (ok) n++; });
        groups.forEach(function (s) { s.hidden = !s.querySelector(".cx-item:not([hidden])"); });
        if (start) start.hidden = !!(words.length || g);
        empty.hidden = n > 0;
        chips.forEach(function (b) {   // live counts per chip for the current words
          var gg = b.dataset.g, c = 0;
          cards.forEach(function (card) { if ((!gg || card.dataset.g === gg) && matches(norm(card.dataset.k), words)) c++; });
          var s = b.querySelector("span"); if (s) s.textContent = c;
        });
        count.textContent = words.length || g ? "Showing " + n + " of " + total + " calculators" : total + " calculators";
        try { var u = new URL(location.href); if (q.value) u.searchParams.set("q", q.value); else u.searchParams.delete("q"); if (g) u.searchParams.set("cat", g); else u.searchParams.delete("cat"); history.replaceState(null, "", u); } catch (e) {}
      };
      q.addEventListener("input", run);
      chips.forEach(function (b) {
        b.addEventListener("click", function () { g = b.dataset.g; chips.forEach(function (x) { x.setAttribute("aria-pressed", String(x === b)); }); run(); });
      });
      doc.getElementById("cxClear").addEventListener("click", function () { q.value = ""; g = ""; chips.forEach(function (x, i) { x.setAttribute("aria-pressed", String(i === 0)); }); run(); q.focus(); });
      doc.addEventListener("keydown", function (e) {
        var t = e.target; if (e.key === "/" && t !== q && !(t && (t.tagName === "INPUT" || t.tagName === "TEXTAREA"))) { e.preventDefault(); q.focus(); }
      });
      try {
        var sp = new URL(location.href).searchParams, p = sp.get("q"), pc = sp.get("cat");
        if (p) q.value = p;
        if (pc) chips.forEach(function (x) { if (x.dataset.g === pc) { g = pc; } x.setAttribute("aria-pressed", String(x.dataset.g === (g || ""))); });
      } catch (e) {}
      run();
    }

    /* 5. hero records roll: a Pause button (WCAG 2.2.2), only where the roll actually moves */
    var hf = doc.querySelector(".hf"), hp = hf && doc.querySelector(".hf-pause");
    if (hp && !matchMedia("(prefers-reduced-motion: reduce)").matches) {
      hp.hidden = false;
      hp.removeAttribute("aria-pressed");
      hp.addEventListener("click", function () { var on = !hf.classList.contains("paused"); hf.classList.toggle("paused", on); hp.textContent = on ? "Play" : "Pause"; });
    }

    /* 4. on-this-page bar: mark the section in view */
    var otp = doc.querySelector(".otp");
    if (otp && "IntersectionObserver" in window) {
      var links = [].slice.call(otp.querySelectorAll('a[href^="#"]')), seen = {};
      var secs = links.map(function (a) { return doc.getElementById(a.getAttribute("href").slice(1)); });
      var io = new IntersectionObserver(function (es) {
        es.forEach(function (e) { seen[e.target.id] = e.isIntersecting; });
        var cur = null;
        for (var i = 0; i < secs.length; i++) if (secs[i] && seen[secs[i].id]) { cur = i; break; }
        if (cur === null) return;
        links.forEach(function (a, i) { if (i === cur) a.setAttribute("aria-current", "true"); else a.removeAttribute("aria-current"); });
        var on = links[cur]; if (on && on.parentNode.scrollWidth > on.parentNode.clientWidth) on.parentNode.scrollTo({ left: on.offsetLeft - 16, behavior: matchMedia("(prefers-reduced-motion: reduce)").matches ? "auto" : "smooth" });
      }, { rootMargin: "-30% 0px -60% 0px" });
      secs.forEach(function (s) { if (s) io.observe(s); });
    }
  });
})();
