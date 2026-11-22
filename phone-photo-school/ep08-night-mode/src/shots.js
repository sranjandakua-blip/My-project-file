// PHONE PHOTO SCHOOL · LESSON 08: NIGHT MODE (25 s): the shot list.
// Keep key action between y 200 and 1250: the caption lives at y 1250-1550.
import { ctx, C, W, H, clamp, lerp, seg, eo, eio, eob, rr, line, circle } from './core/lib.js';
import { L, Wd, T } from './core/timing.js';
import * as K from './core/kit.js';

const LESSON = 8, F = K.FRAME;

export function buildShots() {
  const S = [], CUES = [];
  const add = (o) => (S.push(o), o);
  const cue = (t, type, o = {}) => CUES.push({ t: +t.toFixed(3), type, ...o });
  const cut = (i) => (i === 0 ? 0 : L(i) - 0.08);
  const s = 0.92, PW = K.PHONE.w * s, PH = K.PHONE.h * s, m = 14 * s, sw = PW - 2 * m, sh = PH - 2 * m;
  const toWorld = (fx, fy, py = 800) => [540 - PW / 2 + m + sw * fx / 923, py - PH / 2 + m + sh * fy / 2000];
  const noisy = (key, o, g, t) => (vw, vh) => { K.grain(vw, vh, g, Math.floor(t * 30)); };

  // ── 0 · HOOK: the church at night, too dark and grainy ──
  {
    const st = cut(0), gr = Wd('grainy', 0) - st;
    add({ id: 'S01', at: st, cam: [540, 800], zoom: 0.06, note: 'phone rises, dark grainy church photo, pill on "grainy"',
      draw(lt, d, t) {
        K.studio(t);
        const rise = eob(seg(lt, 0, 0.6));
        K.phone(540, lerp(1900, 800, rise), 0.92, lerp(-0.2, -0.04, rise), (w, h) => K.cameraApp(w, h, {
          t, photo: 'church', photoOpts: { cy: 0.5, bright: 0.38, blur: 1 }, reticle: false, over: (vw, vh, k) => {
            K.grain(vw, vh, 0.8, Math.floor(t * 30));
            if (lt > gr) K.pill('DARK + GRAINY', vw / 2, 50 * k, 30 * k, C.red, C.white, eob(seg(lt, gr, gr + 0.25))); } }));
      } });
    cue(st + 0.05, 'whoosh'); cue(st + gr, 'boing', { gain: 0.5 });
  }

  // ── 1 · LESSON CARD ──
  {
    const st = cut(1);
    add({ id: 'S02', at: st, cam: [540, 700], zoom: 0.1, note: 'lesson card 08, NIGHT MODE',
      draw: (lt, d, t) => K.lessonCard(lt, t, LESSON, 'NIGHT MODE', Wd('eight', 1) - st, Wd('night', 1) - st) });
    cue(st, 'whoosh'); cue(Wd('eight', 1) - 0.02, 'slam', { gain: 0.8 }); cue(Wd('night', 1), 'pop');
  }

  // ── 2 · THE MOON ICON: the monastery gate, dark; the moon 4 lights up on "moon" ──
  const [mx, my] = toWorld(836, 1320);
  {
    const st = cut(2), mo = Wd('moon', 2) - st;
    add({ id: 'S03', at: st, cam: [mx, my], zoom: 0.35, note: 'gate photo in the app, the moon icon pulses on "moon"',
      draw(lt, d, t) {
        K.studio(t);
        K.phone(540, 800, s, 0, (w, h) => K.cameraApp(w, h, { t, photo: 'gate', photoOpts: { cy: 0.55, bright: 0.45 }, moon: 4,
          moonHi: lt > mo ? 0.6 + 0.4 * Math.sin(lt * 8) : 0, over: (vw, vh) => K.grain(vw, vh, 0.5, Math.floor(t * 30)) }));
        K.pill('NIGHT MODE', mx - 170, my - 130, 40, C.yellow, C.ink, eob(seg(lt, mo, mo + 0.25)));
      } });
    cue(st, 'whoosh'); cue(st + mo, 'pop');
  }

  // ── 3 · THE NUMBER = SECONDS: a big moon "4", counting ──
  {
    const st = cut(3), nu = Wd('number', 3) - st, se = Wd('seconds', 3) - st;
    add({ id: 'S04', at: st, cam: [540, 700], zoom: 0.05, note: 'big moon 4 on "number", "4 SECONDS" on "seconds"',
      draw(lt, d, t) {
        K.studio(t);
        const p = eob(seg(lt, 0.05, 0.4));
        ctx.save(); ctx.translate(430, 680); ctx.scale(p, p);
        circle(0, 0, 150, C.yellow); circle(60, -50, 135, C.bg);
        ctx.restore();
        if (p > 0) { ctx.fillStyle = C.yellow; ctx.font = '900 300px Inter'; ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
          ctx.globalAlpha = seg(lt, nu - 0.1, nu + 0.2); ctx.fillText('4', 720, 690); ctx.globalAlpha = 1; }
        K.pill('= 4 SECONDS', 540, 1000, 60, C.yellow, C.ink, eob(seg(lt, se, se + 0.25)));
      } });
    cue(st, 'whoosh'); cue(st + nu, 'pop'); cue(st + se, 'tock'); cue(st + se + 0.5, 'tock'); cue(st + se + 1.0, 'tock');
  }

  // ── 4 · TAP + HOLD STILL: tap the moon, the shutter ring counts down, the photo brightens ──
  {
    const st = cut(4), tp = Wd('tap', 4) - st, hold = Wd('hold', 4) - st, fin = Wd('finishes', 4) - st;
    add({ id: 'S05', at: st, cam: [540, 800], zoom: 0.05, note: 'tap moon on "tap", countdown ring, gate brightens by "finishes"',
      draw(lt, d, t) {
        K.studio(t);
        const p = seg(lt, hold - 0.2, fin + 0.3), br = lerp(0.45, 1.05, eio(p));
        K.phone(540, 800, s, 0, (w, h) => K.cameraApp(w, h, { t, photo: 'gate', photoOpts: { cy: 0.55, bright: br }, moon: Math.max(1, 4 - Math.floor(p * 4)),
          moonHi: lt > tp ? 1 : 0, reticle: false, over: (vw, vh) => K.grain(vw, vh, 0.5 * (1 - p), Math.floor(t * 30)) }));
        K.tap(mx, my, seg(lt, tp - 0.05, tp + 0.4), 0.9);
        const [sx, sy] = toWorld(461, 1663);
        if (p > 0 && p < 1) { ctx.strokeStyle = C.yellow; ctx.lineWidth = 12; ctx.lineCap = 'round'; ctx.beginPath(); ctx.arc(sx, sy, 92, -Math.PI / 2, -Math.PI / 2 + p * Math.PI * 2); ctx.stroke(); }
        K.pill('HOLD STILL', 540, 1210, 50, C.yellow, C.ink, eob(seg(lt, hold, hold + 0.25)));
      } });
    cue(st, 'whoosh'); cue(st + tp, 'tap'); cue(st + hold, 'tock'); cue(st + hold + 0.6, 'tock'); cue(st + hold + 1.2, 'tock'); cue(st + fin + 0.3, 'shutter');
  }

  // ── 5 · BRACE / REST: the phone wobbles, steadies on "elbows", a wall slides under it on "rest" ──
  {
    const st = cut(5), el = Wd('elbows', 5) - st, re = Wd('rest', 5) - st;
    add({ id: 'S06', at: st, cam: [540, 760], zoom: 0.04, note: 'wobble → steady on "elbows", ledge on "rest"',
      draw(lt, d, t) {
        K.studio(t);
        const wob = 1 - eo(seg(lt, el - 0.2, el + 0.3)), ledge = eo(seg(lt, re - 0.1, re + 0.4));
        const py = lerp(700, 640, ledge);
        K.phone(540 + Math.sin(lt * 21) * 22 * wob, py, 0.68, Math.sin(lt * 17) * 0.08 * wob, (w, h) => K.cameraApp(w, h, { t, photo: 'pyramids', photoOpts: { bright: 0.9, blur: 6 * wob }, reticle: false }));
        if (wob > 0.05) for (const sx of [-1, 1]) { ctx.globalAlpha = wob; line([[540 + sx * 230, 520], [540 + sx * 260, 560]], C.white, 8); line([[540 + sx * 235, 620], [540 + sx * 270, 650]], C.white, 8); ctx.globalAlpha = 1; }
        if (ledge > 0) { ctx.fillStyle = '#5A4A3A'; ctx.fillRect(150, lerp(1400, 1000, ledge), 780, 60); ctx.fillStyle = '#6E5A46'; ctx.fillRect(150, lerp(1400, 1000, ledge), 780, 16); }
        K.pill('BRACE YOUR ELBOWS', 540, 330, 44, C.yellow, C.ink, eob(seg(lt, el, el + 0.25)));
        K.pill('OR REST IT', 820, 940, 40, C.teal, C.ink, eob(seg(lt, re, re + 0.25)));
      } });
    cue(st, 'whoosh'); cue(st + el, 'pop'); cue(st + re, 'thud', { gain: 0.6 });
  }

  // ── 6 · STICK TO 1X: the glass pyramids at night, 1x tapped ──
  {
    const st = cut(6), one = Wd('one', 6) - st, li = Wd('light', 6) - st;
    add({ id: 'S07', at: st, cam: [540, 800], zoom: 0.05, note: 'pyramids photo in the app, tap 1× on "one", MOST LIGHT on "light"',
      draw(lt, d, t) {
        K.studio(t);
        K.phone(540, 800, s, 0, (w, h) => K.cameraApp(w, h, { t, photo: 'pyramids', photoOpts: { cy: 0.6 }, zoomSel: lt > one ? '1' : '3', moon: 2 }));
        const [zx, zy] = toWorld(307, 1476); K.tap(zx, zy, seg(lt, one - 0.05, one + 0.4), 0.9);
        K.pill('MAIN CAMERA = MOST LIGHT', 540, 1210, 42, C.yellow, C.ink, eob(seg(lt, li, li + 0.25)));
      } });
    cue(st, 'whoosh'); cue(st + one, 'tap'); cue(st + li, 'pop');
  }

  // ── 7 · RESULTS: three of the creator's night shots ──
  {
    const st = cut(7), wds = ['bright', 'clean', 'sharp'].map((w) => Wd(w, 7) - st);
    const P = [['gate', 300, -0.07, { cy: 0.72 }], ['church', 780, 0.07, { cy: 0.45 }], ['roof', 540, 0, { cy: 0.7 }]];
    add({ id: 'S08', at: st, cam: [540, 740], zoom: 0.04, note: 'three night prints pop on "bright", "clean", "sharp"',
      draw(lt, d, t) {
        K.studio(t);
        P.forEach(([k, x, r, o], i) => { const a = eob(seg(lt, wds[i] - 0.1, wds[i] + 0.25)); if (a > 0) K.photoPrint(lerp(540, x, a), i === 2 ? 760 : 680, 420, 560, r * a, k, o); });
        K.check(880, 420, eob(seg(lt, wds[2], wds[2] + 0.25)) * 0.8);
        K.shotTag(940, 1100, seg(lt, wds[2] + 0.2, wds[2] + 0.5));
      } });
    cue(st, 'whoosh'); [0, 1, 2].forEach((i) => cue(Wd(['bright', 'clean', 'sharp'][i], 7), 'pop', { gain: 0.6 }));
  }

  // ── 8 · END CARD ──
  {
    const st = cut(8);
    add({ id: 'S09', at: st, cam: [540, 700], zoom: 0.05, note: 'avatar, FOLLOW, next: lesson 09',
      draw: (lt, d, t) => K.endCard(lt, t, Wd('follow', 8) - st, Wd('nine', 8) - st, 9, 'MEGAPIXELS') });
    cue(st, 'whoosh'); cue(Wd('follow', 8), 'pop'); cue(Wd('nine', 8), 'pop', { gain: 0.6 });
  }

  const overlay = (t) => K.seriesBadge(LESSON, seg(t, 0.15, 0.55), t);
  return { shots: S, cues: CUES, overlay };
}
