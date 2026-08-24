import React, { useEffect, useState } from 'react';

export default function WaveformBar({ isSpeaking = true }) {
  const [heights, setHeights] = useState([40, 75, 55, 90, 60, 80, 45, 95, 70, 50, 85, 65, 90, 40, 70, 50]);

  useEffect(() => {
    if (!isSpeaking) return;
    const interval = setInterval(() => {
      setHeights(
        Array.from({ length: 16 }, () => Math.floor(Math.random() * 75) + 20)
      );
    }, 150);
    return () => clearInterval(interval);
  }, [isSpeaking]);

  return (
    <div class="flex items-end gap-1.5 h-12 w-48 justify-center">
      {heights.map((h, idx) => (
        <div
          key={idx}
          style={{ height: isSpeaking ? `${h}%` : '15%' }}
          class="w-1.5 bg-indigo-500 rounded-full transition-all duration-150"
        />
      ))}
    </div>
  );
}
