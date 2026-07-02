/* ============================================================
   Lab landing — global interactions
   Theme toggle, mobile nav, scroll-spy, reveal, track drift.
   Vanilla JS, no dependencies.
   ============================================================ */
(function () {
  "use strict";

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

  /* ---- scroll-spy: section links + floating dots ---- */
  var sectionLinks = document.querySelectorAll("[data-section-link]");
  var floatDots = document.querySelectorAll("[data-float-section]");
  var ids = ["#top", "#research", "#institutions", "#papers", "#tools", "#news", "#join"];
  var sections = ids
    .map(function (id) { return document.querySelector(id); })
    .filter(Boolean);

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
    }, { threshold: 0.12 });
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
