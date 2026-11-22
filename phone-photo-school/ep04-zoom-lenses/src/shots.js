// PHONE PHOTO SCHOOL · LESSON 04: THE ZOOM LENSES: the shot list.
// Keep key action between y 200 and 1250: the caption lives at y 1250-1550.
import { ctx, C, W, H, clamp, lerp, seg, eo, eio, eob } from './core/lib.js';
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

/** the zoom demo: viewfinder between lens a and b (p 0..1), chip row with b selected */
function zoomView(t, a, b, p, tapP) {
  const A = Z[a], B = Z[b], q = eio(clamp(p));
  const zoom = Math.exp(lerp(Math.log(A.zoom), Math.log(B.zoom), q));
  K.finder(t, { ...SCENE, zoom, zx: lerp(A.zx, B.zx, q), zy: lerp(A.zy, B.zy, q) }, { frame: FR });
  K.pill(B.name, 540, FR.y + 60, 40, 'rgba(10,12,16,0.75)', C.white, 1);
  Z.forEach((z, i) => {
    const sel = i === b, s = sel ? 1 + 0.12 * eob(clamp(tapP)) : 1;
    ctx.save(); ctx.translate(chipX(i), CHIP_Y); ctx.scale(s, s);
    ctx.beginPath(); ctx.arc(0, 4, 62, 0, 7); ctx.fillStyle = C.ink; ctx.fill();
    ctx.beginPath(); ctx.arc(0, 0, 62, 0, 7); ctx.fillStyle = sel ? C.yellow : C.panel2; ctx.fill();
    ctx.fillStyle = sel ? C.ink : C.white; ctx.font = '900 46px Inter'; ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.fillText(z.chip, 0, 2);
    ctx.restore();
  });
  K.tap(chipX(b), CHIP_Y, tapP, 1.2);
}

export function buildShots() {
  const S = [], CUES = [];
  const add = (o) => (S.push(o), o);
  const cue = (t, type, o = {}) => CUES.push({ t: +t.toFixed(3), type, ...o });
  const cut = (i) => (i === 0 ? 0 : L(i) - 0.08);

  // ── 1 · HOOK: phone back rises; the four lenses light up one by one on "four cameras" ──
  {
    const st = cut(0), four = Wd('four', 0) - st, use = Wd('use', 0) - st, s = 0.92;
    const lens = K.LENSES(s).map(([x, y]) => [540 + x, 800 + y]);
    const labelAt = [[-120, 0], [-120, 0], [-120, 0], [125, 0]];
    add({ id: 'S01', at: st, cam: [470, 520], zoom: 0.25, note: 'phone back, lenses light up on "four", bounce on "use"',
      draw(lt, d, t) {
        K.studio(t);
        const rise = eob(seg(lt, 0, 0.55)), bounce = lt > use ? Math.sin(seg(lt, use, use + 0.35) * Math.PI) * 30 : 0;
        const glow = [0, 1, 2, 3].map((i) => seg(lt, four + i * 0.14, four + i * 0.14 + 0.15) * 0.9);
        K.phoneBack(540, lerp(1900, 800, rise) - bounce, s, lerp(0.2, 0, rise), { glow });
        Z.forEach((z, i) => { const [x, y] = lens[i]; K.pill(z.chip, x + labelAt[i][0], y - bounce, 40, C.yellow, C.ink, eob(seg(lt, four + i * 0.14, four + i * 0.14 + 0.25))); });
      } });
    cue(st + 0.05, 'whoosh'); [0, 1, 2, 3].forEach((i) => cue(st + four + i * 0.14, 'pop', { gain: 0.6 })); cue(st + use, 'boing', { gain: 0.5 });
  }

  // ── 2 · LESSON CARD ──
  {
    const st = cut(1);
    add({ id: 'S02', at: st, cam: [540, 700], zoom: 0.1, note: 'lesson card 04, ZOOM LENSES',
      draw: (lt, d, t) => K.lessonCard(lt, t, LESSON, 'ZOOM LENSES', Wd('four', 1) - st, Wd('zoom', 1) - st) });
    cue(st, 'whoosh'); cue(Wd('four', 1) - 0.02, 'slam', { gain: 0.8 }); cue(Wd('zoom', 1), 'pop');
  }

  // ── 3-6 · one lens per line: tap the chip, the view zooms ──
  [[2, 'point', 'landscapes'], [3, 'one', 'everyday'], [4, 'three', 'portraits'], [5, 'five', 'details']].forEach(([line, w0, key], n) => {
    const st = cut(line), tapT = Wd(w0, line) - st, from = Math.max(0, n - 1);
    add({ id: `S0${line + 1}`, at: st, cam: [540, 760], zoom: 0.03, note: `${Z[n].chip}: tap on "${w0}", zoom to ${Z[n].name}`,
      draw(lt, d, t) {
        K.studio(t);
        zoomView(t, from, n, seg(lt, tapT + 0.05, tapT + 0.7), seg(lt, tapT - 0.05, tapT + 0.4));
      } });
    cue(st, 'whoosh'); cue(st + tapT, 'tap'); if (n) cue(st + tapT + 0.05, 'slide', { dur: 0.6, gain: 0.6 }); cue(Wd(key, line), 'pop', { gain: 0.4 });
  });

  // ── 7 · END CARD ──
  {
    const st = cut(6);
    add({ id: 'S07', at: st, cam: [540, 700], zoom: 0.05, note: 'FOLLOW, next: lesson 05',
      draw: (lt, d, t) => K.endCard(lt, t, Wd('follow', 6) - st, Wd('five', 6) - st, 5, 'LEADING LINES') });
    cue(st, 'whoosh'); cue(Wd('follow', 6), 'pop'); cue(Wd('five', 6), 'pop', { gain: 0.6 });
  }

  const overlay = (t) => K.seriesBadge(LESSON, seg(t, 0.15, 0.55));
  return { shots: S, cues: CUES, overlay };
}
