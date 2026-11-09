/* Shared by lucy-3D, s1130-3D and s5100-3D. glTF is Y-up. */
(function (global) {
  'use strict';
  function attach(mv, options = {}) {
    const host = options.host || window;
    const orbit = options.orbit || mv.cameraOrbit;
    const target = options.target || mv.cameraTarget;
    const min = options.min || 0.2, max = options.max || 8;
    const pan = options.pan || 0.08;
    function rotation(on) {
      mv.autoRotate = on;
      if (on) mv.setAttribute('auto-rotate', ''); else mv.removeAttribute('auto-rotate');
      if (options.rotateButton) options.rotateButton.textContent = on ? 'Pause rotation' : 'Resume rotation';
    }
    function adjust(theta = 0, phi = 0, zoom = 1) {
      const o = mv.getCameraOrbit();
      rotation(false);
      mv.cameraOrbit = `${o.theta + theta}rad ${Math.max(.05, Math.min(Math.PI-.05, o.phi + phi))}rad ${Math.max(min, Math.min(max, o.radius * zoom))}m`;
    }
    function move(dy) {
      const t = mv.getCameraTarget();
      rotation(false);
      mv.cameraTarget = `${t.x}m ${t.y + dy}m ${t.z}m`;
    }
    const actions = {
      'zoom-in': () => adjust(0,0,.8), 'zoom-out': () => adjust(0,0,1.25),
      left: () => adjust(-.12), right: () => adjust(.12),
      up: () => adjust(0,-.10), down: () => adjust(0,.10),
      'pan-up': () => move(pan), 'pan-down': () => move(-pan),
      rotate: () => rotation(!mv.autoRotate),
      reset: () => { mv.cameraOrbit = orbit; mv.cameraTarget = target; rotation(false); }
    };
    const keys = {w:'zoom-in',s:'zoom-out',a:'left',d:'right',arrowleft:'left',arrowright:'right',arrowup:'up',arrowdown:'down',i:'pan-up',k:'pan-down',r:'reset',' ':'rotate'};
    function keydown(e) {
      if (e.ctrlKey || e.metaKey || e.altKey || e.target?.isContentEditable || /^(INPUT|TEXTAREA|SELECT)$/.test(e.target?.tagName)) return;
      const action = keys[e.key.toLowerCase()];
      if (action) { e.preventDefault(); e.stopPropagation?.(); actions[action](); }
    }
    host.addEventListener('keydown', keydown, {capture:true});
    return { actions, setView(o,t) { rotation(false); mv.cameraOrbit=o; mv.cameraTarget=t; }, dispose() { host.removeEventListener('keydown',keydown, {capture:true}); } };
  }
  global.ModelControls = {attach};
  if (typeof module !== 'undefined') module.exports = {attach};
})(globalThis);
