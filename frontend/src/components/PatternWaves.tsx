'use client';

import { useRef, useEffect, useCallback } from 'react';

export interface PatternWavesProps {
  color?: string;
  backgroundColor?: string;
  preset?: string;
  fade?: 'edges' | 'none' | string;
  interactive?: boolean;
  cursorSize?: number;
  cursorStrength?: number;
  pattern?: 'dot' | 'characters' | string;
  wave?: string;
  spacing?: number;
  markSize?: number;
  depth?: number;
  light?: number;
  shine?: number;
  contrast?: number;
  speed?: number;
  scale?: number;
  direction?: number;
  opacity?: number;
  fadeSize?: number;
  characters?: string;
  intro?: boolean;
  paused?: boolean;
  className?: string;
}

export default function PatternWaves({
  color = '#ffffff',
  backgroundColor = '#120f17',
  preset = 'silk',
  fade = 'edges',
  interactive = true,
  cursorSize = 50,
  cursorStrength = 0.6,
  pattern = 'dot',
  wave = 'silk',
  spacing = 9,
  markSize = 0.95,
  depth = 0.95,
  light = 0,
  shine = 0.8,
  contrast = 1.2,
  speed = 0.35,
  scale = 1,
  direction = 20,
  opacity = 1,
  fadeSize = 0.5,
  characters = '.:-=+*#%@',
  intro = false,
  paused = false,
  className = '',
}: PatternWavesProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const mouse = useRef({ x: -9999, y: -9999 });
  const time = useRef(0);
  const raf = useRef<number>(0);

  const hexToRgb = (hex: string) => {
    let clean = hex.replace('#', '');
    if (clean.length === 3) {
      clean = clean.split('').map((c) => c + c).join('');
    }
    const r = parseInt(clean.slice(0, 2), 16) || 255;
    const g = parseInt(clean.slice(2, 4), 16) || 255;
    const b = parseInt(clean.slice(4, 6), 16) || 255;
    return { r, g, b };
  };

  const draw = useCallback(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    if (!paused) {
      time.current += speed * 0.02;
    }

    const W = canvas.width;
    const H = canvas.height;

    ctx.fillStyle = backgroundColor;
    ctx.fillRect(0, 0, W, H);

    const step = Math.max(4, spacing * scale);
    const cols = Math.ceil(W / step) + 2;
    const rows = Math.ceil(H / step) + 2;
    const dirRad = (direction * Math.PI) / 180;
    const rgb = hexToRgb(color);

    const chars = characters || '.:-=+*#%@';

    for (let row = 0; row < rows; row++) {
      for (let col = 0; col < cols; col++) {
        const x = col * step;
        const y = row * step;

        // Wave calculation
        const wx = Math.sin((x * 0.012 + time.current) * contrast) * depth * 20;
        const wy = Math.cos((y * 0.01 + time.current * 0.7 + dirRad) * contrast) * depth * 15;
        const wVal = (wx + wy) / 35 + 0.5;

        // Cursor interaction
        let cursorInfluence = 0;
        if (interactive) {
          const dx = x - mouse.current.x;
          const dy = y - mouse.current.y;
          const dist = Math.sqrt(dx * dx + dy * dy);
          const radius = cursorSize * step;
          if (dist < radius) {
            cursorInfluence = (1 - dist / radius) * cursorStrength;
          }
        }

        const brightness = Math.min(1, Math.max(0, wVal * shine + cursorInfluence + light));
        const alpha = brightness * opacity;

        if (alpha <= 0.01) continue;

        ctx.fillStyle = `rgba(${rgb.r},${rgb.g},${rgb.b},${alpha})`;

        if (pattern === 'characters') {
          const charIdx = Math.floor(brightness * (chars.length - 1));
          const char = chars[Math.min(chars.length - 1, Math.max(0, charIdx))];
          ctx.font = `${Math.round(step * markSize)}px monospace`;
          ctx.textAlign = 'center';
          ctx.textBaseline = 'middle';
          ctx.fillText(char, x, y);
        } else {
          const size = markSize * step * 0.4 * (0.3 + brightness * 0.7);
          ctx.beginPath();
          ctx.arc(x, y, Math.max(0.5, size), 0, Math.PI * 2);
          ctx.fill();
        }
      }
    }

    if (!paused) {
      raf.current = requestAnimationFrame(draw);
    }
  }, [
    backgroundColor,
    color,
    contrast,
    cursorSize,
    cursorStrength,
    depth,
    direction,
    interactive,
    light,
    markSize,
    opacity,
    paused,
    scale,
    shine,
    spacing,
    speed,
    characters,
    pattern,
  ]);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const resize = () => {
      const parent = canvas.parentElement;
      if (parent) {
        canvas.width = parent.clientWidth;
        canvas.height = parent.clientHeight;
      }
    };

    resize();
    window.addEventListener('resize', resize);
    raf.current = requestAnimationFrame(draw);

    return () => {
      window.removeEventListener('resize', resize);
      cancelAnimationFrame(raf.current);
    };
  }, [draw]);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas || !interactive) return;

    const handleMove = (e: MouseEvent) => {
      const rect = canvas.getBoundingClientRect();
      mouse.current = { x: e.clientX - rect.left, y: e.clientY - rect.top };
    };

    const handleLeave = () => {
      mouse.current = { x: -9999, y: -9999 };
    };

    canvas.addEventListener('mousemove', handleMove);
    canvas.addEventListener('mouseleave', handleLeave);
    return () => {
      canvas.removeEventListener('mousemove', handleMove);
      canvas.removeEventListener('mouseleave', handleLeave);
    };
  }, [interactive]);

  const maskStyle =
    fade === 'edges'
      ? {
          WebkitMaskImage: `radial-gradient(ellipse at center, rgba(0,0,0,1) ${Math.round(
            (1 - fadeSize) * 80
          )}%, rgba(0,0,0,0) 95%)`,
          maskImage: `radial-gradient(ellipse at center, rgba(0,0,0,1) ${Math.round(
            (1 - fadeSize) * 80
          )}%, rgba(0,0,0,0) 95%)`,
        }
      : {};

  return (
    <canvas
      ref={canvasRef}
      className={`absolute inset-0 w-full h-full pointer-events-auto ${className}`}
      style={{ display: 'block', ...maskStyle }}
    />
  );
}
