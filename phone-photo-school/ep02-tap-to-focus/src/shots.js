// PHONE PHOTO SCHOOL · LESSON 02: TAP TO FOCUS (25 s): the shot list.
// Keep key action between y 200 and 1250: the caption lives at y 1250-1550.
import { ctx, C, W, H, clamp, lerp, seg, eo, eio, eob } from './core/lib.js';
import { L, Wd, T } from './core/timing.js';
import * as K from './core/kit.js';

const LESSON = 2, F = K.FRAME;
const FL = { x: 0.7, y: 0.97, s: 0.42 };                    // the foreground flower (fractions of the frame)
const head = (w, h, fx = FL.x) => [fx * w, FL.y * h - FL.s * h * 0.8];
const TREE = [0.38, 0.55];                                  // the background tree's canopy (fractions)

export function buildShots() {
  const S = [], CUES = [];
  const add = (o) => (S.push(o), o);
  const cue = (t, type, o = {}) => CUES.push({ t: +t.toFixed(3), type, ...o });
  const cut = (i) => (i === 0 ? 0 : L(i) - 0.08);
  const ringAt = () => { const [fx, fy] = head(F.w, F.h); return [F.x + fx, F.y + fy]; };
  const slider = (val, a) => { const [rx, ry] = ringAt(); K.sunSlider(rx - 160, ry, 380, val, a, 46); };
  const focused = { subj: 0.38, flower: { ...FL, blur: 0 }, blur: 7 };
  const ring = (w, h) => { const [fx, fy] = head(w, h); K.focusRing(fx, fy, 95, 1); };

  // ── 0 · HOOK: phone rises; it focused on the tree, the flower is a blur; ring turns red on "wrong" ──
  {
    const st = cut(0), wrong = Wd('wrong', 0) - st, blurry = Wd('blurry', 0) - st;
    add({ id: 'S01', at: st, cam: [540, 800], zoom: 0.06, note: 'phone rises, flower blurred, ring on tree goes red on "wrong"',
      draw(lt, d, t) {
        K.studio(t);
        const rise = eob(seg(lt, 0, 0.6));
        K.phone(540, lerp(1900, 800, rise), 0.92, lerp(-0.2, -0.04, rise), (w, h) => K.cameraApp(w, h, {
          t, subj: 0.38, scene: { flower: { ...FL, blur: 16 } },
          over: (vw, vh, k) => { K.focusRing(TREE[0] * vw, TREE[1] * vh, 46 * k, seg(lt, blurry, blurry + 0.3), lt > wrong ? C.red : C.yellow);
            if (lt > wrong) K.pill('WRONG FOCUS', vw / 2, 50 * k, 30 * k, C.red, C.white, eob(seg(lt, wrong, wrong + 0.25))); },
        }));
      } });
    cue(st + 0.05, 'whoosh'); cue(st + blurry, 'tap'); cue(st + wrong, 'boing', { gain: 0.5 });
  }

  // ── 1 · LESSON CARD ──
  {
    const st = cut(1);
    add({ id: 'S02', at: st, cam: [540, 700], zoom: 0.1, note: 'lesson card 02, TAP TO FOCUS',
      draw: (lt, d, t) => K.lessonCard(lt, t, LESSON, 'TAP TO FOCUS', Wd('two', 1) - st, Wd('tap', 1) - st) });
    cue(st, 'whoosh'); cue(Wd('two', 1) - 0.02, 'slam', { gain: 0.8 }); cue(Wd('tap', 1), 'pop');
  }

  // ── 2 · AUTO FOCUS: the AUTO ring hunts (flower, tree, flower…) and settles on the background on "background" ──
  {
    const st = cut(2), mat = Wd('matters', 2) - st, bg = Wd('background', 2) - st;
    add({ id: 'S03', at: st, cam: [540, 760], zoom: 0.05, note: 'AUTO ring hunts between subjects, lands on the tree (red) on "background"',
      draw(lt, d, t) {
        K.studio(t);
        // ring position: hunt between flower and tree until "background", then stay on the tree
        const [fx, fy] = head(F.w, F.h), tx = TREE[0] * F.w, ty = TREE[1] * F.h;
        const hunt = lt < bg ? (Math.sin((lt - mat) * 7) * 0.5 + 0.5) : 1;
        const u = lt < mat ? 0 : eio(hunt);
        const blurF = lerp(2, 14, u), blurB = lerp(6, 0, u);
        K.finder(t, { subj: 0.38, flower: { ...FL, blur: blurF }, blur: blurB }, { over: () => {
          const bad = lt > bg;
          K.focusRing(lerp(fx, tx, u), lerp(fy, ty, u), 85, 1, bad ? C.red : C.yellow);
          K.pill('AUTO', lerp(fx, tx, u), lerp(fy, ty, u) - 135, 38, bad ? C.red : C.yellow, bad ? C.white : C.ink, 1);
        } });
        if (lt > bg) K.pill('PICKED THE BACKGROUND', 540, 1150, 46, C.red, C.white, eob(seg(lt, bg, bg + 0.25)));
      } });
    cue(st, 'whoosh'); cue(st + mat, 'slide', { dur: bg - mat, gain: 0.4 }); cue(st + bg, 'boing', { gain: 0.5 });
  }

  // ── 3 · TAP: tap the flower → ring lands → flower snaps sharp on "snaps" ──
  {
    const st = cut(3), tap = Wd('subject', 3) - st - 0.1, sharp = Wd('snaps', 3) - st;
    add({ id: 'S04', at: st, cam: [640, 760], zoom: 0.06, note: 'tap flower on "subject", sharp on "snaps"',
      draw(lt, d, t) {
        K.studio(t);
        const p = eio(seg(lt, sharp - 0.15, sharp + 0.2));
        K.finder(t, { subj: 0.38, flower: { ...FL, blur: lerp(14, 0, p) }, blur: lerp(0, 8, p) }, { over: (w, h) => {
          const [fx, fy] = head(w, h); K.focusRing(fx, fy, 95, seg(lt, tap, tap + 0.3));
        } });
        const [rx, ry] = ringAt(); K.tap(rx, ry, seg(lt, tap - 0.05, tap + 0.4), 1.3);
        if (lt > sharp) K.pill('SHARP', 300, 420, 60, C.green, C.ink, eob(seg(lt, sharp, sharp + 0.25)));
      } });
    cue(st, 'whoosh'); cue(st + tap, 'tap'); cue(st + sharp, 'sparkle', { dur: 0.6 });
  }

  // ── 4 · THE SUN: over-bright shot; the sun slider pops on "sun", starts down on "down" ──
  {
    const st = cut(4), sun = Wd('sun', 4) - st, down = Wd('down', 4) - st;
    add({ id: 'S05', at: st, cam: [440, 700], zoom: 0.08, note: 'over-exposed, slider on "sun", moves on "down"',
      draw(lt, d, t) {
        K.studio(t);
        const v = lerp(0.6, 0.35, eio(seg(lt, down, d)));
        K.finder(t, { ...focused, bright: 1 + v * 1.5 }, { over: ring });
        slider(v, seg(lt, sun - 0.1, sun + 0.15));
        if (lt > sun && lt < sun + 0.6) { const [rx, ry] = ringAt(); K.hotspot(rx - 160, ry - v * 190, 1.6, seg(lt, sun, sun + 0.2), t); }
        K.pill('TOO BRIGHT', 540, 385, 52, C.red, C.white, eob(seg(lt, 0.1, 0.4)));
      } });
    cue(st, 'whoosh'); cue(st + sun, 'pop'); cue(st + down, 'slide', { dur: 0.6, gain: 0.6 });
  }

  // ── 5 · DOWN: the sky comes back on "skies" ──
  {
    const st = cut(5), skies = Wd('skies', 5) - st;
    add({ id: 'S06', at: st, cam: [440, 700], zoom: 0.04, note: 'slider down, sky returns on "skies"',
      draw(lt, d, t) {
        K.studio(t);
        const v = lerp(0.35, -0.1, eio(seg(lt, 0, skies)));
        K.finder(t, { ...focused, bright: 1 + Math.max(v, 0) * 1.5 + Math.min(v, 0) * 0.3 }, { over: ring });
        slider(v, 1);
        K.check(860, 400, eob(seg(lt, skies, skies + 0.25)) * 0.8);
      } });
    cue(st, 'whoosh'); cue(st, 'slide', { dur: 0.5, gain: 0.6 }); cue(st + skies, 'sparkle', { dur: 0.5 });
  }

  // ── 6 · UP: a dark shot; slide up and it brightens on "shadows" ──
  {
    const st = cut(6), up = Wd('up', 6) - st, sh = Wd('shadows', 6) - st;
    add({ id: 'S07', at: st, cam: [440, 700], zoom: 0.05, note: 'dark shot, slider up on "up", bright on "shadows"',
      draw(lt, d, t) {
        K.studio(t);
        const v = lerp(-0.6, 0.15, eio(seg(lt, up, sh + 0.2)));
        K.finder(t, { ...focused, bright: 1 + v * 0.75 }, { over: ring });
        slider(v, 1);
        if (v < -0.25) K.pill('TOO DARK', 540, 385, 52, C.red, C.white, eob(seg(lt, 0.05, 0.3)));
        K.check(860, 400, eob(seg(lt, sh + 0.1, sh + 0.35)) * 0.8);
      } });
    cue(st, 'whoosh'); cue(st + up, 'slide', { dur: 0.7, gain: 0.6 }); cue(st + sh + 0.1, 'sparkle', { dur: 0.5 });
  }

  // ── 7 · PRO TIP: press and hold on the flower: a ring fills, then LOCKED on "lock" ──
  {
    const st = cut(7), pro = Wd('pro', 7) - st, hold = Wd('press', 7) - st, lock = Wd('lock', 7) - st;
    add({ id: 'S08', at: st, cam: [640, 700], zoom: 0.06, note: 'PRO TIP pill, press & hold fills a ring, padlock + AE/AF LOCK on "lock"',
      draw(lt, d, t) {
        K.studio(t);
        K.finder(t, focused, { over: ring });
        const [rx, ry] = ringAt();
        const hp = seg(lt, hold, lock);
        if (hp > 0 && lt < lock + 0.2) {                    // the finger is down: a glow + a filling arc
          ctx.save(); ctx.globalAlpha = 0.85; K.tap(rx, ry, 0.15, 1.4); ctx.restore();
          ctx.strokeStyle = C.white; ctx.lineWidth = 12; ctx.lineCap = 'round';
          ctx.beginPath(); ctx.arc(rx, ry, 125, -Math.PI / 2, -Math.PI / 2 + hp * Math.PI * 2); ctx.stroke();
        }
        if (lt > lock) {
          const p = eob(seg(lt, lock, lock + 0.25));
          ctx.save(); ctx.translate(rx, ry - 170); ctx.scale(p, p); K.padlock(0, 0, 110); ctx.restore();
          K.pill('AE/AF LOCK', 540, 1150, 54, C.yellow, C.ink, p);
        }
        K.pill('PRO TIP', 300, 420, 54, C.teal, C.ink, eob(seg(lt, pro - 0.05, pro + 0.2)));
      } });
    cue(st, 'whoosh'); cue(st + pro, 'pop'); cue(st + hold, 'slide', { dur: lock - hold, gain: 0.4 }); cue(st + lock, 'thud', { gain: 0.6 }); cue(st + lock + 0.05, 'pop');
  }

  // ── 8 · REFRAME: the framing moves, the flower slides across, focus + exposure stay locked to it ──
  {
    const st = cut(8), put = Wd('put', 8) - st, re = Wd('reframe', 8) - st;
    add({ id: 'S09', at: st, cam: [540, 760], zoom: 0.04, note: 'frame pans, flower + locked ring move together, check on "reframe"',
      draw(lt, d, t) {
        K.studio(t);
        const fx = lerp(0.7, 0.46, eio(seg(lt, 0.1, re + 0.2)));
        K.finder(t, { subj: lerp(0.38, 0.16, eio(seg(lt, 0.1, re + 0.2))), flower: { ...FL, x: fx, blur: 0 }, blur: 7 }, { over: (w, h) => {
          const [x, y] = head(w, h, fx); K.focusRing(x, y, 95, 1); K.padlock(x, y - 175, 90);
        } });
        K.check(860, 400, eob(seg(lt, re, re + 0.25)) * 0.8);
        K.pill('STAYS LOCKED', 540, 1150, 50, C.yellow, C.ink, eob(seg(lt, put, put + 0.25)));
      } });
    cue(st, 'whoosh'); cue(st + 0.1, 'slide', { dur: re + 0.1, gain: 0.6 }); cue(st + re, 'sparkle', { dur: 0.5 });
  }

  // ── 9 · END CARD ──
  {
    const st = cut(9);
    add({ id: 'S10', at: st, cam: [540, 700], zoom: 0.05, note: 'avatar, FOLLOW, next: lesson 03',
      draw: (lt, d, t) => K.endCard(lt, t, Wd('follow', 9) - st, Wd('three', 9) - st, 3, 'CLEAN YOUR LENS') });
    cue(st, 'whoosh'); cue(Wd('follow', 9), 'pop'); cue(Wd('three', 9), 'pop', { gain: 0.6 });
  }

  const overlay = (t) => K.seriesBadge(LESSON, seg(t, 0.15, 0.55));
  return { shots: S, cues: CUES, overlay };
}
