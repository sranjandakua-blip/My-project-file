// PHONE PHOTO SCHOOL · LESSON 10: EXPERT RAW (25 s): the shot list.
// Keep key action between y 200 and 1250: the caption lives at y 1250-1550.
import { ctx, C, W, H, clamp, lerp, seg, eo, eio, eob, rr, line, circle } from './core/lib.js';
import { L, Wd, T } from './core/timing.js';
import * as K from './core/kit.js';

const LESSON = 10, F = K.FRAME;

/** an editing slider row (label + track + knob at v 0..1), centred at y */
function slider(label, y, v, a = 1) {
  if (a <= 0) return;
  ctx.save(); ctx.globalAlpha = a;
  ctx.fillStyle = 'rgba(10,12,16,0.8)'; rr(160, y - 44, 760, 88, 44); ctx.fill();
  ctx.fillStyle = C.white; ctx.font = '800 30px Inter'; ctx.textAlign = 'left'; ctx.textBaseline = 'middle'; ctx.fillText(label, 200, y);
  ctx.fillStyle = C.line; rr(460, y - 5, 420, 10, 5); ctx.fill();
  ctx.fillStyle = C.yellow; rr(460, y - 5, 420 * v, 10, 5); ctx.fill(); circle(460 + 420 * v, y, 20, C.white);
  ctx.restore();
}

export function buildShots() {
  const S = [], CUES = [];
  const add = (o) => (S.push(o), o);
  const cue = (t, type, o = {}) => CUES.push({ t: +t.toFixed(3), type, ...o });
  const cut = (i) => (i === 0 ? 0 : L(i) - 0.08);
  const s = 0.92, PW = K.PHONE.w * s, PH = K.PHONE.h * s, m = 14 * s, sw = PW - 2 * m, sh = PH - 2 * m;
  const toWorld = (lx, ly) => [540 - PW / 2 + m + lx, 800 - PH / 2 + m + ly];

  // ── 0 · HOOK: the monastery roof, edit sliders slide in ──
  {
    const st = cut(0), po = Wd('power', 0) - st, ca = Wd('camera', 0) - st;
    add({ id: 'S01', at: st, cam: [540, 760], zoom: 0.06, note: 'roof photo, edit sliders on "power", RAW pill on "camera"',
      draw(lt, d, t) {
        K.studio(t);
        const e = eio(seg(lt, po, ca + 0.5));
        K.photoFinder('roof', { cy: 0.6, bright: lerp(0.8, 1.08, e) });
        slider('EXPOSURE', 1000, lerp(0.35, 0.62, e), seg(lt, po - 0.1, po + 0.2));
        slider('HIGHLIGHTS', 1110, lerp(0.7, 0.4, e), seg(lt, po, po + 0.3));
        K.pill('RAW', 540, 400, 60, C.yellow, C.ink, eob(seg(lt, ca, ca + 0.25)));
      } });
    cue(st + 0.05, 'whoosh'); cue(st + po, 'slide', { dur: 0.8, gain: 0.5 }); cue(st + ca, 'pop');
  }

  // ── 1 · LESSON CARD ──
  {
    const st = cut(1);
    add({ id: 'S02', at: st, cam: [540, 700], zoom: 0.1, note: 'lesson card 10, EXPERT RAW',
      draw: (lt, d, t) => K.lessonCard(lt, t, LESSON, 'EXPERT RAW', Wd('ten', 1) - st, Wd('expert', 1) - st) });
    cue(st, 'whoosh'); cue(Wd('ten', 1) - 0.02, 'slam', { gain: 0.8 }); cue(Wd('expert', 1), 'pop');
  }

  // ── 2 · OPEN MORE → EXPERT RAW (the creator's MORE menu) ──
  {
    const st = cut(2), mo = Wd('more', 2) - st, raw = Wd('raw', 2) - st;
    add({ id: 'S03', at: st, cam: [540, 860], zoom: 0.08, note: 'MORE menu opens on "more", EXPERT RAW tapped on "raw"',
      draw(lt, d, t) {
        K.studio(t);
        let r = null;
        K.phone(540, 800, s, 0, (w, h) => { r = K.moreMenu(w, h, seg(lt, mo - 0.1, mo + 0.35), seg(lt, raw - 0.15, raw + 0.1)); });
        const [mxw, myw] = toWorld(sw * 462 / 923, sh * 1845 / 2000); K.tap(mxw, myw, seg(lt, mo - 0.15, mo + 0.3), 0.9);
        if (r && r.raw) { const [rx, ry] = toWorld(...r.raw); K.tap(rx, ry, seg(lt, raw - 0.05, raw + 0.4), 0.9); }
      } });
    cue(st, 'whoosh'); cue(st + mo - 0.1, 'tap'); cue(st + mo, 'slide', { dur: 0.35, gain: 0.6 }); cue(st + raw, 'tap');
  }

  // ── 3 · RAW + PHOTO: two files fly out of the shot ──
  {
    const st = cut(3), ra = Wd('raw', 3) - st, ph = Wd('photo', 3) - st;
    add({ id: 'S04', at: st, cam: [540, 760], zoom: 0.04, note: 'gate photo shrinks, RAW file on "raw", JPG on "photo"',
      draw(lt, d, t) {
        K.studio(t);
        const p = eio(seg(lt, 0, ra - 0.1));
        K.photoPrint(540, lerp(760, 440, p), lerp(880, 340, p), lerp(910, 300, p), 0, 'gate', { cy: 0.6 });
        K.fileCard(300, 880, 'RAW', 'DNG · EDITABLE', 0.85, C.yellow, eob(seg(lt, ra - 0.1, ra + 0.25)) * 1.25);
        K.fileCard(780, 880, 'JPG', 'READY TO SHARE', 0.3, C.teal, eob(seg(lt, ph - 0.1, ph + 0.25)) * 1.25);
      } });
    cue(st, 'whoosh'); cue(st + ra, 'pop'); cue(st + ph, 'pop');
  }

  // ── 4 · HIGHLIGHTS + SHADOWS: the creator's valley, labels on the bright clouds and the dark slope ──
  {
    const st = cut(4), hi = Wd('highlights', 4) - st, sha = Wd('shadows', 4) - st;
    add({ id: 'S05', at: st, cam: [540, 760], zoom: 0.04, note: 'valley photo, HIGHLIGHTS on clouds, SHADOWS on the slope',
      draw(lt, d, t) {
        K.studio(t);
        K.photoFinder('valley', { cy: 0.55 }, { tag: 1, over: (w, h, mp) => {
          const [ax, ay] = mp.at(0.4, 0.4), [bx, by] = mp.at(0.2, 0.78);
          if (lt > hi) { K.hotspot(ax, ay, 1.2, seg(lt, hi, hi + 0.2), t); K.pill('HIGHLIGHTS', ax + 170, ay, 40, C.white, C.ink, eob(seg(lt, hi, hi + 0.25))); }
          if (lt > sha) { K.hotspot(bx, by, 1.2, seg(lt, sha, sha + 0.2), t); K.pill('SHADOWS', bx + 150, by, 40, C.ink, C.white, eob(seg(lt, sha, sha + 0.25))); }
        } });
        K.pill('MORE DETAIL KEPT', 540, 400, 46, C.yellow, C.ink, eob(seg(lt, 0.1, 0.4)));
      } });
    cue(st, 'whoosh'); cue(st + hi, 'pop'); cue(st + sha, 'pop');
  }

  // ── 5 · RESCUE A BRIGHT SKY: the cloud village, blown out → recovered ──
  {
    const st = cut(5), sk = Wd('sky', 5) - st;
    add({ id: 'S06', at: st, cam: [540, 760], zoom: 0.04, note: 'cloud village blown out, highlights slider pulls it back on "sky"',
      draw(lt, d, t) {
        K.studio(t);
        const e = eio(seg(lt, sk - 0.5, sk + 0.3));
        K.photoFinder('cloudVillage', { cy: 0.6, bright: lerp(1.4, 1, e) }, { tag: seg(lt, sk + 0.2, sk + 0.5) });
        slider('HIGHLIGHTS', 1130, lerp(0.8, 0.3, e), 1);
        K.pill('SIMULATED EDIT', 540, 400, 36, 'rgba(10,12,16,0.8)', C.white, 1);
        K.check(860, 400, eob(seg(lt, sk + 0.1, sk + 0.35)) * 0.8);
      } });
    cue(st, 'whoosh'); cue(st + sk - 0.5, 'slide', { dur: 0.8, gain: 0.6 }); cue(st + sk + 0.1, 'sparkle', { dur: 0.5 });
  }

  // ── 6 · LIFT DARK CORNERS: the mural corridor, too dark → shadows lifted ──
  {
    const st = cut(6), co = Wd('corners', 6) - st, ro = Wd('room', 6) - st;
    add({ id: 'S07', at: st, cam: [540, 760], zoom: 0.04, note: 'mural corridor dark, shadows slider lifts on "corners", MORE ROOM on "room"',
      draw(lt, d, t) {
        K.studio(t);
        const e = eio(seg(lt, co - 0.5, co + 0.3));
        K.photoFinder('mural', { cy: 0.55, bright: lerp(0.4, 1, e) }, { tag: seg(lt, co + 0.2, co + 0.5) });
        slider('SHADOWS', 1130, lerp(0.15, 0.7, e), 1);
        K.pill('SIMULATED EDIT', 540, 400, 36, 'rgba(10,12,16,0.8)', C.white, 1);
        K.pill('MORE ROOM TO PLAY', 540, 1020, 44, C.yellow, C.ink, eob(seg(lt, ro, ro + 0.25)));
      } });
    cue(st, 'whoosh'); cue(st + co - 0.5, 'slide', { dur: 0.8, gain: 0.6 }); cue(st + ro, 'pop');
  }

  // ── 7 · THE CATCH: big files + needs editing ──
  {
    const st = cut(7), ca = Wd('catch', 7) - st, fi = Wd('files', 7) - st, ed = Wd('editing', 7) - st;
    add({ id: 'S08', at: st, cam: [540, 740], zoom: 0.04, note: 'THE CATCH, huge RAW file on "files", edit sliders on "editing"',
      draw(lt, d, t) {
        K.studio(t);
        K.pill('THE CATCH', 540, 380, 56, C.red, C.white, eob(seg(lt, ca, ca + 0.25)));
        K.fileCard(540, 680, 'RAW', 'BIG FILES', eo(seg(lt, fi, fi + 0.6)), C.red, eob(seg(lt, fi - 0.1, fi + 0.25)) * 1.5);
        const a = seg(lt, ed - 0.1, ed + 0.2);
        slider('EXPOSURE', 1000, 0.5 + 0.15 * Math.sin(lt * 4), a); slider('SHADOWS', 1110, 0.4 + 0.15 * Math.sin(lt * 3 + 1), a);
      } });
    cue(st, 'whoosh'); cue(st + ca, 'boing', { gain: 0.5 }); cue(st + fi, 'thud', { gain: 0.6 }); cue(st + ed, 'pop');
  }

  // ── 8 · END CARD: next is Pro mode ──
  {
    const st = cut(8);
    add({ id: 'S09', at: st, cam: [540, 700], zoom: 0.05, note: 'avatar, FOLLOW, next: lesson 11 Pro mode',
      draw: (lt, d, t) => K.endCard(lt, t, Wd('follow', 8) - st, Wd('pro', 8) - st, 11, 'PRO MODE') });
    cue(st, 'whoosh'); cue(Wd('follow', 8), 'pop'); cue(Wd('pro', 8), 'pop', { gain: 0.6 });
  }

  const overlay = (t) => K.seriesBadge(LESSON, seg(t, 0.15, 0.55), t);
  return { shots: S, cues: CUES, overlay };
}
