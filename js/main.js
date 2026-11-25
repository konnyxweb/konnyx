/* ============================================================
   Konnyx — lógica principal
   Universal Script: compatible con file:/// y servidores web (http://)
   ============================================================ */

(function () {
  'use strict';

  /* ---------- CONFIGURACIÓN: edita estos datos ---------- */
  var CONFIG = {
    whatsappNumber: '584241925167', // WhatsApp oficial Konnyx
    email: 'hola@konnyx.com'
  };

  /* ---------- Utilidad inteligente para WhatsApp (Web en PC / App en Móvil) ---------- */
  function getWhatsAppUrl(text) {
    var isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
    var baseUrl = isMobile ? 'https://api.whatsapp.com/send' : 'https://web.whatsapp.com/send';
    return baseUrl + '?phone=' + CONFIG.whatsappNumber + '&text=' + encodeURIComponent(text);
  }

  function openWhatsApp(text) {
    var url = getWhatsAppUrl(text);
    var a = document.createElement('a');
    a.href = url;
    a.target = '_blank';
    a.rel = 'noopener noreferrer';
    document.body.appendChild(a);
    a.click();
    setTimeout(function () {
      if (a.parentNode) a.parentNode.removeChild(a);
    }, 200);
  }

  /* ---------- Año del footer ---------- */
  var yearEl = document.getElementById('year');
  if (yearEl) yearEl.textContent = new Date().getFullYear();

  /* ---------- Enlaces directos de contacto ---------- */
  var waLink = document.getElementById('link-whatsapp');
  var mailLink = document.getElementById('link-email');
  if (waLink) {
    waLink.href = getWhatsAppUrl('Hola Konnyx, vengo de su sitio web y me gustaría cotizar un proyecto.');
    waLink.target = '_blank';
    waLink.rel = 'noopener noreferrer';
  }
  if (mailLink) {
    mailLink.href = 'mailto:' + CONFIG.email;
    mailLink.textContent = CONFIG.email;
  }

  /* ---------- Menú móvil ---------- */
  var toggle = document.getElementById('menu-toggle');
  var menu = document.getElementById('mobile-menu');
  var iconOpen = document.getElementById('icon-open');
  var iconClose = document.getElementById('icon-close');

  function setMenu(open) {
    if (!toggle || !menu) return;
    toggle.setAttribute('aria-expanded', String(open));
    toggle.setAttribute('aria-label', open ? 'Cerrar menú' : 'Abrir menú');
    menu.classList.toggle('hidden', !open);
    if (iconOpen) iconOpen.classList.toggle('hidden', open);
    if (iconClose) iconClose.classList.toggle('hidden', !open);
  }

  if (toggle) {
    toggle.addEventListener('click', function () {
      setMenu(toggle.getAttribute('aria-expanded') !== 'true');
    });
  }

  if (menu) {
    menu.querySelectorAll('a').forEach(function (a) {
      a.addEventListener('click', function () {
        setMenu(false);
      });
    });
  }

  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') setMenu(false);
  });

  if (window.matchMedia) {
    window.matchMedia('(min-width: 768px)').addEventListener('change', function (e) {
      if (e.matches) setMenu(false);
    });
  }

  /* ---------- Enlace activo según la sección visible ---------- */
  var navLinks = Array.prototype.slice.call(document.querySelectorAll('.nav-link'));
  var sections = navLinks
    .map(function (a) {
      return document.querySelector(a.getAttribute('href'));
    })
    .filter(Boolean);

  if ('IntersectionObserver' in window && sections.length) {
    var io = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (!entry.isIntersecting) return;
          navLinks.forEach(function (a) {
            a.toggleAttribute('aria-current', false);
            a.removeAttribute('aria-current');
          });
          var active = navLinks.find(function (a) {
            return a.getAttribute('href') === '#' + entry.target.id;
          });
          if (active) active.setAttribute('aria-current', 'true');
        });
      },
      { rootMargin: '-45% 0px -50% 0px' }
    );
    sections.forEach(function (s) {
      io.observe(s);
    });
  }

  /* ---------- Filtro de proyectos ---------- */
  var filterButtons = Array.prototype.slice.call(document.querySelectorAll('.filter-btn'));
  var projects = Array.prototype.slice.call(document.querySelectorAll('.project'));

  filterButtons.forEach(function (btn) {
    btn.addEventListener('click', function () {
      var filter = btn.dataset.filter;
      filterButtons.forEach(function (b) {
        b.setAttribute('aria-pressed', String(b === btn));
      });

      var visible = [];
      projects.forEach(function (p) {
        var show = filter === 'all' || p.dataset.category === filter;
        p.hidden = !show;
        if (show) visible.push(p);
      });

      if (window.animateFilter) {
        window.animateFilter(visible);
      }
    });
  });

  /* ---------- CTAs de pilares: preseleccionan el servicio ---------- */
  var serviceSelect = document.getElementById('servicio');
  document.querySelectorAll('[data-service]').forEach(function (a) {
    a.addEventListener('click', function () {
      if (!serviceSelect) return;
      var opt = Array.prototype.slice.call(serviceSelect.options).find(function (o) {
        return o.dataset.key === a.dataset.service;
      });
      if (opt) serviceSelect.value = opt.value;
    });
  });

  /* ---------- Formulario exclusivo directo a WhatsApp ---------- */
  var form = document.getElementById('contact-form');
  var statusEl = document.getElementById('form-status');

  if (form) {
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var data = new FormData(form);
      var nombre = String(data.get('nombre') || '').trim();
      var email = String(data.get('email') || '').trim();
      var servicio = String(data.get('servicio') || '');
      var mensaje = String(data.get('mensaje') || '').trim();

      // Validación accesible
      var valid = true;
      ['nombre', 'mensaje'].forEach(function (id) {
        var el = document.getElementById(id);
        var empty = !el || !el.value.trim();
        if (el) el.setAttribute('aria-invalid', String(empty));
        if (empty) valid = false;
      });

      if (!valid) {
        if (statusEl) {
          statusEl.textContent = 'Por favor completa tu nombre y cuéntame de tu proyecto.';
          statusEl.classList.replace('text-sky', 'text-red-400');
        }
        return;
      }
      if (statusEl) statusEl.classList.replace('text-red-400', 'text-sky');

      var body =
        '👋 *¡Hola Konnyx!* Vengo de su sitio web y deseo cotizar un proyecto:\n\n' +
        '👤 *Nombre:* ' + nombre + '\n' +
        (email ? '📧 *Correo de contacto:* ' + email + '\n' : '') +
        '💼 *Servicio de interés:* ' + servicio + '\n\n' +
        '📝 *Detalles del proyecto:*\n' + mensaje;

      if (statusEl) statusEl.textContent = 'Abriendo WhatsApp con tu información...';
      openWhatsApp(body);
    });
  }

  /* ---------- Animaciones GSAP ---------- */
  if (typeof window.initGsapAnimations === 'function') {
    window.initGsapAnimations();
  }

})();
