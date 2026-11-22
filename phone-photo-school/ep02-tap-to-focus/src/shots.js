// PHONE PHOTO SCHOOL · LESSON 02: TAP TO FOCUS: the shot list.
// Keep key action between y 200 and 1250: the caption lives at y 1250-1550.
import { ctx, C, W, H, clamp, lerp, seg, eo, eio, eob } from './core/lib.js';
import { L, Wd, T } from './core/timing.js';
import * as K from './core/kit.js';

const LESSON = 2, F = K.FRAME;
const FL = { x: 0.7, y: 0.97, s: 0.42 };                    // the foreground flower (fractions of the frame)
const flowerHead = (w, h) => [FL.x * w, FL.y * h - FL.s * h * 0.8];

export function buildShots() {
  const S = [], CUES = [];
  const add = (o) => (S.push(o), o);
  const cue = (t, type, o = {}) => CUES.push({ t: +t.toFixed(3), type, ...o });
  const cut = (i) => (i === 0 ? 0 : L(i) - 0.08);

  // ── 1 · HOOK: phone rises; it focused on the tree, the flower is a blur; ring turns red on "wrong" ──
  {
    const st = cut(0), wrong = Wd('wrong', 0) - st, blurry = Wd('blurry', 0) - st;
    add({ id: 'S01', at: st, cam: [540, 800], zoom: 0.06, note: 'phone rises, flower blurred, focus ring on tree goes red on "wrong"',
      draw(lt, d, t) {
        K.studio(t);
        const rise = eob(seg(lt, 0, 0.6));
        K.phone(540, lerp(1900, 800, rise), 0.92, lerp(-0.2, -0.04, rise), (w, h) => K.cameraApp(w, h, {
          t, subj: 0.38, scene: { flower: { ...FL, blur: 16 }, blur: 0 },
          over: (vw, vh, k) => { K.focusRing(0.38 * vw, 0.55 * vh, 46 * k, seg(lt, blurry, blurry + 0.3), lt > wrong ? C.red : C.yellow);
            if (lt > wrong) K.pill('WRONG FOCUS', vw / 2, 50 * k, 30 * k, C.red, C.white, eob(seg(lt, wrong, wrong + 0.25))); },
        }));
      } });
    cue(st + 0.05, 'whoosh'); cue(st + blurry, 'tap'); cue(st + wrong, 'boing', { gain: 0.5 });
  }

  // ── 2 · LESSON CARD ──
  {
    const st = cut(1);
    add({ id: 'S02', at: st, cam: [540, 700], zoom: 0.1, note: 'lesson card 02, TAP TO FOCUS',
      draw: (lt, d, t) => K.lessonCard(lt, t, LESSON, 'TAP TO FOCUS', Wd('two', 1) - st, Wd('tap', 1) - st) });
    cue(st, 'whoosh'); cue(Wd('two', 1) - 0.02, 'slam', { gain: 0.8 }); cue(Wd('tap', 1), 'pop');
  }

  // ── 3 · TAP: tap the flower → ring lands → flower snaps sharp, background melts on "sharp" ──
  {
    const st = cut(2), tap = Wd('subject', 2) - st - 0.1, sharp = Wd('snaps', 2) - st;
    add({ id: 'S03', at: st, cam: [640, 760], zoom: 0.06, note: 'tap flower on "subject", sharp on "sharp"',
      draw(lt, d, t) {
        K.studio(t);
        const p = eio(seg(lt, sharp - 0.15, sharp + 0.2));
        K.finder(t, { subj: 0.38, flower: { ...FL, blur: lerp(14, 0, p) }, blur: lerp(0, 8, p) }, { over: (w, h) => {
          const [fx, fy] = flowerHead(w, h); K.focusRing(fx, fy, 95, seg(lt, tap, tap + 0.3));
        } });
        const [fx, fy] = flowerHead(F.w, F.h); K.tap(F.x + fx, F.y + fy, seg(lt, tap - 0.05, tap + 0.4), 1.3);
        if (lt > sharp) K.pill('SHARP', 300, 420, 60, C.green, C.ink, eob(seg(lt, sharp, sharp + 0.25)));
      } });
    cue(st, 'whoosh'); cue(st + tap, 'tap'); cue(st + sharp, 'sparkle', { dur: 0.6 });
  }

  // ── 4 · THE SUN: over-bright shot; the sun slider pops next to the ring on "sun", starts down on "down" ──
  const ringAt = () => { const [fx, fy] = flowerHead(F.w, F.h); return [F.x + fx, F.y + fy]; };
  const slider = (val, a) => { const [rx, ry] = ringAt(); K.sunSlider(rx - 160, ry, 380, val, a, 46); };
  const focused = { subj: 0.38, flower: { ...FL, blur: 0 }, blur: 7 };
  {
    const st = cut(3), sun = Wd('sun', 3) - st, down = Wd('down', 3) - st;
    add({ id: 'S04', at: st, cam: [440, 700], zoom: 0.08, note: 'over-exposed, slider appears on "sun", moves on "down"',
      draw(lt, d, t) {
        K.studio(t);
        const v = lerp(0.6, 0.35, eio(seg(lt, down, d)));
        K.finder(t, { ...focused, bright: 1 + v * 1.5 }, { over: (w, h) => { const [fx, fy] = flowerHead(w, h); K.focusRing(fx, fy, 95, 1); } });
        slider(v, seg(lt, sun - 0.1, sun + 0.15));
        if (lt > sun && lt < sun + 0.6) { const [rx, ry] = ringAt(); K.hotspot(rx - 160, ry - v * 190, 1.6, seg(lt, sun, sun + 0.2), t); }
        K.pill('TOO BRIGHT', 540, 385, 52, C.red, C.white, eob(seg(lt, 0.1, 0.4)));
      } });
    cue(st, 'whoosh'); cue(st + sun, 'pop'); cue(st + down, 'slide', { dur: 0.6, gain: 0.6 });
  }

  // ── 5 · DOWN: slide continues down, the sky comes back on "skies" ──
  {
    const st = cut(4), skies = Wd('skies', 4) - st;
    add({ id: 'S05', at: st, cam: [440, 700], zoom: 0.04, note: 'slider down, sky detail returns on "skies"',
      draw(lt, d, t) {
        K.studio(t);
        const v = lerp(0.35, -0.1, eio(seg(lt, 0, skies)));
        K.finder(t, { ...focused, bright: 1 + Math.max(v, 0) * 1.5 + Math.min(v, 0) * 0.3 }, { over: (w, h) => { const [fx, fy] = flowerHead(w, h); K.focusRing(fx, fy, 95, 1); } });
        slider(v, 1);
        K.check(860, 400, eob(seg(lt, skies, skies + 0.25)) * 0.8);
      } });
    cue(st, 'whoosh'); cue(st, 'slide', { dur: 0.5, gain: 0.6 }); cue(st + skies, 'sparkle', { dur: 0.5 });
  }

  // ── 6 · UP: a dark, shadowy shot; slide up and it brightens on "shadows" ──
  {
    const st = cut(5), up = Wd('up', 5) - st, sh = Wd('shadows', 5) - st;
    add({ id: 'S06', at: st, cam: [440, 700], zoom: 0.05, note: 'dark shot, slider up on "up", bright on "shadows"',
      draw(lt, d, t) {
        K.studio(t);
        const v = lerp(-0.6, 0.15, eio(seg(lt, up, sh + 0.2)));
        K.finder(t, { ...focused, bright: 1 + v * 0.75 }, { over: (w, h) => { const [fx, fy] = flowerHead(w, h); K.focusRing(fx, fy, 95, 1); } });
        slider(v, 1);
        if (v < -0.25) K.pill('TOO DARK', 540, 385, 52, C.red, C.white, eob(seg(lt, 0.05, 0.3)));
        K.check(860, 400, eob(seg(lt, sh + 0.1, sh + 0.35)) * 0.8);
      } });
    cue(st, 'whoosh'); cue(st + up, 'slide', { dur: 0.7, gain: 0.6 }); cue(st + sh + 0.1, 'sparkle', { dur: 0.5 });
  }

  // ── 7 · END CARD ──
  {
    const st = cut(6);
    add({ id: 'S07', at: st, cam: [540, 700], zoom: 0.05, note: 'FOLLOW, next: lesson 03',
      draw: (lt, d, t) => K.endCard(lt, t, Wd('follow', 6) - st, Wd('three', 6) - st, 3, 'CLEAN YOUR LENS') });
    cue(st, 'whoosh'); cue(Wd('follow', 6), 'pop'); cue(Wd('three', 6), 'pop', { gain: 0.6 });
  }

  const overlay = (t) => K.seriesBadge(LESSON, seg(t, 0.15, 0.55));
  return { shots: S, cues: CUES, overlay };
}
