// PHONE PHOTO SCHOOL · LESSON 07: PORTRAIT MODE (25 s): the shot list.
// Keep key action between y 200 and 1250: the caption lives at y 1250-1550.
import { ctx, C, W, H, clamp, lerp, seg, eo, eio, eob, rr, line, circle } from './core/lib.js';
import { L, Wd, T } from './core/timing.js';
import * as K from './core/kit.js';

const LESSON = 7, F = K.FRAME;
// a person in front of the tree; personSharp keeps them sharp while the background blurs
const portrait = (blur, zoom = 1, s = 0.5) => ({ subj: 0.75, treeS: 0.9, person: { x: 0.45, y: 0.98, s }, personSharp: true, blur, zoom, zx: 0.47, zy: 0.62 });

export function buildShots() {
  const S = [], CUES = [];
  const add = (o) => (S.push(o), o);
  const cue = (t, type, o = {}) => CUES.push({ t: +t.toFixed(3), type, ...o });
  const cut = (i) => (i === 0 ? 0 : L(i) - 0.08);
  const s = 0.92, PW = K.PHONE.w * s, PH = K.PHONE.h * s, m = 14 * s, sw = PW - 2 * m, sh = PH - 2 * m;
  const toWorld = (fx, fy) => [540 - PW / 2 + m + sw * fx / 923, 800 - PH / 2 + m + sh * fy / 2000];

  // ── 0 · HOOK: phone rises, the background melts on "blurred" ──
  {
    const st = cut(0), bl = Wd('blurred', 0) - st;
    add({ id: 'S01', at: st, cam: [540, 800], zoom: 0.06, note: 'phone rises, portrait mode, background blurs on "blurred"',
      draw(lt, d, t) {
        K.studio(t);
        const rise = eob(seg(lt, 0, 0.6));
        K.phone(540, lerp(1900, 800, rise), 0.92, lerp(-0.2, -0.04, rise), (w, h) => K.cameraApp(w, h, {
          t, mode: 'PORTRAIT', portraitZoom: '3', ready: 1, reticle: false, scene: portrait(lerp(0, 20, eio(seg(lt, bl - 0.2, bl + 0.4))), 1.6) }));
      } });
    cue(st + 0.05, 'whoosh'); cue(st + bl, 'sparkle', { dur: 0.7 });
  }

  // ── 1 · LESSON CARD ──
  {
    const st = cut(1);
    add({ id: 'S02', at: st, cam: [540, 700], zoom: 0.1, note: 'lesson card 07, PORTRAIT MODE',
      draw: (lt, d, t) => K.lessonCard(lt, t, LESSON, 'PORTRAIT MODE', Wd('seven', 1) - st, Wd('portrait', 1) - st) });
    cue(st, 'whoosh'); cue(Wd('seven', 1) - 0.02, 'slam', { gain: 0.8 }); cue(Wd('portrait', 1), 'pop');
  }

  // ── 2 · SWIPE TO PORTRAIT, WAIT FOR READY ──
  {
    const st = cut(2), sw0 = Wd('swipe', 2) - st, rd = Wd('ready', 2) - st;
    add({ id: 'S03', at: st, cam: [540, 760], zoom: 0.06, note: 'swipe on "swipe" switches to PORTRAIT, Ready appears on "ready"',
      draw(lt, d, t) {
        K.studio(t);
        const port = lt > sw0 + 0.3, bl = eio(seg(lt, rd - 0.1, rd + 0.4));
        K.phone(540, 800, s, 0, (w, h) => K.cameraApp(w, h, { t, mode: port ? 'PORTRAIT' : 'PHOTO', portraitZoom: '3', ready: seg(lt, rd, rd + 0.2),
          reticle: false, scene: portrait(port ? bl * 20 : 0, 1.6) }));
        const p = seg(lt, sw0 - 0.1, sw0 + 0.45), [y0x, y0y] = toWorld(620, 1845);
        if (p > 0 && p < 1) { K.tap(lerp(y0x, y0x - 220, eio(p)), y0y, 0.2, 1); }
        if (lt > rd) { const [rx, ry] = toWorld(461, 228); K.hotspot(rx, ry, 1.2, seg(lt, rd, rd + 0.2), t); }
        K.pill('WAIT FOR "READY"', 540, 1200, 44, C.yellow, C.ink, eob(seg(lt, rd, rd + 0.25)));
      } });
    cue(st, 'whoosh'); cue(st + sw0, 'zip', { gain: 0.6 }); cue(st + rd, 'pop');
  }

  // ── 3 · PICK 3X ──
  {
    const st = cut(3), th = Wd('three', 3) - st, fl = Wd('flattering', 3) - st;
    add({ id: 'S04', at: st, cam: [540, 820], zoom: 0.06, note: 'tap 3 on "three", view tightens to a flattering portrait',
      draw(lt, d, t) {
        K.studio(t);
        const z = eio(seg(lt, th, th + 0.5));
        K.phone(540, 800, s, 0, (w, h) => K.cameraApp(w, h, { t, mode: 'PORTRAIT', portraitZoom: lt > th ? '3' : '1', ready: 1, reticle: false, scene: portrait(20, lerp(1, 2, z)) }));
        const [cx, cy] = toWorld(497, 1476); K.tap(cx, cy, seg(lt, th - 0.05, th + 0.4), 0.9);
        K.pill('3X = FLATTERING', 540, 1200, 46, C.yellow, C.ink, eob(seg(lt, fl, fl + 0.25)));
      } });
    cue(st, 'whoosh'); cue(st + th, 'tap'); cue(st + th + 0.05, 'slide', { dur: 0.5, gain: 0.5 }); cue(st + fl, 'pop');
  }

  // ── 4 · STEP BACK, FILL THE FRAME: too tight (head cut) → step back → brackets ──
  {
    const st = cut(4), bk = Wd('back', 4) - st, fr = Wd('frame', 4) - st;
    add({ id: 'S05', at: st, cam: [540, 760], zoom: 0.05, note: 'too close, step back on "back", brackets on "frame"',
      draw(lt, d, t) {
        K.studio(t);
        const z = lerp(3.6, 2.1, eio(seg(lt, bk - 0.1, bk + 0.5)));
        K.finder(t, portrait(12, z), { brackets: lt > fr ? [0.5, 0.58, lerp(330, 290, eo(seg(lt, fr, fr + 0.3)))] : null });
        if (lt < bk) K.pill('TOO CLOSE', 540, 400, 48, C.red, C.white, eob(seg(lt, 0.05, 0.3)));
        else K.pill('STEP BACK', 540, 400, 48, C.yellow, C.ink, eob(seg(lt, bk, bk + 0.25)));
      } });
    cue(st, 'whoosh'); cue(st + bk, 'slide', { dur: 0.5, gain: 0.6 }); cue(st + fr, 'pop');
  }

  // ── 5 · DISTANCE: the background slides away from the subject, distance arrow grows ──
  {
    const st = cut(5), di = Wd('distance', 5) - st, bg = Wd('background', 5) - st;
    add({ id: 'S06', at: st, cam: [540, 760], zoom: 0.04, note: 'side view: subject, background moves away, DISTANCE arrow',
      draw(lt, d, t) {
        K.studio(t);
        const gx = lerp(560, 900, eio(seg(lt, di - 0.2, bg + 0.3)));
        ctx.fillStyle = C.panel; ctx.fillRect(100, 1000, 880, 8);
        K.person(260, 1000, 380);
        K.tree(gx, 1000, 1.1);
        line([[340, 700], [gx - 120, 700]], C.yellow, 10);
        ctx.fillStyle = C.yellow; ctx.beginPath(); ctx.moveTo(gx - 100, 700); ctx.lineTo(gx - 140, 676); ctx.lineTo(gx - 140, 724); ctx.fill();
        ctx.beginPath(); ctx.moveTo(320, 700); ctx.lineTo(360, 676); ctx.lineTo(360, 724); ctx.fill();
        K.pill('DISTANCE', (340 + gx - 120) / 2, 630, 46, C.yellow, C.ink, eob(seg(lt, di, di + 0.25)));
        K.pill('SUBJECT', 260, 1080, 36, C.teal, C.ink, 1); K.pill('BACKGROUND', gx, 1080, 36, C.panel2, C.white, 1);
      } });
    cue(st, 'whoosh'); cue(st + di - 0.2, 'slide', { dur: bg - di + 0.5, gain: 0.6 }); cue(st + di, 'pop');
  }

  // ── 6 · FARTHER = CREAMIER: blur grows ──
  {
    const st = cut(6), cr = Wd('creamier', 6) - st;
    add({ id: 'S07', at: st, cam: [540, 760], zoom: 0.05, note: 'background blur grows to "creamier"',
      draw(lt, d, t) {
        K.studio(t);
        K.finder(t, portrait(lerp(3, 22, eio(seg(lt, 0, cr + 0.3))), 2.1));
        K.pill('FARTHER = CREAMIER', 540, 400, 46, C.yellow, C.ink, eob(seg(lt, cr, cr + 0.25)));
        K.check(860, 1120, eob(seg(lt, cr + 0.1, cr + 0.35)) * 0.7);
      } });
    cue(st, 'whoosh'); cue(st, 'slide', { dur: 1.2, gain: 0.5 }); cue(st + cr, 'sparkle', { dur: 0.6 });
  }

  // ── 7 · PETS + OBJECTS: the creator's kittens and the Shiva statue behind blossoms ──
  {
    const st = cut(7), pe = Wd('pets', 7) - st, ob = Wd('objects', 7) - st;
    add({ id: 'S08', at: st, cam: [540, 740], zoom: 0.04, note: 'two prints: kittens on "pets", Shiva + blossoms on "objects"',
      draw(lt, d, t) {
        K.studio(t);
        const a = eob(seg(lt, pe - 0.1, pe + 0.3)), b = eob(seg(lt, ob - 0.1, ob + 0.3));
        if (a > 0) { K.photoPrint(lerp(540, 300, a), 720, 440, 600, -0.06 * a, 'kittens', { cy: 0.62 }); K.pill('PETS', 300, 1060, 44, C.teal, C.ink, a); }
        if (b > 0) { K.photoPrint(lerp(540, 780, b), 740, 440, 600, 0.06 * b, 'shiva', { cy: 0.45 }); K.pill('OBJECTS', 780, 1080, 44, C.teal, C.ink, b); }
        K.shotTag(940, 360, seg(lt, ob + 0.3, ob + 0.6));
      } });
    cue(st, 'whoosh'); cue(st + pe, 'pop'); cue(st + ob, 'pop');
  }

  // ── 8 · END CARD ──
  {
    const st = cut(8);
    add({ id: 'S09', at: st, cam: [540, 700], zoom: 0.05, note: 'avatar, FOLLOW, next: lesson 08',
      draw: (lt, d, t) => K.endCard(lt, t, Wd('follow', 8) - st, Wd('eight', 8) - st, 8, 'NIGHT MODE') });
    cue(st, 'whoosh'); cue(Wd('follow', 8), 'pop'); cue(Wd('eight', 8), 'pop', { gain: 0.6 });
  }

  const overlay = (t) => K.seriesBadge(LESSON, seg(t, 0.15, 0.55), t);
  return { shots: S, cues: CUES, overlay };
}
