import React, { useEffect, useRef } from 'react';

export default function RadarCanvas({ scores }) {
  const canvasRef = useRef(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    const width = 320;
    const height = 320;
    canvas.width = width * 2;
    canvas.height = height * 2;
    ctx.scale(2, 2);

    const centerX = width / 2;
    const centerY = height / 2;
    const radius = Math.min(centerX, centerY) - 45;

    const labels = ['邏輯條理性', '專業契合度', '表達清晰度', '臨場應變力'];
    const dataValues = [
      (scores.logic_structure || 8) / 10,
      (scores.major_relevance || 9) / 10,
      (scores.communication_clarity || 8) / 10,
      (scores.adaptability || 7) / 10,
    ];
    const baseline = [0.75, 0.75, 0.75, 0.75];

    const numSides = 4;
    const angleStep = (Math.PI * 2) / numSides;
    const offset = -Math.PI / 2;

    ctx.clearRect(0, 0, width, height);

    function drawPolygon(values, strokeColor, fillColor, isDashed = false) {
      ctx.beginPath();
      for (let i = 0; i < numSides; i++) {
        const val = values[i];
        const r = radius * val;
        const x = centerX + r * Math.cos(angleStep * i + offset);
        const y = centerY + r * Math.sin(angleStep * i + offset);
        if (i === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
      }
      ctx.closePath();

      if (fillColor) {
        ctx.fillStyle = fillColor;
        ctx.fill();
      }

      ctx.setLineDash(isDashed ? [5, 5] : []);
      ctx.strokeStyle = strokeColor;
      ctx.lineWidth = 2;
      ctx.stroke();
    }

    // Grid webs
    for (let j = 1; j <= 5; j++) {
      drawPolygon([j / 5, j / 5, j / 5, j / 5], '#e2e8f0', null);
    }

    // Axes & Labels
    ctx.setLineDash([]);
    ctx.strokeStyle = '#cbd5e1';
    ctx.fillStyle = '#475569';
    ctx.font = '500 12px Sora';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';

    for (let i = 0; i < numSides; i++) {
      const x = centerX + radius * Math.cos(angleStep * i + offset);
      const y = centerY + radius * Math.sin(angleStep * i + offset);

      ctx.beginPath();
      ctx.moveTo(centerX, centerY);
      ctx.lineTo(x, y);
      ctx.stroke();

      const labelR = radius + 22;
      const lx = centerX + labelR * Math.cos(angleStep * i + offset);
      const ly = centerY + labelR * Math.sin(angleStep * i + offset);
      ctx.fillText(labels[i], lx, ly);
    }

    // Baseline
    drawPolygon(baseline, '#94a3b8', null, true);

    // Data polygon
    drawPolygon(dataValues, '#4f46e5', 'rgba(79, 70, 229, 0.18)');

    // Data points
    ctx.fillStyle = '#4f46e5';
    for (let i = 0; i < numSides; i++) {
      const r = radius * dataValues[i];
      const x = centerX + r * Math.cos(angleStep * i + offset);
      const y = centerY + r * Math.sin(angleStep * i + offset);
      ctx.beginPath();
      ctx.arc(x, y, 4, 0, Math.PI * 2);
      ctx.fill();
    }
  }, [scores]);

  return (
    <div class="relative w-full max-w-[320px] aspect-square mx-auto flex items-center justify-center">
      <canvas ref={canvasRef} class="w-full h-full" />
    </div>
  );
}
