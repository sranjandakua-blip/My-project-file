// PHONE PHOTO SCHOOL · LESSON 04: THE ZOOM LENSES (25 s): the shot list.
// Keep key action between y 200 and 1250: the caption lives at y 1250-1550.
import { ctx, C, W, H, clamp, lerp, seg, eo, eio, eob, circle, line } from './core/lib.js';
import { L, Wd, T } from './core/timing.js';
import * as K from './core/kit.js';

const LESSON = 4;
const FR = { x: 100, y: 300, w: 880, h: 790 };
const SCENE = { subj: 0.7, treeS: 0.55, treeY: 0.82, person: { x: 0.36, y: 0.86, s: 0.17 }, balloon: { x: 0.8, y: 0.2, s: 0.03 } };
// one entry per lens: chip label, frame label, view (zoom + centre)
const Z = [
  { chip: '.6', name: 'ULTRA-WIDE', zoom: 1, zx: 0.5, zy: 0.5 },
  { chip: '1x', name: 'MAIN CAMERA', zoom: 1.6, zx: 0.5, zy: 0.62 },
  { chip: '3x', name: '3X TELEPHOTO', zoom: 4.2, zx: 0.36, zy: 0.735 },
  { chip: '5x', name: '5X TELEPHOTO', zoom: 7, zx: 0.8, zy: 0.215 },
];
const chipX = (i) => 540 + (i - 1.5) * 190, CHIP_Y = 1170;

function chips(sel, tapP = 0) {
  Z.forEach((z, i) => {
    const on = i === sel, s = on ? 1 + 0.12 * eob(clamp(tapP)) : 1;
    ctx.save(); ctx.translate(chipX(i), CHIP_Y); ctx.scale(s, s);
    ctx.beginPath(); ctx.arc(0, 4, 62, 0, 7); ctx.fillStyle = C.ink; ctx.fill();
    ctx.beginPath(); ctx.arc(0, 0, 62, 0, 7); ctx.fillStyle = on ? C.yellow : C.panel2; ctx.fill();
    ctx.fillStyle = on ? C.ink : C.white; ctx.font = '900 46px Inter'; ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.fillText(z.chip, 0, 2);
    ctx.restore();
  });
}
/** the zoom demo: viewfinder between lens a and b (p 0..1), chip row with b selected; extra = scene overrides */
function zoomView(t, a, b, p, tapP, extra = {}) {
  const A = Z[a], B = Z[b], q = eio(clamp(p));
  const zoom = Math.exp(lerp(Math.log(A.zoom), Math.log(B.zoom), q));
  K.finder(t, { ...SCENE, zoom, zx: lerp(A.zx, B.zx, q), zy: lerp(A.zy, B.zy, q), ...extra }, { frame: FR });
  K.pill(B.name, 540, FR.y + 60, 40, 'rgba(10,12,16,0.75)', C.white, 1);
  chips(b, tapP);
  K.tap(chipX(b), CHIP_Y, tapP, 1.2);
}

export function buildShots() {
  const S = [], CUES = [];
  const add = (o) => (S.push(o), o);
  const cue = (t, type, o = {}) => CUES.push({ t: +t.toFixed(3), type, ...o });
  const cut = (i) => (i === 0 ? 0 : L(i) - 0.08);

  // ── 0 · HOOK: phone back rises; the four lenses light up one by one on "four cameras" ──
  {
    const st = cut(0), four = Wd('four', 0) - st, use = Wd('use', 0) - st, s = 0.92;
    const lens = K.LENSES(s).map(([x, y]) => [540 + x, 800 + y]);
    const labelAt = [-120, -120, -120, 125];
    add({ id: 'S01', at: st, cam: [470, 520], zoom: 0.25, note: 'phone back, lenses light up on "four", bounce on "use"',
      draw(lt, d, t) {
        K.studio(t);
        const rise = eob(seg(lt, 0, 0.55)), bounce = lt > use ? Math.sin(seg(lt, use, use + 0.35) * Math.PI) * 30 : 0;
        const glow = [0, 1, 2, 3].map((i) => seg(lt, four + i * 0.14, four + i * 0.14 + 0.15) * 0.9);
        K.phoneBack(540, lerp(1900, 800, rise) - bounce, s, lerp(0.2, 0, rise), { glow });
        Z.forEach((z, i) => { const [x, y] = lens[i]; K.pill(z.chip, x + labelAt[i], y - bounce, 40, C.yellow, C.ink, eob(seg(lt, four + i * 0.14, four + i * 0.14 + 0.25))); });
      } });
    cue(st + 0.05, 'whoosh'); [0, 1, 2, 3].forEach((i) => cue(st + four + i * 0.14, 'pop', { gain: 0.6 })); cue(st + use, 'boing', { gain: 0.5 });
  }

  // ── 1 · LESSON CARD ──
  {
    const st = cut(1);
    add({ id: 'S02', at: st, cam: [540, 700], zoom: 0.1, note: 'lesson card 04, ZOOM LENSES',
      draw: (lt, d, t) => K.lessonCard(lt, t, LESSON, 'ZOOM LENSES', Wd('four', 1) - st, Wd('zoom', 1) - st) });
    cue(st, 'whoosh'); cue(Wd('four', 1) - 0.02, 'slam', { gain: 0.8 }); cue(Wd('zoom', 1), 'pop');
  }

  // ── 2 · .6x: tap on "point", wide view; ROOMS pill on "rooms" ──
  {
    const st = cut(2), tapT = Wd('point', 2) - st, land = Wd('landscapes', 2) - st, rooms = Wd('rooms', 2) - st;
    add({ id: 'S03', at: st, cam: [540, 760], zoom: 0.04, note: '.6 tap on "point", LANDSCAPES / ROOMS pills',
      draw(lt, d, t) {
        K.studio(t);
        zoomView(t, 0, 0, 1, seg(lt, tapT - 0.05, tapT + 0.4));
        K.pill('LANDSCAPES', 330, 1010, 44, C.teal, C.ink, eob(seg(lt, land, land + 0.25)));
        K.pill('SMALL ROOMS', 750, 1010, 44, C.teal, C.ink, eob(seg(lt, rooms, rooms + 0.25)));
      } });
    cue(st, 'whoosh'); cue(st + tapT, 'tap'); cue(st + land, 'pop', { gain: 0.5 }); cue(st + rooms, 'pop', { gain: 0.5 });
  }

  // ── 3 · 1x: tap on "one", zoom in; dusk falls + BEST IN LOW LIGHT on "night" ──
  {
    const st = cut(3), tapT = Wd('one', 3) - st, all = Wd('all', 3) - st, night = Wd('night', 3) - st;
    add({ id: 'S04', at: st, cam: [540, 760], zoom: 0.04, note: '1x tap on "one", ALL-ROUNDER, dusk + LOW LIGHT on "night"',
      draw(lt, d, t) {
        K.studio(t);
        const dusk = eio(seg(lt, night - 0.3, night + 0.3));
        zoomView(t, 0, 1, seg(lt, tapT + 0.05, tapT + 0.7), seg(lt, tapT - 0.05, tapT + 0.4), { bright: lerp(1, 0.5, dusk) });
        if (lt < night) K.pill('ALL-ROUNDER', 540, 1010, 44, C.teal, C.ink, eob(seg(lt, all, all + 0.25)));
        else K.pill('BEST IN LOW LIGHT', 540, 1010, 44, C.yellow, C.ink, eob(seg(lt, night, night + 0.25)));
      } });
    cue(st, 'whoosh'); cue(st + tapT, 'tap'); cue(st + tapT + 0.05, 'slide', { dur: 0.6, gain: 0.6 }); cue(st + all, 'pop', { gain: 0.5 }); cue(st + night, 'pop');
  }

  // ── 4 · 3x: portrait ──
  {
    const st = cut(4), tapT = Wd('three', 4) - st, por = Wd('portraits', 4) - st;
    add({ id: 'S05', at: st, cam: [540, 760], zoom: 0.03, note: '3x tap on "three", zoom to the portrait',
      draw(lt, d, t) {
        K.studio(t);
        zoomView(t, 1, 2, seg(lt, tapT + 0.05, tapT + 0.7), seg(lt, tapT - 0.05, tapT + 0.4));
        K.pill('PORTRAITS', 540, 1010, 44, C.teal, C.ink, eob(seg(lt, por, por + 0.25)));
      } });
    cue(st, 'whoosh'); cue(st + tapT, 'tap'); cue(st + tapT + 0.05, 'slide', { dur: 0.6, gain: 0.6 }); cue(st + por, 'pop', { gain: 0.5 });
  }

  // ── 5 · 5x: the far-away balloon ──
  {
    const st = cut(5), tapT = Wd('five', 5) - st, far = Wd('far', 5) - st;
    add({ id: 'S06', at: st, cam: [540, 760], zoom: 0.03, note: '5x tap on "five", zoom to the balloon',
      draw(lt, d, t) {
        K.studio(t);
        zoomView(t, 2, 3, seg(lt, tapT + 0.05, tapT + 0.8), seg(lt, tapT - 0.05, tapT + 0.4));
        K.pill('FAR DETAILS', 540, 1010, 44, C.teal, C.ink, eob(seg(lt, far, far + 0.25)));
      } });
    cue(st, 'whoosh'); cue(st + tapT, 'tap'); cue(st + tapT + 0.05, 'slide', { dur: 0.7, gain: 0.6 }); cue(st + far, 'pop', { gain: 0.5 });
  }

  // ── 6 · TAP, DON'T PINCH: chips pulse with a check on "tap"; a pinch gesture gets a red X on "pinching" ──
  {
    const st = cut(6), tap = Wd('tap', 6) - st, pin = Wd('pinching', 6) - st;
    add({ id: 'S07', at: st, cam: [540, 760], zoom: 0.03, note: 'chips ✓ on "tap", pinch gesture ✗ on "pinching"',
      draw(lt, d, t) {
        K.studio(t);
        K.finder(t, { ...SCENE, zoom: Z[1].zoom, zx: Z[1].zx, zy: Z[1].zy }, { frame: FR });
        const pulse = lt > tap ? Math.floor((lt - tap) / 0.22) % 4 : 1;
        chips(pulse, 0.6);
        K.check(940, 1060, eob(seg(lt, tap, tap + 0.25)) * 0.5);
        // pinch: two fingertips spreading on the screen
        const pp = seg(lt, pin - 0.6, pin + 0.1), sp = lerp(40, 170, eio(pp));
        if (pp > 0) for (const sx of [-1, 1]) {
          circle(540 + sx * sp, 640 - sx * sp * 0.5, 40, 'rgba(255,255,255,0.75)');
          line([[540 + sx * (sp + 50), 640 - sx * (sp + 50) * 0.5], [540 + sx * (sp + 100), 640 - sx * (sp + 100) * 0.5]], C.white, 8);
        }
        K.redX(540, 640, lt > pin ? lerp(1.7, 1, eo(seg(lt, pin, pin + 0.18))) : 0, lt > pin ? 1 : 0);
      } });
    cue(st, 'whoosh'); cue(st + tap, 'pop'); cue(st + pin - 0.5, 'slide', { dur: 0.5, gain: 0.5 }); cue(st + pin + 0.05, 'slam');
  }

  // ── 7 · IN BETWEEN: 2.2x view goes blocky on "cropping", LOSE QUALITY on "quality" ──
  {
    const st = cut(7), bt = Wd('between', 7) - st, cr = Wd('cropping', 7) - st, ql = Wd('quality', 7) - st;
    add({ id: 'S08', at: st, cam: [540, 700], zoom: 0.05, note: '2.2x pinched view, pixels grow on "cropping", LOSE QUALITY on "quality"',
      draw(lt, d, t) {
        K.studio(t);
        const px = lerp(1, 30, eio(seg(lt, cr - 0.15, cr + 0.3)));
        K.finder(t, { ...SCENE, zoom: 3, zx: 0.42, zy: 0.66, pixel: px }, { frame: FR });
        K.pill('2.2x', 540, FR.y + 60, 44, C.red, C.white, eob(seg(lt, bt, bt + 0.25)));
        chips(-1);
        K.pill('LOSE QUALITY', 540, 1010, 48, C.red, C.white, eob(seg(lt, ql, ql + 0.25)));
      } });
    cue(st, 'whoosh'); cue(st + bt, 'pop'); cue(st + cr, 'sizzle', { dur: 0.6 }); cue(st + ql, 'slam', { gain: 0.6 });
  }

  // ── 8 · END CARD ──
  {
    const st = cut(8);
    add({ id: 'S09', at: st, cam: [540, 700], zoom: 0.05, note: 'avatar, FOLLOW, next: lesson 05',
      draw: (lt, d, t) => K.endCard(lt, t, Wd('follow', 8) - st, Wd('five', 8) - st, 5, 'LEADING LINES') });
    cue(st, 'whoosh'); cue(Wd('follow', 8), 'pop'); cue(Wd('five', 8), 'pop', { gain: 0.6 });
  }

  const overlay = (t) => K.seriesBadge(LESSON, seg(t, 0.15, 0.55), t);
  return { shots: S, cues: CUES, overlay };
}
