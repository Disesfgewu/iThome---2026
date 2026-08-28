import React, { useEffect, useRef } from 'react';

export default function RadarCanvas({ scores = {} }) {
  const canvasRef = useRef(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    const width = 320;
    const height = 320;
    
    // Support High DPI / Retina Displays
    const dpr = window.devicePixelRatio || 2;
    canvas.width = width * dpr;
    canvas.height = height * dpr;
    ctx.scale(dpr, dpr);

    const centerX = width / 2;
    const centerY = height / 2;
    const radius = Math.min(centerX, centerY) - 50;

    const s = scores || {};
    const labels = ['邏輯條理性', '專業契合度', '表達清晰度', '臨場應變力'];
    
    // Scale 1-10 scores to 0.0 - 1.0 fraction
    const rawLogic = s.logic_structure ?? s.logic ?? 8;
    const rawRelevance = s.major_relevance ?? s.relevance ?? 9;
    const rawClarity = s.communication_clarity ?? s.clarity ?? 8;
    const rawAdaptability = s.adaptability ?? 7.5;

    const dataValues = [
      Math.min(1.0, Math.max(0.1, rawLogic / 10)),
      Math.min(1.0, Math.max(0.1, rawRelevance / 10)),
      Math.min(1.0, Math.max(0.1, rawClarity / 10)),
      Math.min(1.0, Math.max(0.1, rawAdaptability / 10)),
    ];
    const rawScores = [rawLogic, rawRelevance, rawClarity, rawAdaptability];
    const baseline = [0.75, 0.75, 0.75, 0.75]; // 錄取基準線 (7.5 分)

    const numSides = 4;
    const angleStep = (Math.PI * 2) / numSides;
    const offset = -Math.PI / 2; // Start from top 12 o'clock

    ctx.clearRect(0, 0, width, height);

    function getPoint(index, val) {
      const r = radius * val;
      const x = centerX + r * Math.cos(angleStep * index + offset);
      const y = centerY + r * Math.sin(angleStep * index + offset);
      return { x, y };
    }

    function drawPolygon(values, strokeColor, fillColor, isDashed = false, strokeWidth = 2) {
      ctx.beginPath();
      for (let i = 0; i < numSides; i++) {
        const pt = getPoint(i, values[i]);
        if (i === 0) ctx.moveTo(pt.x, pt.y);
        else ctx.lineTo(pt.x, pt.y);
      }
      ctx.closePath();

      if (fillColor) {
        ctx.fillStyle = fillColor;
        ctx.fill();
      }

      ctx.setLineDash(isDashed ? [4, 4] : []);
      ctx.strokeStyle = strokeColor;
      ctx.lineWidth = strokeWidth;
      ctx.stroke();
    }

    // 1. Draw Concentric Grid Concentric Polygons
    for (let j = 1; j <= 5; j++) {
      const gridVal = j / 5;
      drawPolygon([gridVal, gridVal, gridVal, gridVal], '#e2e8f0', null, false, 1);
    }

    // 2. Draw Axes Lines & Metric Labels
    ctx.setLineDash([]);
    ctx.strokeStyle = '#cbd5e1';
    ctx.lineWidth = 1;
    ctx.font = 'bold 12px sans-serif';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';

    for (let i = 0; i < numSides; i++) {
      const outerPt = getPoint(i, 1.0);
      ctx.beginPath();
      ctx.moveTo(centerX, centerY);
      ctx.lineTo(outerPt.x, outerPt.y);
      ctx.stroke();

      // Axis label placement
      const labelRadius = radius + 24;
      const lx = centerX + labelRadius * Math.cos(angleStep * i + offset);
      const ly = centerY + labelRadius * Math.sin(angleStep * i + offset);

      // Label background pill
      const labelText = `${labels[i]} (${rawScores[i].toFixed(1)})`;
      ctx.fillStyle = '#f8fafc';
      ctx.strokeStyle = '#cbd5e1';
      ctx.lineWidth = 1;
      const tw = ctx.measureText(labelText).width;
      ctx.fillRect(lx - tw / 2 - 6, ly - 10, tw + 12, 20);
      ctx.strokeRect(lx - tw / 2 - 6, ly - 10, tw + 12, 20);

      ctx.fillStyle = '#1e293b';
      ctx.fillText(labelText, lx, ly);
    }

    // 3. Draw Baseline (7.5) Dashed Polygon
    drawPolygon(baseline, '#94a3b8', null, true, 1.5);

    // 4. Draw Score Polygon
    drawPolygon(dataValues, '#4f46e5', 'rgba(79, 70, 229, 0.22)', false, 2.5);

    // 5. Draw Highlight Score Points
    for (let i = 0; i < numSides; i++) {
      const pt = getPoint(i, dataValues[i]);
      ctx.beginPath();
      ctx.arc(pt.x, pt.y, 5, 0, Math.PI * 2);
      ctx.fillStyle = '#4f46e5';
      ctx.fill();
      ctx.strokeStyle = '#ffffff';
      ctx.lineWidth = 2;
      ctx.stroke();
    }
  }, [scores]);

  return (
    <div className="relative w-[320px] h-[320px] mx-auto flex items-center justify-center my-2">
      <canvas
        ref={canvasRef}
        width={320}
        height={320}
        style={{ width: '320px', height: '320px', display: 'block' }}
      />
    </div>
  );
}
