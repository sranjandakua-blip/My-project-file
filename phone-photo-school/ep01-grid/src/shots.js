// PHONE PHOTO SCHOOL · LESSON 01: THE GRID: the shot list (the only file that changes per video, with script.json).
// A shot: { id, at, cam: [cx, cy], zoom, note, draw(lt, d, t) } · lt = time in shot, d = shot length, t = film time.
// Cut = L(i) - 0.08 (picture changes just before its line). Key moments land on words with Wd('word', line).
// Keep key action between y 200 and 1250: the caption lives at y 1250-1550.
import { ctx, C, W, H, clamp, lerp, seg, eo, eio, eob, rr, bigText } from './core/lib.js';
import { L, Le, Wd, T } from './core/timing.js';
import * as K from './core/kit.js';

const LESSON = 1;
const FRAME = { x: 100, y: 300, w: 880, h: 910 };          // the big viewfinder in the composition shots

/** big viewfinder: scene + grid + focus brackets, in FRAME */
function bigFinder(t, subj, gridP, { brackets = true } = {}) {
  const { x, y, w, h } = FRAME;
  ctx.fillStyle = C.ink; rr(x - 14, y - 14, w + 28, h + 28, 46); ctx.fill();
  ctx.save(); rr(x, y, w, h, 34); ctx.clip(); ctx.translate(x, y);
  K.scene(w, h, { subj, t });
  K.grid(0, 0, w, h, gridP, 6, 'rgba(255,255,255,0.9)');
  ctx.restore();
  if (brackets) {                                           // focus brackets follow the subject
    const bx = x + subj * w, by = y + h * 0.56, s = 120;
    ctx.strokeStyle = C.yellow; ctx.lineWidth = 8; ctx.lineCap = 'round';
    for (const [sx, sy] of [[-1, -1], [1, -1], [1, 1], [-1, 1]]) {
      ctx.beginPath(); ctx.moveTo(bx + sx * s, by + sy * s - sy * 40); ctx.lineTo(bx + sx * s, by + sy * s); ctx.lineTo(bx + sx * s - sx * 40, by + sy * s); ctx.stroke();
    }
  }
}
const third = (i, j) => [FRAME.x + (FRAME.w * i) / 3, FRAME.y + (FRAME.h * j) / 3];

export function buildShots() {
  const S = [], CUES = [];
  const add = (o) => (S.push(o), o);
  const cue = (t, type, o = {}) => CUES.push({ t: +t.toFixed(3), type, ...o });
  const cut = (i) => (i === 0 ? 0 : L(i) - 0.08);

  // ── 1 · HOOK: phone rises into frame, camera app open, shutter on "photos" ─────────────
  {
    const st = cut(0), snap = Wd('photos', 0) - st;
    add({ id: 'S01', at: st, cam: [540, 800], zoom: 0.06, note: 'phone rises, camera app, shutter + flash on "photos"',
      draw(lt, d, t) {
        K.studio(t);
        const rise = eob(seg(lt, 0, 0.6));
        const press = lt > snap && lt < snap + 0.25 ? 1 : 0;
        K.phone(540, lerp(1900, 800, rise), 0.92, lerp(-0.2, -0.04, rise), (w, h) => K.cameraApp(w, h, { t, subj: 0.5, press }));
        K.flash(lt > snap ? 0.7 * (1 - seg(lt, snap, snap + 0.25)) : 0);
      } });
    cue(st + 0.05, 'whoosh'); cue(st + 0.15, 'pop', { gain: 0.5 }); cue(st + snap, 'shutter');
  }

  // ── 2 · LESSON CARD: "01" slams in, grid sweeps across, THE GRID pill on "grid" ─────
  {
    const st = cut(1), one = Wd('one', 1) - st, g = Wd('grid', 1) - st;
    add({ id: 'S02', at: st, cam: [540, 700], zoom: 0.1, note: 'lesson card, 01 on "one", THE GRID on "grid"',
      draw(lt, d, t) {
        K.studio(t, C.panel2);
        K.grid(0, 0, W, H, seg(lt, 0, 0.9), 6, C.teal);
        ctx.font = '900 64px Inter'; ctx.letterSpacing = '14px'; ctx.textAlign = 'center'; ctx.fillStyle = C.mute;
        ctx.globalAlpha = seg(lt, 0, 0.25); ctx.fillText('LESSON', 552, 430); ctx.globalAlpha = 1; ctx.letterSpacing = '0px';
        if (lt > one - 0.05) bigText('01', 540, 700, 400, C.white, -0.04, lerp(1.8, 1, eob(seg(lt, one - 0.05, one + 0.2))));
        K.pill('THE GRID', 540, 1030, 84, C.yellow, C.ink, eob(seg(lt, g - 0.05, g + 0.25)));
      } });
    cue(st, 'whoosh'); cue(st + one - 0.02, 'slam', { gain: 0.8 }); cue(st + g, 'pop');
  }

  // ── 3 · HOW: tap the gear, settings slide in, Grid lines toggles ON ────────────────────
  {
    const st = cut(2), sett = Wd('settings', 2) - st, gr = Wd('grid', 2) - st, tapT = sett - 0.3;
    // phone at s 1.02 centred (540, 720): screen-local gear position → world, for the tap ripple
    const s = 0.92, sw = (K.PHONE.w - 28) * s, k = sw / 472;
    const scrX = 540 - (K.PHONE.w * s) / 2 + 14 * s, scrY = 800 - (K.PHONE.h * s) / 2 + 14 * s;
    const gearW = [scrX + 48 * k, scrY + ((K.PHONE.h - 28) * s * 0.1) / 2 + 6 * k];
    const rowW = [scrX + sw - 90 * k, scrY + 190 * k + 2 * 112 * k];
    add({ id: 'S03', at: st, cam: [540, 800], zoom: 0.08, note: 'tap gear, settings slide in on "settings", Grid lines ON on "grid"',
      draw(lt, d, t) {
        K.studio(t);
        K.phone(540, 800, s, 0, (w, h) => {
          K.cameraApp(w, h, { t, subj: 0.5, gearHi: lt > tapT && lt < sett + 0.2 });
          K.settings(w, h, seg(lt, sett, sett + 0.35), seg(lt, gr - 0.5, gr - 0.3), seg(lt, gr, gr + 0.2));
        });
        K.tap(gearW[0], gearW[1], seg(lt, tapT, tapT + 0.45), 0.9);
        K.tap(rowW[0], rowW[1], seg(lt, gr - 0.08, gr + 0.4), 0.9);
        if (lt > gr) K.pill('ON', 900, rowW[1], 54, C.teal, C.ink, eob(seg(lt, gr + 0.05, gr + 0.3)));
      } });
    cue(st, 'whoosh'); cue(st + tapT, 'tap'); cue(st + sett, 'slide', { dur: 0.35, gain: 0.7 }); cue(st + gr - 0.05, 'tap'); cue(st + gr + 0.05, 'pop');
  }

  // ── 4 · RULE: big viewfinder with the grid, the tree slides to the right third, power points glow on "cross" ──
  {
    const st = cut(3), subj = Wd('subject', 3) - st, cross = Wd('cross', 3) - st;
    add({ id: 'S04', at: st, cam: [540, 760], zoom: 0.05, note: 'grid on, tree moves centre → right third, hotspots on "cross"',
      draw(lt, d, t) {
        K.studio(t);
        const u = lerp(0.5, 2 / 3, eio(seg(lt, subj - 0.1, cross)));
        bigFinder(t, u, 1);
        [[1, 1], [2, 1], [1, 2], [2, 2]].forEach(([i, j], n) => {
          const [hx, hy] = third(i, j); K.hotspot(hx, hy, i === 2 ? 1.25 : 0.8, seg(lt, cross - 0.1 + n * 0.06, cross + 0.15 + n * 0.06), t);
        });
      } });
    cue(st, 'whoosh'); cue(st + subj, 'slide', { dur: cross - subj, gain: 0.8 }); cue(st + cross, 'sparkle', { dur: 0.6 });
  }

  // ── 5 · MYTH: centred version, red X on "center" ───────────────────────────────────────
  {
    const st = cut(4), x = Wd('center', 4) - st - 0.05;
    add({ id: 'S05', at: st, cam: [540, 760], zoom: 0.04, note: 'tree dead centre, red X slams on "center"',
      draw(lt, d, t) {
        K.studio(t);
        bigFinder(t, 0.5, 1, { brackets: false });
        ctx.save(); ctx.globalAlpha = 0.6; ctx.strokeStyle = C.red; ctx.lineWidth = 6; ctx.setLineDash([22, 16]);
        ctx.beginPath(); ctx.moveTo(540, FRAME.y + 30); ctx.lineTo(540, FRAME.y + FRAME.h - 30); ctx.stroke(); ctx.restore();
        K.redX(540, 740, lt > x ? lerp(1.9, 1.15, eo(seg(lt, x, x + 0.18))) : 0, lt > x ? 1 : 0);
      } });
    cue(st, 'whoosh'); cue(st + x + 0.08, 'slam');
  }

  // ── 6 · RESULT: back on the third, shutter on "shot", the print + check on "balanced" ──
  {
    const st = cut(5), shot = Wd('shot', 5) - st, bal = Wd('balanced', 5) - st;
    add({ id: 'S06', at: st, cam: [540, 760], zoom: 0.05, note: 'shutter on "shot", photo prints, green check on "balanced"',
      draw(lt, d, t) {
        K.studio(t);
        const p = eio(seg(lt, shot + 0.15, shot + 0.75));            // viewfinder → tilted print
        const cx = 540, cy = lerp(FRAME.y + FRAME.h / 2, 760, p);
        const w = lerp(FRAME.w, 740, p), h = lerp(FRAME.h, 820, p);
        if (p <= 0) bigFinder(t, 2 / 3, 1);
        else K.print(cx, cy, w, h, lerp(0, -0.06, p), 2 / 3, t);
        K.check(850, 400, eob(seg(lt, bal - 0.05, bal + 0.25)) * 0.9);
        K.flash(lt > shot ? 0.85 * (1 - seg(lt, shot, shot + 0.3)) : 0);
      } });
    cue(st, 'whoosh'); cue(st + shot, 'shutter'); cue(st + shot + 0.2, 'slide', { dur: 0.5, gain: 0.6 }); cue(st + bal, 'sparkle', { dur: 0.8 });
  }

  // ── 7 · END CARD: follow + next lesson ─────────────────────────────────────────────────
  {
    const st = cut(6), fol = Wd('follow', 6) - st, two = Wd('two', 6) - st;
    add({ id: 'S07', at: st, cam: [540, 700], zoom: 0.05, note: 'FOLLOW button, NEXT: LESSON 02 card',
      draw(lt, d, t) {
        K.studio(t, C.panel2);
        K.aperture(540, 470, 190, 0.45 + 0.15 * Math.sin(t * 2), t * 0.6, C.teal);
        // follow button
        const sc = eob(seg(lt, fol - 0.1, fol + 0.2)) * (1 + 0.04 * Math.sin(Math.max(0, lt - fol) * 8));
        if (sc > 0) {
          ctx.save(); ctx.translate(540, 800); ctx.scale(sc, sc);
          ctx.fillStyle = C.ink; rr(-260, -78, 520, 168, 84); ctx.fill();
          ctx.fillStyle = C.yellow; rr(-260, -90, 520, 168, 84); ctx.fill();
          ctx.fillStyle = C.ink; ctx.font = '900 84px Inter'; ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.fillText('+ FOLLOW', 0, -4);
          ctx.restore();
        }
        // next lesson card
        const q = eo(seg(lt, two - 0.1, two + 0.35));
        if (q > 0) {
          ctx.save(); ctx.globalAlpha = q; ctx.translate(0, lerp(60, 0, q));
          ctx.fillStyle = C.panel; rr(150, 960, 780, 200, 36); ctx.fill();
          ctx.fillStyle = C.teal; ctx.font = '900 40px Inter'; ctx.letterSpacing = '6px'; ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
          ctx.fillText('NEXT · LESSON 02', 540, 1020); ctx.letterSpacing = '0px';
          ctx.fillStyle = C.white; ctx.font = '900 62px Inter'; ctx.fillText('TAP TO FOCUS', 540, 1098);
          ctx.restore();
        }
      } });
    cue(st, 'whoosh'); cue(st + fol, 'pop'); cue(st + two, 'pop', { gain: 0.6 });
  }

  // drawn on top of every shot, outside the camera moves (so it never gets cropped)
  const overlay = (t) => K.seriesBadge(LESSON, seg(t, 0.15, 0.55));
  return { shots: S, cues: CUES, overlay };
}
