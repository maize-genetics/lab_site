/* ============================================================
   Lab archive + timeline rendering.
   Reads window.LAB_PUBS / LAB_THEMES (js/publications-data.js),
   window.LAB_PEOPLE (js/people-data.js), and window.LAB_LINES
   (defined inline on research.html). Pure DOM, no dependencies.
   Include AFTER the data files on the pages that need it.
   ============================================================ */
(function () {
  "use strict";

  var NOW_YEAR = new Date().getFullYear();
  var T0 = 1998;                 // timeline origin
  var T1 = Math.max(NOW_YEAR, 2026);

  function esc(s) {
    return String(s == null ? "" : s).replace(/[&<>"]/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c];
    });
  }
  function authorsHTML(a) {
    return esc(a); // no author is bolded (bolding only the PI would be inconsistent)
  }
  function pct(year) {
    var y = year === "present" ? T1 : year;
    return Math.max(0, Math.min(100, ((y - T0) / (T1 - T0)) * 100));
  }
  function el(id) { return document.getElementById(id); }

  var themeBySlug = {};
  (window.LAB_THEMES || []).forEach(function (t) { themeBySlug[t.slug] = t; });

  /* ---------- publication cards ---------- */
  function pubCard(p) {
    var venue = esc(p.v) + (p.y ? "<br>" + p.y : "");
    var inner =
      '<div class="venue">' + venue + "</div>" +
      "<div><h3>" + esc(p.t) + "</h3>" +
      '<p class="authors">' + authorsHTML(p.a) + "</p></div>";
    if (p.doi) {
      return '<a class="pub" href="https://doi.org/' + esc(p.doi) +
        '" target="_blank" rel="noopener">' + inner +
        '<span class="go">read →</span></a>';
    }
    if (p.u) {
      return '<a class="pub" href="' + esc(p.u) +
        '" target="_blank" rel="noopener">' + inner +
        '<span class="go">find →</span></a>';
    }
    return '<div class="pub pub-static">' + inner + "</div>";
  }
  function byYearDesc(a, b) { return b.y - a.y; }

  function renderLandmarks(containerId, limit) {
    var c = el(containerId); if (!c) return;
    var items = (window.LAB_PUBS || []).filter(function (p) {
      return p.flags && p.flags.indexOf("landmark") !== -1;
    }).sort(byYearDesc);
    if (limit) items = items.slice(0, limit);
    c.innerHTML = items.map(pubCard).join("");
  }

  function renderRecent(containerId, limit) {
    var c = el(containerId); if (!c) return;
    var items = (window.LAB_PUBS || []).slice().sort(byYearDesc).slice(0, limit || 10);
    c.innerHTML = items.map(pubCard).join("");
  }

  function countForTheme(slug) {
    return (window.LAB_PUBS || []).filter(function (p) {
      return p.themes && p.themes.indexOf(slug) !== -1;
    }).length;
  }

  function renderThemeTiles(containerId) {
    var c = el(containerId); if (!c) return;
    c.innerHTML = (window.LAB_THEMES || []).map(function (t) {
      var n = countForTheme(t.slug);
      return '<a class="theme-tile" href="theme.html#' + t.slug + '">' +
        '<span class="theme-count">' + n + '<span>' + (n === 1 ? "paper" : "papers") + "</span></span>" +
        "<h3>" + esc(t.name) + "</h3>" +
        "<p>" + esc(t.blurb) + "</p>" +
        '<span class="theme-go">Browse →</span></a>';
    }).join("");
  }

  /* ---------- featured cards: landmarks + recent ---------- */
  var SPECIAL = {
    landmarks: {
      name: "Landmark papers",
      blurb: "The foundational papers the field still builds on.",
      items: function () {
        return (window.LAB_PUBS || []).filter(function (p) {
          return p.flags && p.flags.indexOf("landmark") !== -1;
        }).sort(byYearDesc);
      }
    },
    directions: {
      name: "New Directions",
      blurb: "Where the lab is heading now — AI foundation models, sustainable corn, and open breeding tools.",
      items: function () {
        return (window.LAB_PUBS || []).filter(function (p) {
          return p.flags && p.flags.indexOf("direction") !== -1;
        }).sort(byYearDesc);
      }
    },
    recent: {
      name: "Most recent",
      blurb: "The newest papers and preprints from the lab, refreshed as they appear.",
      items: function () {
        return (window.LAB_PUBS || []).slice().sort(byYearDesc).slice(0, 10);
      }
    }
  };

  function featTile(slug) {
    var m = SPECIAL[slug];
    var n = m.items().length;
    return '<a class="theme-tile feature" href="theme.html#' + slug + '">' +
      '<span class="theme-count">' + n + "<span>papers</span></span>" +
      "<h3>" + esc(m.name) + "</h3>" +
      "<p>" + esc(m.blurb) + "</p>" +
      '<span class="theme-go">Browse →</span></a>';
  }
  function renderFeaturedTiles(containerId) {
    var c = el(containerId); if (!c) return;
    c.innerHTML = featTile("landmarks") + featTile("directions") + featTile("recent");
  }

  /* ---------- single theme page ---------- */
  function renderThemePage() {
    var slug = (location.hash || "").replace(/^#/, "");
    var titleEl = el("themeTitle"), blurbEl = el("themeBlurb"),
        listEl = el("themeList"), countEl = el("themeCount");

    if (SPECIAL[slug]) {
      var m = SPECIAL[slug];
      var sItems = m.items();
      document.title = m.name + " · Publications · Lab for Plant Genomic Diversity & Design";
      if (titleEl) titleEl.textContent = m.name;
      if (blurbEl) blurbEl.textContent = m.blurb;
      if (countEl) countEl.textContent = sItems.length + (sItems.length === 1 ? " paper" : " papers");
      if (listEl) listEl.innerHTML = sItems.map(pubCard).join("");
      return;
    }

    var t = themeBySlug[slug];
    if (!t) {
      if (titleEl) titleEl.textContent = "Browse by theme";
      if (blurbEl) blurbEl.textContent = "Pick a research theme to see its papers.";
      if (listEl) {
        listEl.innerHTML = (window.LAB_THEMES || []).map(function (x) {
          return '<a class="pub" href="theme.html#' + x.slug + '"><div class="venue">' +
            countForTheme(x.slug) + ' papers</div><div><h3>' + esc(x.name) +
            '</h3><p class="authors">' + esc(x.blurb) + '</p></div><span class="go">open →</span></a>';
        }).join("");
      }
      return;
    }
    document.title = t.name + " · Publications · Lab for Plant Genomic Diversity & Design";
    if (titleEl) titleEl.textContent = t.name;
    if (blurbEl) blurbEl.textContent = t.blurb;
    var items = (window.LAB_PUBS || []).filter(function (p) {
      return p.themes && p.themes.indexOf(slug) !== -1;
    }).sort(byYearDesc);
    if (countEl) countEl.textContent = items.length + (items.length === 1 ? " paper" : " papers");
    if (listEl) listEl.innerHTML = items.map(pubCard).join("");
  }

  /* ---------- year axis (shared) ---------- */
  function axisHTML() {
    var ticks = [];
    for (var y = T0; y <= T1; y += 4) ticks.push(y);
    if (ticks[ticks.length - 1] !== T1) ticks.push(T1);
    return '<div class="tl-axis">' + ticks.map(function (y) {
      return '<span class="tl-tick" style="left:' + pct(y) + '%">' +
        (y >= T1 ? "now" : y) + "</span>";
    }).join("") + "</div>";
  }

  /* ---------- research-lines timeline ---------- */
  function renderResearchTimeline(containerId) {
    var c = el(containerId); if (!c || !window.LAB_LINES) return;
    var rows = window.LAB_LINES.map(function (ln) {
      // same end-of-year rule as the people timeline: a line runs through the
      // whole of its final year, so a single-year line isn't zero width
      var lnEnd = ln.end || "present",
          left = pct(ln.start),
          right = lnEnd === "present" ? pct("present") : pct(lnEnd + 1);
      var dots = (ln.milestones || []).map(function (m) {
        return '<span class="tl-dot" style="left:' + pct(m.y) + '%" title="' +
          esc(m.y + " · " + m.label) + '"><span class="tl-dot-lbl">' + esc(m.label) + "</span></span>";
      }).join("");
      return '<div class="tl-row">' +
        '<div class="tl-name">' + esc(ln.name) + "</div>" +
        '<div class="tl-track"><span class="tl-bar" style="left:' + left + "%;width:" +
        (right - left) + '%"></span>' + dots + "</div></div>";
    }).join("");
    c.innerHTML = axisHTML() + '<div class="tl-rows">' + rows + "</div>";
  }

  /* ---------- people timeline ---------- */
  var ROLES = [
    { key: "pi", label: "PI" },
    { key: "postdoc", label: "Postdocs" },
    { key: "grad", label: "Grad students" },
    { key: "staff", label: "Staff" },
    { key: "visiting", label: "Visiting" },
    { key: "undergrad", label: "Undergrads" }
  ];
  var ICON_WEB = '<svg viewBox="0 0 24 24" width="13" height="13" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c2.5 2.6 2.5 15.4 0 18M12 3c-2.5 2.6-2.5 15.4 0 18"/></svg>';
  var ICON_LI = '<svg viewBox="0 0 24 24" width="13" height="13" fill="currentColor"><path d="M4.98 3.5a2.5 2.5 0 1 0 0 5 2.5 2.5 0 0 0 0-5zM3 9h4v12H3zM10 9h3.8v1.7h.05c.53-1 1.83-2.05 3.77-2.05 4.03 0 4.78 2.65 4.78 6.1V21h-4v-5.4c0-1.3 0-2.95-1.8-2.95s-2.08 1.4-2.08 2.85V21H10z"/></svg>';
  function slugify(name) {
    return String(name).toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "");
  }
  function initials(name) {
    var t = String(name).replace(/[^A-Za-z \-]/g, "").split(/[\s\-]+/).filter(Boolean);
    return ((t[0] || "")[0] || "") + ((t[t.length - 1] || "")[0] || "");
  }
  function hasProfile(slug) {
    return !!(slug && window.LAB_PROFILES && window.LAB_PROFILES[slug]);
  }

  /* ---------- current-team roster (data-driven from LAB_PROFILES) ---------- */
  function avatar(p, big) {
    if (p && p.photo) return '<span class="' + (big ? "avatar" : "av") + ' has-photo"><img src="images/people/' +
      esc(p.photo) + '" alt="' + esc(p.name) + '" loading="lazy"></span>';
    return '<span class="' + (big ? "avatar" : "av") + '">' + esc(initials(p ? p.name : "")) + "</span>";
  }
  function renderRoster() {
    var cfg = window.LAB_ROSTER || {};
    var P = window.LAB_PROFILES || {};
    var lead = el("leadGrid");
    if (lead && cfg.lead) {
      lead.innerHTML = cfg.lead.map(function (c) {
        var p = P[c.slug] || { name: c.name || c.slug };
        var av = p.photo ? '<div class="avatar has-photo"><img src="images/people/' + esc(p.photo) +
          '" alt="' + esc(p.name) + '"></div>' : '<div class="avatar">' + esc(initials(p.name)) + "</div>";
        return '<a class="lead-card" id="' + c.slug + '" href="person.html#' + c.slug + '">' + av +
          "<h4>" + esc(p.name) + "</h4><span class=\"r\">" + esc(c.role) +
          "</span><span class=\"i\">" + esc(c.inst) + "</span></a>";
      }).join("");
    }
    var team = el("teamRoster");
    if (team && cfg.groups) {
      team.innerHTML = cfg.groups.map(function (g) {
        var cards = g.slugs.map(function (slug) {
          var p = P[slug] || { name: slug };
          return '<a class="person" id="' + slug + '" href="person.html#' + slug + '">' +
            avatar(p) + '<span class="who"><span class="nm">' + esc(p.name) +
            '</span><span class="rl">' + esc(g.label) + "</span></span></a>";
        }).join("");
        return '<div class="roster-group"><div class="pub-year">' + esc(g.heading) +
          '</div><div class="roster-grid">' + cards + "</div></div>";
      }).join("");
    }
  }

  /* ---------- per-person profile page (person.html) ---------- */
  function renderProfile() {
    var host = el("profile"); if (!host) return;
    var slug = (location.hash || "").replace(/^#/, "");
    var p = (window.LAB_PROFILES || {})[slug];
    var crumb = el("profileCrumb");
    if (!p) {
      if (crumb) crumb.innerHTML = '<a href="index.html">Home</a> / <a href="people.html">People</a> / Not found';
      host.innerHTML = '<div class="wrap"><h1 class="subhead">Profile not found</h1>' +
        '<p class="lead-copy">This person may not have a profile yet. See the ' +
        '<a href="people.html">full team and alumni</a>.</p></div>';
      document.title = "People · Lab for Plant Genomic Diversity & Design";
      return;
    }
    document.title = p.name + " · Lab for Plant Genomic Diversity & Design";
    if (crumb) crumb.innerHTML = '<a href="index.html">Home</a> / <a href="people.html">People</a> / ' + esc(p.name);
    var years = "";
    if (p.start) years = p.start + " – " + (p.end === "present" ? "present" : (p.end || "present"));
    var ICON_MAIL = '<svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="5" width="18" height="14" rx="2"/><path d="M3 7l9 6 9-6"/></svg>';
    var links = [];
    if (p.email) links.push('<a class="p-link" href="mailto:' + esc(p.email) + '">' + ICON_MAIL + " Email</a>");
    if (p.scholar) links.push('<a class="p-link" href="' + esc(p.scholar) + '" target="_blank" rel="noopener">' + ICON_WEB + " Scholar</a>");
    if (p.website) links.push('<a class="p-link" href="' + esc(p.website) + '" target="_blank" rel="noopener">' + ICON_WEB + " Website</a>");
    if (p.orcid) links.push('<a class="p-link" href="' + esc(p.orcid) + '" target="_blank" rel="noopener">ORCID</a>');
    if (p.linkedin) links.push('<a class="p-link" href="' + esc(p.linkedin) + '" target="_blank" rel="noopener">' + ICON_LI + " LinkedIn</a>");
    if (p.twitter) links.push('<a class="p-link" href="' + esc(p.twitter) + '" target="_blank" rel="noopener">Twitter / X</a>');
    var photo = p.photo ? '<div class="p-photo"><img src="images/people/' + esc(p.photo) + '" alt="' + esc(p.name) + '"></div>' : "";
    var bioParas = (p.bio || "").split(/\n+/).map(function (t) { return "<p>" + esc(t) + "</p>"; }).join("");
    host.innerHTML = '<div class="wrap"><div class="profile-grid">' +
      '<aside class="profile-side">' + photo +
      (links.length ? '<div class="p-links">' + links.join("") + "</div>" : "") + "</aside>" +
      '<div class="profile-main"><span class="eyebrow">' + esc(p.title || "") + "</span>" +
      "<h1>" + esc(p.name) + "</h1>" +
      (years ? '<p class="p-years">' + esc(years) + "</p>" : "") +
      (p.now ? '<p class="p-now">' + esc(p.now) + "</p>" : "") +
      '<div class="p-bio">' + bioParas + "</div>" +
      '<p class="p-back"><a href="people.html">← Back to the team &amp; alumni</a></p>' +
      "</div></div></div>";
  }
  function personLinks(p) {
    var out = "";
    if (p.site) out += '<a class="tl-link" href="' + esc(p.site) + '" target="_blank" rel="noopener" aria-label="Website" title="Website">' + ICON_WEB + "</a>";
    if (p.linkedin) out += '<a class="tl-link" href="' + esc(p.linkedin) + '" target="_blank" rel="noopener" aria-label="LinkedIn" title="LinkedIn">' + ICON_LI + "</a>";
    return out ? '<span class="tl-links">' + out + "</span>" : "";
  }

  function renderPeopleTimeline(containerId, filterId) {
    var c = el(containerId); if (!c || !window.LAB_PEOPLE) return;
    var people = window.LAB_PEOPLE.slice().sort(function (a, b) {
      return a.start - b.start || String(a.name).localeCompare(b.name);
    });
    var rows = people.map(function (p) {
      // a tenure runs to the END of its final year, so 2016–2016 spans the whole
      // of 2016 rather than collapsing to zero width
      var left = pct(p.start),
          right = p.end === "present" ? pct("present") : pct(p.end + 1);
      var end = p.end === "present" ? "present" : p.end;
      var now = p.now ? ' — <span class="tl-now">' + esc(p.now) + "</span>" : "";
      var slug = p.slug || slugify(p.name);
      var nm = hasProfile(slug) ? '<a class="tl-namelink" href="person.html#' + slug + '">' + esc(p.name) + "</a>" : esc(p.name);
      return '<div class="tl-row person-row" id="tl-' + slug + '" data-role="' + esc(p.role) + '">' +
        '<div class="tl-name">' + nm + personLinks(p) +
        '<span class="tl-span">' + esc(p.start + "–" + end) + now + "</span></div>" +
        '<div class="tl-track"><span class="tl-bar role-' + esc(p.role) +
        '" style="left:' + left + "%;width:" + Math.max(1.5, right - left) + '%"></span></div></div>';
    }).join("");
    c.innerHTML = axisHTML() + '<div class="tl-rows">' + rows + "</div>";

    var filter = el(filterId);
    if (filter) {
      var present = {};
      window.LAB_PEOPLE.forEach(function (p) { present[p.role] = true; });
      var btns = ['<button class="tl-filter active" data-role="all">All</button>'];
      ROLES.forEach(function (r) {
        if (present[r.key]) btns.push('<button class="tl-filter" data-role="' + r.key + '">' + r.label + "</button>");
      });
      filter.innerHTML = btns.join("");
      filter.addEventListener("click", function (e) {
        var b = e.target.closest(".tl-filter"); if (!b) return;
        filter.querySelectorAll(".tl-filter").forEach(function (x) { x.classList.remove("active"); });
        b.classList.add("active");
        var role = b.getAttribute("data-role");
        c.querySelectorAll(".person-row").forEach(function (row) {
          row.style.display = (role === "all" || row.getAttribute("data-role") === role) ? "" : "none";
        });
      });
    }
  }

  /* ---------- auto-init by data attributes ---------- */
  function init() {
    if (el("landmarkList")) renderLandmarks("landmarkList", 10);
    if (el("recentList")) renderRecent("recentList", 10);
    if (el("featuredTiles")) renderFeaturedTiles("featuredTiles");
    if (el("themeTiles")) renderThemeTiles("themeTiles");
    if (el("themeList")) { renderThemePage(); window.addEventListener("hashchange", renderThemePage); }
    if (el("researchTimeline")) renderResearchTimeline("researchTimeline");
    if (el("peopleTimeline")) renderPeopleTimeline("peopleTimeline", "peopleFilter");
    if (el("leadGrid") || el("teamRoster")) renderRoster();
    if (el("profile")) { renderProfile(); window.addEventListener("hashchange", renderProfile); }
  }
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else { init(); }
})();
