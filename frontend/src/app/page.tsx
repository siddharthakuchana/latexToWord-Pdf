'use client';

import { useState, useEffect } from 'react';
import PatternWaves from '@/components/PatternWaves';
import MicroSlats from '@/components/MicroSlats';
import FlexCarousel, { CarouselItem } from '@/components/FlexCarousel';
import ToolWorkspace from '@/components/ToolWorkspaces';
import { fetchHealth, HealthStatus } from '@/lib/api';

const TOOLS: CarouselItem[] = [
  { id: 'joiner', icon: '📑', name: 'OmniMerge', tag: 'MULTI-FORMAT', tagColor: 'emerald', desc: 'Join PDFs & images (JPG, PNG, WEBP, TIFF) into a unified PDF or image archive.' },
  { id: 'splitter', icon: '✂️', name: 'PageSlicer', tag: 'EXTRACTOR', tagColor: 'sky', desc: 'Divide multi-page PDFs into single-page files or extract custom page intervals.' },
  { id: 'organizer', icon: '🔄', name: 'PageForge', tag: 'ORGANIZER', tagColor: 'pink', desc: 'Rotate pages, reorder sequences, delete pages, stamp dynamic page numbers.' },
  { id: 'security', icon: '🔐', name: 'GuardPDF', tag: 'SECURITY', tagColor: 'red', desc: 'Password encryption, permissions, custom watermarks, and metadata scrubbing.' },
  { id: 'raster', icon: '🖼️', name: 'PixelRender', tag: 'DPI-RASTER', tagColor: 'indigo', desc: 'Export PDF pages into crisp PNG, JPEG, WEBP, or TIFF images at custom DPI.' },
  { id: 'diff', icon: '⚖️', name: 'DiffVision', tag: 'PIXEL-DIFF', tagColor: 'cyan', desc: 'Compare two PDF versions side-by-side with pixel diff highlights and metrics.' },
  { id: 'extractor', icon: '🔍', name: 'TextScope', tag: 'TEXT / OCR', tagColor: 'emerald', desc: 'Extract digital text or run OCR on scanned documents; export Markdown & TXT.' },
  { id: 'audio', icon: '🎧', name: 'AudioDoc', tag: 'VOICE-AI', tagColor: 'violet', desc: 'Transform PDFs into spoken audiobooks; listen live or download MP3s.' },
  { id: 'compressor', icon: '🗜️', name: 'OptiCompress', tag: 'OPTIMIZER', tagColor: 'amber', desc: 'Compress PDFs & images to exact target KB/MB or quality sliders.' },
  { id: 'docmorph', icon: '🔄', name: 'OmniConvert', tag: 'PDF ⇄ WORD', tagColor: 'emerald', desc: 'Convert PDF to Word (.docx), Word to PDF, or PDF to PDF with custom file renaming.' },
  { id: 'latex', icon: '📝', name: 'TeXPublish', tag: 'DOCX / MATH', tagColor: 'purple', desc: 'Convert LaTeX to Word & PDF, render math formulas, validate BibTeX.' },
];

export default function Home() {
  const [activeTool, setActiveTool] = useState<string>('joiner');
  const [bgMode, setBgMode] = useState<'waves' | 'slats'>('waves');
  const [health, setHealth] = useState<HealthStatus | null>(null);
  const [serverOnline, setServerOnline] = useState<boolean | null>(null);

  useEffect(() => {
    fetchHealth()
      .then((data) => {
        setHealth(data);
        setServerOnline(true);
      })
      .catch(() => {
        setServerOnline(false);
      });
  }, []);

  const currentToolObj = TOOLS.find((t) => t.id === activeTool) || TOOLS[0];

  return (
    <div className="min-h-screen bg-[#120f17] text-white flex flex-col font-sans selection:bg-purple-500 selection:text-white">
      {/* ------------------------------------------------------------------ */}
      {/* TOP NAVBAR */}
      {/* ------------------------------------------------------------------ */}
      <header className="fixed top-0 left-0 right-0 z-50 bg-[#120f17]/75 backdrop-blur-xl border-b border-white/10 px-6 py-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-purple-500 via-indigo-600 to-pink-500 flex items-center justify-center font-bold text-lg shadow-[0_0_20px_rgba(168,85,247,0.4)]">
            Ω
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-extrabold text-base tracking-tight bg-gradient-to-r from-white via-zinc-200 to-zinc-400 bg-clip-text text-transparent">
                OmniDoc Studio
              </span>
              <span className="text-[10px] uppercase font-bold tracking-widest px-2 py-0.5 rounded-full bg-purple-500/20 text-purple-300 border border-purple-500/30">
                PRO 2.0
              </span>
            </div>
            <p className="text-[11px] text-zinc-400 hidden sm:block">11-in-1 Document & PDF Power Suite</p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          {/* Background Canvas Mode Selector */}
          <div className="flex items-center gap-1 bg-white/[0.05] border border-white/10 rounded-xl p-1 text-xs">
            <button
              onClick={() => setBgMode('waves')}
              className={`px-3 py-1.5 rounded-lg transition-all ${
                bgMode === 'waves'
                  ? 'bg-purple-600 text-white shadow-md'
                  : 'text-zinc-400 hover:text-white'
              }`}
            >
              🌊 PatternWaves
            </button>
            <button
              onClick={() => setBgMode('slats')}
              className={`px-3 py-1.5 rounded-lg transition-all ${
                bgMode === 'slats'
                  ? 'bg-purple-600 text-white shadow-md'
                  : 'text-zinc-400 hover:text-white'
              }`}
            >
              ✨ MicroSlats
            </button>
          </div>

          {/* Backend Status Pill */}
          <div
            className={`flex items-center gap-2 px-3 py-1.5 rounded-xl border text-xs ${
              serverOnline
                ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-300'
                : serverOnline === false
                ? 'bg-amber-500/10 border-amber-500/30 text-amber-300'
                : 'bg-zinc-800 border-zinc-700 text-zinc-400'
            }`}
          >
            <span
              className={`w-2 h-2 rounded-full ${
                serverOnline
                  ? 'bg-emerald-400 animate-pulse'
                  : serverOnline === false
                  ? 'bg-amber-400'
                  : 'bg-zinc-400'
              }`}
            />
            <span className="hidden sm:inline">
              {serverOnline ? 'Backend Online (Port 8000)' : serverOnline === false ? 'Backend Offline' : 'Connecting...'}
            </span>
          </div>
        </div>
      </header>

      {/* ------------------------------------------------------------------ */}
      {/* HERO SECTION WITH INTERACTIVE BACKGROUND CANVAS */}
      {/* ------------------------------------------------------------------ */}
      <section className="relative pt-24 pb-12 overflow-hidden flex flex-col items-center justify-center min-h-[640px]">
        {/* Exact PatternWaves component requested by user */}
        {bgMode === 'waves' ? (
          <div style={{ width: '100%', height: '600px', position: 'relative' }}>
            <PatternWaves
              preset="silk"
              color="#ffffff"
              backgroundColor="#120f17"
              fade="edges"
              interactive
              cursorSize={50}
              cursorStrength={0.6}
              pattern="dot"
              wave="silk"
              spacing={9}
              markSize={0.95}
              depth={0.95}
              light={0}
              shine={0.8}
              contrast={1.2}
              speed={0.35}
              scale={1}
              direction={20}
              opacity={1}
              fadeSize={0.5}
              characters=".:-=+*#%@"
              intro
              paused={false}
            />
          </div>
        ) : (
          <div style={{ width: '100%', height: '600px', position: 'relative' }}>
            <MicroSlats
              preset="swell"
              color="#A855F7"
              glintColor="#ffffff"
              backgroundColor="#120f17"
              slatWidth={10}
              slatHeight={25}
              gap={3}
              roundness={0.75}
              interactive
              cursorStrength={1}
              cursorSize={40}
              speed={0.6}
              direction={250}
              chop={0.55}
              glint={0.7}
              contrast={1.25}
              perspective={0.55}
              fog={0.55}
              scale={1.5}
            />
          </div>
        )}

        {/* Hero Overlay Content */}
        <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none px-6 text-center max-w-4xl mx-auto z-10">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-purple-500/10 border border-purple-500/30 text-purple-300 text-xs font-semibold uppercase tracking-wider mb-4 backdrop-blur-md">
            <span>✨ Complete Local PDF & LaTeX Engineering</span>
          </div>

          <h1 className="text-4xl md:text-6xl font-black tracking-tight text-white leading-tight drop-shadow-2xl">
            Next-Gen Document Studio{' '}
            <span className="bg-gradient-to-r from-purple-400 via-pink-400 to-indigo-300 bg-clip-text text-transparent">
              Built with Precision
            </span>
          </h1>

          <p className="mt-4 text-base md:text-lg text-zinc-300 max-w-2xl leading-relaxed drop-shadow">
            Merge multi-format assets, slice intervals, stamp watermarks, compare pixel diffs,
            transcribe audio, and compile LaTeX locally with zero cloud leakage.
          </p>

          <div className="mt-8 flex flex-wrap gap-4 pointer-events-auto">
            <a
              href="#tools-section"
              className="px-6 py-3 rounded-xl font-medium text-white bg-gradient-to-r from-purple-600 via-indigo-600 to-pink-600 hover:from-purple-500 hover:to-pink-500 transition-all shadow-[0_0_30px_rgba(168,85,247,0.4)] flex items-center gap-2"
            >
              <span>Explore 10 Tools</span>
              <span>↓</span>
            </a>
            <button
              onClick={() => setBgMode(bgMode === 'waves' ? 'slats' : 'waves')}
              className="px-6 py-3 rounded-xl font-medium text-zinc-200 bg-white/10 hover:bg-white/15 border border-white/15 backdrop-blur-md transition-all"
            >
              Toggle Canvas: {bgMode === 'waves' ? 'MicroSlats' : 'PatternWaves'}
            </button>
          </div>
        </div>
      </section>

      {/* ------------------------------------------------------------------ */}
      {/* TOOLS CAROUSEL & HUB */}
      {/* ------------------------------------------------------------------ */}
      <section id="tools-section" className="relative z-20 px-6 py-8 max-w-7xl mx-auto w-full">
        <div className="mb-6 flex flex-col md:flex-row md:items-end justify-between gap-4">
          <div>
            <h2 className="text-2xl font-bold text-white tracking-tight flex items-center gap-2">
              🛠️ Tool Suite Carousel
            </h2>
            <p className="text-sm text-zinc-400 mt-1">
              Select an engine card below to launch its dedicated high-performance workspace.
            </p>
          </div>
          <div className="text-xs text-zinc-400 bg-white/[0.03] border border-white/10 px-3 py-1.5 rounded-lg">
            Active: <span className="font-semibold text-purple-400">{currentToolObj.name}</span> ({currentToolObj.tag})
          </div>
        </div>

        {/* FlexCarousel Component */}
        <div className="mb-10">
          <FlexCarousel
            items={TOOLS}
            activeId={activeTool}
            onSelect={(item) => setActiveTool(item.id)}
          />
        </div>

        {/* Active Tool Workspace */}
        <div className="mb-16">
          <ToolWorkspace toolId={activeTool} />
        </div>

        {/* ------------------------------------------------------------------ */}
        {/* ARCHITECTURE & FEATURE HIGHLIGHTS */}
        {/* ------------------------------------------------------------------ */}
        <div className="border-t border-white/10 pt-12 pb-8">
          <h3 className="text-xl font-bold text-white mb-6 text-center">
            OmniDoc Studio Engine Architecture
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <div className="p-5 rounded-2xl bg-white/[0.02] border border-white/10">
              <div className="text-2xl mb-2">🔒</div>
              <h4 className="font-bold text-white text-sm">100% Offline & Private</h4>
              <p className="text-xs text-zinc-400 mt-1 leading-relaxed">
                Documents are processed entirely locally through your FastAPI instance. No external data telemetry.
              </p>
            </div>

            <div className="p-5 rounded-2xl bg-white/[0.02] border border-white/10">
              <div className="text-2xl mb-2">⚡</div>
              <h4 className="font-bold text-white text-sm">Hardware-Accelerated</h4>
              <p className="text-xs text-zinc-400 mt-1 leading-relaxed">
                Streamlit or React frontend communicating with native PyMuPDF, Pillow, and pypandoc C-extensions.
              </p>
            </div>

            <div className="p-5 rounded-2xl bg-white/[0.02] border border-white/10">
              <div className="text-2xl mb-2">🎯</div>
              <h4 className="font-bold text-white text-sm">Pixel-Perfect Rasterization</h4>
              <p className="text-xs text-zinc-400 mt-1 leading-relaxed">
                Custom DPI rendering up to 300 DPI for press-ready outputs, multi-page TIFF, and differential overlays.
              </p>
            </div>

            <div className="p-5 rounded-2xl bg-white/[0.02] border border-white/10">
              <div className="text-2xl mb-2">🎧</div>
              <h4 className="font-bold text-white text-sm">Audio & Vision AI</h4>
              <p className="text-xs text-zinc-400 mt-1 leading-relaxed">
                Text-to-speech narration with multi-accent synthesis, paired with Tesseract OCR computer vision.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* ------------------------------------------------------------------ */}
      {/* FOOTER */}
      {/* ------------------------------------------------------------------ */}
      <footer className="border-t border-white/10 py-8 px-6 text-center text-xs text-zinc-500 bg-[#0d0b11]">
        <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-4">
          <p>© 2026 OmniDoc Studio Pro. Built with Next.js, FastAPI, PyMuPDF, and React Bits.</p>
          <div className="flex items-center gap-4 text-zinc-400">
            <span>FastAPI: localhost:8000</span>
            <span>•</span>
            <span>Next.js: localhost:3000</span>
            <span>•</span>
            <span className="text-emerald-400">All 10 Modules Ready</span>
          </div>
        </div>
      </footer>
    </div>
  );
}
