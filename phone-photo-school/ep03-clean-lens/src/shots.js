// PHONE PHOTO SCHOOL · LESSON 03: CLEAN YOUR LENS: the shot list.
// Keep key action between y 200 and 1250: the caption lives at y 1250-1550.
import { ctx, C, W, H, clamp, lerp, seg, eo, eio, eob } from './core/lib.js';
import { L, Wd, T } from './core/timing.js';
import * as K from './core/kit.js';

const LESSON = 3;

export function buildShots() {
  const S = [], CUES = [];
  const add = (o) => (S.push(o), o);
  const cue = (t, type, o = {}) => CUES.push({ t: +t.toFixed(3), type, ...o });
  const cut = (i) => (i === 0 ? 0 : L(i) - 0.08);

  // ── 1 · HOOK: phone rises, the photo on screen is milky and soft ──
  {
    const st = cut(0), hazy = Wd('hazy', 0) - st;
    add({ id: 'S01', at: st, cam: [540, 800], zoom: 0.06, note: 'phone rises, hazy soft photo, HAZY pill on "hazy"',
      draw(lt, d, t) {
        K.studio(t);
        const rise = eob(seg(lt, 0, 0.6));
        K.phone(540, lerp(1900, 800, rise), 0.92, lerp(-0.2, -0.04, rise), (w, h) => K.cameraApp(w, h, {
          t, subj: 0.62, scene: { haze: 1, blur: 3 },
          over: (vw, vh, k) => { if (lt > hazy) K.pill('HAZY?', vw / 2, 50 * k, 32 * k, C.red, C.white, eob(seg(lt, hazy, hazy + 0.25))); },
        }));
      } });
    cue(st + 0.05, 'whoosh'); cue(st + hazy, 'boing', { gain: 0.5 });
  }

  // ── 2 · LESSON CARD ──
  {
    const st = cut(1);
    add({ id: 'S02', at: st, cam: [540, 700], zoom: 0.1, note: 'lesson card 03, CLEAN YOUR LENS',
      draw: (lt, d, t) => K.lessonCard(lt, t, LESSON, 'CLEAN YOUR LENS', Wd('three', 1) - st, Wd('clean', 1) - st) });
    cue(st, 'whoosh'); cue(Wd('three', 1) - 0.02, 'slam', { gain: 0.8 }); cue(Wd('clean', 1), 'pop');
  }

  // ── 3 · GREASE: phone back, a fingertip presses the top lens and leaves a print on "grease" ──
  {
    const st = cut(2), gr = Wd('grease', 2) - st, s = 0.92;
    const [lx, ly] = K.LENSES(s)[0], LX = 540 + lx, LY = 800 + ly;
    add({ id: 'S03', at: st, cam: [LX, LY + 80], zoom: 0.3, note: 'phone back, finger touches top lens, print on "grease"',
      draw(lt, d, t) {
        K.studio(t);
        K.phoneBack(540, 800, s, 0, { smudge: eo(seg(lt, gr, gr + 0.2)) });
        const inP = eio(seg(lt, 0, gr)), outP = eio(seg(lt, gr + 0.15, gr + 0.7));
        const fy = lerp(LY + 520, LY + 10, inP) + lerp(0, 420, outP), fx = lerp(1250, LX + 20, inP) + lerp(0, 800, outP);
        K.finger(fx, fy, 96, -0.95);
        if (lt > gr + 0.4) K.pill('GREASE', LX + 250, LY - 30, 54, C.red, C.white, eob(seg(lt, gr + 0.4, gr + 0.65)));
      } });
    cue(st, 'whoosh'); cue(st + gr, 'tap'); cue(st + gr + 0.4, 'pop');
  }

  // ── 4 · SMUDGE: the photo through a dirty lens: lights glow on "glow", details blur on "blur" ──
  {
    const st = cut(3), glow = Wd('glow', 3) - st, blur = Wd('blur', 3) - st;
    add({ id: 'S04', at: st, cam: [540, 700], zoom: 0.06, note: 'clean photo hazes on "glow", blurs on "blur"; smudged lens inset',
      draw(lt, d, t) {
        K.studio(t);
        K.finder(t, { subj: 0.62, haze: eo(seg(lt, glow - 0.1, glow + 0.4)), blur: lerp(0, 6, eo(seg(lt, blur - 0.1, blur + 0.3))) });
        const ip = eob(seg(lt, 0.1, 0.4));
        if (ip > 0) { ctx.save(); ctx.translate(850, 420); ctx.scale(ip, ip); K.lens(0, 0, 90, 1); ctx.restore(); }
      } });
    cue(st, 'whoosh'); cue(st + 0.1, 'pop', { gain: 0.6 }); cue(st + glow, 'sparkle', { dur: 0.5, gain: 0.6 }); cue(st + blur, 'slide', { dur: 0.4, gain: 0.5 });
  }

  // ── 5 · WIPE: a big lens, the cloth sweeps across twice, the print fades ──
  {
    const st = cut(4), soft = Wd('soft', 4) - st, end = L(5) - st;
    add({ id: 'S05', at: st, cam: [540, 720], zoom: 0.05, note: 'big lens, cloth wipes on "wipe"/"soft", smudge gone',
      draw(lt, d, t) {
        K.studio(t);
        const wp = seg(lt, 0.1, end - 0.05);
        K.lens(540, 720, 300, 1 - eio(wp));
        if (wp > 0 && wp < 1) { const sw = Math.sin(wp * Math.PI * 2); K.cloth(540 + sw * 260, 760 + Math.cos(wp * Math.PI * 4) * 40, 1.1, sw * 0.15); }
        if (wp >= 1) for (let i = 0; i < 3; i++) K.hotspot(400 + i * 140, 560 + (i % 2) * 120, 0.6, seg(lt, end - 0.05 + i * 0.05, end + 0.2), t);
        if (lt > soft) K.pill('MICROFIBER', 540, 330, 54, C.teal, C.ink, eob(seg(lt, soft, soft + 0.25)));
      } });
    cue(st, 'whoosh'); cue(st + 0.1, 'slide', { dur: end - 0.15, gain: 0.8 });
  }

  // ── 6 · NOT YOUR SHIRT: cloth ✓ vs shirt ✗ ──
  {
    const st = cut(5), shirt = Wd('shirt', 5) - st;
    add({ id: 'S06', at: st, cam: [540, 720], zoom: 0.05, note: 'cloth with check, shirt with red X on "shirt"',
      draw(lt, d, t) {
        K.studio(t);
        K.cloth(290, 740, 1.15, -0.08); K.check(290, 480, eob(seg(lt, 0, 0.25)) * 0.8);
        K.shirt(800, 740, 1.55);
        K.redX(800, 740, lt > shirt ? lerp(2.2, 1.25, eo(seg(lt, shirt, shirt + 0.18))) : 0, lt > shirt ? 1 : 0);
      } });
    cue(st, 'whoosh'); cue(st + shirt + 0.05, 'slam');
  }

  // ── 7 · CRISP: the clean photo, check on "clear" ──
  {
    const st = cut(6), clear = Wd('clear', 6) - st;
    add({ id: 'S07', at: st, cam: [540, 700], zoom: 0.06, note: 'crisp photo, green check on "clear"',
      draw(lt, d, t) {
        K.studio(t);
        K.finder(t, { subj: 0.62 });
        K.check(850, 400, eob(seg(lt, clear, clear + 0.25)) * 0.8);
      } });
    cue(st, 'whoosh'); cue(st + clear, 'sparkle', { dur: 0.6 });
  }

  // ── 8 · END CARD ──
  {
    const st = Wd('follow', 6) - 0.12;
    add({ id: 'S08', at: st, cam: [540, 700], zoom: 0.05, note: 'FOLLOW, next: lesson 04',
      draw: (lt, d, t) => K.endCard(lt, t, Wd('follow', 6) - st, Wd('four', 6) - st, 4, 'THE ZOOM LENSES') });
    cue(st, 'whoosh'); cue(Wd('follow', 6), 'pop'); cue(Wd('four', 6), 'pop', { gain: 0.6 });
  }

  const overlay = (t) => K.seriesBadge(LESSON, seg(t, 0.15, 0.55));
  return { shots: S, cues: CUES, overlay };
}
