'use client';

import { useRef, useEffect, useCallback } from 'react';

export interface MicroSlatsProps {
  preset?: string;
  color?: string;
  glintColor?: string;
  backgroundColor?: string;
  slatWidth?: number;
  slatHeight?: number;
  gap?: number;
  roundness?: number;
  interactive?: boolean;
  cursorStrength?: number;
  cursorSize?: number;
  speed?: number;
  direction?: number;
  chop?: number;
  glint?: number;
  contrast?: number;
  perspective?: number;
  fog?: number;
  className?: string;
  scale?: number;
  paused?: boolean;
}

export default function MicroSlats({
  preset = 'swell',
  color = '#A855F7',
  glintColor = '#ffffff',
  backgroundColor = '#120f17',
  slatWidth = 10,
  slatHeight = 25,
  gap = 3,
  roundness = 0.75,
  interactive = true,
  cursorStrength = 1,
  cursorSize = 40,
  speed = 0.6,
  direction = 250,
  chop = 0.55,
  glint = 0.7,
  contrast = 1.25,
  perspective = 0.55,
  fog = 0.55,
  scale = 1.5,
  paused = false,
  className = '',
}: MicroSlatsProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const mouse = useRef({ x: -9999, y: -9999 });
  const time = useRef(0);
  const raf = useRef<number>(0);

  const hexToRgb = (hex: string) => {
    let clean = hex.replace('#', '');
    if (clean.length === 3) {
      clean = clean.split('').map((c) => c + c).join('');
    }
    const r = parseInt(clean.slice(0, 2), 16) || 168;
    const g = parseInt(clean.slice(2, 4), 16) || 85;
    const b = parseInt(clean.slice(4, 6), 16) || 247;
    return { r, g, b };
  };

  const draw = useCallback(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const W = canvas.width;
    const H = canvas.height;

    if (!paused) {
      time.current += speed * 0.015;
    }

    ctx.fillStyle = backgroundColor;
    ctx.fillRect(0, 0, W, H);

    const totalW = (slatWidth + gap) * scale;
    const totalH = (slatHeight + gap) * scale;
    const cols = Math.ceil(W / totalW) + 2;
    const rows = Math.ceil(H / totalH) + 2;
    const dirRad = (direction * Math.PI) / 180;

    const baseColor = hexToRgb(color);
    const glintRgb = hexToRgb(glintColor);

    for (let row = 0; row < rows; row++) {
      for (let col = 0; col < cols; col++) {
        const cx = col * totalW;
        const cy = row * totalH;

        // Wave function
        const wx = Math.sin((cx * 0.008 + time.current + dirRad) * contrast);
        const wy = Math.cos((cy * 0.006 + time.current * 0.8) * contrast);
        const wave = (wx + wy) * 0.5;

        // Perspective tilt effect
        const perspY = (cy / H - 0.5) * perspective;
        const tiltScale = 1 - Math.abs(perspY) * 0.3;

        // Cursor interaction
        let cursorGlow = 0;
        if (interactive) {
          const dx = cx - mouse.current.x;
          const dy = cy - mouse.current.y;
          const dist = Math.sqrt(dx * dx + dy * dy);
          const radius = cursorSize * totalW;
          if (dist < radius) {
            cursorGlow = (1 - dist / radius) * cursorStrength;
          }
        }

        // Height chop
        const sH = slatHeight * scale * tiltScale * (0.5 + (wave + 1) * 0.5 * chop);

        // Fog/distance falloff
        const fogFactor = 1 - (cy / H) * fog * 0.6;

        // Glint highlight
        const glintFactor = Math.max(0, wave) * glint + cursorGlow;
        const r = Math.round(baseColor.r + (glintRgb.r - baseColor.r) * glintFactor);
        const g = Math.round(baseColor.g + (glintRgb.g - baseColor.g) * glintFactor);
        const b = Math.round(baseColor.b + (glintRgb.b - baseColor.b) * glintFactor);
        const alpha = Math.min(1, Math.max(0.15, fogFactor * (0.5 + glintFactor * 0.5)));

        const sW = slatWidth * scale * tiltScale;
        const radius = roundness * Math.min(sW, sH) * 0.5;

        ctx.fillStyle = `rgba(${r},${g},${b},${alpha})`;
        ctx.beginPath();
        if (radius > 0 && ctx.roundRect) {
          ctx.roundRect(cx - sW / 2, cy - sH / 2, sW, sH, radius);
        } else {
          ctx.rect(cx - sW / 2, cy - sH / 2, sW, sH);
        }
        ctx.fill();
      }
    }

    if (!paused) {
      raf.current = requestAnimationFrame(draw);
    }
  }, [
    backgroundColor,
    chop,
    color,
    contrast,
    cursorSize,
    cursorStrength,
    direction,
    fog,
    gap,
    glint,
    glintColor,
    interactive,
    paused,
    perspective,
    roundness,
    scale,
    slatHeight,
    slatWidth,
    speed,
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

  return (
    <canvas
      ref={canvasRef}
      className={`absolute inset-0 w-full h-full pointer-events-auto ${className}`}
      style={{ display: 'block' }}
    />
  );
}
