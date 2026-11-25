/**
 * ==============================================================================
 * KONNYX — Puerta de enlace de Animaciones (compatibilidad universal)
 * ==============================================================================
 */
(function (global) {
  'use strict';
  global.initAnimations = global.initGsapAnimations;
})(typeof window !== 'undefined' ? window : this);
