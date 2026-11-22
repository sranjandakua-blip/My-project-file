// PHONE PHOTO SCHOOL · LESSON 05: LEADING LINES: the shot list.
// Keep key action between y 200 and 1250: the caption lives at y 1250-1550.
import { ctx, C, W, H, clamp, lerp, seg, eo, eio, eob, rr, line, circle } from './core/lib.js';
import { L, Wd, T } from './core/timing.js';
import * as K from './core/kit.js';

const LESSON = 5, F = K.FRAME;
const SUBJ = 0.66;
const roadScene = (vx) => ({ subj: SUBJ, treeY: 0.67, treeS: 0.62, road: { vx } });
const arrowsTo = (w, h, vx) => K.roadEdges(w, h, vx).map(([a, b]) => [[a[0], a[1] - h * 0.04], [lerp(a[0], b[0], 0.97), lerp(a[1], b[1], 0.97)]]);

/** a little example tile: 0 road · 1 rails · 2 fence · 3 river. glow 0..1 = yellow lead lines */
function tile(kind, cx, cy, s, sc, glow) {
  if (sc <= 0) return;
  const x0 = -s / 2, y0 = -s / 2, hz = y0 + s * 0.42, vx = kind === 2 ? s * 0.2 : 0;
  ctx.save(); ctx.translate(cx, cy); ctx.scale(sc, sc);
  ctx.fillStyle = C.ink; rr(x0 - 10, y0 - 4, s + 20, s + 20, 40); ctx.fill();
  ctx.save(); rr(x0, y0, s, s, 32); ctx.clip();
  ctx.fillStyle = C.sky; ctx.fillRect(x0, y0, s, s); ctx.fillStyle = C.ground; ctx.fillRect(x0, hz, s, s);
  let lines = [];
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
  } else {
    ctx.fillStyle = '#3D8FD6'; ctx.beginPath(); ctx.moveTo(x0 - 10, -y0); ctx.quadraticCurveTo(-s * 0.1, y0 + s * 0.75, vx - 3, hz);
    ctx.lineTo(vx + 3, hz); ctx.quadraticCurveTo(s * 0.25, y0 + s * 0.75, -x0 * 0.6, -y0); ctx.fill();
    lines = [[[-s * 0.25, -y0], [vx, hz]], [[s * 0.15, -y0], [vx, hz]]];
  }
  ctx.fillStyle = C.mtnNear; ctx.beginPath(); ctx.moveTo(x0, hz); ctx.lineTo(x0 + s * 0.3, hz - s * 0.12); ctx.lineTo(x0 + s * 0.6, hz - s * 0.05); ctx.lineTo(-x0, hz - s * 0.14); ctx.lineTo(-x0, hz); ctx.fill();
  if (glow > 0) { K.leadArrows(lines.map(([a, b]) => [a, [lerp(a[0], b[0], 0.95), lerp(a[1], b[1], 0.95)]]), glow, 9); K.hotspot(vx, hz, 0.8, glow, glow * 3); }
  ctx.restore(); ctx.restore();
}

export function buildShots() {
  const S = [], CUES = [];
  const add = (o) => (S.push(o), o);
  const cue = (t, type, o = {}) => CUES.push({ t: +t.toFixed(3), type, ...o });
  const cut = (i) => (i === 0 ? 0 : L(i) - 0.08);

  // ── 1 · HOOK: phone rises on a road shot; arrows race up the road on "pull" ──
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

  // ── 2 · LESSON CARD ──
  {
    const st = cut(1);
    add({ id: 'S02', at: st, cam: [540, 700], zoom: 0.1, note: 'lesson card 05, LEADING LINES',
      draw: (lt, d, t) => K.lessonCard(lt, t, LESSON, 'LEADING LINES', Wd('five', 1) - st, Wd('leading', 1) - st) });
    cue(st, 'whoosh'); cue(Wd('five', 1) - 0.02, 'slam', { gain: 0.8 }); cue(Wd('leading', 1), 'pop');
  }

  // ── 3 · EXAMPLES: road, rails, fence, river tiles pop on their words; lead lines light up on "eye" ──
  {
    const st = cut(2), words = ['roads', 'rails', 'fences', 'rivers'].map((w) => Wd(w, 2) - st), eye = Wd('eye', 2) - st;
    const pos = [[300, 560], [780, 560], [300, 1010], [780, 1010]];
    add({ id: 'S03', at: st, cam: [540, 780], zoom: 0.04, note: 'four example tiles pop on their words, arrows on "eye"',
      draw(lt, d, t) {
        K.studio(t);
        pos.forEach(([x, y], i) => tile(i, x, y, 400, eob(seg(lt, words[i] - 0.05, words[i] + 0.2)), seg(lt, eye - 0.05 + i * 0.05, eye + 0.4 + i * 0.05)));
      } });
    cue(st, 'whoosh'); words.forEach((w) => cue(st + w, 'pop', { gain: 0.7 })); cue(st + eye, 'sparkle', { dur: 0.6 });
  }

  // ── 4 · LINE THEM UP: the road swings round until it points at the tree ──
  {
    const st = cut(3), up = Wd('up', 3) - st;
    add({ id: 'S04', at: st, cam: [540, 760], zoom: 0.05, note: 'road swings from left to the tree, lands on "up"',
      draw(lt, d, t) {
        K.studio(t);
        const vx = lerp(0.12, SUBJ, eio(seg(lt, 0.1, up + 0.2)));
        K.finder(t, roadScene(vx), { grid: 1 });
      } });
    cue(st, 'whoosh'); cue(st + 0.1, 'slide', { dur: up + 0.1, gain: 0.7 }); cue(st + up + 0.2, 'thud', { gain: 0.6 });
  }

  // ── 5 · TOWARD YOUR SUBJECT: arrows race up the road, brackets on the tree on "subject" ──
  {
    const st = cut(4), str = Wd('straight', 4) - st, subj = Wd('subject', 4) - st;
    add({ id: 'S05', at: st, cam: [640, 700], zoom: 0.1, note: 'arrows run up the road on "straight", brackets on "subject"',
      draw(lt, d, t) {
        K.studio(t);
        K.finder(t, roadScene(SUBJ), { over: (w, h) => K.leadArrows(arrowsTo(w, h, SUBJ), seg(lt, str, subj), 12),
          brackets: lt > subj ? [SUBJ, 0.55, lerp(160, 110, eo(seg(lt, subj, subj + 0.25)))] : null });
        if (lt > subj) K.check(860, 400, eob(seg(lt, subj, subj + 0.25)) * 0.8);
      } });
    cue(st, 'whoosh'); cue(st + str, 'zip'); cue(st + subj, 'sparkle', { dur: 0.5 });
  }

  // ── 6 · NOT OFF THE EDGE: the road runs out of frame, arrows follow it, red X on "edge" ──
  {
    const st = cut(5), edge = Wd('edge', 5) - st;
    add({ id: 'S06', at: st, cam: [540, 760], zoom: 0.04, note: 'road leads off the left edge, red X on "edge"',
      draw(lt, d, t) {
        K.studio(t);
        K.finder(t, roadScene(-0.35), { over: (w, h) => K.leadArrows(arrowsTo(w, h, -0.35), seg(lt, 0, edge), 12) });
        K.redX(540, 740, lt > edge ? lerp(1.9, 1.15, eo(seg(lt, edge, edge + 0.18))) : 0, lt > edge ? 1 : 0);
      } });
    cue(st, 'whoosh'); cue(st + 0.05, 'zip'); cue(st + edge + 0.05, 'slam');
  }

  // ── 7 · END CARD ──
  {
    const st = cut(6);
    add({ id: 'S07', at: st, cam: [540, 700], zoom: 0.05, note: 'FOLLOW, next: lesson 06',
      draw: (lt, d, t) => K.endCard(lt, t, Wd('follow', 6) - st, Wd('six', 6) - st, 6, 'GOLDEN HOUR') });
    cue(st, 'whoosh'); cue(Wd('follow', 6), 'pop'); cue(Wd('six', 6), 'pop', { gain: 0.6 });
  }

  const overlay = (t) => K.seriesBadge(LESSON, seg(t, 0.15, 0.55));
  return { shots: S, cues: CUES, overlay };
}
