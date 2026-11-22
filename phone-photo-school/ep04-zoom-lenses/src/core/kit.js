// Phone Photo School component kit: flat 2D shapes, two tones per object, teal = camera UI, yellow = the one key thing,
// red = wrong, green = right. Every component is a pure function of its arguments (no state between frames).
import { ctx, setCtx, C, W, H, TAU, clamp, lerp, seg, eo, eob, rr, circle, ell, line } from './lib.js';

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
/** a flat landscape in local box (0,0,w,h). Options:
 *  subj (0..1 tree x) · treeY (base, 0..1 of h, default .8) · treeS (size mult) · t (cloud drift) · sunX
 *  zoom + zx/zy (view centre, 0..1): crop into the scene like a longer lens · blur (px, background) · bright (1 = normal exposure)
 *  flower {x, y, s, blur}: a foreground flower (own blur) · haze 0..1: greasy-lens glow · person {x, y, s} · balloon {x, y, s}
 *  road {vx}: a road running to the vanishing point x = vx (0..1, may be off-frame) */
export function scene(w, h, o = {}) {
  const { subj = 0.5, t = 0, sunX = 0.3, zoom = 1, blur = 0, bright = 1, haze = 0 } = o;
  const hz = h * (o.hz ?? 0.64), dy = hz - h * 0.64;            // o.hz moves the horizon (0..1)
  ctx.save(); ctx.beginPath(); ctx.rect(0, 0, w, h); ctx.clip();
  const f = []; if (blur > 0.2) f.push(`blur(${blur}px)`); if (bright !== 1) f.push(`brightness(${bright})`); if (haze > 0) f.push(`blur(${haze * 5}px)`, `contrast(${1 - haze * 0.3})`);
  if (f.length) ctx.filter = f.join(' ');
  if (zoom !== 1) {
    const half = 0.5 / zoom, cx = clamp(o.zx ?? 0.5, half, 1 - half), cy = clamp(o.zy ?? 0.5, half, 1 - half);
    ctx.translate(w / 2, h / 2); ctx.scale(zoom, zoom); ctx.translate(-cx * w, -cy * h);
  }
  ctx.fillStyle = C.sky; ctx.fillRect(0, 0, w, hz);
  ctx.fillStyle = C.skyLow; ctx.fillRect(0, hz * 0.62, w, hz * 0.38);
  circle(w * sunX, h * 0.27 + dy, w * 0.085, C.sun);
  for (let i = 0; i < 2; i++) {
    const cx = ((w * (0.25 + i * 0.5) + t * 18 * (i + 1)) % (w * 1.3)) - w * 0.15, cy = h * (0.12 + i * 0.1), s = w * 0.05;
    ctx.fillStyle = C.white; ctx.beginPath();
    ctx.arc(cx, cy, s, 0, TAU); ctx.arc(cx + s * 1.1, cy - s * 0.4, s * 1.2, 0, TAU); ctx.arc(cx + s * 2.2, cy, s * 0.9, 0, TAU); ctx.fill();
    ctx.fillRect(cx, cy, s * 2.2, s * 0.9);
  }
  if (o.balloon) balloon(o.balloon.x * w, o.balloon.y * h + Math.sin(t * 1.5) * h * 0.004, o.balloon.s * w);
  const ridge = (pts, col) => { ctx.beginPath(); ctx.moveTo(0, hz); pts.forEach(([a, b]) => ctx.lineTo(a * w, b * h + dy)); ctx.lineTo(w, hz); ctx.closePath(); ctx.fillStyle = col; ctx.fill(); };
  ridge([[0, 0.5], [0.18, 0.38], [0.34, 0.5], [0.52, 0.33], [0.72, 0.48], [0.88, 0.4], [1, 0.47]], C.mtnFar);
  ridge([[0, 0.58], [0.22, 0.47], [0.4, 0.6], [0.62, 0.5], [0.82, 0.6], [1, 0.54]], C.mtnNear);
  ctx.fillStyle = C.ground; ctx.fillRect(0, hz, w, h - hz);
  ctx.fillStyle = C.groundDark; ctx.fillRect(0, hz + (h - hz) * 0.55, w, h);
  if (o.road) road(w, h, hz, o.road.vx, o.road.spread ?? 0);
  tree(subj * w, h * (o.treeY ?? 0.8), h * 0.0011 * (o.treeS ?? 1));
  if (o.person) person(o.person.x * w, o.person.y * h, o.person.s * h);
  ctx.filter = 'none';
  if (o.flower) { const fl = o.flower; if (fl.blur > 0.2) ctx.filter = `blur(${fl.blur}px)${bright !== 1 ? ` brightness(${bright})` : ''}`; else if (bright !== 1) ctx.filter = `brightness(${bright})`;
    flower(fl.x * w, fl.y * h, fl.s * h); ctx.filter = 'none'; }
  if (haze > 0) {                                                  // greasy lens: milky veil + blooming sun
    ctx.globalAlpha = 0.28 * haze; ctx.fillStyle = '#FFF6E0'; ctx.fillRect(0, 0, w, h);
    for (let i = 1; i <= 4; i++) { ctx.globalAlpha = 0.16 * haze; circle(w * sunX, h * 0.27, w * 0.085 * (1 + i * 0.6), '#FFF1C2'); }
    ctx.globalAlpha = 1;
  }
  ctx.restore();
}

/** a road from the bottom of the frame to the vanishing point x = vx*w on the horizon */
export function road(w, h, hz, vx, spread = 0) {
  const ax = vx * w, ay = hz + h * 0.005, bl = w * (0.12 - spread), br = w * (0.98 + spread);
  ctx.fillStyle = '#5C6478'; ctx.beginPath(); ctx.moveTo(bl, h); ctx.lineTo(ax - w * 0.006, ay); ctx.lineTo(ax + w * 0.006, ay); ctx.lineTo(br, h); ctx.closePath(); ctx.fill();
  ctx.fillStyle = '#6E778C'; ctx.beginPath(); ctx.moveTo(bl, h); ctx.lineTo(ax - w * 0.006, ay); ctx.lineTo(ax, ay); ctx.lineTo((bl + br) / 2, h); ctx.closePath(); ctx.fill();
  const mx = (bl + br) / 2;                                        // centre dashes, shrinking with distance
  for (let i = 0; i < 9; i++) {
    const u0 = Math.pow(i / 9, 1.6), u1 = Math.pow((i + 0.5) / 9, 1.6);
    const p = (u) => [lerp(mx, ax, u), lerp(h, ay, u)], [x0, y0] = p(u0), [x1, y1] = p(u1);
    ctx.strokeStyle = C.yellow; ctx.lineWidth = lerp(w * 0.018, w * 0.002, u0); ctx.lineCap = 'butt'; ctx.beginPath(); ctx.moveTo(x0, y0); ctx.lineTo(x1, y1); ctx.stroke();
  }
}
export const roadEdges = (w, h, vx, spread = 0, hzF = 0.64) => { const hz = h * hzF; return [[[w * (0.12 - spread), h], [vx * w, hz]], [[w * (0.98 + spread), h], [vx * w, hz]]]; };

/** a foreground flower (stem + petals), base at (x, y), s ≈ height */
export function flower(x, y, s) {
  line([[x, y], [x + s * 0.03, y - s * 0.55], [x, y - s * 0.8]], '#2E8B4E', s * 0.05);
  ell(x + s * 0.12, y - s * 0.45, s * 0.12, s * 0.05, '#3FA45E', -0.5);
  for (let i = 0; i < 6; i++) { const a = (i / 6) * TAU; ell(x + Math.cos(a) * s * 0.13, y - s * 0.8 + Math.sin(a) * s * 0.13, s * 0.12, s * 0.075, i % 2 ? '#FF7A93' : '#FF5C7A', a); }
  circle(x, y - s * 0.8, s * 0.09, C.yellow); circle(x - s * 0.025, y - s * 0.82, s * 0.03, '#FFE28A');
}

/** a simple standing person, feet at (x, y), s ≈ height */
export function person(x, y, s) {
  ell(x, y, s * 0.16, s * 0.025, 'rgba(0,0,0,0.2)');
  ctx.fillStyle = '#2B3A5C'; rr(x - s * 0.09, y - s * 0.42, s * 0.18, s * 0.42, s * 0.03); ctx.fill();   // legs
  ctx.fillStyle = '#E2574C'; rr(x - s * 0.13, y - s * 0.75, s * 0.26, s * 0.38, s * 0.08); ctx.fill();   // jacket
  ctx.fillStyle = '#C94238'; rr(x - s * 0.13, y - s * 0.75, s * 0.07, s * 0.38, s * 0.04); ctx.fill();
  circle(x, y - s * 0.86, s * 0.11, '#E8B89A');                                                           // head
  ctx.fillStyle = '#3B2A20'; ctx.beginPath(); ctx.arc(x, y - s * 0.88, s * 0.115, Math.PI * 1.05, Math.PI * 1.95); ctx.fill();
  circle(x - s * 0.04, y - s * 0.85, s * 0.012, C.ink); circle(x + s * 0.04, y - s * 0.85, s * 0.012, C.ink);
  ctx.strokeStyle = C.ink; ctx.lineWidth = s * 0.01; ctx.beginPath(); ctx.arc(x, y - s * 0.81, s * 0.035, 0.3, Math.PI - 0.3); ctx.stroke();
}

/** a hot-air balloon (a far-away detail), centre (x, y), s = radius */
export function balloon(x, y, s) {
  ctx.fillStyle = '#E2574C'; ctx.beginPath(); ctx.ellipse(x, y, s, s * 1.15, 0, 0, TAU); ctx.fill();
  ctx.fillStyle = C.yellow; ctx.beginPath(); ctx.ellipse(x, y, s * 0.42, s * 1.15, 0, 0, TAU); ctx.fill();
  ctx.fillStyle = '#E2574C'; ctx.beginPath(); ctx.ellipse(x, y, s * 0.12, s * 1.15, 0, 0, TAU); ctx.fill();
  line([[x - s * 0.5, y + s * 1.0], [x - s * 0.25, y + s * 1.55]], C.ink, s * 0.05); line([[x + s * 0.5, y + s * 1.0], [x + s * 0.25, y + s * 1.55]], C.ink, s * 0.05);
  ctx.fillStyle = C.trunk; rr(x - s * 0.28, y + s * 1.5, s * 0.56, s * 0.4, s * 0.06); ctx.fill();
}

/** the subject: a lone round tree, base at (x, y) */
export function tree(x, y, s) {
  if (s <= 0) return;
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
  scene(v.w, v.h, { subj: o.subj ?? 0.5, t: o.t ?? 0, ...(o.scene || {}) });
  if (o.grid) grid(0, 0, v.w, v.h, o.grid, 3 * k, 'rgba(255,255,255,0.85)');
  if (o.over) o.over(v.w, v.h, k);
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
    ctx.fillStyle = z === (o.zoomSel ?? '1x') ? C.yellow : C.white; ctx.font = `900 ${18 * k}px Inter`; ctx.fillText(z, zx, zy + 1);
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

// ---------- shared episode pieces ----------
export const HANDLE = '@the_linse_art';                         // shown on every end card
export const FRAME = { x: 100, y: 300, w: 880, h: 910 };            // the big viewfinder in demo shots
/** big viewfinder: scene + optional grid + focus brackets at (bx, by) fractions; over(w, h) draws on top in frame coords */
export function finder(t, sceneOpts = {}, { grid: g = 0, brackets = null, over = null, frame = FRAME } = {}) {
  const { x, y, w, h } = frame;
  ctx.fillStyle = C.ink; rr(x - 14, y - 14, w + 28, h + 28, 46); ctx.fill();
  ctx.save(); rr(x, y, w, h, 34); ctx.clip(); ctx.translate(x, y);
  if (sceneOpts.pixel > 1) pixelScene(w, h, { t, ...sceneOpts }, sceneOpts.pixel); else scene(w, h, { t, ...sceneOpts });
  if (g) grid(0, 0, w, h, g, 6, 'rgba(255,255,255,0.9)');
  if (over) over(w, h);
  ctx.restore();
  if (brackets) {
    const bx = x + brackets[0] * w, by = y + brackets[1] * h, s = brackets[2] ?? 120;
    ctx.strokeStyle = C.yellow; ctx.lineWidth = 8; ctx.lineCap = 'round';
    for (const [sx, sy] of [[-1, -1], [1, -1], [1, 1], [-1, 1]]) {
      ctx.beginPath(); ctx.moveTo(bx + sx * s, by + sy * s - sy * 40); ctx.lineTo(bx + sx * s, by + sy * s); ctx.lineTo(bx + sx * s - sx * 40, by + sy * s); ctx.stroke();
    }
  }
}

/** shot 2 of every episode: LESSON + big number (lands at numAt) + topic pill (lands at titleAt). lt = time in shot */
export function lessonCard(lt, t, n, title, numAt, titleAt) {
  studio(t, C.panel2);
  grid(0, 0, W, H, seg(lt, 0, 0.9), 6, C.teal);
  ctx.font = '900 64px Inter'; ctx.letterSpacing = '14px'; ctx.textAlign = 'center'; ctx.textBaseline = 'alphabetic'; ctx.fillStyle = C.mute;
  ctx.globalAlpha = seg(lt, 0, 0.25); ctx.fillText('LESSON', 552, 470); ctx.globalAlpha = 1; ctx.letterSpacing = '0px';
  if (lt > numAt - 0.05) bigLabel(String(n).padStart(2, '0'), 540, 730, 400, lerp(1.8, 1, eob(seg(lt, numAt - 0.05, numAt + 0.2))));
  pill(title, 540, 1060, title.length > 12 ? 70 : 84, C.yellow, C.ink, eob(seg(lt, titleAt - 0.05, titleAt + 0.25)));
}
function bigLabel(text, x, y, size, sc) {
  ctx.save(); ctx.translate(x, y); ctx.rotate(-0.04); ctx.scale(sc, sc);
  ctx.font = `900 ${size}px Inter`; ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.lineJoin = 'round';
  ctx.lineWidth = size * 0.2; ctx.strokeStyle = C.ink; ctx.strokeText(text, 0, 0); ctx.fillStyle = C.white; ctx.fillText(text, 0, 0); ctx.restore();
}

/** last shot of every episode: creator avatar + handle, + FOLLOW (pops at fol) and the next-lesson card (at nxt) */
export function endCard(lt, t, fol, nxt, nextN, nextTitle) {
  studio(t, C.panel2);
  avatar(540, 480, 175, eob(seg(lt, 0.05, 0.4)));
  const hq = eo(seg(lt, 0.25, 0.55));
  if (hq > 0) {
    ctx.save(); ctx.globalAlpha = hq; ctx.font = '900 54px Inter'; ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
    ctx.fillStyle = C.white; ctx.fillText(HANDLE, 540, 725 + lerp(20, 0, hq)); ctx.restore();
  }
  const sc = eob(seg(lt, fol - 0.1, fol + 0.2)) * (1 + 0.04 * Math.sin(Math.max(0, lt - fol) * 8));
  if (sc > 0) {
    ctx.save(); ctx.translate(540, 865); ctx.scale(sc, sc);
    ctx.fillStyle = C.ink; rr(-240, -70, 480, 150, 75); ctx.fill();
    ctx.fillStyle = C.yellow; rr(-240, -80, 480, 150, 75); ctx.fill();
    ctx.fillStyle = C.ink; ctx.font = '900 76px Inter'; ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.fillText('+ FOLLOW', 0, -4);
    ctx.restore();
  }
  const q = eo(seg(lt, nxt - 0.1, nxt + 0.35));
  if (q > 0) {
    ctx.save(); ctx.globalAlpha = q; ctx.translate(0, lerp(60, 0, q));
    ctx.fillStyle = C.panel; rr(150, 995, 780, 190, 36); ctx.fill();
    ctx.fillStyle = C.teal; ctx.font = '900 40px Inter'; ctx.letterSpacing = '6px'; ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
    ctx.fillText(`NEXT · LESSON ${String(nextN).padStart(2, '0')}`, 540, 1050); ctx.letterSpacing = '0px';
    ctx.fillStyle = C.white; ctx.font = '900 62px Inter'; ctx.fillText(nextTitle, 540, 1125);
    ctx.restore();
  }
}

// ---------- focus + exposure ----------
/** the focus ring (yellow circle with ticks). p 0..1 = appear (shrinks onto the subject) */
export function focusRing(x, y, r, p, color = C.yellow) {
  if (p <= 0) return;
  const rr_ = r * lerp(1.6, 1, eo(clamp(p)));
  ctx.save(); ctx.globalAlpha = clamp(p * 3); ctx.strokeStyle = color; ctx.lineWidth = r * 0.07;
  ctx.beginPath(); ctx.arc(x, y, rr_, 0, TAU); ctx.stroke();
  for (let i = 0; i < 4; i++) { const a = (i / 4) * TAU; line([[x + Math.cos(a) * rr_, y + Math.sin(a) * rr_], [x + Math.cos(a) * rr_ * 0.82, y + Math.sin(a) * rr_ * 0.82]], color, r * 0.07); }
  ctx.restore();
}
/** sun icon */
export function sunIcon(x, y, r, color = C.yellow) {
  circle(x, y, r * 0.5, color);
  for (let i = 0; i < 8; i++) { const a = (i / 8) * TAU; line([[x + Math.cos(a) * r * 0.72, y + Math.sin(a) * r * 0.72], [x + Math.cos(a) * r, y + Math.sin(a) * r]], color, r * 0.16); }
}
/** brightness slider: vertical track of length len centred at (x, y); val -1 (down/darker) .. 1 (up/brighter); a = alpha */
export function sunSlider(x, y, len, val, a = 1, r = 34) {
  if (a <= 0) return;
  ctx.save(); ctx.globalAlpha = a;
  line([[x, y - len / 2], [x, y + len / 2]], 'rgba(255,255,255,0.85)', r * 0.14);
  const sy = y - (val * len) / 2; circle(sx(x), sy, r * 1.15, 'rgba(10,12,16,0.55)'); sunIcon(x, sy, r);
  ctx.restore();
  function sx(v) { return v; }
}

// ---------- the lens episodes ----------
/** the back of the phone with the quad camera: ultra-wide, wide, 3x (left column) + 5x (right). smudge 0..1 on the top lens */
export function phoneBack(x, y, s, rot, { smudge = 0, glow = [] } = {}) {
  const w = PHONE.w * s, h = PHONE.h * s;
  ctx.save(); ctx.translate(x, y); ctx.rotate(rot);
  ell(0, h * 0.53, w * 0.42, h * 0.025, 'rgba(0,0,0,0.35)');
  ctx.fillStyle = C.phoneEdge; rr(-w / 2 - 6 * s, -h / 2 - 6 * s, w + 12 * s, h + 12 * s, 40 * s); ctx.fill();
  ctx.fillStyle = '#2C3342'; rr(-w / 2, -h / 2, w, h, 34 * s); ctx.fill();
  ctx.fillStyle = '#323A4B'; rr(-w / 2, -h / 2, w * 0.5, h, 34 * s); ctx.fill();
  LENSES(s).forEach((L, i) => lens(L[0], L[1], 58 * s, i === 0 ? smudge : 0, glow[i] ?? 0));
  circle(LENSES(s)[3][0], -h / 2 + 410 * s, 14 * s, '#E8E2C8');                         // flash
  ctx.restore();
}
/** lens centres (phone-local) for phoneBack at scale s: [ultra-wide, wide, 3x, 5x] */
export const LENSES = (s) => [[-150 * s, -400 * s], [-150 * s, -265 * s], [-150 * s, -130 * s], [-20 * s, -330 * s]];
/** one camera lens, r = outer radius. smudge 0..1 = greasy fingerprint, glow 0..1 = highlight ring */
export function lens(x, y, r, smudge = 0, glow = 0) {
  if (glow > 0) { ctx.save(); ctx.globalAlpha = glow; circle(x, y, r * 1.25, C.yellow); ctx.restore(); }
  circle(x, y, r, '#7C869A'); circle(x, y, r * 0.86, '#11151D'); circle(x, y, r * 0.6, '#1D2C4A');
  circle(x, y, r * 0.34, '#0A0E16'); circle(x - r * 0.22, y - r * 0.24, r * 0.12, 'rgba(255,255,255,0.8)'); circle(x + r * 0.2, y + r * 0.22, r * 0.05, 'rgba(255,255,255,0.5)');
  if (smudge > 0) fingerprint(x + r * 0.08, y + r * 0.05, r * 0.75, smudge);
}
/** an oily fingerprint smear */
export function fingerprint(x, y, r, a) {
  ctx.save(); ctx.globalAlpha = a * 0.5; ell(x, y, r, r * 1.15, '#E6D6A0', 0.3);
  ctx.globalAlpha = a * 0.75; ctx.strokeStyle = '#F6EAC0'; ctx.lineWidth = r * 0.06;
  for (let i = 1; i <= 5; i++) { ctx.beginPath(); ctx.ellipse(x, y, r * i * 0.18, r * i * 0.22, 0.3, 3.6, 8.6); ctx.stroke(); }
  ctx.restore();
}
/** a fingertip (from below), tip at (x, y), s = width */
export function finger(x, y, s, rot = 0) {
  ctx.save(); ctx.translate(x, y); ctx.rotate(rot);
  ctx.fillStyle = '#D49C7E'; rr(-s / 2 - 4, -4, s + 8, s * 4, s / 2); ctx.fill();
  ctx.fillStyle = '#E8B89A'; rr(-s / 2, 0, s, s * 4, s / 2); ctx.fill();
  ctx.fillStyle = '#F4D3C1'; rr(-s * 0.3, s * 0.12, s * 0.6, s * 0.55, s * 0.25); ctx.fill();
  ctx.restore();
}
/** a microfiber cloth, centre (x, y), s scale */
export function cloth(x, y, s, rot = 0) {
  ctx.save(); ctx.translate(x, y); ctx.rotate(rot); ctx.scale(s, s);
  ctx.fillStyle = '#2F5FC4'; rr(-150, -100, 300, 210, 30); ctx.fill();
  ctx.fillStyle = '#4C7EE6'; rr(-150, -110, 300, 200, 30); ctx.fill();
  ctx.fillStyle = '#6A97F0'; for (let i = 0; i < 4; i++) { rr(-120 + i * 70, -90, 22, 160, 11); ctx.fill(); }
  ctx.restore();
}
/** a flat t-shirt, centre (x, y), s scale */
export function shirt(x, y, s, color = '#E2574C') {
  ctx.save(); ctx.translate(x, y); ctx.scale(s, s); ctx.fillStyle = color;
  ctx.beginPath(); ctx.moveTo(-60, -120); ctx.lineTo(-160, -70); ctx.lineTo(-120, 10); ctx.lineTo(-90, -5); ctx.lineTo(-90, 140); ctx.lineTo(90, 140);
  ctx.lineTo(90, -5); ctx.lineTo(120, 10); ctx.lineTo(160, -70); ctx.lineTo(60, -120); ctx.quadraticCurveTo(0, -70, -60, -120); ctx.fill();
  ctx.fillStyle = 'rgba(0,0,0,0.15)'; ctx.fillRect(-90, 100, 180, 40);
  ctx.restore();
}

/** yellow arrows drawn along lines (each [[x0,y0],[x1,y1]]), p 0..1 = how far they've run */
export function leadArrows(lines, p, lw = 12, color = C.yellow) {
  if (p <= 0) return;
  for (const [[x0, y0], [x1, y1]] of lines) {
    const q = eo(clamp(p)), x = lerp(x0, x1, q * 0.92), y = lerp(y0, y1, q * 0.92), a = Math.atan2(y1 - y0, x1 - x0);
    ctx.save(); ctx.strokeStyle = C.ink; ctx.lineWidth = lw + 8; ctx.lineCap = 'round';
    ctx.beginPath(); ctx.moveTo(x0, y0); ctx.lineTo(x, y); ctx.stroke(); ctx.strokeStyle = color; ctx.lineWidth = lw; ctx.stroke();
    ctx.fillStyle = color; ctx.translate(x, y); ctx.rotate(a); ctx.beginPath(); ctx.moveTo(lw * 2.6, 0); ctx.lineTo(-lw * 1.2, -lw * 2); ctx.lineTo(-lw * 1.2, lw * 2); ctx.closePath();
    ctx.lineWidth = 6; ctx.strokeStyle = C.ink; ctx.stroke(); ctx.fill(); ctx.restore();
  }
}

/** the creator avatar (flat cartoon from the profile photo: rust beanie, dark puffer jacket, camera up to the eye),
 *  centre (x, y), radius r, sc = pop-in scale */
export function avatar(x, y, r, sc = 1) {
  if (sc <= 0) return;
  ctx.save(); ctx.translate(x, y); ctx.scale(sc * r / 160, sc * r / 160);
  circle(0, 8, 172, C.ink); circle(0, 0, 172, C.teal);
  ctx.save(); ctx.beginPath(); ctx.arc(0, 0, 160, 0, TAU); ctx.clip();
  ctx.fillStyle = '#CFE3EC'; ctx.fillRect(-170, -170, 340, 340);                         // pale wall
  ctx.fillStyle = '#C8742E'; ctx.fillRect(72, -170, 100, 340);                            // warm wood door
  ctx.fillStyle = '#A85E22'; ctx.fillRect(96, -170, 7, 340);
  const skin = '#C98B67', skinD = '#A86F50', jacket = '#2A2326', jacketHi = '#3B3135';
  ctx.fillStyle = jacket; ctx.beginPath(); ctx.moveTo(-170, 170); ctx.lineTo(-155, 70); ctx.quadraticCurveTo(-120, 30, -55, 26);
  ctx.lineTo(55, 26); ctx.quadraticCurveTo(120, 30, 155, 70); ctx.lineTo(170, 170); ctx.closePath(); ctx.fill();
  ctx.strokeStyle = jacketHi; ctx.lineWidth = 6; ctx.lineCap = 'round';
  for (const yy of [92, 132]) { ctx.beginPath(); ctx.moveTo(-150, yy); ctx.quadraticCurveTo(-90, yy - 12, -40, yy + 4); ctx.stroke(); }
  ell(-6, 32, 40, 14, '#1E191B');                                                         // collar
  ell(-10, -28, 58, 68, skin); circle(-67, -22, 12, skinD);                              // head + ear
  ctx.fillStyle = '#B5532E'; ctx.beginPath(); ctx.arc(-10, -52, 66, Math.PI, 0); ctx.lineTo(56, -46); ctx.lineTo(-76, -46); ctx.closePath(); ctx.fill();
  ctx.fillStyle = '#9A4325'; rr(-80, -62, 140, 22, 10); ctx.fill();                       // beanie fold
  ctx.fillStyle = jacket; ctx.beginPath(); ctx.moveTo(30, 170); ctx.lineTo(92, 40); ctx.lineTo(132, 52); ctx.lineTo(96, 170); ctx.fill();     // right arm
  ctx.beginPath(); ctx.moveTo(-96, 170); ctx.lineTo(-22, 48); ctx.lineTo(22, 58); ctx.lineTo(-36, 170); ctx.fill();                       // left arm
  ell(14, 40, 48, 20, skinD); ell(14, 36, 44, 17, skin);                                 // left hand under the lens
  ctx.fillStyle = '#16181D'; rr(-44, -52, 126, 80, 14); ctx.fill(); rr(-22, -66, 42, 20, 6); ctx.fill();   // camera body
  ctx.fillStyle = '#3A3F4A'; rr(46, -62, 20, 12, 4); ctx.fill();                          // dial
  circle(28, -10, 42, '#2A2E36'); circle(28, -10, 32, '#0F1115'); circle(28, -10, 19, '#2D3F5E');
  circle(20, -18, 6, 'rgba(255,255,255,0.75)');
  ctx.fillStyle = skin; rr(72, -46, 32, 84, 15); ctx.fill();                              // right hand gripping
  ctx.fillStyle = skinD; for (let i = 0; i < 3; i++) { rr(62, -40 + i * 22, 22, 14, 7); ctx.fill(); }
  ctx.restore(); ctx.restore();
}

/** the scene rendered at 1/px resolution and blown up (a digitally cropped, low-quality look) */
let _off = null;
export function pixelScene(w, h, o, px) {
  const sw = Math.max(8, Math.round(w / px)), sh = Math.max(8, Math.round(h / px));
  if (!_off) _off = document.createElement('canvas');
  _off.width = sw; _off.height = sh;
  const prev = ctx, oc = _off.getContext('2d');
  setCtx(oc); oc.setTransform(sw / w, 0, 0, sh / h, 0, 0); scene(w, h, o); setCtx(prev);
  ctx.save(); ctx.imageSmoothingEnabled = false; ctx.drawImage(_off, 0, 0, w, h); ctx.restore();
}

/** a padlock icon (locked), centre (x, y), s = height */
export function padlock(x, y, s, color = C.yellow) {
  ctx.save(); ctx.translate(x, y);
  ctx.strokeStyle = color; ctx.lineWidth = s * 0.13; ctx.beginPath(); ctx.arc(0, -s * 0.12, s * 0.24, Math.PI, 0); ctx.lineTo(s * 0.24, s * 0.05); ctx.moveTo(-s * 0.24, -s * 0.12); ctx.lineTo(-s * 0.24, s * 0.05); ctx.stroke();
  ctx.fillStyle = color; rr(-s * 0.36, 0, s * 0.72, s * 0.5, s * 0.08); ctx.fill(); circle(0, s * 0.22, s * 0.07, C.ink);
  ctx.restore();
}

/** a stylised eye (the viewer's gaze), centre (x, y), s = width */
export function eye(x, y, s) {
  ctx.save(); ctx.translate(x, y);
  ctx.fillStyle = C.ink; ctx.beginPath(); ctx.moveTo(-s / 2 - 6, 0); ctx.quadraticCurveTo(0, -s * 0.5, s / 2 + 6, 0); ctx.quadraticCurveTo(0, s * 0.5, -s / 2 - 6, 0); ctx.fill();
  ctx.fillStyle = C.white; ctx.beginPath(); ctx.moveTo(-s / 2, 0); ctx.quadraticCurveTo(0, -s * 0.42, s / 2, 0); ctx.quadraticCurveTo(0, s * 0.42, -s / 2, 0); ctx.fill();
  circle(0, 0, s * 0.18, C.teal); circle(0, 0, s * 0.09, C.ink); circle(-s * 0.05, -s * 0.05, s * 0.035, C.white);
  ctx.restore();
}
