// Phone Photo School component kit: flat 2D shapes, two tones per object, teal = camera UI, yellow = the one key thing,
// red = wrong, green = right. Every component is a pure function of its arguments (no state between frames).
import { ctx, C, W, H, TAU, clamp, lerp, seg, eo, eob, rr, circle, ell, line } from './lib.js';

// ---------- backgrounds ----------
/** night-studio background: flat fill, soft dot grid, a big faint aperture turning in the corner */
export function studio(t, accent = C.panel) {
  ctx.fillStyle = C.bg; ctx.fillRect(-300, -300, W + 600, H + 600);
  ctx.fillStyle = C.bg2;
  for (let y = -60; y < H + 60; y += 72) for (let x = -60; x < W + 60; x += 72) { ctx.beginPath(); ctx.arc(x + ((y / 72) % 2) * 36, y, 4, 0, TAU); ctx.fill(); }
  aperture(930, 1720, 420, 0.55, t * 0.15, accent);
  aperture(120, 180, 260, 0.6, -t * 0.12, accent);
}

/** 6-blade aperture icon (the series motif). open 0..1 */
export function aperture(x, y, r, open, rot, color) {
  ctx.save(); ctx.translate(x, y); ctx.rotate(rot);
  ctx.beginPath(); ctx.arc(0, 0, r, 0, TAU); ctx.lineWidth = r * 0.08; ctx.strokeStyle = color; ctx.stroke();
  const ir = r * lerp(0.12, 0.62, open);
  for (let i = 0; i < 6; i++) {
    const a = (i / 6) * TAU, b = a + TAU / 6;
    ctx.beginPath(); ctx.moveTo(Math.cos(a) * ir, Math.sin(a) * ir); ctx.lineTo(Math.cos(a + 0.9) * r * 0.9, Math.sin(a + 0.9) * r * 0.9);
    ctx.lineTo(Math.cos(b) * ir, Math.sin(b) * ir); ctx.closePath(); ctx.fillStyle = color; ctx.globalAlpha *= 0.6; ctx.fill(); ctx.globalAlpha /= 0.6;
  }
  ctx.restore();
}

// ---------- the photo scene ----------
/** a flat landscape in local box (0,0,w,h): sky, sun, mountains, ground, a lone tree at subj (0..1 of width) */
export function scene(w, h, { subj = 0.5, t = 0, sunX = 0.3 } = {}) {
  const hz = h * 0.64;
  ctx.fillStyle = C.sky; ctx.fillRect(0, 0, w, hz);
  ctx.fillStyle = C.skyLow; ctx.fillRect(0, hz * 0.62, w, hz * 0.38);
  circle(w * sunX, h * 0.27, w * 0.085, C.sun);
  // clouds drift
  for (let i = 0; i < 2; i++) {
    const cx = ((w * (0.25 + i * 0.5) + t * 18 * (i + 1)) % (w * 1.3)) - w * 0.15, cy = h * (0.12 + i * 0.1), s = w * 0.05;
    ctx.fillStyle = C.white; ctx.beginPath();
    ctx.arc(cx, cy, s, 0, TAU); ctx.arc(cx + s * 1.1, cy - s * 0.4, s * 1.2, 0, TAU); ctx.arc(cx + s * 2.2, cy, s * 0.9, 0, TAU); ctx.fill();
    ctx.fillRect(cx, cy, s * 2.2, s * 0.9);
  }
  const ridge = (pts, col) => { ctx.beginPath(); ctx.moveTo(0, hz); pts.forEach(([a, b]) => ctx.lineTo(a * w, b * h)); ctx.lineTo(w, hz); ctx.closePath(); ctx.fillStyle = col; ctx.fill(); };
  ridge([[0, 0.5], [0.18, 0.38], [0.34, 0.5], [0.52, 0.33], [0.72, 0.48], [0.88, 0.4], [1, 0.47]], C.mtnFar);
  ridge([[0, 0.58], [0.22, 0.47], [0.4, 0.6], [0.62, 0.5], [0.82, 0.6], [1, 0.54]], C.mtnNear);
  ctx.fillStyle = C.ground; ctx.fillRect(0, hz, w, h - hz);
  ctx.fillStyle = C.groundDark; ctx.fillRect(0, hz + (h - hz) * 0.55, w, h);
  tree(subj * w, h * 0.8, h * 0.0011);
}

/** the subject: a lone round tree, base at (x, y) */
export function tree(x, y, s) {
  ell(x, y + 6 * s, 90 * s, 16 * s, 'rgba(0,0,0,0.18)');
  ctx.fillStyle = C.trunk; rr(x - 16 * s, y - 150 * s, 32 * s, 156 * s, 10 * s); ctx.fill();
  circle(x, y - 230 * s, 125 * s, C.leafDark);
  circle(x - 20 * s, y - 248 * s, 104 * s, C.leaf);
  circle(x + 52 * s, y - 280 * s, 30 * s, '#5BCB8A');
}

// ---------- phone + camera app ----------
export const PHONE = { w: 500, h: 1040 };
/** a flat phone (front), centred at (x, y). drawScreen(w, h) draws in screen-local coords, already clipped. */
export function phone(x, y, s, rot, drawScreen) {
  const w = PHONE.w * s, h = PHONE.h * s;
  ctx.save(); ctx.translate(x, y); ctx.rotate(rot);
  ell(0, h * 0.53, w * 0.42, h * 0.025, 'rgba(0,0,0,0.35)');                       // contact shadow
  ctx.fillStyle = C.phoneEdge; rr(-w / 2 - 6 * s, -h / 2 - 6 * s, w + 12 * s, h + 12 * s, 40 * s); ctx.fill();
  ctx.fillStyle = C.phoneEdgeHi; rr(w / 2 + 4 * s, -h * 0.26, 8 * s, 120 * s, 4 * s); ctx.fill();   // side keys
  ctx.fillStyle = C.phone; rr(-w / 2, -h / 2, w, h, 34 * s); ctx.fill();            // squared-off "ultra" corners
  const m = 14 * s, sw = w - 2 * m, sh = h - 2 * m;
  ctx.save(); ctx.translate(-w / 2 + m, -h / 2 + m); rr(0, 0, sw, sh, 24 * s); ctx.clip();
  drawScreen(sw, sh);
  ctx.restore();
  circle(0, -h / 2 + m + 26 * s, 9 * s, '#000');                                     // punch-hole camera
  ctx.restore();
}

/** the viewfinder rect inside a screen of size (w, h) */
export const viewfinder = (w, h) => ({ x: 0, y: h * 0.1, w, h: h * 0.68 });

/** camera app screen: viewfinder (scene + optional grid) and the UI chrome. o: { t, subj, grid, press, gearHi } */
export function cameraApp(w, h, o = {}) {
  const k = w / 472, v = viewfinder(w, h);
  ctx.fillStyle = '#000'; ctx.fillRect(0, 0, w, h);
  ctx.save(); ctx.translate(v.x, v.y); ctx.beginPath(); ctx.rect(0, 0, v.w, v.h); ctx.clip();
  scene(v.w, v.h, { subj: o.subj ?? 0.5, t: o.t ?? 0 });
  if (o.grid) grid(0, 0, v.w, v.h, o.grid, 3 * k, 'rgba(255,255,255,0.85)');
  ctx.restore();
  // top bar: gear, flash, ratio
  gear(48 * k, v.y / 2 + 6 * k, 20 * k, o.gearHi ? C.yellow : C.white, (o.t ?? 0) * (o.gearHi ? 3 : 0));
  ctx.strokeStyle = C.white; ctx.lineWidth = 4 * k; ctx.lineJoin = 'round';
  ctx.beginPath(); const fx = 150 * k, fy = v.y / 2 + 6 * k;                         // flash bolt
  ctx.moveTo(fx + 4 * k, fy - 18 * k); ctx.lineTo(fx - 8 * k, fy + 2 * k); ctx.lineTo(fx + 4 * k, fy + 2 * k); ctx.lineTo(fx - 4 * k, fy + 18 * k); ctx.stroke();
  ctx.font = `900 ${22 * k}px Inter`; ctx.fillStyle = C.white; ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
  ctx.fillText('3:4', 250 * k, fy); ctx.fillText('12M', 350 * k, fy);
  // zoom chips
  const zy = v.y + v.h - 48 * k;
  ['.6', '1x', '3', '5'].forEach((z, i) => {
    const zx = w / 2 + (i - 1.5) * 70 * k; circle(zx, zy, 26 * k, 'rgba(0,0,0,0.45)');
    ctx.fillStyle = z === '1x' ? C.yellow : C.white; ctx.font = `900 ${18 * k}px Inter`; ctx.fillText(z, zx, zy + 1);
  });
  // modes + shutter
  const by = v.y + v.h;
  ctx.font = `900 ${20 * k}px Inter`;
  [['PORTRAIT', -150], ['PHOTO', 0], ['VIDEO', 130], ['PRO', 235]].forEach(([m, dx]) => { ctx.fillStyle = m === 'PHOTO' ? C.yellow : '#BFC6D4'; ctx.fillText(m, w / 2 + dx * k, by + 40 * k); });
  const sx = w / 2, sy = by + (h - by) * 0.58, pr = o.press ?? 0;
  circle(sx, sy, 64 * k, C.white); circle(sx, sy, 54 * k, '#000'); circle(sx, sy, 48 * k * (1 - 0.15 * pr), pr > 0 ? '#DDE2EA' : C.white);
  ctx.fillStyle = '#3A4150'; rr(sx - 170 * k, sy - 30 * k, 60 * k, 60 * k, 14 * k); ctx.fill();          // gallery thumb
  circle(sx + 140 * k, sy, 34 * k, '#2A303B');                                                              // flip camera
  ctx.strokeStyle = C.white; ctx.lineWidth = 3.5 * k; ctx.beginPath(); ctx.arc(sx + 140 * k, sy, 15 * k, 0.4, 5.2); ctx.stroke();
}

/** settings screen sliding in from the right (p 0..1); the "Grid lines" row highlights (hl 0..1) and its toggle turns on (on 0..1) */
export function settings(w, h, p, hl, on) {
  if (p <= 0) return;
  const k = w / 472, x0 = (1 - eo(p)) * w;
  ctx.save(); ctx.translate(x0, 0);
  ctx.fillStyle = C.bg2; ctx.fillRect(0, 0, w, h);
  ctx.fillStyle = C.white; ctx.font = `900 ${34 * k}px Inter`; ctx.textAlign = 'left'; ctx.textBaseline = 'middle';
  line([[48 * k, 80 * k], [32 * k, 96 * k], [48 * k, 112 * k]], C.white, 5 * k);
  ctx.fillText('Camera settings', 70 * k, 98 * k);
  const rows = ['Picture formats', 'Shooting methods', 'Grid lines', 'Location tags', 'Shutter sound', 'Watermark'];
  rows.forEach((r, i) => {
    const y = 190 * k + i * 112 * k, isGrid = r === 'Grid lines';
    if (isGrid && hl > 0) { ctx.globalAlpha = hl; ctx.fillStyle = C.panel2; rr(16 * k, y - 46 * k, w - 32 * k, 92 * k, 22 * k); ctx.fill();
      ctx.strokeStyle = C.yellow; ctx.lineWidth = 4 * k; ctx.stroke(); ctx.globalAlpha = 1; }
    ctx.fillStyle = isGrid ? C.white : '#9AA3B5'; ctx.font = `900 ${28 * k}px Inter`; ctx.fillText(r, 44 * k, y);
    if (isGrid) toggle(w - 90 * k, y, k, on);
    else if (i !== 0 && i !== 1) toggle(w - 90 * k, y, k, i === 3 ? 0 : 1, true);
    else line([[w - 70 * k, y - 12 * k], [w - 56 * k, y], [w - 70 * k, y + 12 * k]], '#6B7385', 4 * k);
  });
  ctx.restore();
}

/** a switch, on 0..1 (animated), dim = greyed */
export function toggle(x, y, k, on, dim = false) {
  const w = 84 * k, h = 46 * k;
  ctx.fillStyle = dim ? (on ? '#3D6E8F' : '#3A4150') : on > 0.5 ? C.teal : '#4A5263';
  rr(x - w / 2, y - h / 2, w, h, h / 2); ctx.fill();
  circle(x - w / 2 + h / 2 + (w - h) * eo(clamp(on)), y, h * 0.38, dim ? '#C9CED8' : C.white);
}

/** settings gear icon */
export function gear(x, y, r, color, rot = 0) {
  ctx.save(); ctx.translate(x, y); ctx.rotate(rot); ctx.fillStyle = color;
  for (let i = 0; i < 8; i++) { ctx.save(); ctx.rotate((i / 8) * TAU); ctx.fillRect(-r * 0.22, -r * 1.15, r * 0.44, r * 0.5); ctx.restore(); }
  ctx.beginPath(); ctx.arc(0, 0, r * 0.85, 0, TAU); ctx.fill();
  circle(0, 0, r * 0.36, '#000');
  ctx.restore();
}

// ---------- composition graphics ----------
/** rule-of-thirds grid inside (x, y, w, h); p 0..1 draws the lines in */
export function grid(x, y, w, h, p, lw, color) {
  ctx.save(); ctx.strokeStyle = color; ctx.lineWidth = lw; ctx.lineCap = 'round';
  for (let i = 1; i <= 2; i++) {
    const q = eo(seg(p, (i - 1) * 0.2, 0.6 + (i - 1) * 0.2));
    ctx.beginPath(); ctx.moveTo(x + (w * i) / 3, y); ctx.lineTo(x + (w * i) / 3, y + h * q); ctx.stroke();
    ctx.beginPath(); ctx.moveTo(x, y + (h * i) / 3); ctx.lineTo(x + w * q, y + (h * i) / 3); ctx.stroke();
  }
  ctx.restore();
}

/** a glowing "power point" where two grid lines cross */
export function hotspot(x, y, s, p, t) {
  if (p <= 0) return;
  const sc = eob(clamp(p)) * s, pulse = 0.5 + 0.5 * Math.sin(t * 9);
  ctx.save(); ctx.globalAlpha = 0.35 * (1 - pulse); circle(x, y, 44 * sc * (1 + pulse * 0.6), C.yellow); ctx.restore();
  circle(x, y, 22 * sc, C.yellow); circle(x, y, 9 * sc, C.ink);
}

/** tap ripple (p 0..1 over the tap) with a fingertip dot */
export function tap(x, y, p, s = 1) {
  if (p <= 0 || p >= 1) return;
  ctx.save(); ctx.globalAlpha = 1 - p; ctx.strokeStyle = C.white; ctx.lineWidth = 6 * s;
  ctx.beginPath(); ctx.arc(x, y, (20 + 70 * eo(p)) * s, 0, TAU); ctx.stroke(); ctx.restore();
  ctx.save(); ctx.globalAlpha = Math.min(1, (1 - p) * 2) * 0.9; circle(x, y, 26 * s, 'rgba(255,255,255,0.75)'); ctx.restore();
}

/** a big red X (wrong). s = scale, a = alpha */
export function redX(x, y, s, a = 1) {
  if (a <= 0) return;
  ctx.save(); ctx.globalAlpha = a; ctx.translate(x, y); ctx.scale(s, s); ctx.lineCap = 'round';
  for (const [w, c] of [[64, C.ink], [44, C.red]]) {
    ctx.strokeStyle = c; ctx.lineWidth = w; ctx.beginPath(); ctx.moveTo(-110, -110); ctx.lineTo(110, 110); ctx.moveTo(110, -110); ctx.lineTo(-110, 110); ctx.stroke();
  }
  ctx.restore();
}

/** a green check badge (right) */
export function check(x, y, s, a = 1) {
  if (a <= 0 || s <= 0) return;
  ctx.save(); ctx.globalAlpha = a; ctx.translate(x, y); ctx.scale(s, s);
  circle(0, 6, 92, C.ink); circle(0, 0, 90, C.green);
  line([[-42, 2], [-12, 34], [46, -30]], C.white, 22);
  ctx.restore();
}

/** a rounded label pill, centred */
export function pill(text, x, y, size, bg = C.yellow, fg = C.ink, sc = 1) {
  if (sc <= 0) return;
  ctx.save(); ctx.translate(x, y); ctx.scale(sc, sc);
  ctx.font = `900 ${size}px Inter`; ctx.letterSpacing = `${size * 0.04}px`;
  const tw = ctx.measureText(text).width, pw = tw + size * 1.1, ph = size * 1.7;
  ctx.fillStyle = C.ink; rr(-pw / 2, -ph / 2 + size * 0.12, pw, ph, ph / 2); ctx.fill();
  ctx.fillStyle = bg; rr(-pw / 2, -ph / 2, pw, ph, ph / 2); ctx.fill();
  ctx.fillStyle = fg; ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.fillText(text, size * 0.02, size * 0.06);
  ctx.letterSpacing = '0px'; ctx.restore();
}

/** the series badge at the top of every video: "PHONE PHOTO SCHOOL" + lesson chip */
export function seriesBadge(lesson, p = 1) {
  if (p <= 0) return;
  ctx.save(); ctx.globalAlpha = clamp(p * 2); ctx.translate(0, lerp(-60, 0, eo(clamp(p))));
  ctx.font = '900 34px Inter'; ctx.letterSpacing = '4px'; ctx.textBaseline = 'middle'; ctx.textAlign = 'left';
  const label = 'PHONE PHOTO SCHOOL', tw = ctx.measureText(label).width, chip = `L${String(lesson).padStart(2, '0')}`;
  ctx.font = '900 30px Inter'; const cw = ctx.measureText(chip).width + 36;
  const total = 56 + tw + 20 + cw, x0 = 540 - total / 2, y = 205;
  ctx.fillStyle = 'rgba(10,12,16,0.75)'; rr(x0 - 22, y - 38, total + 44, 76, 38); ctx.fill();
  aperture(x0 + 22, y, 22, 0.5, 0, C.teal);
  ctx.font = '900 34px Inter'; ctx.fillStyle = C.white; ctx.fillText(label, x0 + 56, y + 2);
  ctx.font = '900 30px Inter'; ctx.fillStyle = C.teal; rr(x0 + 56 + tw + 20, y - 24, cw, 48, 24); ctx.fill();
  ctx.fillStyle = C.ink; ctx.textAlign = 'center'; ctx.fillText(chip, x0 + 56 + tw + 20 + cw / 2, y + 2);
  ctx.letterSpacing = '0px'; ctx.restore();
}

/** "shot on" chip, bottom of the phone shots */
export function shotOn(text, x, y, a = 1) {
  if (a <= 0) return;
  ctx.save(); ctx.globalAlpha = a; ctx.font = '900 26px Inter'; ctx.letterSpacing = '3px'; ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
  ctx.fillStyle = C.mute; ctx.fillText(text, x, y); ctx.letterSpacing = '0px'; ctx.restore();
}

/** a full-frame white shutter flash, a 0..1 */
export function flash(a) { if (a <= 0) return; ctx.save(); ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.globalAlpha = a; ctx.fillStyle = C.white; ctx.fillRect(0, 0, W, H); ctx.restore(); }

/** a framed photo print (white border), centred, with the scene inside */
export function print(x, y, w, h, rot, subj, t) {
  ctx.save(); ctx.translate(x, y); ctx.rotate(rot);
  ctx.fillStyle = 'rgba(0,0,0,0.35)'; rr(-w / 2 + 14, -h / 2 + 18, w, h, 18); ctx.fill();
  ctx.fillStyle = C.white; rr(-w / 2, -h / 2, w, h, 18); ctx.fill();
  const m = w * 0.05; ctx.save(); ctx.translate(-w / 2 + m, -h / 2 + m); ctx.beginPath(); ctx.rect(0, 0, w - 2 * m, h - 2 * m - m * 2); ctx.clip();
  scene(w - 2 * m, h - 2 * m - m * 2, { subj, t }); ctx.restore();
  ctx.restore();
}
