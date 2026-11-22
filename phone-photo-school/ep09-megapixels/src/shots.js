// PHONE PHOTO SCHOOL · LESSON 09: MEGAPIXELS (25 s): the shot list.
// Keep key action between y 200 and 1250: the caption lives at y 1250-1550.
import { ctx, C, W, H, clamp, lerp, seg, eo, eio, eob, rr, line, circle } from './core/lib.js';
import { L, Wd, T } from './core/timing.js';
import * as K from './core/kit.js';

const LESSON = 9, F = K.FRAME;

export function buildShots() {
  const S = [], CUES = [];
  const add = (o) => (S.push(o), o);
  const cue = (t, type, o = {}) => CUES.push({ t: +t.toFixed(3), type, ...o });
  const cut = (i) => (i === 0 ? 0 : L(i) - 0.08);
  const s = 0.92, PW = K.PHONE.w * s, PH = K.PHONE.h * s, m = 14 * s, sw = PW - 2 * m, sh = PH - 2 * m;
  const toWorld = (fx, fy) => [540 - PW / 2 + m + sw * fx / 923, 800 - PH / 2 + m + sh * fy / 2000];
  const badge = (txt, x, y, a, col = C.yellow) => K.pill(txt, x, y, 54, col, C.ink, a);

  // ── 0 · HOOK: the snowy mountains, a big "200MP?" ──
  {
    const st = cut(0), mp = Wd('megapixels', 0) - st;
    add({ id: 'S01', at: st, cam: [540, 760], zoom: 0.06, note: 'snow photo, 200MP? on "megapixels"',
      draw(lt, d, t) {
        K.studio(t);
        K.photoFinder('snow', { cy: 0.55, zoom: lerp(1.2, 1, eio(seg(lt, 0, d))) });
        badge('200 MP ?', 540, 420, eob(seg(lt, mp - 0.1, mp + 0.2)));
      } });
    cue(st + 0.05, 'whoosh'); cue(st + mp, 'pop');
  }

  // ── 1 · LESSON CARD ──
  {
    const st = cut(1);
    add({ id: 'S02', at: st, cam: [540, 700], zoom: 0.1, note: 'lesson card 09, MEGAPIXELS',
      draw: (lt, d, t) => K.lessonCard(lt, t, LESSON, 'MEGAPIXELS', Wd('nine', 1) - st, Wd('megapixels', 1) - st) });
    cue(st, 'whoosh'); cue(Wd('nine', 1) - 0.02, 'slam', { gain: 0.8 }); cue(Wd('megapixels', 1), 'pop');
  }

  // ── 2 · TAP 12M: the 12M at the top highlights, the 200M · 50M · 12M picker opens on "resolution" ──
  {
    const st = cut(2), tw = Wd('twelve', 2) - st, re = Wd('resolution', 2) - st;
    add({ id: 'S03', at: st, cam: [540, 800], zoom: 0.06, note: 'tap 12M at top on "twelve", picker on "resolution"',
      draw(lt, d, t) {
        K.studio(t);
        K.phone(540, 800, s, 0, (w, h) => K.cameraApp(w, h, { t, photo: 'stadium', photoOpts: { cy: 0.5 }, resHi: lt > tw - 0.1, res: seg(lt, re - 0.2, re + 0.15) }));
        const [tx, ty] = toWorld(603, 112); K.tap(tx, ty, seg(lt, tw - 0.1, tw + 0.35), 0.9);
        if (lt > re) { const [px, py] = toWorld(461, 1476); K.pill('200M · 50M · 12M', px, py - 150, 40, C.yellow, C.ink, eob(seg(lt, re, re + 0.25))); }
      } });
    cue(st, 'whoosh'); cue(st + tw, 'tap'); cue(st + re, 'pop');
  }

  // ── 3 · 12M = EVERYDAY: the creator's stadium shot ──
  {
    const st = cut(3), ev = Wd('everyday', 3) - st;
    add({ id: 'S04', at: st, cam: [540, 760], zoom: 0.05, note: 'stadium photo, 12M badge, EVERYDAY on "everyday"',
      draw(lt, d, t) {
        K.studio(t);
        K.photoFinder('stadium', { cy: 0.55 }, { tag: 1 });
        badge('12M', 260, 400, eob(seg(lt, 0.05, 0.3)));
        K.pill('BEST EVERYDAY CHOICE', 540, 1150, 46, C.teal, C.ink, eob(seg(lt, ev, ev + 0.25)));
      } });
    cue(st, 'whoosh'); cue(st + 0.05, 'pop', { gain: 0.6 }); cue(st + ev, 'pop');
  }

  // ── 4 · LOW LIGHT + SMALL FILES: the church at night, a small file card ──
  {
    const st = cut(4), lo = Wd('low', 4) - st, sm = Wd('small', 4) - st;
    add({ id: 'S05', at: st, cam: [540, 760], zoom: 0.05, note: 'church at night on "low light", small 12M file on "small"',
      draw(lt, d, t) {
        K.studio(t);
        K.photoFinder('church', { cy: 0.5 }, { tag: 1 });
        K.pill('GREAT IN LOW LIGHT', 540, 400, 46, C.yellow, C.ink, eob(seg(lt, lo, lo + 0.25)));
        K.fileCard(790, 960, '12M', 'SMALL FILE', eo(seg(lt, sm, sm + 0.4)) * 0.18, C.green, eob(seg(lt, sm - 0.1, sm + 0.2)) * 0.8);
      } });
    cue(st, 'whoosh'); cue(st + lo, 'pop'); cue(st + sm, 'pop');
  }

  // ── 5 · 50 / 200M DETAIL: the snow valley, a loupe zooms into the tiny people ──
  {
    const st = cut(5), fi = Wd('fifty', 5) - st, de = Wd('detail', 5) - st;
    add({ id: 'S06', at: st, cam: [540, 760], zoom: 0.04, note: 'snow photo, 200M badge on "fifty", detail loupe on "detail"',
      draw(lt, d, t) {
        K.studio(t);
        K.photoFinder('snow', { cy: 0.6 }, { tag: 1 });
        badge('50M · 200M', 540, 400, eob(seg(lt, fi, fi + 0.25)));
        const p = eob(seg(lt, de - 0.1, de + 0.3));
        if (p > 0) {
          const R = 230 * p, cx = 700, cy = 820;
          ctx.save(); ctx.beginPath(); ctx.arc(cx, cy, R, 0, Math.PI * 2); ctx.clip();
          ctx.translate(cx - R, cy - R); K.photo('snow', R * 2, R * 2, { cx: 0.45, cy: 0.9, zoom: 5 }); ctx.restore();
          ctx.strokeStyle = C.yellow; ctx.lineWidth = 12; ctx.beginPath(); ctx.arc(cx, cy, R, 0, Math.PI * 2); ctx.stroke();
          K.pill('HUGE DETAIL', cx, cy + R + 40, 40, C.yellow, C.ink, p);
        }
      } });
    cue(st, 'whoosh'); cue(st + fi, 'pop'); cue(st + de, 'sparkle', { dur: 0.6 });
  }

  // ── 6 · CROPS + MASSIVE FILES: crop into the houses, then 12M vs 200M file sizes ──
  {
    const st = cut(6), cr = Wd('crops', 6) - st, ma = Wd('massive', 6) - st;
    add({ id: 'S07', at: st, cam: [540, 760], zoom: 0.04, note: 'houses photo crops in on "crops", file cards on "massive"',
      draw(lt, d, t) {
        K.studio(t);
        const z = lerp(1, 3, eio(seg(lt, cr - 0.1, cr + 0.7))), fade = seg(lt, ma - 0.5, ma - 0.1);
        ctx.save(); ctx.globalAlpha = 1 - fade * 0.75; K.photoFinder('houses', { cx: 0.35, cy: 0.58, zoom: z }, { tag: 1 }); ctx.restore();
        if (z > 1.05 && fade < 0.5) K.pill('CROP IT LATER', 540, 400, 46, C.teal, C.ink, eob(seg(lt, cr, cr + 0.25)));
        const a = eob(seg(lt, ma - 0.15, ma + 0.2));
        K.fileCard(300, 760, '12M', 'SMALL', 0.18, C.green, a * 1.2);
        K.fileCard(780, 760, '200M', 'MASSIVE', eo(seg(lt, ma, ma + 0.6)), C.red, a * 1.2);
      } });
    cue(st, 'whoosh'); cue(st + cr, 'slide', { dur: 0.7, gain: 0.5 }); cue(st + ma, 'slam', { gain: 0.6 });
  }

  // ── 7 · THE RULE: 12M by default (kittens), 200M for landscapes (the valley) ──
  {
    const st = cut(7), de = Wd('default', 7) - st, la = Wd('landscapes', 7) - st;
    add({ id: 'S08', at: st, cam: [540, 740], zoom: 0.04, note: 'kittens print 12M on "default", valley print 200M on "landscapes"',
      draw(lt, d, t) {
        K.studio(t);
        const a = eob(seg(lt, de - 0.1, de + 0.3)), b = eob(seg(lt, la - 0.1, la + 0.3));
        if (a > 0) { K.photoPrint(lerp(540, 300, a), 720, 440, 600, -0.06 * a, 'kittens', { cy: 0.62 }); K.pill('12M · DEFAULT', 300, 1060, 40, C.yellow, C.ink, a); }
        if (b > 0) { K.photoPrint(lerp(540, 780, b), 740, 440, 600, 0.06 * b, 'valley', { cy: 0.6 }); K.pill('200M · LANDSCAPES', 780, 1080, 40, C.teal, C.ink, b); }
        K.shotTag(940, 360, seg(lt, la + 0.3, la + 0.6));
      } });
    cue(st, 'whoosh'); cue(st + de, 'pop'); cue(st + la, 'pop');
  }

  // ── 8 · END CARD ──
  {
    const st = cut(8);
    add({ id: 'S09', at: st, cam: [540, 700], zoom: 0.05, note: 'avatar, FOLLOW, next: lesson 10',
      draw: (lt, d, t) => K.endCard(lt, t, Wd('follow', 8) - st, Wd('ten', 8) - st, 10, 'EXPERT RAW') });
    cue(st, 'whoosh'); cue(Wd('follow', 8), 'pop'); cue(Wd('ten', 8), 'pop', { gain: 0.6 });
  }

  const overlay = (t) => K.seriesBadge(LESSON, seg(t, 0.15, 0.55), t);
  return { shots: S, cues: CUES, overlay };
}
