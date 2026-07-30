/* ==========================================================================
   The God Who Hears Her — interactions
   Everything here is progressive enhancement: with JS off, the form still
   POSTs to Formspree and the PDF is still linkable.
   ========================================================================== */
(function () {
  'use strict';

  /* ------------------------------------------------------------------
     CONFIGURE ME
     Paste your Formspree endpoint (https://formspree.io/f/xxxxxxxx).
     Leave it as-is and the form still hands over the PDF — it just
     won't store the address anywhere. See README.md.
     ------------------------------------------------------------------ */
  var FORM_ENDPOINT = 'https://formspree.io/f/YOUR_FORM_ID';

  // The PDF's location is read off the thank-you link in the page, so this
  // works from the landing page and from /devotions/* alike.
  var PDF_FALLBACK = 'downloads/the-god-who-hears-her-sample-chapter.pdf';
  var PDF_FILENAME = 'The-God-Who-Hears-Her-Sample-Chapter.pdf';

  var isConfigured = FORM_ENDPOINT.indexOf('YOUR_FORM_ID') === -1;

  var $ = function (sel) { return document.querySelector(sel); };

  /* ---------------- footer year ---------------- */
  var year = $('#year');
  if (year) year.textContent = String(new Date().getFullYear());

  /* ---------------- reveal on scroll ---------------- */
  var revealables = document.querySelectorAll('.reveal');
  if (!('IntersectionObserver' in window)) {
    Array.prototype.forEach.call(revealables, function (el) { el.classList.add('is-in'); });
  } else {
    var revealer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        entry.target.classList.add('is-in');
        revealer.unobserve(entry.target);
      });
    }, { rootMargin: '0px 0px -8% 0px', threshold: 0.12 });
    Array.prototype.forEach.call(revealables, function (el) { revealer.observe(el); });
  }

  /* ---------------- top bar + sticky mobile CTA ----------------
     Both appear once the hero CTA has scrolled out of reach, and the
     sticky bar hides again while the form itself is on screen.        */
  var topbar = $('#topbar');
  var stickybar = $('#stickybar');
  var capture = $('#free-chapter');
  var captureVisible = false;

  if (stickybar) stickybar.hidden = false;

  function onScroll() {
    var past = window.scrollY > window.innerHeight * 0.6;
    if (topbar) topbar.classList.toggle('is-visible', past);
    if (stickybar) stickybar.classList.toggle('is-visible', past && !captureVisible);
  }

  if ('IntersectionObserver' in window && capture) {
    new IntersectionObserver(function (entries) {
      captureVisible = entries[0].isIntersecting;
      onScroll();
    }, { threshold: 0.18 }).observe(capture);
  }

  var ticking = false;
  window.addEventListener('scroll', function () {
    if (ticking) return;
    ticking = true;
    window.requestAnimationFrame(function () { onScroll(); ticking = false; });
  }, { passive: true });
  onScroll();

  /* ---------------- the form ---------------- */
  var form = $('#chapter-form');
  if (!form) return;

  var submitBtn = $('#submit-btn');
  var statusEl = $('#form-status');
  var thanks = $('#thanks');
  var thanksName = $('#thanks-name');
  var thanksLink = $('#thanks-download');
  var firstName = $('#firstName');
  var email = $('#email');

  if (isConfigured) form.setAttribute('action', FORM_ENDPOINT);

  var pdfPath = (thanksLink && thanksLink.getAttribute('href')) || PDF_FALLBACK;
  if (thanksLink) thanksLink.setAttribute('download', PDF_FILENAME);

  var EMAIL_RE = /^[^\s@]+@[^\s@]+\.[a-z]{2,}$/i;

  function setError(input, on) {
    var field = input.closest('.field');
    var msg = document.getElementById(input.id + '-error');
    if (field) field.classList.toggle('has-error', on);
    if (msg) msg.hidden = !on;
    input.setAttribute('aria-invalid', on ? 'true' : 'false');
  }

  function validate() {
    var nameOk = firstName.value.trim().length > 0;
    var mailOk = EMAIL_RE.test(email.value.trim());
    setError(firstName, !nameOk);
    setError(email, !mailOk);
    if (!nameOk) firstName.focus();
    else if (!mailOk) email.focus();
    return nameOk && mailOk;
  }

  [firstName, email].forEach(function (input) {
    input.addEventListener('input', function () {
      if (input.getAttribute('aria-invalid') === 'true') setError(input, false);
      if (statusEl) statusEl.textContent = '';
    });
  });

  /* Hand the PDF over without navigating away from the thank-you panel. */
  function startDownload() {
    var a = document.createElement('a');
    a.href = pdfPath;
    a.setAttribute('download', PDF_FILENAME);
    a.style.display = 'none';
    document.body.appendChild(a);
    a.click();
    window.setTimeout(function () { document.body.removeChild(a); }, 0);
  }

  function showThanks(name) {
    if (thanksName) thanksName.textContent = name || 'friend';
    form.hidden = true;
    var head = document.querySelector('.capture__head');
    if (head) head.hidden = true;
    if (thanks) {
      thanks.hidden = false;
      thanks.focus();
    }
    if (statusEl) statusEl.textContent = '';
    startDownload();
  }

  form.addEventListener('submit', function (event) {
    event.preventDefault();
    if (statusEl) statusEl.textContent = '';
    if (!validate()) return;

    var name = firstName.value.trim().replace(/\s+/g, ' ');

    // No endpoint wired up yet — never hold the reader's chapter hostage.
    if (!isConfigured) {
      if (window.console) {
        console.warn('[TGWHH] FORM_ENDPOINT is not configured in assets/js/main.js — ' +
                     'the email address was not stored. See README.md.');
      }
      showThanks(name);
      return;
    }

    if (submitBtn) submitBtn.classList.add('is-busy');

    var payload = new FormData(form);
    payload.append('_subject', 'New sample-chapter request — ' + name);

    fetch(FORM_ENDPOINT, {
      method: 'POST',
      body: payload,
      headers: { Accept: 'application/json' }
    })
      .then(function (response) {
        if (!response.ok) throw new Error('HTTP ' + response.status);
        showThanks(name);
      })
      .catch(function () {
        if (statusEl) {
          statusEl.textContent =
            'Something went wrong sending that. Please try again — or email ' +
            'hello@thegodwhohearsher.com and we will send the chapter over.';
        }
      })
      .then(function () {
        if (submitBtn) submitBtn.classList.remove('is-busy');
      });
  });
})();
