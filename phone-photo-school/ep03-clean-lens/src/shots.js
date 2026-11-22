// PHONE PHOTO SCHOOL · LESSON 03: CLEAN YOUR LENS (25 s): the shot list.
// Keep key action between y 200 and 1250: the caption lives at y 1250-1550.
import { ctx, C, W, H, clamp, lerp, seg, eo, eio, eob, rnd, line, circle } from './core/lib.js';
import { L, Wd, T } from './core/timing.js';
import * as K from './core/kit.js';

const LESSON = 3, PS = 0.92;
const LENS0 = (() => { const [x, y] = K.LENSES(PS)[0]; return [540 + x, 800 + y]; })();

/** dust specks + lint fibres around (cx, cy), p 0..1 = how many have landed */
function dust(cx, cy, p, spread = 260) {
  for (let i = 0; i < 26; i++) {
    const q = seg(p, rnd(i) * 0.7, rnd(i) * 0.7 + 0.3); if (q <= 0) continue;
    const tx = cx + (rnd(i + 9) - 0.5) * spread, ty = cy + (rnd(i + 19) - 0.5) * spread * 1.4;
    const x = tx + (rnd(i + 29) - 0.5) * 300 * (1 - eo(q)), y = lerp(ty - 500, ty, eo(q));
    if (i % 5 === 0) { ctx.save(); ctx.translate(x, y); ctx.rotate(rnd(i) * 6); line([[-18, 0], [-6, -8], [6, 6], [18, -2]], '#D9D2C3', 4); ctx.restore(); }
    else circle(x, y, 4 + rnd(i + 3) * 5, '#CFC8B8');
  }
}

export function buildShots() {
  const S = [], CUES = [];
  const add = (o) => (S.push(o), o);
  const cue = (t, type, o = {}) => CUES.push({ t: +t.toFixed(3), type, ...o });
  const cut = (i) => (i === 0 ? 0 : L(i) - 0.08);

  // ── 0 · HOOK: phone rises, the photo on screen is milky and soft ──
  {
    const st = cut(0), hazy = Wd('hazy', 0) - st;
    add({ id: 'S01', at: st, cam: [540, 800], zoom: 0.06, note: 'phone rises, hazy photo, HAZY? on "hazy"',
      draw(lt, d, t) {
        K.studio(t);
        const rise = eob(seg(lt, 0, 0.6));
        K.phone(540, lerp(1900, 800, rise), 0.92, lerp(-0.2, -0.04, rise), (w, h) => K.cameraApp(w, h, {
          t, subj: 0.62, scene: { haze: 1, blur: 3 },
          over: (vw, vh, k) => { if (lt > hazy) K.pill('HAZY?', vw / 2, 50 * k, 32 * k, C.red, C.white, eob(seg(lt, hazy, hazy + 0.25))); },
        }));
      } });
    cue(st + 0.05, 'whoosh'); cue(st + hazy, 'boing', { gain: 0.5 });
  }

  // ── 1 · LESSON CARD ──
  {
    const st = cut(1);
    add({ id: 'S02', at: st, cam: [540, 700], zoom: 0.1, note: 'lesson card 03, CLEAN YOUR LENS',
      draw: (lt, d, t) => K.lessonCard(lt, t, LESSON, 'CLEAN YOUR LENS', Wd('three', 1) - st, Wd('clean', 1) - st) });
    cue(st, 'whoosh'); cue(Wd('three', 1) - 0.02, 'slam', { gain: 0.8 }); cue(Wd('clean', 1), 'pop');
  }

  // ── 2 · GREASE: a fingertip comes in from the side, presses the top lens, leaves a print on "grease" ──
  {
    const st = cut(2), touch = Wd('touch', 2) - st, gr = Wd('grease', 2) - st;
    const [LX, LY] = LENS0;
    add({ id: 'S03', at: st, cam: [LX, LY + 80], zoom: 0.3, note: 'finger touches the top lens on "touch", print + GREASE on "grease"',
      draw(lt, d, t) {
        K.studio(t);
        K.phoneBack(540, 800, PS, 0, { smudge: eo(seg(lt, touch + 0.1, touch + 0.3)) });
        const inP = eio(seg(lt, 0, touch)), outP = eio(seg(lt, touch + 0.3, touch + 0.9));
        const fy = lerp(LY + 520, LY + 10, inP) + lerp(0, 420, outP), fx = lerp(1250, LX + 20, inP) + lerp(0, 800, outP);
        K.finger(fx, fy, 96, -0.95);
        K.pill('GREASE', LX + 250, LY - 30, 54, C.red, C.white, eob(seg(lt, gr, gr + 0.25)));
      } });
    cue(st, 'whoosh'); cue(st + touch, 'tap'); cue(st + gr, 'pop');
  }

  // ── 3 · DUST: dust and lint drift down onto the lenses; DUST + LINT on "dust" ──
  {
    const st = cut(3), dst = Wd('dust', 3) - st;
    const [LX, LY] = LENS0;
    add({ id: 'S04', at: st, cam: [LX + 60, LY + 120], zoom: 0.25, note: 'dust + lint settles on the lenses, pill on "dust"',
      draw(lt, d, t) {
        K.studio(t);
        K.phoneBack(540, 800, PS, 0, { smudge: 1 });
        dust(LX + 60, LY + 130, seg(lt, 0, dst + 0.4));
        K.pill('DUST + LINT', LX + 230, LY + 380, 52, C.red, C.white, eob(seg(lt, dst, dst + 0.25)));
      } });
    cue(st, 'whoosh'); cue(st + 0.1, 'sparkle', { dur: 1.2, gain: 0.4 }); cue(st + dst, 'pop');
  }

  // ── 4 · THE RESULT: lights glow on "glow", details blur on "blur"; dirty lens inset ──
  {
    const st = cut(4), glow = Wd('glow', 4) - st, blur = Wd('blur', 4) - st;
    add({ id: 'S05', at: st, cam: [540, 700], zoom: 0.06, note: 'photo hazes on "glow", blurs on "blur"; dirty lens inset',
      draw(lt, d, t) {
        K.studio(t);
        const hz = eo(seg(lt, glow - 0.1, glow + 0.4));
        K.photoFinder('beam', { cx: 0.42, cy: 0.55, zoom: 1.25, haze: hz, blur: lerp(0, 5, eo(seg(lt, blur - 0.1, blur + 0.3))) });
        K.pill('SMUDGE (SIMULATED)', 330, 1160, 36, 'rgba(10,12,16,0.8)', C.white, hz);
        const ip = eob(seg(lt, 0.1, 0.4));
        if (ip > 0) { ctx.save(); ctx.translate(850, 420); ctx.scale(ip, ip); K.lens(0, 0, 90, 1); ctx.restore(); }
      } });
    cue(st, 'whoosh'); cue(st + 0.1, 'pop', { gain: 0.6 }); cue(st + glow, 'sparkle', { dur: 0.5, gain: 0.6 }); cue(st + blur, 'slide', { dur: 0.4, gain: 0.5 });
  }

  // ── 5 · WIPE: a big lens, the cloth sweeps gently, the print fades; MICROFIBER on "microfiber" ──
  {
    const st = cut(5), mf = Wd('microfiber', 5) - st, end = L(6) - st;
    add({ id: 'S06', at: st, cam: [540, 720], zoom: 0.05, note: 'big lens, cloth wipes in circles, smudge gone',
      draw(lt, d, t) {
        K.studio(t);
        const wp = seg(lt, 0.15, end - 0.3);
        K.lens(540, 720, 300, 1 - eio(wp));
        if (wp > 0 && wp < 1) { const a = wp * Math.PI * 4; K.cloth(540 + Math.cos(a) * 180, 740 + Math.sin(a) * 120, 1.1, Math.sin(a) * 0.15); }
        if (wp >= 1) for (let i = 0; i < 3; i++) K.hotspot(400 + i * 140, 560 + (i % 2) * 120, 0.6, seg(lt, end - 0.3 + i * 0.05, end - 0.05), t);
        K.pill('MICROFIBER', 540, 330, 54, C.teal, C.ink, eob(seg(lt, mf, mf + 0.25)));
      } });
    cue(st, 'whoosh'); cue(st + 0.15, 'slide', { dur: end - 0.5, gain: 0.8 }); cue(st + end - 0.3, 'sparkle', { dur: 0.4 });
  }

  // ── 6 · NOT YOUR SHIRT: cloth ✓ vs shirt ✗; grit specks on "grit", scratches on "glass" ──
  {
    const st = cut(6), shirt = Wd('shirt', 6) - st, grit = Wd('grit', 6) - st, glass = Wd('glass', 6) - st;
    add({ id: 'S07', at: st, cam: [540, 720], zoom: 0.05, note: 'cloth ✓ / shirt ✗ on "shirt", grit on "grit", scratched lens on "glass"',
      draw(lt, d, t) {
        K.studio(t);
        const g = eo(seg(lt, glass - 0.1, glass + 0.3));       // the pair slides up to make room for the scratched lens
        ctx.save(); ctx.translate(0, lerp(0, -110, g));
        K.cloth(290, 740, 1.15, -0.08); K.check(290, 480, eob(seg(lt, 0, 0.25)) * 0.8);
        K.shirt(800, 740, 1.55);
        for (let i = 0; i < 14; i++) { const q = seg(lt, grit + i * 0.03, grit + i * 0.03 + 0.2); if (q > 0) circle(800 + (rnd(i) - 0.5) * 180, 740 + (rnd(i + 5) - 0.5) * 200, 7 * eob(q), '#E9E1CF'); }
        K.redX(800, 740, lt > shirt ? lerp(2.2, 1.25, eo(seg(lt, shirt, shirt + 0.18))) : 0, lt > shirt ? 1 : 0);
        ctx.restore();
        if (g > 0) {
          ctx.save(); ctx.globalAlpha = g; K.lens(540, 1040, 150 * eob(g));
          ctx.strokeStyle = 'rgba(255,255,255,0.85)'; ctx.lineWidth = 4;
          for (const [a, b, c, e] of [[-70, -40, 50, 10], [-40, 50, 60, -30], [-80, 20, -10, 70]]) { ctx.beginPath(); ctx.moveTo(540 + a, 1040 + b); ctx.lineTo(540 + c, 1040 + e); ctx.stroke(); }
          ctx.restore();
          K.pill('SCRATCHES', 810, 1110, 44, C.red, C.white, eob(seg(lt, glass + 0.1, glass + 0.35)));
        }
      } });
    cue(st, 'whoosh'); cue(st + shirt + 0.05, 'slam'); cue(st + grit, 'sizzle', { dur: 0.5 }); cue(st + glass, 'pop');
  }

  // ── 7 · HABIT: phone back, a quick wipe on "wipe", shutter flash on "shot" ──
  {
    const st = cut(7), hab = Wd('habit', 7) - st, wipe = Wd('wipe', 7) - st, shot = Wd('shot', 7) - st;
    const [LX, LY] = LENS0;
    add({ id: 'S08', at: st, cam: [540, 760], zoom: 0.06, note: 'HABIT pill, quick cloth swipe on "wipe", shutter flash on "shot"',
      draw(lt, d, t) {
        K.studio(t);
        const wp = seg(lt, wipe - 0.1, wipe + 0.45);
        K.phoneBack(540, 750, 0.75, 0, { smudge: 1 - eio(wp), glow: lt > shot ? [0.9, 0.9, 0.9, 0.9] : [] });
        if (wp > 0 && wp < 1) K.cloth(lerp(150, 900, eio(wp)), 470, 0.8, -0.1);
        K.pill('1 WIPE = 1 SHOT', 540, 1195, 50, C.yellow, C.ink, eob(seg(lt, hab - 0.1, hab + 0.2)));
        K.flash(lt > shot ? 0.8 * (1 - seg(lt, shot, shot + 0.3)) : 0);
      } });
    cue(st, 'whoosh'); cue(st + hab, 'pop'); cue(st + wipe - 0.1, 'zip'); cue(st + shot, 'shutter');
  }

  // ── 8 · CRISP: the clean photo, check on "clear" ──
  {
    const st = cut(8), clear = Wd('clear', 8) - st;
    add({ id: 'S09', at: st, cam: [540, 700], zoom: 0.06, note: 'crisp photo, check on "clear"',
      draw(lt, d, t) {
        K.studio(t);
        K.photoFinder('beam', { cx: 0.42, cy: 0.55, zoom: 1.25 }, { tag: seg(lt, clear + 0.1, clear + 0.4) });
        K.check(850, 400, eob(seg(lt, clear, clear + 0.25)) * 0.8);
      } });
    cue(st, 'whoosh'); cue(st + clear, 'sparkle', { dur: 0.6 });
  }

  // ── 9 · END CARD ──
  {
    const st = cut(9);
    add({ id: 'S10', at: st, cam: [540, 700], zoom: 0.05, note: 'avatar, FOLLOW, next: lesson 04',
      draw: (lt, d, t) => K.endCard(lt, t, Wd('follow', 9) - st, Wd('four', 9) - st, 4, 'THE ZOOM LENSES') });
    cue(st, 'whoosh'); cue(Wd('follow', 9), 'pop'); cue(Wd('four', 9), 'pop', { gain: 0.6 });
  }

  const overlay = (t) => K.seriesBadge(LESSON, seg(t, 0.15, 0.55), t);
  return { shots: S, cues: CUES, overlay };
}
