// PHONE PHOTO SCHOOL · LESSON 06: GOLDEN HOUR (25 s): the shot list.
// Keep key action between y 200 and 1250: the caption lives at y 1250-1550.
import { ctx, C, W, H, clamp, lerp, seg, eo, eio, eob, rr, line, circle } from './core/lib.js';
import { L, Wd, T } from './core/timing.js';
import * as K from './core/kit.js';

const LESSON = 6, F = K.FRAME;
const PERSON = { x: 0.42, y: 0.94, s: 0.42 };

export function buildShots() {
  const S = [], CUES = [];
  const add = (o) => (S.push(o), o);
  const cue = (t, type, o = {}) => CUES.push({ t: +t.toFixed(3), type, ...o });
  const cut = (i) => (i === 0 ? 0 : L(i) - 0.08);

  // ── 0 · HOOK: phone rises showing the creator's sunset; a warm glow blooms on "glow" ──
  {
    const st = cut(0), glow = Wd('glow', 0) - st;
    add({ id: 'S01', at: st, cam: [540, 800], zoom: 0.06, note: 'phone rises with the sunset photo, glow on "glow"',
      draw(lt, d, t) {
        K.studio(t);
        const rise = eob(seg(lt, 0, 0.6)), g = eo(seg(lt, glow - 0.1, glow + 0.4));
        K.phone(540, lerp(1900, 800, rise), 0.92, lerp(-0.2, -0.04, rise), (w, h) => K.cameraApp(w, h, {
          t, photo: 'sunset', photoOpts: { cy: 0.7, bright: lerp(0.9, 1.15, g) }, grid: 1,
          over: (vw, vh) => { if (g > 0) { ctx.save(); ctx.globalCompositeOperation = 'lighter'; ctx.globalAlpha = 0.35 * g; circle(vw * 0.39, vh * 0.78, vw * 0.4, '#FFB347'); ctx.restore(); } },
        }));
      } });
    cue(st + 0.05, 'whoosh'); cue(st + glow, 'sparkle', { dur: 0.8 });
  }

  // ── 1 · LESSON CARD ──
  {
    const st = cut(1);
    add({ id: 'S02', at: st, cam: [540, 700], zoom: 0.1, note: 'lesson card 06, GOLDEN HOUR',
      draw: (lt, d, t) => K.lessonCard(lt, t, LESSON, 'GOLDEN HOUR', Wd('six', 1) - st, Wd('golden', 1) - st) });
    cue(st, 'whoosh'); cue(Wd('six', 1) - 0.02, 'slam', { gain: 0.8 }); cue(Wd('golden', 1), 'pop');
  }

  // ── 2 · WHEN: the sun's path across the day; the two golden ends light up on "sunrise" / "sunset" ──
  {
    const st = cut(2), rise = Wd('sunrise', 2) - st, set = Wd('sunset', 2) - st;
    const cx = 540, cy = 980, r = 400;
    add({ id: 'S03', at: st, cam: [540, 760], zoom: 0.05, note: 'day arc; golden ends glow on "sunrise" and "sunset", sun travels',
      draw(lt, d, t) {
        K.studio(t);
        ctx.fillStyle = C.panel; ctx.fillRect(80, cy, 920, 6);                       // horizon
        ctx.strokeStyle = C.line; ctx.lineWidth = 10; ctx.setLineDash([16, 18]); ctx.beginPath(); ctx.arc(cx, cy, r, Math.PI, 0); ctx.stroke(); ctx.setLineDash([]);
        const seg1 = eo(seg(lt, rise - 0.15, rise + 0.35)), seg2 = eo(seg(lt, set - 0.15, set + 0.35)), A = 0.42;
        ctx.lineCap = 'round'; ctx.lineWidth = 22; ctx.strokeStyle = '#F5A142';
        if (seg1 > 0) { ctx.beginPath(); ctx.arc(cx, cy, r, Math.PI, Math.PI + A * seg1); ctx.stroke(); }
        if (seg2 > 0) { ctx.beginPath(); ctx.arc(cx, cy, r, -A * seg2, 0); ctx.stroke(); }
        const u = clamp(lt / d), a = Math.PI + u * Math.PI, golden = u < 0.13 || u > 0.87;
        K.sunIcon(cx + Math.cos(a) * r, cy + Math.sin(a) * r, 52, golden ? '#F5A142' : C.yellow);
        K.pill('1 HR AFTER SUNRISE', 290, cy + 90, 36, '#F5A142', C.ink, eob(seg(lt, rise, rise + 0.25)));
        K.pill('1 HR BEFORE SUNSET', 790, cy + 90, 36, '#F5A142', C.ink, eob(seg(lt, set, set + 0.25)));
      } });
    cue(st, 'whoosh'); cue(st + rise, 'pop'); cue(st + set, 'pop');
  }

  // ── 3 · SOFT + WARM: low sun, warm sky, long shadows ──
  {
    const st = cut(3), low = Wd('low', 3) - st, warm = Wd('warm', 3) - st;
    add({ id: 'S04', at: st, cam: [540, 760], zoom: 0.05, note: 'golden scene: sun sinks on "low", SOFT + WARM on "warm"',
      draw(lt, d, t) {
        K.studio(t);
        K.photoFinder('stupa', { cy: 0.45, zoom: lerp(1.25, 1.05, eio(seg(lt, 0, d))) }, { tag: seg(lt, warm, warm + 0.3) });
        K.pill('LOW SUN', 300, 420, 48, '#F5A142', C.ink, eob(seg(lt, low, low + 0.25)));
        K.pill('SOFT + WARM', 540, 1150, 54, C.yellow, C.ink, eob(seg(lt, warm, warm + 0.25)));
      } });
    cue(st, 'whoosh'); cue(st + 0.1, 'slide', { dur: low + 0.2, gain: 0.5 }); cue(st + low, 'pop', { gain: 0.6 }); cue(st + warm, 'sparkle', { dur: 0.6 });
  }

  // ── 4 · HARSH NOON: sun overhead, hard little shadows, red X ──
  {
    const st = cut(4), mid = Wd('midday', 4) - st, sh = Wd('shadows', 4) - st, sq = Wd('squinting', 4) - st;
    add({ id: 'S05', at: st, cam: [540, 760], zoom: 0.05, note: 'noon scene, HARD SHADOWS on "shadows", red X on "squinting"',
      draw(lt, d, t) {
        K.studio(t);
        K.finder(t, { light: 'noon', subj: 0.78, treeS: 0.8, person: { x: 0.4, y: 0.9, s: 0.36 } }, { over: (w, h) => {
          if (lt > mid) for (let i = 0; i < 8; i++) { const a = i / 8 * Math.PI * 2 + t; line([[w * 0.5 + Math.cos(a) * 70, h * 0.09 + Math.sin(a) * 70], [w * 0.5 + Math.cos(a) * 100, h * 0.09 + Math.sin(a) * 100]], '#FFFDF0', 8); }
        } });
        K.pill('MIDDAY', 300, 420, 48, C.white, C.ink, eob(seg(lt, mid, mid + 0.25)));
        K.pill('HARD SHADOWS', 540, 1150, 54, C.red, C.white, eob(seg(lt, sh, sh + 0.25)));
        K.redX(780, 760, lt > sq ? lerp(1.6, 0.9, eo(seg(lt, sq, sq + 0.18))) : 0, lt > sq ? 1 : 0);
      } });
    cue(st, 'whoosh'); cue(st + mid, 'pop'); cue(st + sh, 'pop'); cue(st + sq + 0.05, 'slam', { gain: 0.7 });
  }

  // ── 5 · SUN BEHIND: the sun slides round behind the subject on "behind" ──
  const golden = (sx, rim) => ({ light: 'golden', sunX: sx, sunY: 0.52, subj: 0.85, treeS: 0.6, treeY: 0.8, person: { ...PERSON, rim } });
  {
    const st = cut(5), be = Wd('behind', 5) - st, su = Wd('subject', 5) - st;
    add({ id: 'S06', at: st, cam: [480, 700], zoom: 0.06, note: 'sun moves behind the person on "behind"',
      draw(lt, d, t) {
        K.studio(t);
        K.finder(t, golden(lerp(0.8, 0.42, eio(seg(lt, be - 0.3, su))), 0), { brackets: lt > su ? [0.42, 0.68, 150] : null });
        K.pill('SUN BEHIND', 300, 420, 48, '#F5A142', C.ink, eob(seg(lt, be, be + 0.25)));
      } });
    cue(st, 'whoosh'); cue(st + be - 0.3, 'slide', { dur: su - be + 0.3, gain: 0.6 }); cue(st + su, 'pop', { gain: 0.6 });
  }

  // ── 6 · RIM LIGHT: a warm glowing edge appears around the subject on "rim" ──
  {
    const st = cut(6), rim = Wd('rim', 6) - st;
    add({ id: 'S07', at: st, cam: [400, 640], zoom: 0.12, note: 'rim glow on "rim"',
      draw(lt, d, t) {
        K.studio(t);
        K.finder(t, golden(0.42, eo(seg(lt, rim - 0.2, rim + 0.3))));
        K.pill('RIM LIGHT', 300, 420, 48, C.yellow, C.ink, eob(seg(lt, rim, rim + 0.25)));
        K.check(860, 400, eob(seg(lt, rim + 0.1, rim + 0.35)) * 0.8);
      } });
    cue(st, 'whoosh'); cue(st + rim, 'sparkle', { dur: 0.7 });
  }

  // ── 7 · SILHOUETTE: the creator's sunset, too bright → tap the sky, slide down → the real silhouette ──
  {
    const st = cut(7), tap = Wd('tap', 7) - st, down = Wd('down', 7) - st, sil = Wd('silhouette', 7) - st;
    const SF = [0.42, 0.62];
    add({ id: 'S08', at: st, cam: [480, 760], zoom: 0.05, note: 'sunset photo: tap sky on "tap", slide down on "down", silhouette + tag on "silhouette"',
      draw(lt, d, t) {
        K.studio(t);
        const v = lerp(0.55, -0.05, eio(seg(lt, down - 0.1, sil)));
        let r = [540, 760];
        K.photoFinder('sunset', { cy: 0.7, bright: 1 + Math.max(v, 0) * 1.6 }, { tag: seg(lt, sil + 0.2, sil + 0.5), over: (w, h, m) => {
          const [x, y] = m.at(...SF); r = [F.x + x, F.y + y]; K.focusRing(x, y, 90, seg(lt, tap, tap + 0.25));
        } });
        K.tap(r[0], r[1], seg(lt, tap - 0.05, tap + 0.4), 1.2);
        if (lt > tap) K.sunSlider(r[0] - 150, r[1], 380, v, seg(lt, tap + 0.1, tap + 0.3), 46);
        K.pill('SILHOUETTE', 540, 1150, 54, C.yellow, C.ink, eob(seg(lt, sil, sil + 0.25)));
      } });
    cue(st, 'whoosh'); cue(st + tap, 'tap'); cue(st + down - 0.1, 'slide', { dur: sil - down + 0.1, gain: 0.6 }); cue(st + sil, 'sparkle', { dur: 0.6 });
  }

  // ── 8 · END CARD ──
  {
    const st = cut(8);
    add({ id: 'S09', at: st, cam: [540, 700], zoom: 0.05, note: 'avatar, FOLLOW, next: lesson 07',
      draw: (lt, d, t) => K.endCard(lt, t, Wd('follow', 8) - st, Wd('seven', 8) - st, 7, 'PORTRAIT MODE') });
    cue(st, 'whoosh'); cue(Wd('follow', 8), 'pop'); cue(Wd('seven', 8), 'pop', { gain: 0.6 });
  }

  const overlay = (t) => K.seriesBadge(LESSON, seg(t, 0.15, 0.55), t);
  return { shots: S, cues: CUES, overlay };
}
