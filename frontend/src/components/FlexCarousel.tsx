'use client';

import { useRef, useState, useCallback, useEffect } from 'react';

export interface CarouselItem {
  id: string;
  icon: string;
  name: string;
  tag: string;
  tagColor: string;
  desc: string;
}

interface FlexCarouselProps {
  items: CarouselItem[];
  onSelect?: (item: CarouselItem) => void;
  activeId?: string;
}

const TAG_COLORS: Record<string, string> = {
  emerald: 'bg-emerald-500/20 text-emerald-400 border-emerald-500/40',
  sky: 'bg-sky-500/20 text-sky-400 border-sky-500/40',
  pink: 'bg-pink-500/20 text-pink-400 border-pink-500/40',
  red: 'bg-red-500/20 text-red-400 border-red-500/40',
  indigo: 'bg-indigo-500/20 text-indigo-400 border-indigo-500/40',
  cyan: 'bg-cyan-500/20 text-cyan-400 border-cyan-500/40',
  violet: 'bg-violet-500/20 text-violet-400 border-violet-500/40',
  amber: 'bg-amber-500/20 text-amber-400 border-amber-500/40',
  purple: 'bg-purple-500/20 text-purple-400 border-purple-500/40',
};

export default function FlexCarousel({ items, onSelect, activeId }: FlexCarouselProps) {
  const scrollRef = useRef<HTMLDivElement>(null);
  const [hoveredId, setHoveredId] = useState<string | null>(null);

  return (
    <div className="relative w-full">
      <div
        ref={scrollRef}
        className="flex gap-4 overflow-x-auto pb-4 snap-x snap-mandatory scrollbar-hide"
        style={{ scrollbarWidth: 'none', msOverflowStyle: 'none' }}
      >
        {items.map((item) => {
          const isActive = activeId === item.id;
          const isHovered = hoveredId === item.id;
          const tagStyle = TAG_COLORS[item.tagColor] || TAG_COLORS.emerald;

          return (
            <button
              key={item.id}
              onClick={() => onSelect?.(item)}
              onMouseEnter={() => setHoveredId(item.id)}
              onMouseLeave={() => setHoveredId(null)}
              className={`
                group relative flex-shrink-0 w-[220px] snap-center
                rounded-2xl p-5 text-left
                border backdrop-blur-xl
                transition-all duration-300 ease-out
                ${isActive
                  ? 'border-purple-500/60 bg-gradient-to-br from-purple-900/40 to-indigo-900/40 shadow-[0_0_30px_rgba(168,85,247,0.3)]'
                  : 'border-white/[0.08] bg-white/[0.04] hover:border-white/20 hover:bg-white/[0.08]'
                }
                ${isHovered && !isActive ? 'scale-[1.03] -translate-y-1' : ''}
              `}
            >
              {/* Active glow ring */}
              {isActive && (
                <div className="absolute inset-0 rounded-2xl bg-gradient-to-br from-purple-500/10 to-cyan-500/5 pointer-events-none" />
              )}

              <div className="relative z-10">
                {/* Tag */}
                <span className={`inline-block text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-md border mb-3 ${tagStyle}`}>
                  {item.tag}
                </span>

                {/* Icon & Name */}
                <div className="flex items-center gap-2 mb-2">
                  <span className="text-2xl">{item.icon}</span>
                  <h3 className="text-sm font-bold text-white/90">{item.name}</h3>
                </div>

                {/* Description */}
                <p className="text-xs text-white/50 leading-relaxed line-clamp-3">{item.desc}</p>

                {/* Active indicator */}
                {isActive && (
                  <div className="mt-3 flex items-center gap-1.5">
                    <div className="w-1.5 h-1.5 rounded-full bg-purple-400 animate-pulse" />
                    <span className="text-[10px] font-semibold text-purple-400 uppercase tracking-wider">Active</span>
                  </div>
                )}
              </div>
            </button>
          );
        })}
      </div>
    </div>
  );
}
