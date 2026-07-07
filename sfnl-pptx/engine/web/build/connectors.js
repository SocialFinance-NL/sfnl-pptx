/** connectors.js — plan connector line segments between two rects (inches). */
function centers(r) {
  return {
    left:   { x: r.x,          y: r.y + r.h / 2 },
    right:  { x: r.x + r.w,    y: r.y + r.h / 2 },
    top:    { x: r.x + r.w / 2, y: r.y },
    bottom: { x: r.x + r.w / 2, y: r.y + r.h }
  };
}

function pickAnchors(from, to) {
  const f = centers(from);
  const t = centers(to);
  const dx = (to.x + to.w / 2) - (from.x + from.w / 2);
  const dy = (to.y + to.h / 2) - (from.y + from.h / 2);
  if (Math.abs(dx) >= Math.abs(dy)) {
    return dx >= 0 ? { start: f.right, end: t.left, axis: 'h' } : { start: f.left, end: t.right, axis: 'h' };
  }
  return dy >= 0 ? { start: f.bottom, end: t.top, axis: 'v' } : { start: f.top, end: t.bottom, axis: 'v' };
}

function planConnector(from, to, opts = {}) {
  const { start, end, axis } = pickAnchors(from, to);
  const route = opts.route || 'straight';
  let segments;
  if (route === 'elbow' && (Math.abs(start.x - end.x) > 1e-6 && Math.abs(start.y - end.y) > 1e-6)) {
    if (axis === 'h') {
      const midX = (start.x + end.x) / 2;
      segments = [
        { x1: start.x, y1: start.y, x2: midX, y2: start.y },
        { x1: midX, y1: start.y, x2: midX, y2: end.y },
        { x1: midX, y1: end.y, x2: end.x, y2: end.y }
      ];
    } else {
      const midY = (start.y + end.y) / 2;
      segments = [
        { x1: start.x, y1: start.y, x2: start.x, y2: midY },
        { x1: start.x, y1: midY, x2: end.x, y2: midY },
        { x1: end.x, y1: midY, x2: end.x, y2: end.y }
      ];
    }
  } else {
    segments = [{ x1: start.x, y1: start.y, x2: end.x, y2: end.y }];
  }
  const mid = segments[Math.floor(segments.length / 2)];
  const labelPos = { x: (mid.x1 + mid.x2) / 2, y: (mid.y1 + mid.y2) / 2 };
  return { segments, labelPos };
}

module.exports = { planConnector };
