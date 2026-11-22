// PHONE PHOTO SCHOOL · LESSON 01: THE GRID (25 s): the shot list.
// Keep key action between y 200 and 1250: the caption lives at y 1250-1550.
import { ctx, C, W, H, clamp, lerp, seg, eo, eio, eob, rr, line } from './core/lib.js';
import { L, Wd, T } from './core/timing.js';
import * as K from './core/kit.js';

const LESSON = 1, F = K.FRAME;
const third = (i, j) => [F.x + (F.w * i) / 3, F.y + (F.h * j) / 3];

export function buildShots() {
  const S = [], CUES = [];
  const add = (o) => (S.push(o), o);
  const cue = (t, type, o = {}) => CUES.push({ t: +t.toFixed(3), type, ...o });
  const cut = (i) => (i === 0 ? 0 : L(i) - 0.08);

  // ── 0 · HOOK: phone rises into frame, camera app open, shutter on "photos" ──
  {
    const st = cut(0), snap = Wd('photos', 0) - st;
    add({ id: 'S01', at: st, cam: [540, 800], zoom: 0.06, note: 'phone rises, shutter + flash on "photos"',
      draw(lt, d, t) {
        K.studio(t);
        const rise = eob(seg(lt, 0, 0.6)), press = lt > snap && lt < snap + 0.25 ? 1 : 0;
        K.phone(540, lerp(1900, 800, rise), 0.92, lerp(-0.2, -0.04, rise), (w, h) => K.cameraApp(w, h, { t, subj: 0.5, press }));
        K.flash(lt > snap ? 0.7 * (1 - seg(lt, snap, snap + 0.25)) : 0);
      } });
    cue(st + 0.05, 'whoosh'); cue(st + snap, 'shutter');
  }

  // ── 1 · LESSON CARD ──
  {
    const st = cut(1);
    add({ id: 'S02', at: st, cam: [540, 700], zoom: 0.1, note: 'lesson card 01, THE GRID',
      draw: (lt, d, t) => K.lessonCard(lt, t, LESSON, 'THE GRID', Wd('one', 1) - st, Wd('grid', 1) - st) });
    cue(st, 'whoosh'); cue(Wd('one', 1) - 0.02, 'slam', { gain: 0.8 }); cue(Wd('grid', 1), 'pop');
  }

  // ── 2 · HOW: tap ⁘ → quick bar → gear on "settings" → General › Composition guide ON on "grid" ──
  {
    const st = cut(2), open = Wd('open', 2) - st, sett = Wd('settings', 2) - st, gr = Wd('grid', 2) - st;
    const s = 0.92, PW = K.PHONE.w * s, PH = K.PHONE.h * s, m = 14 * s, sw = PW - 2 * m, sh = PH - 2 * m;
    const toWorld = (lx, ly) => [540 - PW / 2 + m + lx, 800 - PH / 2 + m + ly];
    const dots = toWorld(sw * 830 / 923, sh * 1476 / 2000), gearP = toWorld(sw * 89 / 923, sh * 1476 / 2000);
    add({ id: 'S03', at: st, cam: [540, 760], zoom: 0.07, note: 'tap ⁘ on "open", gear on "settings", Composition guide ON on "grid"',
      draw(lt, d, t) {
        K.studio(t);
        let tg = null;
        K.phone(540, 800, s, 0, (w, h) => {
          K.cameraApp(w, h, { t, subj: 0.5, quick: seg(lt, open + 0.1, open + 0.35), gearHi: lt > sett - 0.35 && lt < sett + 0.2 });
          tg = K.settings(w, h, seg(lt, sett, sett + 0.35), seg(lt, gr - 0.6, gr - 0.35), seg(lt, gr, gr + 0.2));
        });
        K.tap(dots[0], dots[1], seg(lt, open - 0.1, open + 0.35), 0.9);
        K.tap(gearP[0], gearP[1], seg(lt, sett - 0.4, sett + 0.05), 0.9);
        if (tg) { const [tx, ty] = toWorld(...tg.toggle); K.tap(tx, ty, seg(lt, gr - 0.08, gr + 0.4), 0.9);
          if (lt > gr) K.pill('GRID LINES + LEVEL ON', 540, ty + 190, 44, C.teal, C.ink, eob(seg(lt, gr + 0.05, gr + 0.3))); }
      } });
    cue(st, 'whoosh'); cue(st + open - 0.05, 'tap'); cue(st + sett - 0.35, 'tap'); cue(st + sett, 'slide', { dur: 0.35, gain: 0.7 }); cue(st + gr - 0.05, 'tap'); cue(st + gr + 0.05, 'pop');
  }

  // ── 3 · THIRDS: lines draw across on "across", down on "down", 1/3 labels on "thirds" ──
  {
    const st = cut(3), ac = Wd('across', 3) - st, dn = Wd('down', 3) - st, th = Wd('thirds', 3) - st;
    add({ id: 'S04', at: st, cam: [540, 750], zoom: 0.05, note: 'horizontal lines on "across", vertical on "down", 1/3 labels on "thirds"',
      draw(lt, d, t) {
        K.studio(t);
        K.photoFinder('tower', { cx: 0.62, cy: 0.5 }, { tag: seg(lt, 0.3, 0.6), over: (w, h) => {
          ctx.lineCap = 'round';
          for (const [col, lw] of [[C.ink, 16], [C.white, 9]]) {
            ctx.strokeStyle = col; ctx.lineWidth = lw;
            for (let i = 1; i <= 2; i++) {
              const a = eo(seg(lt, ac - 0.1 + i * 0.12, ac + 0.4 + i * 0.12)), b = eo(seg(lt, dn - 0.1 + i * 0.12, dn + 0.4 + i * 0.12));
              if (a > 0) { ctx.beginPath(); ctx.moveTo(0, (h * i) / 3); ctx.lineTo(w * a, (h * i) / 3); ctx.stroke(); }
              if (b > 0) { ctx.beginPath(); ctx.moveTo((w * i) / 3, 0); ctx.lineTo((w * i) / 3, h * b); ctx.stroke(); }
            }
          }
          for (let i = 0; i < 3; i++) K.pill('1/3', (w * (i + 0.5)) / 3, 70, 42, C.yellow, C.ink, eob(seg(lt, th + i * 0.1, th + i * 0.1 + 0.25)));
        } });
      } });
    cue(st, 'whoosh'); cue(st + ac, 'zip', { gain: 0.6 }); cue(st + dn, 'zip', { gain: 0.6 }); [0, 1, 2].forEach((i) => cue(st + th + i * 0.1, 'pop', { gain: 0.5 }));
  }

  // ── 4 · RULE: tree slides to the right third, power points glow on "cross" ──
  {
    const st = cut(4), subj = Wd('subject', 4) - st, cross = Wd('cross', 4) - st;
    add({ id: 'S05', at: st, cam: [540, 760], zoom: 0.05, note: 'tree centre → right third, hotspots on "cross"',
      draw(lt, d, t) {
        K.studio(t);
        const u = lerp(0.5, 2 / 3, eio(seg(lt, subj - 0.1, cross)));
        K.finder(t, { subj: u }, { grid: 1, brackets: [u, 0.56] });
        [[1, 1], [2, 1], [1, 2], [2, 2]].forEach(([i, j], n) => {
          const [hx, hy] = third(i, j); K.hotspot(hx, hy, i === 2 ? 1.25 : 0.8, seg(lt, cross - 0.1 + n * 0.06, cross + 0.15 + n * 0.06), t);
        });
      } });
    cue(st, 'whoosh'); cue(st + subj, 'slide', { dur: cross - subj, gain: 0.8 }); cue(st + cross, 'sparkle', { dur: 0.6 });
  }

  // ── 5 · MYTH: centred version, red X on "center" ──
  {
    const st = cut(5), x = Wd('center', 5) - st - 0.05;
    add({ id: 'S06', at: st, cam: [540, 760], zoom: 0.04, note: 'tree dead centre, red X on "center"',
      draw(lt, d, t) {
        K.studio(t);
        K.finder(t, { subj: 0.5 }, { grid: 1 });
        ctx.save(); ctx.globalAlpha = 0.6; ctx.strokeStyle = C.red; ctx.lineWidth = 6; ctx.setLineDash([22, 16]);
        ctx.beginPath(); ctx.moveTo(540, F.y + 30); ctx.lineTo(540, F.y + F.h - 30); ctx.stroke(); ctx.restore();
        K.redX(540, 740, lt > x ? lerp(1.9, 1.15, eo(seg(lt, x, x + 0.18))) : 0, lt > x ? 1 : 0);
      } });
    cue(st, 'whoosh'); cue(st + x + 0.08, 'slam');
  }

  // ── 6 · HORIZON: horizon drops from the middle to the lower line on "line"; red ghost of the middle on "middle" ──
  {
    const st = cut(6), ln = Wd('line', 6) - st, mid = Wd('middle', 6) - st;
    add({ id: 'S07', at: st, cam: [540, 760], zoom: 0.04, note: 'horizon 1/2 → 2/3 on "line" (check), red dashed middle on "middle"',
      draw(lt, d, t) {
        K.studio(t);
        const hz = lerp(0.5, 0.64, eio(seg(lt, ln - 0.4, ln + 0.1)));
        K.finder(t, { subj: 2 / 3, hz }, { grid: 1, over: (w, h) => {
          if (lt > mid) { ctx.save(); ctx.strokeStyle = C.red; ctx.lineWidth = 8; ctx.setLineDash([26, 18]); ctx.globalAlpha = seg(lt, mid, mid + 0.2);
            ctx.beginPath(); ctx.moveTo(0, h / 2); ctx.lineTo(w, h / 2); ctx.stroke(); ctx.restore();
            K.pill('NOT HERE', w * 0.22, h / 2, 44, C.red, C.white, eob(seg(lt, mid, mid + 0.25))); }
        } });
        K.check(860, 400, eob(seg(lt, ln, ln + 0.25)) * 0.8);
      } });
    cue(st, 'whoosh'); cue(st + ln - 0.4, 'slide', { dur: 0.5, gain: 0.6 }); cue(st + ln + 0.1, 'pop'); cue(st + mid, 'boing', { gain: 0.5 });
  }

  // ── 7 · RESULT: shutter on "shot", the print + check on "balanced" ──
  {
    const st = cut(7), shot = Wd('shot', 7) - st, bal = Wd('balanced', 7) - st;
    add({ id: 'S08', at: st, cam: [540, 760], zoom: 0.05, note: 'shutter on "shot", photo prints, check on "balanced"',
      draw(lt, d, t) {
        K.studio(t);
        const p = eio(seg(lt, shot + 0.15, shot + 0.75));
        if (p <= 0) K.photoFinder('lighthouse', { cy: 0.55 }, { grid: 1 });
        else K.photoPrint(540, lerp(F.y + F.h / 2, 760, p), lerp(F.w, 740, p), lerp(F.h, 820, p), lerp(0, -0.06, p), 'lighthouse', { cy: 0.55 });
        if (p >= 1) K.shotTag(880, 1135, seg(lt, shot + 0.8, shot + 1.1));
        K.check(850, 400, eob(seg(lt, bal - 0.05, bal + 0.25)) * 0.9);
        K.flash(lt > shot ? 0.85 * (1 - seg(lt, shot, shot + 0.3)) : 0);
      } });
    cue(st, 'whoosh'); cue(st + shot, 'shutter'); cue(st + shot + 0.2, 'slide', { dur: 0.5, gain: 0.6 }); cue(st + bal, 'sparkle', { dur: 0.8 });
  }

  // ── 8 · TRY IT: three prints fan out, TAG @handle on "tag" ──
  {
    const st = cut(8), tag = Wd('tag', 8) - st;
    add({ id: 'S09', at: st, cam: [540, 740], zoom: 0.05, note: 'three prints fan out, tag pill on "tag"',
      draw(lt, d, t) {
        K.studio(t);
        [[-0.16, 300, 'boats', { cy: 0.7 }], [0.14, 780, 'tower', { cx: 0.7 }], [0, 540, 'couple', { cx: 0.55 }]].forEach(([rot, x, key, o], i) => {
          const p = eob(seg(lt, i * 0.15, i * 0.15 + 0.4)); if (p <= 0) return;
          K.photoPrint(lerp(540, x, p), 720 + (i === 2 ? 0 : 40), 460, 540, rot * p, key, o);
        });
        K.shotTag(880, 1030, seg(lt, 0.7, 1.0));
        K.pill(`TAG ${K.HANDLE}`, 540, 1130, 56, C.yellow, C.ink, eob(seg(lt, tag, tag + 0.25)));
      } });
    cue(st, 'whoosh'); [0, 1, 2].forEach((i) => cue(st + i * 0.15, 'slide', { dur: 0.3, gain: 0.4 })); cue(st + tag, 'pop');
  }

  // ── 9 · END CARD ──
  {
    const st = cut(9);
    add({ id: 'S10', at: st, cam: [540, 700], zoom: 0.05, note: 'avatar, FOLLOW, next: lesson 02',
      draw: (lt, d, t) => K.endCard(lt, t, Wd('follow', 9) - st, Wd('two', 9) - st, 2, 'TAP TO FOCUS') });
    cue(st, 'whoosh'); cue(Wd('follow', 9), 'pop'); cue(Wd('two', 9), 'pop', { gain: 0.6 });
  }

  const overlay = (t) => K.seriesBadge(LESSON, seg(t, 0.15, 0.55), t);
  return { shots: S, cues: CUES, overlay };
}
