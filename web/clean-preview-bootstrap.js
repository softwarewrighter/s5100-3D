/* Load 3D only when WebGL initializes; retain inspection renders on failure. */
(() => {
  const mv = document.getElementById('mv');
  const status = document.getElementById('status');
  const image = document.getElementById('render-fallback');
  const names = ['overview', 'front', 'left', 'right', 'top', 'detail', 'keyboard-layout', 'power-switch'];
  const forceRenders = new URLSearchParams(location.search).get('renders') === '1';
  function renderMode(reason) {
    window.previewRenderMode = true;
    window.previewControls?.dispose();
    mv.style.display = 'none';
    image.hidden = false;
    status.textContent = reason;
    document.querySelectorAll('[data-action]').forEach(button => button.disabled = true);
    document.querySelectorAll('[data-preset]').forEach(button => {
      button.onclick = () => { image.src = names[Number(button.dataset.preset)] + '.png'; };
    });
  }
  const isGraphicsError = value => /WebGL|renderer|context|reading '(xr|getFieldOfView)'/i.test(String(value || ''));
  window.addEventListener('error', event => {
    if (isGraphicsError(event.message)) renderMode('3D unavailable in this browser. Showing Blender renders; use the view buttons below.');
  });
  window.addEventListener('unhandledrejection', event => {
    if (isGraphicsError(event.reason?.message || event.reason)) {
      renderMode('3D unavailable in this browser. Showing Blender renders; use the view buttons below.');
      event.preventDefault();
    }
  });
  mv.addEventListener('error', () => renderMode('3D could not load. Showing Blender renders.'));
  if (forceRenders) { renderMode('Blender renders · choose a view below.'); return; }
  try {
    const probe = document.createElement('canvas');
    const gl = probe.getContext('webgl2');
    if (!gl) { renderMode('WebGL is unavailable. Showing Blender renders; use the view buttons below.'); return; }
    gl.getExtension('WEBGL_lose_context')?.loseContext();
  } catch (_) {
    renderMode('WebGL is unavailable. Showing Blender renders; use the view buttons below.'); return;
  }
  import('./vendor/model-viewer-4.0.0.min.js').catch(() => {
    renderMode('3D could not initialize. Showing Blender renders; use the view buttons below.');
  });
})();
