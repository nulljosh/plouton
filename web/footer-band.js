// Footer band: Plouton's things in a row (tally, calendar, coins, envelope, house, mountain), cut like a line engraving
// in plain 2D canvas, after the Hermes footer. Faint rules run across the band; inside the glyphs they thicken, and
// thicken again on the edge facing away from the light, so the glyphs look cut into the page. Drawn once per size and theme.
// The glyphs are the same art/*.svg files the landing uses, so the band and the page never disagree.
(function () {
  var band = document.querySelector('.word-band'), canvas = band && band.querySelector('canvas');
  if (!canvas) return;
  var ctx = canvas.getContext('2d');
  if (!ctx) return;

  var NAMES = ['tally', 'calendar', 'coins', 'envelope', 'house', 'mountain'];
  var imgs = NAMES.map(function (n) { var i = new Image(); i.src = '/art/' + n + '.svg'; return i; });

  // One row, or two on a narrow band.
  function grid(w, h) {
    var n = imgs.length, rows = w < h * 3 ? 2 : 1, per = Math.ceil(n / rows);
    return { rows: rows, per: per, cell: Math.min(h / rows * 0.86, w / per) };
  }
  function layer(w, h) { var c = document.createElement('canvas'); c.width = w; c.height = h; return c; }
  // Every glyph drawn as a solid white silhouette, laid out evenly.
  function silhouettes(w, h) {
    var c = layer(w, h), x = c.getContext('2d'), g = grid(w, h), gap = (w - g.cell * g.per) / g.per, rowH = h / g.rows;
    imgs.forEach(function (img, i) {
      if (!img.complete || !img.naturalWidth) return;
      var col = i % g.per, row = Math.floor(i / g.per);
      x.drawImage(img, gap / 2 + col * (g.cell + gap), row * rowH + (rowH - g.cell) / 2, g.cell, g.cell);
    });
    x.globalCompositeOperation = 'source-in'; x.fillStyle = '#fff'; x.fillRect(0, 0, w, h);
    return c;
  }
  // Horizontal rules `t` px thick, one every `pitch` px, kept only where `mask` is drawn (everywhere when null).
  function rules(w, h, pitch, t, colour, mask) {
    var c = layer(w, h), x = c.getContext('2d');
    x.fillStyle = colour;
    for (var y = 0; y < h; y += pitch) x.fillRect(0, Math.round(y + (pitch - t) / 2), w, Math.max(1, Math.round(t)));
    if (mask) { x.globalCompositeOperation = 'destination-in'; x.drawImage(mask, 0, 0); }
    return c;
  }

  var drawnW = 0;
  function draw() {
    var dpr = Math.min(window.devicePixelRatio || 1, 2), w = Math.round(canvas.clientWidth * dpr), h = Math.round(canvas.clientHeight * dpr);
    if (!w || !h) return;
    drawnW = w; canvas.width = w; canvas.height = h;
    var colour = getComputedStyle(band).color, pitch = Math.min(5 * dpr, Math.max(3 * dpr, grid(w, h).cell / 22)), s = Math.max(2, h * 0.014);
    var glyphs = silhouettes(w, h);
    // the shadow side: glyph pixels whose neighbour down and right is outside the glyph (light from the top left)
    var shade = layer(w, h), sc = shade.getContext('2d');
    sc.drawImage(glyphs, 0, 0); sc.globalCompositeOperation = 'destination-out'; sc.drawImage(glyphs, -s, -s);
    ctx.clearRect(0, 0, w, h);
    ctx.globalAlpha = 0.28; ctx.drawImage(rules(w, h, pitch, dpr * 0.75, colour, null), 0, 0);
    ctx.globalAlpha = 1; ctx.drawImage(rules(w, h, pitch, pitch * 0.32, colour, glyphs), 0, 0);
    ctx.drawImage(rules(w, h, pitch, pitch * 0.6, colour, shade), 0, 0);
    // fade out toward the legal line
    var g = ctx.createLinearGradient(0, h * 0.88, 0, h);
    g.addColorStop(0, '#000'); g.addColorStop(1, 'rgba(0,0,0,0)');
    ctx.globalCompositeOperation = 'destination-in'; ctx.fillStyle = g; ctx.fillRect(0, 0, w, h);
    ctx.globalCompositeOperation = 'source-over';
  }
  band.classList.add('live');
  draw();
  imgs.forEach(function (i) { i.addEventListener('load', draw); });
  // iOS fires resize as the toolbar slides; only a width change needs a redraw
  window.addEventListener('resize', function () { if (Math.round(canvas.clientWidth * Math.min(window.devicePixelRatio || 1, 2)) !== drawnW) draw(); });
  matchMedia('(prefers-color-scheme: dark)').addEventListener('change', draw);
})();
