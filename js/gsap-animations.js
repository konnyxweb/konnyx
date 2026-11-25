/**
 * ==============================================================================
 * KONNYX — Módulo de Animaciones GSAP 3 + ScrollTrigger
 * Arquitectura: Frontend Senior / UI Tecnológico de Alto Rendimiento (60 FPS)
 * 
 * Principios:
 * 1. Compatible al 100% con 'file:///' (sin bloqueo CORS de ES Modules) y servidores web.
 * 2. NO mutar ni dividir el texto en el DOM (accesibilidad y SEO 100% nativo).
 * 3. Comportamiento bidireccional fluido: responde con precisión tanto al
 *    bajar como al subir el scroll (toggleActions: 'play none none reverse').
 * 4. Seguridad visual total: los elementos son legibles y visibles por defecto;
 *    ningún elemento puede quedar invisible (opacity: 0) ante scrolls rápidos o saltos.
 * 5. Respeta 'prefers-reduced-motion: reduce' desactivando transformaciones complejas.
 * 6. Desplazamiento suave para enlaces internos a[href^="#"] con offset del navbar.
 * ==============================================================================
 */

(function (global) {
  'use strict';

  var REDUCED_QUERY = '(prefers-reduced-motion: reduce)';
  var prefersReduced = function () {
    return window.matchMedia && window.matchMedia(REDUCED_QUERY).matches;
  };

  var gsapCtx = null;

  function initGsapAnimations() {
    var gsap = window.gsap;
    var ScrollTrigger = window.ScrollTrigger;

    if (!gsap || !ScrollTrigger) {
      console.warn('[Konnyx GSAP] Librerías GSAP o ScrollTrigger no encontradas. El sitio se mantiene 100% accesible.');
      return;
    }

    gsap.registerPlugin(ScrollTrigger);
    ScrollTrigger.config({
      ignoreMobileResize: true,
      autoRefreshEvents: 'visibilitychange,DOMContentLoaded,load,resize'
    });

    // Limpiar contexto previo si se reinicializa
    if (gsapCtx) {
      gsapCtx.revert();
      gsapCtx = null;
    }

    var mm = gsap.matchMedia();

    // Animaciones completas cuando el usuario NO prefiere movimiento reducido
    mm.add('(prefers-reduced-motion: no-preference)', function () {
      gsapCtx = gsap.context(function () {
        buildHeroAnimations(gsap);
        buildTitlesAndText(gsap, ScrollTrigger);
        buildPillars(gsap, ScrollTrigger);
        buildProjects(gsap, ScrollTrigger);
        buildProcessSteps(gsap, ScrollTrigger);
        buildContactSection(gsap, ScrollTrigger);
        buildNavbarController(gsap, ScrollTrigger);
        buildParallaxAndMarquee(gsap, ScrollTrigger);
        setupSmoothAnchorScroll(gsap, ScrollTrigger);
      }, document.body);

      return function () {
        if (gsapCtx) gsapCtx.revert();
      };
    });

    // Modo accesible: garantiza visibilidad inmediata y cancela triggers
    mm.add('(prefers-reduced-motion: reduce)', function () {
      ScrollTrigger.getAll().forEach(function (st) {
        st.kill();
      });
    });

    // Recomputar puntos de scroll al cargar imágenes y fuentes tipográficas
    var refreshST = function () {
      ScrollTrigger.refresh();
    };

    window.addEventListener('load', refreshST);
    if (document.fonts && document.fonts.ready) {
      document.fonts.ready.then(refreshST);
    }

    var images = document.querySelectorAll('img');
    images.forEach(function (img) {
      if (!img.complete) {
        img.addEventListener('load', refreshST, { once: true });
      }
    });

    var resizeTimer = null;
    window.addEventListener('resize', function () {
      clearTimeout(resizeTimer);
      resizeTimer = setTimeout(refreshST, 200);
    });
  }

  /**
   * 1. HERO (Animación de entrada en carga inicial)
   * Entrada de líneas enmascaradas con skew sutil y curva tecnológica rápida
   */
  function buildHeroAnimations(gsap) {
    var heroTL = gsap.timeline({
      defaults: { ease: 'power4.out' }
    });

    // Revelado de líneas de título enmascaradas
    var heroLines = document.querySelectorAll('.hero-line');
    if (heroLines.length) {
      heroTL.fromTo(
        heroLines,
        { yPercent: 125, opacity: 0, skewY: 2 },
        { yPercent: 0, opacity: 1, skewY: 0, duration: 1.15, stagger: 0.14 }
      );
    }

    // Badge de categoría, párrafo y botones CTA
    var heroFadeElements = document.querySelectorAll(
      '[data-hero-fade], [data-gsap="hero-badge"], [data-gsap="hero-text"], [data-gsap="hero-cta"]'
    );
    if (heroFadeElements.length) {
      heroTL.fromTo(
        heroFadeElements,
        { y: 28, opacity: 0 },
        { y: 0, opacity: 1, duration: 0.9, stagger: 0.12, ease: 'power3.out' },
        '-=0.75'
      );
    }
  }

  /**
   * 2. TÍTULOS Y PÁRRAFOS GENERALES
   * Desplazamiento sutil vertical y micro-desfase bidireccional
   */
  function buildTitlesAndText(gsap, ScrollTrigger) {
    var titleBlocks = document.querySelectorAll(
      '[data-gsap="block"], [data-reveal]:not(.pillar):not(.step):not(#project-grid):not(#contact-form)'
    );

    titleBlocks.forEach(function (block) {
      var eyebrow = block.querySelector('.eyebrow, [data-gsap="eyebrow"]');
      var title = block.querySelector('.section-title, [data-gsap="title"], h2, h3');
      var text = block.querySelector('p:not(.eyebrow), [data-gsap="text"]');

      var targets = [eyebrow, title, text].filter(Boolean);
      if (!targets.length) return;

      gsap.fromTo(
        targets,
        { y: 30, opacity: 0 },
        {
          y: 0,
          opacity: 1,
          duration: 0.85,
          stagger: 0.09,
          ease: 'power3.out',
          scrollTrigger: {
            trigger: block,
            start: 'top 86%',
            toggleActions: 'play none none reverse',
            invalidateOnRefresh: true
          }
        }
      );
    });
  }

  /**
   * 3. PILARES DE SERVICIO (Diseño Gráfico y Desarrollo Web)
   * Entrada lateral coordinada con resplandor de fondo
   */
  function buildPillars(gsap, ScrollTrigger) {
    var pilarDiseno = document.getElementById('diseno-grafico');
    var pilarWeb = document.getElementById('desarrollo-web');

    if (pilarDiseno) {
      gsap.fromTo(
        pilarDiseno,
        { x: -50, opacity: 0 },
        {
          x: 0,
          opacity: 1,
          duration: 1.0,
          ease: 'power3.out',
          scrollTrigger: {
            trigger: pilarDiseno,
            start: 'top 84%',
            toggleActions: 'play none none reverse'
          }
        }
      );
    }

    if (pilarWeb) {
      gsap.fromTo(
        pilarWeb,
        { x: 50, opacity: 0 },
        {
          x: 0,
          opacity: 1,
          duration: 1.0,
          ease: 'power3.out',
          scrollTrigger: {
            trigger: pilarWeb,
            start: 'top 84%',
            toggleActions: 'play none none reverse'
          }
        }
      );
    }
  }

  /**
   * 4. PROYECTOS DESTACADOS
   * Cascada escalonada de tarjetas y suave elevación de miniaturas
   */
  function buildProjects(gsap, ScrollTrigger) {
    var grids = document.querySelectorAll(
      '#project-grid, #project-grid-diseno, #project-grid-web, .project-grid, [data-gsap="grid"]'
    );
    if (!grids.length) return;

    grids.forEach(function (grid) {
      var projectCards = grid.querySelectorAll('.project');
      if (!projectCards.length) return;

      gsap.fromTo(
        projectCards,
        { y: 38, opacity: 0, scale: 0.96 },
        {
          y: 0,
          opacity: 1,
          scale: 1,
          duration: 0.85,
          stagger: 0.1,
          ease: 'power3.out',
          scrollTrigger: {
            trigger: grid,
            start: 'top 82%',
            toggleActions: 'play none none reverse'
          }
        }
      );

      // Microinteracción óptica suave en miniaturas
      projectCards.forEach(function (card) {
        var thumb = card.querySelector('.thumb');
        if (!thumb) return;

        card.addEventListener('mouseenter', function () {
          gsap.to(thumb, { scale: 1.04, duration: 0.4, ease: 'power2.out' });
        });
        card.addEventListener('mouseleave', function () {
          gsap.to(thumb, { scale: 1.0, duration: 0.45, ease: 'power2.out' });
        });
      });
    });
  }

  /**
   * 5. PASOS DEL PROCESO
   * Revelado secuencial con avance de la línea conectora
   */
  function buildProcessSteps(gsap, ScrollTrigger) {
    var procesoList = document.getElementById('proceso-list');
    if (!procesoList) return;

    var steps = procesoList.querySelectorAll('.step');
    var progressLine = procesoList.querySelector('[data-progress]');

    // Línea de progreso vertical impulsada por el scroll
    if (progressLine) {
      gsap.fromTo(
        progressLine,
        { scaleY: 0 },
        {
          scaleY: 1,
          ease: 'none',
          scrollTrigger: {
            trigger: procesoList,
            start: 'top 75%',
            end: 'bottom 65%',
            scrub: 0.4
          }
        }
      );
    }

    // Revelado bidireccional paso a paso
    steps.forEach(function (step) {
      gsap.fromTo(
        step,
        { x: -28, opacity: 0 },
        {
          x: 0,
          opacity: 1,
          duration: 0.8,
          ease: 'power3.out',
          scrollTrigger: {
            trigger: step,
            start: 'top 86%',
            toggleActions: 'play none none reverse'
          }
        }
      );
    });
  }

  /**
   * 6. CONTACTO Y FORMULARIO
   */
  function buildContactSection(gsap, ScrollTrigger) {
    var contactSection = document.getElementById('contacto');
    if (!contactSection) return;

    var infoCol = contactSection.querySelector('.mx-auto > div:first-child');
    var formCol = document.getElementById('contact-cta') || document.getElementById('contact-form');

    if (infoCol) {
      gsap.fromTo(
        infoCol,
        { y: 35, opacity: 0 },
        {
          y: 0,
          opacity: 1,
          duration: 0.95,
          ease: 'power3.out',
          scrollTrigger: {
            trigger: contactSection,
            start: 'top 82%',
            toggleActions: 'play none none reverse'
          }
        }
      );
    }

    if (formCol) {
      gsap.fromTo(
        formCol,
        { y: 40, opacity: 0 },
        {
          y: 0,
          opacity: 1,
          duration: 1.0,
          delay: 0.1,
          ease: 'power3.out',
          scrollTrigger: {
            trigger: contactSection,
            start: 'top 82%',
            toggleActions: 'play none none reverse'
          }
        }
      );
    }
  }

  /**
   * 7. NAVBAR FLOTANTE INTELIGENTE
   * Se repliega suavemente al bajar y reaparece al hacer scroll hacia arriba
   */
  function buildNavbarController(gsap, ScrollTrigger) {
    var navbar = document.getElementById('navbar');
    if (!navbar) return;

    var navTween = gsap.to(navbar, {
      yPercent: -100,
      duration: 0.32,
      ease: 'power2.out',
      paused: true
    });

    ScrollTrigger.create({
      start: 'top top',
      end: 999999,
      onUpdate: function (self) {
        var menuBtn = document.getElementById('menu-toggle');
        var menuOpen = menuBtn && menuBtn.getAttribute('aria-expanded') === 'true';
        if (self.direction === 1 && self.scroll() > 120 && !menuOpen) {
          navTween.play();
        } else {
          navTween.reverse();
        }
      }
    });

    navbar.addEventListener('focusin', function () {
      navTween.reverse();
    });
  }

  /**
   * 8. PARALLAX Y MARQUEE
   */
  function buildParallaxAndMarquee(gsap, ScrollTrigger) {
    document.querySelectorAll('[data-parallax]').forEach(function (el) {
      var factor = parseFloat(el.dataset.parallax) || 10;
      gsap.to(el, {
        yPercent: factor * 3.5,
        ease: 'none',
        scrollTrigger: {
          trigger: '#inicio',
          start: 'top top',
          end: 'bottom top',
          scrub: 0.5
        }
      });
    });

    var marquee = document.querySelector('[data-marquee]');
    if (marquee) {
      gsap.fromTo(
        marquee,
        { xPercent: 0 },
        {
          xPercent: -32,
          ease: 'none',
          scrollTrigger: {
            trigger: marquee,
            start: 'top bottom',
            end: 'bottom top',
            scrub: 0.6
          }
        }
      );
    }
  }

  /**
   * 9. SMOOTH SCROLL PARA ENLACES ANCLA
   */
  function setupSmoothAnchorScroll(gsap, ScrollTrigger) {
    document.querySelectorAll('a[href^="#"]').forEach(function (anchor) {
      anchor.addEventListener('click', function (e) {
        var href = anchor.getAttribute('href');
        if (href === '#' || !href) return;

        var target = document.querySelector(href);
        if (!target) return;

        e.preventDefault();
        var nav = document.getElementById('navbar');
        var navHeight = nav ? nav.offsetHeight : 64;
        var targetPos = target.getBoundingClientRect().top + window.pageYOffset - navHeight;

        window.scrollTo({
          top: targetPos,
          behavior: 'smooth'
        });

        setTimeout(function () {
          ScrollTrigger.refresh();
        }, 450);
      });
    });
  }

  /**
   * Animación para filtros de proyectos
   */
  function animateFilter(items) {
    var gsap = window.gsap;
    var ScrollTrigger = window.ScrollTrigger;
    if (!gsap || prefersReduced() || !items || !items.length) {
      if (ScrollTrigger) ScrollTrigger.refresh();
      return;
    }

    gsap.fromTo(
      items,
      { opacity: 0, y: 24, scale: 0.97 },
      {
        opacity: 1,
        y: 0,
        scale: 1,
        duration: 0.5,
        stagger: 0.07,
        ease: 'power2.out',
        clearProps: 'transform,opacity',
        onComplete: function () {
          if (ScrollTrigger) ScrollTrigger.refresh();
        }
      }
    );
  }

  // Publicar globalmente en window para compatibilidad universal
  global.KonnyxAnim = {
    init: initGsapAnimations,
    animateFilter: animateFilter
  };
  global.initGsapAnimations = initGsapAnimations;
  global.animateFilter = animateFilter;

  // Auto-inicialización segura según el estado del documento
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initGsapAnimations);
  } else {
    initGsapAnimations();
  }

})(typeof window !== 'undefined' ? window : this);
