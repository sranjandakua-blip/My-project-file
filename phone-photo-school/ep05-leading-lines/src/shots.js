// PHONE PHOTO SCHOOL · LESSON 05: LEADING LINES (25 s): the shot list.
// Keep key action between y 200 and 1250: the caption lives at y 1250-1550.
import { ctx, C, W, H, clamp, lerp, seg, eo, eio, eob, rr, line, circle } from './core/lib.js';
import { L, Wd, T } from './core/timing.js';
import * as K from './core/kit.js';

const LESSON = 5, F = K.FRAME;
const SUBJ = 0.66;
const roadScene = (vx, spread = 0) => ({ subj: SUBJ, treeY: 0.67, treeS: 0.62, road: { vx, spread } });
const arrowsTo = (w, h, vx, spread = 0, hzF = 0.64) => K.roadEdges(w, h, vx, spread, hzF).map(([a, b]) => [[a[0], a[1] - h * 0.04], [lerp(a[0], b[0], 0.97), lerp(a[1], b[1], 0.97)]]);

/** an example tile: 0 road · 1 rails · 2 fence · 3 river · 4 shadows · 5 staircase · 6 shoreline. glow 0..1 = yellow lead lines */
function tile(kind, cx, cy, s, sc, glow) {
  if (sc <= 0) return;
  const x0 = -s / 2, y0 = -s / 2, hz = y0 + s * 0.42, vx = kind === 2 ? s * 0.2 : 0;
  ctx.save(); ctx.translate(cx, cy); ctx.scale(sc, sc);
  ctx.fillStyle = C.ink; rr(x0 - 10, y0 - 4, s + 20, s + 20, 40); ctx.fill();
  ctx.save(); rr(x0, y0, s, s, 32); ctx.clip();
  ctx.fillStyle = C.sky; ctx.fillRect(x0, y0, s, s); ctx.fillStyle = C.ground; ctx.fillRect(x0, hz, s, s);
  let lines = [], mtn = true;
  if (kind === 0) {
    ctx.fillStyle = '#5C6478'; ctx.beginPath(); ctx.moveTo(x0 + s * 0.08, -y0); ctx.lineTo(vx - 4, hz); ctx.lineTo(vx + 4, hz); ctx.lineTo(-x0 - s * 0.08, -y0); ctx.fill();
    line([[0, -y0], [vx, hz]], C.yellow, 6); lines = [[[x0 + s * 0.08, -y0], [vx, hz]], [[-x0 - s * 0.08, -y0], [vx, hz]]];
  } else if (kind === 1) {
    ctx.fillStyle = '#B49A7A'; ctx.beginPath(); ctx.moveTo(x0 + s * 0.12, -y0); ctx.lineTo(vx - 3, hz); ctx.lineTo(vx + 3, hz); ctx.lineTo(-x0 - s * 0.12, -y0); ctx.fill();
    for (let i = 0; i < 8; i++) { const u = Math.pow(i / 8, 1.5), y = lerp(-y0, hz, u), hw = lerp(s * 0.36, 2, u); ctx.fillStyle = '#7A4B2E'; ctx.fillRect(-hw, y - lerp(14, 2, u), hw * 2, lerp(14, 2, u)); }
    lines = [[[-s * 0.26, -y0], [vx, hz]], [[s * 0.26, -y0], [vx, hz]]];
    for (const l of lines) line(l, '#C9CED8', 8);
  } else if (kind === 2) {
    const a = [x0, -y0 - s * 0.05], b = [vx, hz];
    for (let i = 0; i < 9; i++) { const u = Math.pow(i / 9, 1.3), px = lerp(a[0], b[0], u), py = lerp(a[1], b[1], u), ph = lerp(s * 0.4, 6, u);
      ctx.fillStyle = '#8A5A3A'; ctx.fillRect(px - lerp(12, 1, u), py - ph, lerp(24, 2, u), ph); }
    lines = [[[a[0], a[1] - s * 0.3], [vx, hz - 4]], [[a[0], a[1] - s * 0.12], [vx, hz - 2]]];
    for (const l of lines) line(l, '#8A5A3A', 9);
  } else if (kind === 3) {
    ctx.fillStyle = '#3D8FD6'; ctx.beginPath(); ctx.moveTo(x0 - 10, -y0); ctx.quadraticCurveTo(-s * 0.1, y0 + s * 0.75, vx - 3, hz);
    ctx.lineTo(vx + 3, hz); ctx.quadraticCurveTo(s * 0.25, y0 + s * 0.75, -x0 * 0.6, -y0); ctx.fill();
    lines = [[[-s * 0.25, -y0], [vx, hz]], [[s * 0.15, -y0], [vx, hz]]];
  } else if (kind === 4) {                                   // long shadows across a sunny plaza
    ctx.fillStyle = '#E8D9B5'; ctx.fillRect(x0, hz, s, s);
    ctx.fillStyle = '#B8A684';
    for (const ox of [-0.38, -0.08, 0.22]) { ctx.beginPath(); ctx.moveTo(ox * s, -y0); ctx.lineTo(ox * s + s * 0.14, -y0); ctx.lineTo(s * 0.08, hz); ctx.lineTo(s * 0.06, hz); ctx.fill(); }
    lines = [[[-0.31 * s, -y0], [s * 0.07, hz]], [[0.29 * s, -y0], [s * 0.07, hz]]];
  } else if (kind === 5) {                                   // looking up a staircase
    mtn = false; ctx.fillStyle = '#D5DAE3'; ctx.fillRect(x0, y0, s, s);
    for (let i = 0; i < 9; i++) { const u0 = i / 9, u1 = (i + 1) / 9, y = lerp(-y0, y0 + s * 0.08, u0), y2 = lerp(-y0, y0 + s * 0.08, u1);
      const hw = lerp(s * 0.5, s * 0.08, u0), hw2 = lerp(s * 0.5, s * 0.08, u1);
      ctx.fillStyle = i % 2 ? '#9AA3B5' : '#B8BFCC'; ctx.beginPath(); ctx.moveTo(-hw, y); ctx.lineTo(hw, y); ctx.lineTo(hw2, y2); ctx.lineTo(-hw2, y2); ctx.fill(); }
    lines = [[[-s * 0.46, -y0], [-s * 0.07, y0 + s * 0.1]], [[s * 0.46, -y0], [s * 0.07, y0 + s * 0.1]]];
    for (const l of lines) line(l, '#6B7385', 10);
  } else {                                                   // shoreline curving to the horizon
    ctx.fillStyle = '#3D8FD6'; ctx.fillRect(x0, hz, s, s);
    ctx.fillStyle = '#EAD7A4'; ctx.beginPath(); ctx.moveTo(x0, -y0); ctx.lineTo(x0, hz); ctx.lineTo(-s * 0.05, hz); ctx.quadraticCurveTo(-s * 0.02, y0 + s * 0.75, s * 0.2, -y0); ctx.fill();
    line([[s * 0.2, -y0], [-s * 0.02, y0 + s * 0.72], [-s * 0.05, hz]], C.white, 6);
    lines = [[[s * 0.2, -y0], [-s * 0.05, hz]]];
  }
  if (mtn) { ctx.fillStyle = C.mtnNear; ctx.beginPath(); ctx.moveTo(x0, hz); ctx.lineTo(x0 + s * 0.3, hz - s * 0.12); ctx.lineTo(x0 + s * 0.6, hz - s * 0.05); ctx.lineTo(-x0, hz - s * 0.14); ctx.lineTo(-x0, hz); ctx.fill(); }
  if (glow > 0) { K.leadArrows(lines.map(([a, b]) => [a, [lerp(a[0], b[0], 0.95), lerp(a[1], b[1], 0.95)]]), glow, 9); }
  ctx.restore(); ctx.restore();
}

export function buildShots() {
  const S = [], CUES = [];
  const add = (o) => (S.push(o), o);
  const cue = (t, type, o = {}) => CUES.push({ t: +t.toFixed(3), type, ...o });
  const cut = (i) => (i === 0 ? 0 : L(i) - 0.08);

  // ── 0 · HOOK: phone rises on a road shot; arrows race up the road on "pull" ──
  {
    const st = cut(0), pull = Wd('pull', 0) - st;
    add({ id: 'S01', at: st, cam: [540, 800], zoom: 0.1, note: 'phone rises, road scene, arrows run to the tree on "pull"',
      draw(lt, d, t) {
        K.studio(t);
        const rise = eob(seg(lt, 0, 0.6));
        K.phone(540, lerp(1900, 800, rise), 0.92, lerp(-0.2, -0.04, rise), (w, h) => K.cameraApp(w, h, {
          t, subj: SUBJ, scene: roadScene(SUBJ),
          over: (vw, vh) => K.leadArrows(arrowsTo(vw, vh, SUBJ), seg(lt, pull, pull + 0.6), 7),
        }));
      } });
    cue(st + 0.05, 'whoosh'); cue(st + pull, 'zip');
  }

  // ── 1 · LESSON CARD ──
  {
    const st = cut(1);
    add({ id: 'S02', at: st, cam: [540, 700], zoom: 0.1, note: 'lesson card 05, LEADING LINES',
      draw: (lt, d, t) => K.lessonCard(lt, t, LESSON, 'LEADING LINES', Wd('five', 1) - st, Wd('leading', 1) - st) });
    cue(st, 'whoosh'); cue(Wd('five', 1) - 0.02, 'slam', { gain: 0.8 }); cue(Wd('leading', 1), 'pop');
  }

  // ── 2 · EXAMPLES: road, rails, fence, river tiles pop on their words; arrows on "eye" ──
  {
    const st = cut(2), words = ['roads', 'rails', 'fences', 'rivers'].map((w) => Wd(w, 2) - st), eye = Wd('eye', 2) - st;
    const pos = [[300, 560], [780, 560], [300, 1010], [780, 1010]];
    add({ id: 'S03', at: st, cam: [540, 780], zoom: 0.04, note: 'four tiles pop on their words, arrows on "eye"',
      draw(lt, d, t) {
        K.studio(t);
        pos.forEach(([x, y], i) => tile(i, x, y, 400, eob(seg(lt, words[i] - 0.05, words[i] + 0.2)), seg(lt, eye - 0.05 + i * 0.05, eye + 0.4 + i * 0.05)));
      } });
    cue(st, 'whoosh'); words.forEach((w) => cue(st + w, 'pop', { gain: 0.7 })); cue(st + eye, 'sparkle', { dur: 0.6 });
  }

  // ── 3 · MORE: shadows, staircase, shoreline tiles pop on their words, arrows on "work" ──
  {
    const st = cut(3), words = ['shadows', 'staircases', 'shorelines'].map((w) => Wd(w, 3) - st), work = Wd('work', 3) - st;
    const pos = [[300, 560], [780, 560], [540, 1010]];
    add({ id: 'S04', at: st, cam: [540, 780], zoom: 0.04, note: 'shadows / stairs / shoreline tiles, arrows on "work"',
      draw(lt, d, t) {
        K.studio(t);
        pos.forEach(([x, y], i) => tile(4 + i, x, y, 400, eob(seg(lt, i ? words[i] - 0.05 : Math.min(words[0] - 0.05, 0.1), (i ? words[i] : Math.min(words[0], 0.15)) + 0.2)), seg(lt, work - 0.05 + i * 0.05, work + 0.4 + i * 0.05)));
      } });
    cue(st, 'whoosh'); words.forEach((w) => cue(st + w, 'pop', { gain: 0.7 })); cue(st + work, 'sparkle', { dur: 0.6 });
  }

  // ── 4 · LINE THEM UP: the road swings round until it points at the tree ──
  {
    const st = cut(4), up = Wd('up', 4) - st;
    add({ id: 'S05', at: st, cam: [540, 760], zoom: 0.05, note: 'road swings from left to the tree, lands on "up"',
      draw(lt, d, t) {
        K.studio(t);
        K.finder(t, roadScene(lerp(0.12, SUBJ, eio(seg(lt, 0.1, up + 0.2)))), { grid: 1 });
      } });
    cue(st, 'whoosh'); cue(st + 0.1, 'slide', { dur: up + 0.1, gain: 0.7 }); cue(st + up + 0.2, 'thud', { gain: 0.6 });
  }

  // ── 5 · TOWARD YOUR SUBJECT: arrows race up the road, brackets on the tree on "subject" ──
  {
    const st = cut(5), str = Wd('straight', 5) - st, subj = Wd('subject', 5) - st;
    add({ id: 'S06', at: st, cam: [640, 700], zoom: 0.1, note: 'arrows on "straight", brackets on "subject"',
      draw(lt, d, t) {
        K.studio(t);
        K.finder(t, roadScene(SUBJ), { over: (w, h) => K.leadArrows(arrowsTo(w, h, SUBJ), seg(lt, str, subj), 12),
          brackets: lt > subj ? [SUBJ, 0.55, lerp(160, 110, eo(seg(lt, subj, subj + 0.25)))] : null });
        if (lt > subj) K.check(860, 400, eob(seg(lt, subj, subj + 0.25)) * 0.8);
      } });
    cue(st, 'whoosh'); cue(st + str, 'zip'); cue(st + subj, 'sparkle', { dur: 0.5 });
  }

  // ── 6 · NOT OFF THE EDGE: the road runs out of frame, red X on "edge" ──
  {
    const st = cut(6), edge = Wd('edge', 6) - st;
    add({ id: 'S07', at: st, cam: [540, 760], zoom: 0.04, note: 'road leads off the left edge, red X on "edge"',
      draw(lt, d, t) {
        K.studio(t);
        K.finder(t, roadScene(-0.35), { over: (w, h) => K.leadArrows(arrowsTo(w, h, -0.35), seg(lt, 0, edge), 12) });
        K.redX(540, 740, lt > edge ? lerp(1.9, 1.15, eo(seg(lt, edge, edge + 0.18))) : 0, lt > edge ? 1 : 0);
      } });
    cue(st, 'whoosh'); cue(st + 0.05, 'zip'); cue(st + edge + 0.05, 'slam');
  }

  // ── 7 · THE EYE FOLLOWS: an eye travels up the road on "follows", lands on the tree on "lands" ──
  {
    const st = cut(7), fol = Wd('follows', 7) - st, lands = Wd('lands', 7) - st, want = Wd('want', 7) - st;
    add({ id: 'S08', at: st, cam: [600, 720], zoom: 0.08, note: 'eye travels up the road on "follows", hits the tree on "lands", check on "want"',
      draw(lt, d, t) {
        K.studio(t);
        const p = eio(seg(lt, fol - 0.2, lands));
        K.finder(t, roadScene(SUBJ), { over: (w, h) => {
          const x0 = w * 0.55, y0 = h * 0.97, x1 = SUBJ * w, y1 = h * 0.55;
          ctx.save(); ctx.setLineDash([18, 16]); ctx.strokeStyle = C.yellow; ctx.lineWidth = 8;
          ctx.beginPath(); ctx.moveTo(x0, y0); ctx.lineTo(lerp(x0, x1, p), lerp(y0, y1, p)); ctx.stroke(); ctx.restore();
          if (lt > lands) K.hotspot(x1, y1, 2, seg(lt, lands, lands + 0.2), t);
          K.eye(lerp(x0, x1, p), lerp(y0, y1, p) - 60, lerp(150, 90, p));
        }, brackets: lt > lands ? [SUBJ, 0.55, 120] : null });
        K.check(860, 400, eob(seg(lt, want, want + 0.25)) * 0.8);
      } });
    cue(st, 'whoosh'); cue(st + fol - 0.2, 'slide', { dur: lands - fol + 0.2, gain: 0.7 }); cue(st + lands, 'pop'); cue(st + want, 'sparkle', { dur: 0.5 });
  }

  // ── 8 · GET LOW + .6x: the road spreads wide at the bottom; .6x chip on "point", arrows on "stretch" ──
  {
    const st = cut(8), low = Wd('low', 8) - st, wide = Wd('wide', 8) - st, pt = Wd('point', 8) - st, str = Wd('stretch', 8) - st;
    add({ id: 'S09', at: st, cam: [540, 760], zoom: 0.06, note: 'GET LOW on "low", road widens on "wide", .6x chip on "point", arrows on "stretch"',
      draw(lt, d, t) {
        K.studio(t);
        const g = eio(seg(lt, low - 0.1, pt + 0.5)), sp = lerp(0, 0.6, g), hzF = lerp(0.64, 0.47, g);
        K.finder(t, { ...roadScene(SUBJ, sp), hz: hzF, treeY: hzF + 0.03, treeS: lerp(0.62, 0.42, g) },
          { over: (w, h) => K.leadArrows(arrowsTo(w, h, SUBJ, Math.min(sp, 0.12), hzF), seg(lt, str - 0.1, str + 0.5), 14) });
        K.pill('GET LOW', 300, 400, 54, C.yellow, C.ink, eob(seg(lt, low, low + 0.25)));
        if (lt > pt) { const p = eob(seg(lt, pt, pt + 0.25)); ctx.save(); ctx.translate(840, 400); ctx.scale(p, p);
          circle(0, 5, 66, C.ink); circle(0, 0, 66, C.yellow); ctx.fillStyle = C.ink; ctx.font = '900 54px Inter'; ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.fillText('.6', 0, 3); ctx.restore(); }
      } });
    cue(st, 'whoosh'); cue(st + low, 'pop'); cue(st + wide, 'slide', { dur: 0.8, gain: 0.6 }); cue(st + pt, 'tap'); cue(st + str, 'zip');
  }

  // ── 9 · END CARD ──
  {
    const st = cut(9);
    add({ id: 'S10', at: st, cam: [540, 700], zoom: 0.05, note: 'avatar, FOLLOW, next: lesson 06',
      draw: (lt, d, t) => K.endCard(lt, t, Wd('follow', 9) - st, Wd('six', 9) - st, 6, 'GOLDEN HOUR') });
    cue(st, 'whoosh'); cue(Wd('follow', 9), 'pop'); cue(Wd('six', 9), 'pop', { gain: 0.6 });
  }

  const overlay = (t) => K.seriesBadge(LESSON, seg(t, 0.15, 0.55));
  return { shots: S, cues: CUES, overlay };
}
