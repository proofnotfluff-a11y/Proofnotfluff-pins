import React, {useEffect, useState} from 'react';
import {AbsoluteFill, continueRender, delayRender, interpolate, staticFile, useCurrentFrame, useVideoConfig, Easing} from 'remotion';

// A painter, nothing more: it draws the elements listed in props at the boxes tools/video_layout.py computed, so the
// layout check before rendering sees exactly what the frame shows. No text is wrapped here (lines arrive broken).

const FAMILIES = {P: 'PNF Poppins', I: 'PNF Inter'};
const FONT_FILES = [
  ['PNF Poppins', 700, 'fonts/poppins-700.woff2'],
  ['PNF Poppins', 600, 'fonts/poppins-600.woff2'],
  ['PNF Inter', 400, 'fonts/inter-400.woff2'],
  ['PNF Inter', 600, 'fonts/inter-600.woff2'],
  ['PNF Inter', 700, 'fonts/inter-700.woff2'],
];

const useFonts = () => {
  const [handle] = useState(() => delayRender('fonts'));
  useEffect(() => {
    Promise.all(FONT_FILES.map(([family, weight, file]) => {
      const f = new FontFace(family, `url(${staticFile(file)}) format('woff2')`, {weight: String(weight)});
      return f.load().then((loaded) => document.fonts.add(loaded));
    })).then(() => continueRender(handle)).catch((err) => {
      // A missing font must fail the render, never fall back to a system face silently.
      throw new Error('font load failed: ' + err);
    });
  }, [handle]);
};

const visible = (e, t) => t >= e.tIn && (e.tOut === null || e.tOut === undefined || t < e.tOut);

const fade = (e, t, fps) => {
  if (e.anim === 'none' || e.tIn === 0) return {opacity: 1, dy: 0};
  const p = interpolate(t, [e.tIn, e.tIn + 0.3], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.out(Easing.cubic)});
  return {opacity: p, dy: e.anim === 'rise' ? (1 - p) * 18 : 0};
};

const grow = (e, t) => {
  if (e.anim !== 'grow') return 1;
  return interpolate(t, [e.tIn, e.tIn + 0.6], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.out(Easing.cubic)});
};

const Text = ({e, t, fps, driftY}) => {
  const {opacity, dy} = fade(e, t, fps);
  return (
    <div style={{
      position: 'absolute', left: e.x, top: e.y + dy + (e.group === 'pic' ? driftY : 0), width: Math.ceil(e.w) + 4, height: e.h,
      fontFamily: FAMILIES[e.font], fontWeight: e.weight, fontSize: e.size, lineHeight: `${e.size * e.lh}px`,
      letterSpacing: e.tracking ? `${e.tracking}em` : 'normal', color: e.color, whiteSpace: 'pre', opacity,
      fontVariantNumeric: 'tabular-nums', fontKerning: 'normal', textAlign: 'left',
    }}>
      {e.lines.join('\n')}
    </div>
  );
};

const Rect = ({e, t, driftY}) => {
  const {opacity} = fade(e, t);
  const g = grow(e, t);
  return (
    <div style={{
      position: 'absolute', left: e.x, top: e.y + (e.group === 'pic' ? driftY : 0), width: e.w * g, height: e.h,
      background: e.color, borderRadius: e.radius || 0, opacity,
      boxShadow: e.line ? `inset 0 0 0 2px ${e.line}` : 'none',
    }} />
  );
};

const MapEl = ({e, t, driftY}) => {
  const {opacity} = fade(e, t);
  const focusP = interpolate(t, [e.focusIn || e.tIn, (e.focusIn || e.tIn) + 0.5], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const on = !e.focusSpans || e.focusSpans.some((s) => t >= s[0] && t < s[1]);   // accent only while its own number shows
  return (
    <svg style={{position: 'absolute', left: 0, top: driftY, opacity}} width={1080} height={1920} viewBox="0 0 1080 1920">
      {e.areas.map((a) => (
        <path key={a.n} d={a.d} fill={a.focus && on ? e.focusColor : (a.focus ? e.restColor : a.fill)} fillOpacity={a.focus && on ? 0.25 + 0.75 * focusP : 1}
          stroke={e.stroke} strokeWidth={a.focus && on ? 0 : (e.strokeWidth || 1.5)} strokeLinejoin="round" />
      ))}
      {e.areas.filter((a) => a.focus && on).map((a) => (
        <path key={'f' + a.n} d={a.d} fill="none" stroke={e.focusStroke} strokeWidth={4} strokeLinejoin="round" />
      ))}
    </svg>
  );
};

const Line = ({e, t, driftY}) => {
  const p = interpolate(t, [e.tIn, e.tIn + 1.2], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.inOut(Easing.cubic)});
  const pts = e.points;
  const total = pts.reduce((s, q, i) => (i ? s + Math.hypot(q[0] - pts[i - 1][0], q[1] - pts[i - 1][1]) : 0), 0);
  const d = pts.map((q, i) => `${i ? 'L' : 'M'}${q[0]},${q[1]}`).join('');
  const hi = e.highlightFrom >= 0 ? pts.slice(e.highlightFrom) : [];
  const dh = hi.map((q, i) => `${i ? 'L' : 'M'}${q[0]},${q[1]}`).join('');
  const hp = interpolate(t, [e.tIn + 1.2, e.tIn + 1.8], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  return (
    <svg style={{position: 'absolute', left: 0, top: driftY}} width={1080} height={1920} viewBox="0 0 1080 1920">
      <path d={d} fill="none" stroke={e.color} strokeWidth={8} strokeLinecap="round" strokeLinejoin="round"
        strokeDasharray={total} strokeDashoffset={total * (1 - p)} />
      {hi.length > 1 ? <path d={dh} fill="none" stroke={e.highlight} strokeWidth={10} strokeLinecap="round" strokeLinejoin="round" opacity={hp} /> : null}
      {(e.dots || []).map((q, i) => (
        <circle key={i} cx={q[0]} cy={q[1]} r={12} fill={q[2]} opacity={interpolate(t, [e.tIn + 1.2, e.tIn + 1.5], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'})} />
      ))}
    </svg>
  );
};

const Wave = ({e, frame}) => {
  // The voice's loudness, frame by frame, as a row of bars in the five brand colors: it moves with every syllable.
  const v = e.env[Math.min(e.env.length - 1, frame)] || 0;
  const tt = frame / 30;
  const span = (e.colorSpans || []).find((c) => tt >= c[0] && tt < c[1]);
  const color = span ? span[2] : e.colors[0];
  const gap = 12;
  const bw = (e.w - gap * (e.bars - 1)) / e.bars;
  return (
    <div style={{position: 'absolute', left: e.x, top: e.y, width: e.w, height: e.h}}>
      {Array.from({length: e.bars}).map((_, i) => {
        const shape = 0.35 + 0.65 * Math.abs(Math.sin((i + 1) * 1.7 + frame * 0.21 + i * i * 0.13));
        const h = Math.max(10, e.h * Math.min(1, v * shape));
        return (
          <div key={i} style={{position: 'absolute', left: i * (bw + gap), top: (e.h - h) / 2, width: bw, height: h,
            borderRadius: bw / 2, background: color}} />
        );
      })}
    </div>
  );
};

const Leader = ({e, t}) => {
  const p = interpolate(t, [e.tIn, e.tIn + 0.35], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const [[x1, y1], [x2, y2]] = e.points;
  return (
    <svg style={{position: 'absolute', left: 0, top: 0}} width={1080} height={1920} viewBox="0 0 1080 1920">
      <line x1={x1} y1={y1} x2={x1 + (x2 - x1) * p} y2={y1 + (y2 - y1) * p} stroke={e.color} strokeWidth={e.width} strokeLinecap="round" />
      <circle cx={x1} cy={y1} r={7} fill={e.color} opacity={p} />
    </svg>
  );
};

const Caption = ({c, t}) => {
  // Every word sits at the x the layout measured; the word being said gets an accent pill that slides from word to
  // word, so the frame moves with the voice and a sound-off viewer can follow it.
  const fadeIn = c.tIn === 0 ? 1 : interpolate(t, [c.tIn, c.tIn + 0.12], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const lh = c.size * c.lh;
  const flat = [];
  c.lineWords.forEach((ws, li) => ws.forEach((w) => flat.push({...w, li})));
  const cur = flat.find((w) => t >= w.tIn && t < w.tOut);
  return (
    <div style={{position: 'absolute', left: c.x, top: c.y, width: Math.ceil(c.w) + 4, height: c.h, opacity: fadeIn,
      fontFamily: FAMILIES[c.font], fontWeight: c.weight, fontSize: c.size, lineHeight: `${lh}px`, whiteSpace: 'pre'}}>
      {cur ? (
        <div style={{position: 'absolute', left: cur.x - 10, top: cur.li * lh + lh * 0.04, width: cur.w + 20, height: lh * 0.92,
          background: c.pill, borderRadius: 8}} />
      ) : null}
      {flat.map((w, i) => (
        <span key={i} style={{position: 'absolute', left: w.x, top: w.li * lh,
          color: cur === w ? c.pillText : (t >= w.tIn ? c.color : c.dim)}}>{w.text}</span>
      ))}
    </div>
  );
};

export const RatCheck = (props) => {
  useFonts();
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const t = frame / fps;
  const driftY = props.drift ? props.drift * Math.sin((2 * Math.PI * t) / 6) : 0;
  return (
    <AbsoluteFill style={{background: props.background || '#F3F1EC'}}>
      {props.elements.filter((e) => visible(e, t)).map((e) => {
        if (e.kind === 'text') return <Text key={e.id} e={e} t={t} fps={fps} driftY={driftY} />;
        if (e.kind === 'rect') return <Rect key={e.id} e={e} t={t} driftY={driftY} />;
        if (e.kind === 'map') return <MapEl key={e.id} e={e} t={t} driftY={driftY} />;
        if (e.kind === 'line') return <Line key={e.id} e={e} t={t} driftY={driftY} />;
        if (e.kind === 'wave') return <Wave key={e.id} e={e} frame={frame} />;
        if (e.kind === 'leader') return <Leader key={e.id} e={e} t={t} />;
        return null;
      })}
      {props.progress ? (
        <div style={{position: 'absolute', left: props.progress.x, top: props.progress.y, height: props.progress.h,
          width: props.progress.w * Math.min(1, t / props.progress.until), background: props.progress.color, borderRadius: props.progress.h / 2}} />
      ) : null}
      {(props.captions || []).filter((c) => visible(c, t)).map((c) => <Caption key={c.id} c={c} t={t} />)}
    </AbsoluteFill>
  );
};
