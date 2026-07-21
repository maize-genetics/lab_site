/* ============================================================
   Lab site — global interactions + shared chrome
   Injects the primary nav and footer (so the six pages stay DRY
   with no build step), then wires theme toggle, mobile nav,
   scroll-spy, reveal, and the genome-track drift.
   Vanilla JS, no dependencies. Works on file://, http.server,
   and GitHub Pages (no fetch of partials).
   ============================================================ */
(function () {
  "use strict";

  /* ---------- shared chrome ---------- */
  var PAGES = [
    { key: "research", href: "research.html", label: "Research" },
    { key: "people", href: "people.html", label: "People" },
    { key: "publications", href: "publications.html", label: "Publications" },
    { key: "tools", href: "tools.html", label: "Tools" },
    { key: "join", href: "join.html", label: "About &amp; Join" }
  ];

  var BRAND_MARK =
    '<svg class="mark" viewBox="0 0 40 40" fill="none" aria-hidden="true">' +
    '<rect x="2" y="17" width="36" height="6" rx="1" fill="#E3A324"/>' +
    '<rect x="6" y="17" width="5" height="6" fill="#16342A"/>' +
    '<rect x="16" y="17" width="5" height="6" fill="#16342A"/>' +
    '<rect x="29" y="17" width="5" height="6" fill="#16342A"/>' +
    '<path d="M20 4 C13 10 13 16 20 17 C27 16 27 10 20 4Z" fill="#6B2C4D"/>' +
    '<path d="M20 36 C13 30 13 24 20 23 C27 24 27 30 20 36Z" fill="#2a4a3a"/>' +
    "</svg>";

  function renderNav(active) {
    var links = PAGES.map(function (p) {
      var cur = p.key === active ? ' aria-current="page"' : "";
      return '<a href="' + p.href + '"' + cur + ">" + p.label + "</a>";
    }).join("");
    return (
      '<div class="nav-wrap" id="siteNav">' +
      '<div class="container nav">' +
      '<a class="brand" href="index.html" aria-label="Lab for Plant Genomic Diversity and Design — home">' +
      BRAND_MARK +
      '<span class="wordmark">' +
      '<span class="name">Lab for Plant Genomic Diversity <b>&amp; Design</b></span>' +
      '<span class="byline">Founding Director · Edward Buckler</span>' +
      "</span></a>" +
      '<div class="nav-right">' +
      '<div class="nav-links" id="navLinks">' + links + "</div>" +
      '<button class="theme-toggle" id="themeToggle" type="button" aria-label="Toggle dark and light mode" aria-pressed="false">' +
      '<span class="track"><span class="thumb"></span></span>' +
      '<span class="lbl" id="themeLabel">Light</span></button>' +
      '<button class="mobile-toggle" id="mobileToggle" aria-label="Toggle navigation">Menu</button>' +
      "</div></div></div>"
    );
  }

  function renderFooter() {
    var explore = PAGES.map(function (p) {
      return '<a href="' + p.href + '">' + p.label + "</a>";
    }).join("");
    return (
      '<div class="wrap">' +
      '<div class="foot-grid">' +
      '<div class="foot-brand">' +
      '<div class="name">Lab for Plant Genomic Diversity &amp; Design</div>' +
      "<p>Maize genetics, computational biology, and the design of sustainable crops. " +
      "A multi-PI team across USDA-ARS, Cornell University, the Boyce Thompson Institute, " +
      "and the University of Florida.</p>" +
      '<p class="heritage">Formerly the Buckler Lab · maizegenetics.net</p></div>' +
      "<div><h4>Explore</h4>" + explore + "</div>" +
      '<div><h4>Contact</h4><p>175 Biotechnology Building<br>Ithaca, NY 14853-2703<br><br>' +
      '607-255-1809<br>sara.miller@cornell.edu</p></div></div>' +
      '<div class="foot-bottom">' +
      '<p>© <span id="yr"></span> Lab for Plant Genomic Diversity &amp; Design · USDA-ARS · Cornell · BTI · UF</p>' +
      '<div class="foot-social">' +
      '<a href="https://www.youtube.com/channel/UCS1SdXlyMI1OsSf5yA_oFqw" target="_blank" rel="noopener" aria-label="YouTube"><svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><path d="M23 12s0-3.8-.5-5.6a2.9 2.9 0 0 0-2-2C18.7 4 12 4 12 4s-6.7 0-8.5.4a2.9 2.9 0 0 0-2 2C1 8.2 1 12 1 12s0 3.8.5 5.6a2.9 2.9 0 0 0 2 2C5.3 20 12 20 12 20s6.7 0 8.5-.4a2.9 2.9 0 0 0 2-2C23 15.8 23 12 23 12zM10 15.5v-7l6 3.5-6 3.5z"/></svg></a>' +
      '<a href="https://twitter.com/EdBuckler" target="_blank" rel="noopener" aria-label="Twitter / X"><svg width="15" height="15" viewBox="0 0 24 24" fill="currentColor"><path d="M18.9 2H22l-7.6 8.7L23.3 22h-7l-5.5-7.2L4.5 22H1.4l8.1-9.3L.9 2h7.2l5 6.6L18.9 2zm-1.2 18h1.9L7.1 4H5.1l12.6 16z"/></svg></a>' +
      '<a href="https://www.facebook.com/Buckler-Lab-199945150087322/" target="_blank" rel="noopener" aria-label="Facebook"><svg width="15" height="15" viewBox="0 0 24 24" fill="currentColor"><path d="M22 12a10 10 0 1 0-11.6 9.9v-7H7.9V12h2.5V9.8c0-2.5 1.5-3.9 3.8-3.9 1.1 0 2.2.2 2.2.2v2.5h-1.3c-1.2 0-1.6.8-1.6 1.6V12h2.8l-.4 2.9h-2.4v7A10 10 0 0 0 22 12z"/></svg></a>' +
      '<a href="https://scholar.google.com/citations?user=M7O1p6oAAAAJ&hl=en" target="_blank" rel="noopener" aria-label="Google Scholar"><svg width="15" height="15" viewBox="0 0 24 24" fill="currentColor"><path d="M12 2 1 8l11 6 9-4.9V16h2V8L12 2zM5 13.2V17c0 1.7 3.1 3 7 3s7-1.3 7-3v-3.8l-7 3.8-7-3.8z"/></svg></a>' +
      "</div></div></div>"
    );
  }

  function renderChrome() {
    var active = document.body.getAttribute("data-page") || "";
    var navSlot = document.getElementById("site-nav");
    if (navSlot) navSlot.innerHTML = renderNav(active);
    var footSlot = document.getElementById("site-footer");
    if (footSlot) footSlot.innerHTML = renderFooter();
  }

  renderChrome();

  /* ---- keep anchor offset in sync with whichever bar stays pinned ---- */
  (function () {
    var secNav = document.querySelector(".section-nav");
    var primary = document.querySelector(".nav-wrap");
    var pinned = secNav || primary; // section-nav on home, primary nav elsewhere
    if (pinned) {
      document.documentElement.style.scrollPaddingTop = (pinned.offsetHeight + 12) + "px";
    }
  })();

  /* ---- year ---- */
  var yr = document.getElementById("yr");
  if (yr) yr.textContent = new Date().getFullYear();

  /* ---- theme toggle (persisted) ---- */
  var themeToggle = document.getElementById("themeToggle");
  var themeLabel = document.getElementById("themeLabel");
  function applyTheme(dark) {
    document.body.classList.toggle("theme-dark", dark);
    if (themeToggle) themeToggle.setAttribute("aria-pressed", String(dark));
    if (themeLabel) themeLabel.textContent = dark ? "Dark" : "Light";
  }
  var stored = null;
  try { stored = localStorage.getItem("lab-theme"); } catch (e) {}
  var prefersDark = window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches;
  applyTheme(stored ? stored === "dark" : prefersDark);
  if (themeToggle) {
    themeToggle.addEventListener("click", function () {
      var dark = !document.body.classList.contains("theme-dark");
      applyTheme(dark);
      try { localStorage.setItem("lab-theme", dark ? "dark" : "light"); } catch (e) {}
    });
  }

  /* ---- mobile nav ---- */
  var mobileToggle = document.getElementById("mobileToggle");
  var navLinks = document.getElementById("navLinks");
  if (mobileToggle && navLinks) {
    mobileToggle.addEventListener("click", function () {
      navLinks.classList.toggle("open");
    });
    navLinks.querySelectorAll("a").forEach(function (a) {
      a.addEventListener("click", function () { navLinks.classList.remove("open"); });
    });
  }

  /* ---- scroll-spy: section links + floating dots (home only) ---- */
  var sectionLinks = document.querySelectorAll("[data-section-link]");
  var floatDots = document.querySelectorAll("[data-float-section]");
  var sections = [];
  document.querySelectorAll("[data-spy-section]").forEach(function (s) { sections.push(s); });

  function setActive(hash) {
    sectionLinks.forEach(function (l) {
      l.classList.toggle("active", l.getAttribute("data-section-link") === hash);
    });
    floatDots.forEach(function (d) {
      d.classList.toggle("active", d.getAttribute("data-float-section") === hash);
    });
  }

  if ("IntersectionObserver" in window && sections.length) {
    var spy = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) setActive("#" + e.target.id);
      });
    }, { rootMargin: "-45% 0px -50% 0px", threshold: 0 });
    sections.forEach(function (s) { spy.observe(s); });
  }

  /* ---- reveal on scroll ---- */
  if ("IntersectionObserver" in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) { e.target.classList.add("in"); io.unobserve(e.target); }
      });
      // threshold 0 (not a fraction): an element taller than the viewport — e.g.
      // the ~140-row people timeline — can never reach a fractional threshold,
      // so it would never reveal. rootMargin keeps the "reveal on scroll" feel.
    }, { threshold: 0, rootMargin: "0px 0px -60px 0px" });
    document.querySelectorAll(".reveal").forEach(function (el) { io.observe(el); });
  } else {
    document.querySelectorAll(".reveal").forEach(function (el) { el.classList.add("in"); });
  }

  /* ---- genome-track drift ---- */
  (function () {
    if (window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;
    var g = document.querySelector(".drift");
    if (!g) return;
    var x = 0;
    function tick() {
      x = (x - 0.25) % 1440;
      g.setAttribute("transform", "translate(" + x + ",0)");
      requestAnimationFrame(tick);
    }
    requestAnimationFrame(tick);
  })();
})();
