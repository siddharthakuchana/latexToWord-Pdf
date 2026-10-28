'use client';

import { useState, useEffect } from 'react';
import FileDropZone from './FileDropZone';
import {
  uploadFile,
  uploadTwoFiles,
  uploadMultipleFiles,
  downloadFromResponse,
  postForm,
} from '@/lib/api';

interface ToolWorkspaceProps {
  toolId: string;
}

export default function ToolWorkspace({ toolId }: ToolWorkspaceProps) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);

  // Clear state when switching tools
  useEffect(() => {
    setError(null);
    setSuccessMsg(null);
  }, [toolId]);

  return (
    <div className="w-full max-w-5xl mx-auto bg-white/[0.03] border border-white/10 rounded-3xl p-6 md:p-8 backdrop-blur-2xl shadow-2xl relative overflow-hidden">
      {error && (
        <div className="mb-6 p-4 rounded-xl bg-red-500/10 border border-red-500/30 text-red-300 text-sm flex items-center justify-between">
          <span>⚠️ {error}</span>
          <button onClick={() => setError(null)} className="text-red-400 hover:text-white">✕</button>
        </div>
      )}
      {successMsg && (
        <div className="mb-6 p-4 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 text-sm flex items-center justify-between">
          <span>✅ {successMsg}</span>
          <button onClick={() => setSuccessMsg(null)} className="text-emerald-400 hover:text-white">✕</button>
        </div>
      )}

      {toolId === 'joiner' && <JoinerWorkspace setLoading={setLoading} loading={loading} setError={setError} setSuccess={setSuccessMsg} />}
      {toolId === 'splitter' && <SplitterWorkspace setLoading={setLoading} loading={loading} setError={setError} setSuccess={setSuccessMsg} />}
      {toolId === 'organizer' && <OrganizerWorkspace setLoading={setLoading} loading={loading} setError={setError} setSuccess={setSuccessMsg} />}
      {toolId === 'security' && <SecurityWorkspace setLoading={setLoading} loading={loading} setError={setError} setSuccess={setSuccessMsg} />}
      {toolId === 'raster' && <RasterWorkspace setLoading={setLoading} loading={loading} setError={setError} setSuccess={setSuccessMsg} />}
      {toolId === 'diff' && <DiffWorkspace setLoading={setLoading} loading={loading} setError={setError} setSuccess={setSuccessMsg} />}
      {toolId === 'extractor' && <ExtractorWorkspace setLoading={setLoading} loading={loading} setError={setError} setSuccess={setSuccessMsg} />}
      {toolId === 'audio' && <AudioWorkspace setLoading={setLoading} loading={loading} setError={setError} setSuccess={setSuccessMsg} />}
      {toolId === 'compressor' && <CompressorWorkspace setLoading={setLoading} loading={loading} setError={setError} setSuccess={setSuccessMsg} />}
      {toolId === 'docmorph' && <DocMorphWorkspace setLoading={setLoading} loading={loading} setError={setError} setSuccess={setSuccessMsg} />}
      {toolId === 'latex' && <LatexWorkspace setLoading={setLoading} loading={loading} setError={setError} setSuccess={setSuccessMsg} />}
    </div>
  );
}

// ---------------------------------------------------------------------------
// 1. OMNIMERGE
// ---------------------------------------------------------------------------
function JoinerWorkspace({ setLoading, loading, setError, setSuccess }: any) {
  const [files, setFiles] = useState<File[]>([]);
  const [format, setFormat] = useState('PDF');
  const [filename, setFilename] = useState('merged_document');

  const handleFiles = (newFiles: File[]) => {
    setFiles((prev) => [...prev, ...newFiles]);
  };

  const removeFile = (idx: number) => {
    setFiles((prev) => prev.filter((_, i) => i !== idx));
  };

  const moveFile = (idx: number, dir: -1 | 1) => {
    if ((dir === -1 && idx === 0) || (dir === 1 && idx === files.length - 1)) return;
    const newFiles = [...files];
    const target = newFiles[idx];
    newFiles[idx] = newFiles[idx + dir];
    newFiles[idx + dir] = target;
    setFiles(newFiles);
  };

  const handleMerge = async () => {
    if (files.length === 0) {
      setError('Please add at least one PDF or image file.');
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const res = await uploadMultipleFiles('/api/joiner/merge', files, {
        output_format: format,
        output_filename: filename,
        add_bookmarks: 'true',
        render_dpi: '150',
      });
      if (!res.ok) {
        const data = await res.json().catch(() => ({ detail: 'Merge failed' }));
        throw new Error(data.detail || 'Merge failed');
      }
      await downloadFromResponse(res, `${filename}.${format === 'PDF' ? 'pdf' : 'zip'}`);
      setSuccess(`Successfully merged ${files.length} files! Download started.`);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-white/10 pb-4">
        <div>
          <h3 className="text-xl font-bold text-white flex items-center gap-2">📑 OmniMerge</h3>
          <p className="text-sm text-zinc-400">Combine multiple PDFs and image files into a single document.</p>
        </div>
        <div className="flex items-center gap-3">
          <select
            value={format}
            onChange={(e) => setFormat(e.target.value)}
            className="bg-zinc-900 border border-white/20 rounded-xl px-3 py-2 text-sm text-white focus:outline-none focus:border-purple-500"
          >
            <option value="PDF">Target: Unified PDF</option>
            <option value="PNG_ZIP">Target: PNG Archive (ZIP)</option>
            <option value="JPEG_ZIP">Target: JPEG Archive (ZIP)</option>
            <option value="TIFF">Target: Multi-page TIFF</option>
          </select>
          <input
            type="text"
            value={filename}
            onChange={(e) => setFilename(e.target.value)}
            placeholder="Output filename"
            className="bg-zinc-900 border border-white/20 rounded-xl px-3 py-2 text-sm text-white focus:outline-none focus:border-purple-500 w-40"
          />
        </div>
      </div>

      <FileDropZone
        accept=".pdf,.png,.jpg,.jpeg,.webp,.tiff"
        multiple
        label="Drop PDF & Image files here"
        sublabel="Supports PDFs, PNG, JPG, WEBP, TIFF"
        onFiles={handleFiles}
      />

      {files.length > 0 && (
        <div className="space-y-2">
          <div className="flex justify-between items-center text-xs text-zinc-400 uppercase tracking-wider">
            <span>Files to Merge ({files.length})</span>
            <button onClick={() => setFiles([])} className="text-red-400 hover:underline">Clear All</button>
          </div>
          <div className="max-h-60 overflow-y-auto space-y-2 pr-1">
            {files.map((f, i) => (
              <div
                key={`${f.name}-${i}`}
                className="flex items-center justify-between bg-zinc-900/60 border border-white/5 rounded-xl px-4 py-2.5 text-sm text-zinc-200"
              >
                <div className="flex items-center gap-3 truncate">
                  <span className="text-xs text-zinc-500 w-5">{i + 1}.</span>
                  <span className="truncate">{f.name}</span>
                  <span className="text-xs text-zinc-500">({(f.size / 1024).toFixed(0)} KB)</span>
                </div>
                <div className="flex items-center gap-2 flex-shrink-0">
                  <button onClick={() => moveFile(i, -1)} disabled={i === 0} className="px-1.5 py-0.5 text-xs bg-zinc-800 hover:bg-zinc-700 disabled:opacity-30 rounded">▲</button>
                  <button onClick={() => moveFile(i, 1)} disabled={i === files.length - 1} className="px-1.5 py-0.5 text-xs bg-zinc-800 hover:bg-zinc-700 disabled:opacity-30 rounded">▼</button>
                  <button onClick={() => removeFile(i)} className="text-red-400 hover:text-red-300 ml-2">✕</button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      <button
        onClick={handleMerge}
        disabled={loading || files.length === 0}
        className="w-full py-3.5 rounded-xl font-medium text-white bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 disabled:opacity-50 transition-all shadow-lg shadow-purple-900/30 flex items-center justify-center gap-2"
      >
        {loading ? <Spinner /> : '🚀 Merge & Download Document'}
      </button>
    </div>
  );
}

// ---------------------------------------------------------------------------
// 2. PAGESLICER (SPLITTER)
// ---------------------------------------------------------------------------
function SplitterWorkspace({ setLoading, loading, setError, setSuccess }: any) {
  const [file, setFile] = useState<File | null>(null);
  const [pageCount, setPageCount] = useState<number | null>(null);
  const [mode, setMode] = useState<'all' | 'range'>('all');
  const [startPage, setStartPage] = useState(1);
  const [endPage, setEndPage] = useState(1);

  const handleFile = async (files: File[]) => {
    if (files[0]) {
      setFile(files[0]);
      try {
        const formData = new FormData();
        formData.append('file', files[0]);
        const res = await fetch('http://localhost:8000/api/splitter/info', {
          method: 'POST',
          body: formData,
        });
        if (res.ok) {
          const data = await res.json();
          setPageCount(data.pages);
          setEndPage(data.pages);
        }
      } catch {
        // info fetch failed, non-blocking
      }
    }
  };

  const handleSplit = async () => {
    if (!file) {
      setError('Please upload a PDF file first.');
      return;
    }
    setLoading(true);
    setError(null);
    try {
      let res: Response;
      if (mode === 'all') {
        res = await uploadFile('/api/splitter/split', file);
        if (!res.ok) throw new Error('Split all pages failed');
        await downloadFromResponse(res, `${file.name.replace('.pdf', '')}_pages.zip`);
        setSuccess('All pages split into ZIP file successfully!');
      } else {
        res = await uploadFile('/api/splitter/extract', file, {
          start_page: startPage,
          end_page: endPage,
        });
        if (!res.ok) throw new Error('Extract pages failed');
        await downloadFromResponse(res, `${file.name.replace('.pdf', '')}_p${startPage}-p${endPage}.pdf`);
        setSuccess(`Extracted pages ${startPage} to ${endPage} successfully!`);
      }
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="border-b border-white/10 pb-4">
        <h3 className="text-xl font-bold text-white flex items-center gap-2">✂️ PageSlicer</h3>
        <p className="text-sm text-zinc-400">Burst multi-page PDFs into single-page documents or extract specific page ranges.</p>
      </div>

      {!file ? (
        <FileDropZone accept=".pdf" label="Drop PDF here to Split" onFiles={handleFile} />
      ) : (
        <div className="p-4 rounded-xl bg-zinc-900 border border-white/10 flex items-center justify-between">
          <div className="truncate">
            <p className="text-sm font-semibold text-white truncate">{file.name}</p>
            <p className="text-xs text-zinc-400">{pageCount !== null ? `${pageCount} Pages` : 'PDF Ready'}</p>
          </div>
          <button onClick={() => { setFile(null); setPageCount(null); }} className="text-xs text-red-400 hover:underline">Change File</button>
        </div>
      )}

      <div className="grid grid-cols-2 gap-4">
        <button
          onClick={() => setMode('all')}
          className={`p-4 rounded-2xl border text-left transition-all ${
            mode === 'all'
              ? 'bg-purple-900/30 border-purple-500/60 shadow-[0_0_20px_rgba(168,85,247,0.2)]'
              : 'bg-zinc-900/50 border-white/10 hover:border-white/20'
          }`}
        >
          <div className="text-lg">📦 Split All Pages</div>
          <div className="text-xs text-zinc-400 mt-1">Export each page into an individual PDF packed in a ZIP archive.</div>
        </button>

        <button
          onClick={() => setMode('range')}
          className={`p-4 rounded-2xl border text-left transition-all ${
            mode === 'range'
              ? 'bg-purple-900/30 border-purple-500/60 shadow-[0_0_20px_rgba(168,85,247,0.2)]'
              : 'bg-zinc-900/50 border-white/10 hover:border-white/20'
          }`}
        >
          <div className="text-lg">🎯 Extract Page Range</div>
          <div className="text-xs text-zinc-400 mt-1">Extract a custom interval (e.g. pages 2 to 5) as a standalone PDF.</div>
        </button>
      </div>

      {mode === 'range' && (
        <div className="flex items-center gap-4 bg-zinc-900/40 p-4 rounded-xl border border-white/5">
          <div className="flex-1">
            <label className="text-xs text-zinc-400 block mb-1">Start Page</label>
            <input
              type="number"
              min={1}
              max={pageCount || 999}
              value={startPage}
              onChange={(e) => setStartPage(parseInt(e.target.value) || 1)}
              className="w-full bg-zinc-900 border border-white/20 rounded-xl px-3 py-2 text-sm text-white"
            />
          </div>
          <div className="flex-1">
            <label className="text-xs text-zinc-400 block mb-1">End Page</label>
            <input
              type="number"
              min={startPage}
              max={pageCount || 999}
              value={endPage}
              onChange={(e) => setEndPage(parseInt(e.target.value) || 1)}
              className="w-full bg-zinc-900 border border-white/20 rounded-xl px-3 py-2 text-sm text-white"
            />
          </div>
        </div>
      )}

      <button
        onClick={handleSplit}
        disabled={loading || !file}
        className="w-full py-3.5 rounded-xl font-medium text-white bg-gradient-to-r from-sky-600 to-blue-600 hover:from-sky-500 hover:to-blue-500 disabled:opacity-50 transition-all shadow-lg shadow-sky-900/30 flex items-center justify-center gap-2"
      >
        {loading ? <Spinner /> : '✂️ Execute Slice & Download'}
      </button>
    </div>
  );
}

// ---------------------------------------------------------------------------
// 3. PAGEFORGE (ORGANIZER)
// ---------------------------------------------------------------------------
function OrganizerWorkspace({ setLoading, loading, setError, setSuccess }: any) {
  const [file, setFile] = useState<File | null>(null);
  const [action, setAction] = useState<'rotate' | 'reorder' | 'numbers'>('rotate');
  const [angle, setAngle] = useState(90);
  const [customPages, setCustomPages] = useState('');
  const [orderStr, setOrderStr] = useState('');
  const [deletePages, setDeletePages] = useState('');
  const [reverse, setReverse] = useState(false);
  const [numberTemplate, setNumberTemplate] = useState('Page {page} of {total}');

  const handleAction = async () => {
    if (!file) {
      setError('Upload a PDF file first.');
      return;
    }
    setLoading(true);
    setError(null);
    try {
      let res: Response;
      if (action === 'rotate') {
        res = await uploadFile('/api/organizer/rotate', file, {
          angle,
          target_mode: customPages ? 'custom' : 'all',
          custom_pages: customPages,
        });
        await downloadFromResponse(res, 'rotated.pdf');
        setSuccess('Rotated pages successfully!');
      } else if (action === 'reorder') {
        res = await uploadFile('/api/organizer/reorder', file, {
          order_str: orderStr,
          delete_pages: deletePages,
          reverse: String(reverse),
        });
        await downloadFromResponse(res, 'reordered.pdf');
        setSuccess('Reordered/deleted pages successfully!');
      } else {
        res = await uploadFile('/api/organizer/page-numbers', file, {
          template: numberTemplate,
          position: 'bottom_center',
          font_size: 10,
          margin: 30,
        });
        await downloadFromResponse(res, 'numbered.pdf');
        setSuccess('Stamped dynamic page numbers successfully!');
      }
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="border-b border-white/10 pb-4">
        <h3 className="text-xl font-bold text-white flex items-center gap-2">🔄 PageForge</h3>
        <p className="text-sm text-zinc-400">Rotate orientation, reorder sequence, discard pages, or stamp pagination.</p>
      </div>

      {!file ? (
        <FileDropZone accept=".pdf" label="Drop PDF here to Organize" onFiles={(f) => setFile(f[0])} />
      ) : (
        <div className="p-4 rounded-xl bg-zinc-900 border border-white/10 flex items-center justify-between">
          <p className="text-sm font-semibold text-white truncate">{file.name}</p>
          <button onClick={() => setFile(null)} className="text-xs text-red-400 hover:underline">Change File</button>
        </div>
      )}

      <div className="flex gap-2 p-1 bg-zinc-900 rounded-xl border border-white/10">
        {(['rotate', 'reorder', 'numbers'] as const).map((tab) => (
          <button
            key={tab}
            onClick={() => setAction(tab)}
            className={`flex-1 py-2 text-sm font-medium rounded-lg capitalize transition-all ${
              action === tab ? 'bg-purple-600 text-white shadow-md' : 'text-zinc-400 hover:text-white'
            }`}
          >
            {tab === 'numbers' ? 'Page Numbers' : tab}
          </button>
        ))}
      </div>

      {action === 'rotate' && (
        <div className="space-y-4">
          <div className="flex gap-3">
            {[90, 180, 270].map((deg) => (
              <button
                key={deg}
                onClick={() => setAngle(deg)}
                className={`flex-1 py-3 rounded-xl border text-sm font-medium ${
                  angle === deg ? 'border-purple-500 bg-purple-900/30 text-white' : 'border-white/10 text-zinc-400 hover:border-white/20'
                }`}
              >
                Rotate {deg}° CW
              </button>
            ))}
          </div>
          <div>
            <label className="text-xs text-zinc-400 block mb-1">Target Pages (Leave empty for All Pages)</label>
            <input
              type="text"
              placeholder="e.g. 1, 3-5, 8"
              value={customPages}
              onChange={(e) => setCustomPages(e.target.value)}
              className="w-full bg-zinc-900 border border-white/20 rounded-xl px-3 py-2 text-sm text-white"
            />
          </div>
        </div>
      )}

      {action === 'reorder' && (
        <div className="space-y-4">
          <div>
            <label className="text-xs text-zinc-400 block mb-1">New Page Order (comma-separated or empty to keep)</label>
            <input
              type="text"
              placeholder="e.g. 3, 1, 2, 4"
              value={orderStr}
              onChange={(e) => setOrderStr(e.target.value)}
              className="w-full bg-zinc-900 border border-white/20 rounded-xl px-3 py-2 text-sm text-white"
            />
          </div>
          <div>
            <label className="text-xs text-zinc-400 block mb-1">Pages to Discard / Delete</label>
            <input
              type="text"
              placeholder="e.g. 2, 5-7"
              value={deletePages}
              onChange={(e) => setDeletePages(e.target.value)}
              className="w-full bg-zinc-900 border border-white/20 rounded-xl px-3 py-2 text-sm text-white"
            />
          </div>
          <label className="flex items-center gap-2 text-sm text-zinc-300 cursor-pointer">
            <input type="checkbox" checked={reverse} onChange={(e) => setReverse(e.target.checked)} className="rounded" />
            Reverse entire document order
          </label>
        </div>
      )}

      {action === 'numbers' && (
        <div className="space-y-4">
          <div>
            <label className="text-xs text-zinc-400 block mb-1">Pagination Format Template</label>
            <input
              type="text"
              value={numberTemplate}
              onChange={(e) => setNumberTemplate(e.target.value)}
              className="w-full bg-zinc-900 border border-white/20 rounded-xl px-3 py-2 text-sm text-white"
            />
            <p className="text-xs text-zinc-500 mt-1">Available placeholders: {'{page}'}, {'{total}'}</p>
          </div>
        </div>
      )}

      <button
        onClick={handleAction}
        disabled={loading || !file}
        className="w-full py-3.5 rounded-xl font-medium text-white bg-gradient-to-r from-pink-600 to-rose-600 hover:from-pink-500 hover:to-rose-500 disabled:opacity-50 transition-all shadow-lg shadow-pink-900/30 flex items-center justify-center gap-2"
      >
        {loading ? <Spinner /> : '🚀 Apply Transformations'}
      </button>
    </div>
  );
}

// ---------------------------------------------------------------------------
// 4. GUARDPDF (SECURITY)
// ---------------------------------------------------------------------------
function SecurityWorkspace({ setLoading, loading, setError, setSuccess }: any) {
  const [file, setFile] = useState<File | null>(null);
  const [subTool, setSubTool] = useState<'encrypt' | 'decrypt' | 'watermark' | 'metadata'>('encrypt');
  const [userPassword, setUserPassword] = useState('');
  const [decryptPassword, setDecryptPassword] = useState('');
  const [watermarkText, setWatermarkText] = useState('CONFIDENTIAL');
  const [watermarkColor, setWatermarkColor] = useState('gray');
  const [metadataInfo, setMetadataInfo] = useState<any>(null);

  const executeAction = async () => {
    if (!file) {
      setError('Upload a PDF file first.');
      return;
    }
    setLoading(true);
    setError(null);
    try {
      if (subTool === 'encrypt') {
        if (!userPassword) throw new Error('Enter a password to encrypt.');
        const res = await uploadFile('/api/security/encrypt', file, {
          user_password: userPassword,
          allow_printing: 'true',
          allow_copying: 'true',
        });
        await downloadFromResponse(res, 'protected.pdf');
        setSuccess('Document encrypted successfully!');
      } else if (subTool === 'decrypt') {
        if (!decryptPassword) throw new Error('Enter current password to unlock.');
        const res = await uploadFile('/api/security/decrypt', file, { password: decryptPassword });
        await downloadFromResponse(res, 'unlocked.pdf');
        setSuccess('Document unlocked & decrypted!');
      } else if (subTool === 'watermark') {
        const res = await uploadFile('/api/security/watermark', file, {
          text: watermarkText,
          opacity: 0.25,
          angle: 45,
          font_size: 42,
          color: watermarkColor,
        });
        await downloadFromResponse(res, 'watermarked.pdf');
        setSuccess('Watermark stamped successfully!');
      } else if (subTool === 'metadata') {
        const res = await uploadFile('/api/security/strip-metadata', file);
        await downloadFromResponse(res, 'sanitized.pdf');
        setSuccess('Metadata stripped & document sanitized!');
      }
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const inspectMetadata = async () => {
    if (!file) return;
    try {
      const res = await uploadFile('/api/security/metadata', file);
      if (res.ok) {
        const data = await res.json();
        setMetadataInfo(data);
      }
    } catch {
      // non-blocking
    }
  };

  return (
    <div className="space-y-6">
      <div className="border-b border-white/10 pb-4">
        <h3 className="text-xl font-bold text-white flex items-center gap-2">🔐 GuardPDF</h3>
        <p className="text-sm text-zinc-400">Military-grade password encryption, unlock, watermarks, and metadata sanitization.</p>
      </div>

      {!file ? (
        <FileDropZone accept=".pdf" label="Drop PDF here for Security Operations" onFiles={(f) => { setFile(f[0]); inspectMetadata(); }} />
      ) : (
        <div className="p-4 rounded-xl bg-zinc-900 border border-white/10 flex items-center justify-between">
          <p className="text-sm font-semibold text-white truncate">{file.name}</p>
          <button onClick={() => { setFile(null); setMetadataInfo(null); }} className="text-xs text-red-400 hover:underline">Change File</button>
        </div>
      )}

      <div className="grid grid-cols-4 gap-2 p-1 bg-zinc-900 rounded-xl border border-white/10">
        {(['encrypt', 'decrypt', 'watermark', 'metadata'] as const).map((t) => (
          <button
            key={t}
            onClick={() => setSubTool(t)}
            className={`py-2 text-xs md:text-sm font-medium rounded-lg capitalize transition-all ${
              subTool === t ? 'bg-red-600 text-white shadow-md' : 'text-zinc-400 hover:text-white'
            }`}
          >
            {t}
          </button>
        ))}
      </div>

      {subTool === 'encrypt' && (
        <div>
          <label className="text-xs text-zinc-400 block mb-1">Set Document Password</label>
          <input
            type="password"
            placeholder="Choose strong password"
            value={userPassword}
            onChange={(e) => setUserPassword(e.target.value)}
            className="w-full bg-zinc-900 border border-white/20 rounded-xl px-3 py-2 text-sm text-white"
          />
        </div>
      )}

      {subTool === 'decrypt' && (
        <div>
          <label className="text-xs text-zinc-400 block mb-1">Current Password to Unlock</label>
          <input
            type="password"
            placeholder="Enter password"
            value={decryptPassword}
            onChange={(e) => setDecryptPassword(e.target.value)}
            className="w-full bg-zinc-900 border border-white/20 rounded-xl px-3 py-2 text-sm text-white"
          />
        </div>
      )}

      {subTool === 'watermark' && (
        <div className="space-y-4">
          <div>
            <label className="text-xs text-zinc-400 block mb-1">Watermark Stamp Text</label>
            <input
              type="text"
              value={watermarkText}
              onChange={(e) => setWatermarkText(e.target.value)}
              className="w-full bg-zinc-900 border border-white/20 rounded-xl px-3 py-2 text-sm text-white"
            />
          </div>
          <div>
            <label className="text-xs text-zinc-400 block mb-1">Color Palette</label>
            <select
              value={watermarkColor}
              onChange={(e) => setWatermarkColor(e.target.value)}
              className="w-full bg-zinc-900 border border-white/20 rounded-xl px-3 py-2 text-sm text-white"
            >
              <option value="gray">Neutral Translucent Gray</option>
              <option value="red">High-Security Red</option>
              <option value="blue">Corporate Blue</option>
              <option value="green">Approval Emerald Green</option>
            </select>
          </div>
        </div>
      )}

      {subTool === 'metadata' && metadataInfo && (
        <div className="p-4 rounded-xl bg-zinc-900/50 border border-white/5 space-y-2 text-xs text-zinc-300">
          <p className="font-semibold text-zinc-100">Metadata In File:</p>
          <p>Author: {metadataInfo.author || 'None'}</p>
          <p>Creator / Producer: {metadataInfo.producer || metadataInfo.creator || 'None'}</p>
          <p>Created: {metadataInfo.creation_date || 'Unknown'}</p>
        </div>
      )}

      <button
        onClick={executeAction}
        disabled={loading || !file}
        className="w-full py-3.5 rounded-xl font-medium text-white bg-gradient-to-r from-red-600 to-rose-600 hover:from-red-500 hover:to-rose-500 disabled:opacity-50 transition-all shadow-lg shadow-red-900/30 flex items-center justify-center gap-2"
      >
        {loading ? <Spinner /> : `Execute ${subTool.toUpperCase()}`}
      </button>
    </div>
  );
}

// ---------------------------------------------------------------------------
// 5. PIXELRENDER (RASTERIZER)
// ---------------------------------------------------------------------------
function RasterWorkspace({ setLoading, loading, setError, setSuccess }: any) {
  const [file, setFile] = useState<File | null>(null);
  const [dpi, setDpi] = useState(150);
  const [fmt, setFmt] = useState('PNG');
  const [previews, setPreviews] = useState<any[]>([]);

  const handleFile = async (files: File[]) => {
    if (!files[0]) return;
    setFile(files[0]);
    // fetch thumbnail previews
    try {
      const res = await uploadFile('/api/raster/preview', files[0], { dpi: 72 });
      if (res.ok) {
        const data = await res.json();
        setPreviews(data.previews || []);
      }
    } catch {
      // preview fail non-critical
    }
  };

  const handleConvert = async () => {
    if (!file) return;
    setLoading(true);
    setError(null);
    try {
      const res = await uploadFile('/api/raster/convert', file, { dpi, output_format: fmt, quality: 85 });
      if (!res.ok) throw new Error('Raster conversion failed');
      await downloadFromResponse(res, `${file.name.replace('.pdf', '')}_images.zip`);
      setSuccess(`Rendered high-res ${fmt} archive successfully!`);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="border-b border-white/10 pb-4">
        <h3 className="text-xl font-bold text-white flex items-center gap-2">🖼️ PixelRender</h3>
        <p className="text-sm text-zinc-400">Export PDF pages into pristine PNG, JPEG, WEBP, or TIFF graphics at razor-sharp DPI.</p>
      </div>

      {!file ? (
        <FileDropZone accept=".pdf" label="Drop PDF here to Render as Images" onFiles={handleFile} />
      ) : (
        <div className="p-4 rounded-xl bg-zinc-900 border border-white/10 flex items-center justify-between">
          <p className="text-sm font-semibold text-white truncate">{file.name}</p>
          <button onClick={() => { setFile(null); setPreviews([]); }} className="text-xs text-red-400 hover:underline">Change File</button>
        </div>
      )}

      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="text-xs text-zinc-400 block mb-1">Resolution: {dpi} DPI</label>
          <input
            type="range"
            min={72}
            max={300}
            step={25}
            value={dpi}
            onChange={(e) => setDpi(parseInt(e.target.value))}
            className="w-full accent-indigo-500 cursor-pointer"
          />
          <div className="flex justify-between text-[10px] text-zinc-500 mt-1">
            <span>72 (Web)</span>
            <span>150 (Screen)</span>
            <span>300 (Print-Ready)</span>
          </div>
        </div>

        <div>
          <label className="text-xs text-zinc-400 block mb-1">Target Format</label>
          <select
            value={fmt}
            onChange={(e) => setFmt(e.target.value)}
            className="w-full bg-zinc-900 border border-white/20 rounded-xl px-3 py-2 text-sm text-white"
          >
            <option value="PNG">PNG (Lossless Sharp)</option>
            <option value="JPEG">JPEG (Compressed)</option>
            <option value="WEBP">WEBP (Modern Web)</option>
            <option value="TIFF">TIFF (Archival)</option>
          </select>
        </div>
      </div>

      {previews.length > 0 && (
        <div className="space-y-2">
          <p className="text-xs text-zinc-400 uppercase tracking-wider">Page Thumbnails ({previews.length})</p>
          <div className="grid grid-cols-4 md:grid-cols-6 gap-3 max-h-48 overflow-y-auto p-2 bg-zinc-900/40 rounded-xl border border-white/5">
            {previews.map((p, i) => (
              <div key={i} className="flex flex-col items-center">
                <img src={p.data_url} alt={`Page ${p.page}`} className="w-full h-auto rounded border border-white/10 shadow-sm" />
                <span className="text-[10px] text-zinc-400 mt-1">P. {p.page}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      <button
        onClick={handleConvert}
        disabled={loading || !file}
        className="w-full py-3.5 rounded-xl font-medium text-white bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 disabled:opacity-50 transition-all shadow-lg shadow-indigo-900/30 flex items-center justify-center gap-2"
      >
        {loading ? <Spinner /> : '🖼️ Render & Download Image ZIP'}
      </button>
    </div>
  );
}

// ---------------------------------------------------------------------------
// 6. DIFFVISION (COMPARATOR)
// ---------------------------------------------------------------------------
function DiffWorkspace({ setLoading, loading, setError, setSuccess }: any) {
  const [fileA, setFileA] = useState<File | null>(null);
  const [fileB, setFileB] = useState<File | null>(null);
  const [result, setResult] = useState<any>(null);

  const handleCompare = async () => {
    if (!fileA || !fileB) {
      setError('Please upload both Original (A) and Revised (B) PDF documents.');
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const res = await uploadTwoFiles('/api/diff/compare', fileA, fileB, { dpi: 100, threshold: 25 });
      if (!res.ok) throw new Error('Visual diff comparison failed');
      const data = await res.json();
      setResult(data);
      setSuccess(`Compared ${data.pages.length} pages. Overall similarity: ${data.overall_similarity}%`);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="border-b border-white/10 pb-4">
        <h3 className="text-xl font-bold text-white flex items-center gap-2">⚖️ DiffVision</h3>
        <p className="text-sm text-zinc-400">Side-by-side pixel differential engine highlighting text shifts, redactions, and edits.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="p-4 rounded-2xl bg-zinc-900/50 border border-white/10 space-y-2">
          <p className="text-xs uppercase font-semibold text-cyan-400">Document A (Original Baseline)</p>
          {!fileA ? (
            <FileDropZone accept=".pdf" label="Drop Baseline PDF" onFiles={(f) => setFileA(f[0])} />
          ) : (
            <div className="flex items-center justify-between text-sm text-white">
              <span className="truncate">{fileA.name}</span>
              <button onClick={() => setFileA(null)} className="text-xs text-red-400 hover:underline">Remove</button>
            </div>
          )}
        </div>

        <div className="p-4 rounded-2xl bg-zinc-900/50 border border-white/10 space-y-2">
          <p className="text-xs uppercase font-semibold text-pink-400">Document B (Revised Version)</p>
          {!fileB ? (
            <FileDropZone accept=".pdf" label="Drop Revised PDF" onFiles={(f) => setFileB(f[0])} />
          ) : (
            <div className="flex items-center justify-between text-sm text-white">
              <span className="truncate">{fileB.name}</span>
              <button onClick={() => setFileB(null)} className="text-xs text-red-400 hover:underline">Remove</button>
            </div>
          )}
        </div>
      </div>

      <button
        onClick={handleCompare}
        disabled={loading || !fileA || !fileB}
        className="w-full py-3.5 rounded-xl font-medium text-white bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 disabled:opacity-50 transition-all shadow-lg shadow-cyan-900/30 flex items-center justify-center gap-2"
      >
        {loading ? <Spinner /> : '🔍 Run Pixel Diff Comparison'}
      </button>

      {result && (
        <div className="space-y-4 pt-4 border-t border-white/10">
          <div className="flex items-center justify-between bg-zinc-900 p-4 rounded-xl border border-white/10">
            <div>
              <p className="text-xs text-zinc-400">Overall Visual Similarity</p>
              <p className="text-2xl font-bold text-white">{result.overall_similarity}%</p>
            </div>
            <div className="text-right text-xs text-zinc-400">
              <p>Doc A: {result.pages_a} Pages</p>
              <p>Doc B: {result.pages_b} Pages</p>
            </div>
          </div>

          <div className="space-y-4">
            {result.pages.map((p: any) => (
              <div key={p.page} className="bg-zinc-900/60 border border-white/5 p-4 rounded-2xl flex flex-col md:flex-row gap-4 items-center">
                <div className="w-full md:w-1/2">
                  <img src={p.composite_url} alt={`Diff Page ${p.page}`} className="w-full rounded-lg border border-white/10" />
                </div>
                <div className="w-full md:w-1/2 space-y-2">
                  <h4 className="text-lg font-bold text-white">Page {p.page}</h4>
                  <p className="text-sm text-zinc-300">Similarity: <span className="font-semibold text-emerald-400">{p.similarity}%</span></p>
                  <p className="text-sm text-zinc-300">Changed Area: <span className="font-semibold text-rose-400">{p.change}%</span> ({p.changed_pixels} pixels altered)</p>
                  <p className="text-xs text-zinc-500">Red highlights mark deletions or alterations; Green marks additions.</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

// ---------------------------------------------------------------------------
// 7. TEXTSCOPE (EXTRACTOR)
// ---------------------------------------------------------------------------
function ExtractorWorkspace({ setLoading, loading, setError, setSuccess }: any) {
  const [file, setFile] = useState<File | null>(null);
  const [mode, setMode] = useState<'native' | 'ocr'>('native');
  const [data, setData] = useState<any>(null);

  const handleExtract = async () => {
    if (!file) return;
    setLoading(true);
    setError(null);
    try {
      const res = await uploadFile('/api/extractor/extract', file, { mode });
      if (!res.ok) throw new Error('Extraction failed');
      const resData = await res.json();
      setData(resData);
      setSuccess(`Extracted ${resData.total_words} words across ${resData.total_pages} pages!`);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const copyText = () => {
    if (data?.plain_text) {
      navigator.clipboard.writeText(data.plain_text);
      setSuccess('Extracted text copied to clipboard!');
    }
  };

  return (
    <div className="space-y-6">
      <div className="border-b border-white/10 pb-4">
        <h3 className="text-xl font-bold text-white flex items-center gap-2">🔍 TextScope</h3>
        <p className="text-sm text-zinc-400">Extract high-fidelity digital text or run OCR computer vision on scanned PDFs.</p>
      </div>

      {!file ? (
        <FileDropZone accept=".pdf" label="Drop PDF here for Text Extraction" onFiles={(f) => setFile(f[0])} />
      ) : (
        <div className="p-4 rounded-xl bg-zinc-900 border border-white/10 flex items-center justify-between">
          <p className="text-sm font-semibold text-white truncate">{file.name}</p>
          <button onClick={() => { setFile(null); setData(null); }} className="text-xs text-red-400 hover:underline">Change File</button>
        </div>
      )}

      <div className="grid grid-cols-2 gap-4">
        <button
          onClick={() => setMode('native')}
          className={`p-4 rounded-xl border text-left ${mode === 'native' ? 'border-emerald-500 bg-emerald-900/30' : 'border-white/10 bg-zinc-900/50'}`}
        >
          <p className="text-sm font-bold text-white">⚡ Native Digital Text</p>
          <p className="text-xs text-zinc-400 mt-1">Instant vector text stream parsing with structure preservation.</p>
        </button>

        <button
          onClick={() => setMode('ocr')}
          className={`p-4 rounded-xl border text-left ${mode === 'ocr' ? 'border-emerald-500 bg-emerald-900/30' : 'border-white/10 bg-zinc-900/50'}`}
        >
          <p className="text-sm font-bold text-white">👁️ Tesseract OCR Vision</p>
          <p className="text-xs text-zinc-400 mt-1">Optical character recognition for scanned paperwork and photos.</p>
        </button>
      </div>

      <button
        onClick={handleExtract}
        disabled={loading || !file}
        className="w-full py-3.5 rounded-xl font-medium text-white bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 disabled:opacity-50 transition-all shadow-lg shadow-emerald-900/30 flex items-center justify-center gap-2"
      >
        {loading ? <Spinner /> : '🔍 Extract Full Document Text'}
      </button>

      {data && (
        <div className="space-y-4 pt-4 border-t border-white/10">
          <div className="grid grid-cols-3 gap-3">
            <div className="p-3 bg-zinc-900 rounded-xl border border-white/5 text-center">
              <p className="text-xs text-zinc-500">Words</p>
              <p className="text-lg font-bold text-white">{data.total_words}</p>
            </div>
            <div className="p-3 bg-zinc-900 rounded-xl border border-white/5 text-center">
              <p className="text-xs text-zinc-500">Characters</p>
              <p className="text-lg font-bold text-white">{data.total_chars}</p>
            </div>
            <div className="p-3 bg-zinc-900 rounded-xl border border-white/5 text-center">
              <p className="text-xs text-zinc-500">Est. Reading</p>
              <p className="text-lg font-bold text-white">{data.reading_time_mins} min</p>
            </div>
          </div>

          <div className="relative">
            <div className="flex justify-between items-center mb-2">
              <span className="text-xs text-zinc-400 uppercase tracking-wider">Extracted Content</span>
              <button onClick={copyText} className="text-xs text-emerald-400 hover:underline">📋 Copy Text</button>
            </div>
            <textarea
              readOnly
              rows={10}
              value={data.plain_text}
              className="w-full bg-zinc-950 border border-white/10 rounded-xl p-4 text-xs font-mono text-zinc-300 resize-none focus:outline-none"
            />
          </div>
        </div>
      )}
    </div>
  );
}

// ---------------------------------------------------------------------------
// 8. AUDIODOC (AUDIO NARRATOR)
// ---------------------------------------------------------------------------
function AudioWorkspace({ setLoading, loading, setError, setSuccess }: any) {
  const [file, setFile] = useState<File | null>(null);
  const [startPage, setStartPage] = useState(1);
  const [endPage, setEndPage] = useState(3);
  const [accent, setAccent] = useState('com');
  const [slow, setSlow] = useState(false);
  const [audioUrl, setAudioUrl] = useState<string | null>(null);

  const handleGenerate = async () => {
    if (!file) return;
    setLoading(true);
    setError(null);
    try {
      const res = await uploadFile('/api/audio/generate', file, {
        start_page: startPage,
        end_page: endPage,
        accent,
        slow: String(slow),
      });
      if (!res.ok) {
        const d = await res.json().catch(() => ({ detail: 'Audio synthesis failed' }));
        throw new Error(d.detail || 'Audio synthesis failed');
      }
      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      setAudioUrl(url);
      setSuccess('Speech audio synthesis complete! You can play or download below.');
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="border-b border-white/10 pb-4">
        <h3 className="text-xl font-bold text-white flex items-center gap-2">🎧 AudioDoc</h3>
        <p className="text-sm text-zinc-400">Synthesize document pages into clear spoken audio narration.</p>
      </div>

      {!file ? (
        <FileDropZone accept=".pdf" label="Drop PDF here for Audiobook Narration" onFiles={(f) => setFile(f[0])} />
      ) : (
        <div className="p-4 rounded-xl bg-zinc-900 border border-white/10 flex items-center justify-between">
          <p className="text-sm font-semibold text-white truncate">{file.name}</p>
          <button onClick={() => { setFile(null); setAudioUrl(null); }} className="text-xs text-red-400 hover:underline">Change File</button>
        </div>
      )}

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div>
          <label className="text-xs text-zinc-400 block mb-1">Start Page</label>
          <input
            type="number"
            min={1}
            value={startPage}
            onChange={(e) => setStartPage(parseInt(e.target.value) || 1)}
            className="w-full bg-zinc-900 border border-white/20 rounded-xl px-3 py-2 text-sm text-white"
          />
        </div>
        <div>
          <label className="text-xs text-zinc-400 block mb-1">End Page</label>
          <input
            type="number"
            min={startPage}
            value={endPage}
            onChange={(e) => setEndPage(parseInt(e.target.value) || 1)}
            className="w-full bg-zinc-900 border border-white/20 rounded-xl px-3 py-2 text-sm text-white"
          />
        </div>
        <div>
          <label className="text-xs text-zinc-400 block mb-1">Accent</label>
          <select
            value={accent}
            onChange={(e) => setAccent(e.target.value)}
            className="w-full bg-zinc-900 border border-white/20 rounded-xl px-3 py-2 text-sm text-white"
          >
            <option value="com">American (US)</option>
            <option value="co.uk">British (UK)</option>
            <option value="ca">Canadian</option>
            <option value="co.in">Indian</option>
            <option value="com.au">Australian</option>
          </select>
        </div>
        <div className="flex items-center pt-5">
          <label className="flex items-center gap-2 text-sm text-zinc-300 cursor-pointer">
            <input type="checkbox" checked={slow} onChange={(e) => setSlow(e.target.checked)} className="rounded" />
            Slow Pace
          </label>
        </div>
      </div>

      <button
        onClick={handleGenerate}
        disabled={loading || !file}
        className="w-full py-3.5 rounded-xl font-medium text-white bg-gradient-to-r from-violet-600 to-indigo-600 hover:from-violet-500 hover:to-indigo-500 disabled:opacity-50 transition-all shadow-lg shadow-violet-900/30 flex items-center justify-center gap-2"
      >
        {loading ? <Spinner /> : '🎧 Synthesize Audiobook MP3'}
      </button>

      {audioUrl && (
        <div className="p-4 rounded-xl bg-zinc-900 border border-white/10 space-y-3">
          <p className="text-sm font-semibold text-white">Audio Stream Ready</p>
          <audio controls src={audioUrl} className="w-full rounded" />
          <a
            href={audioUrl}
            download="narration.mp3"
            className="inline-block px-4 py-2 bg-violet-600 hover:bg-violet-500 text-white rounded-lg text-xs font-medium"
          >
            💾 Download Narration MP3
          </a>
        </div>
      )}
    </div>
  );
}

// ---------------------------------------------------------------------------
// 9. OPTICOMPRESS (COMPRESSOR)
// ---------------------------------------------------------------------------
function CompressorWorkspace({ setLoading, loading, setError, setSuccess }: any) {
  const [file, setFile] = useState<File | null>(null);
  const [quality, setQuality] = useState(65);
  const [targetKb, setTargetKb] = useState<string>('');

  const handleCompress = async () => {
    if (!file) return;
    setLoading(true);
    setError(null);
    try {
      const extra: any = { quality };
      if (targetKb && parseFloat(targetKb) > 0) {
        extra.target_size_kb = parseFloat(targetKb);
      }
      const res = await uploadFile('/api/compressor/compress', file, extra);
      if (!res.ok) throw new Error('Compression failed');
      const orig = res.headers.get('X-Original-Size');
      const comp = res.headers.get('X-Compressed-Size');
      const pct = res.headers.get('X-Saved-Percent');
      await downloadFromResponse(res, `compressed_${file.name}`);
      setSuccess(`Compressed successfully! Saved ${pct || '0'}% (From ${orig ? (parseInt(orig) / 1024).toFixed(0) : '?'} KB to ${comp ? (parseInt(comp) / 1024).toFixed(0) : '?'} KB)`);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="border-b border-white/10 pb-4">
        <h3 className="text-xl font-bold text-white flex items-center gap-2">🗜️ OptiCompress</h3>
        <p className="text-sm text-zinc-400">Reduce document & image weight with intelligent image sub-sampling and stream re-compression.</p>
      </div>

      {!file ? (
        <FileDropZone accept=".pdf,.png,.jpg,.jpeg,.webp" label="Drop PDF or Image to Compress" onFiles={(f) => setFile(f[0])} />
      ) : (
        <div className="p-4 rounded-xl bg-zinc-900 border border-white/10 flex items-center justify-between">
          <div>
            <p className="text-sm font-semibold text-white truncate">{file.name}</p>
            <p className="text-xs text-zinc-400">Original Size: {(file.size / 1024).toFixed(0)} KB</p>
          </div>
          <button onClick={() => setFile(null)} className="text-xs text-red-400 hover:underline">Change File</button>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label className="text-xs text-zinc-400 block mb-1">Quality Level: {quality}%</label>
          <input
            type="range"
            min={10}
            max={95}
            value={quality}
            onChange={(e) => setQuality(parseInt(e.target.value))}
            className="w-full accent-amber-500 cursor-pointer"
          />
          <div className="flex justify-between text-[10px] text-zinc-500 mt-1">
            <span>Aggressive (10%)</span>
            <span>Balanced (65%)</span>
            <span>Maximum Quality (95%)</span>
          </div>
        </div>

        <div>
          <label className="text-xs text-zinc-400 block mb-1">Exact Target File Size (KB - Optional)</label>
          <input
            type="number"
            placeholder="e.g. 500"
            value={targetKb}
            onChange={(e) => setTargetKb(e.target.value)}
            className="w-full bg-zinc-900 border border-white/20 rounded-xl px-3 py-2 text-sm text-white"
          />
        </div>
      </div>

      <button
        onClick={handleCompress}
        disabled={loading || !file}
        className="w-full py-3.5 rounded-xl font-medium text-white bg-gradient-to-r from-amber-600 to-orange-600 hover:from-amber-500 hover:to-orange-500 disabled:opacity-50 transition-all shadow-lg shadow-amber-900/30 flex items-center justify-center gap-2"
      >
        {loading ? <Spinner /> : '🗜️ Compress & Download'}
      </button>
    </div>
  );
}

// ---------------------------------------------------------------------------
// 10. TEXPUBLISH (LATEX)
// ---------------------------------------------------------------------------
function LatexWorkspace({ setLoading, loading, setError, setSuccess }: any) {
  const [sub, setSub] = useState<'convert' | 'math' | 'bibtex'>('convert');
  const [latexCode, setLatexCode] = useState('\\documentclass{article}\n\\begin{document}\nHello World from LaTeX!\n\\end{document}');
  const [targetFmt, setTargetFmt] = useState('docx');
  const [formula, setFormula] = useState('E = mc^2');
  const [formulaImg, setFormulaImg] = useState<string | null>(null);
  const [bibtexCode, setBibtexCode] = useState('@article{einstein1905,\n  author = {Albert Einstein},\n  title = {Zur Elektrodynamik bewegter Korper},\n  year = {1905}\n}');
  const [bibResult, setBibResult] = useState<any>(null);

  const handleConvertLatex = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await postForm('/api/latex/convert-latex', {
        content: latexCode,
        target_format: targetFmt,
      });
      if (!res.ok) throw new Error('LaTeX conversion failed');
      await downloadFromResponse(res, `converted.${targetFmt}`);
      setSuccess(`Converted LaTeX to ${targetFmt.toUpperCase()} successfully!`);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleRenderFormula = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await postForm('/api/latex/render-equation', {
        formula,
        fontsize: 28,
        dpi: 300,
        transparent: 'true',
      });
      if (!res.ok) throw new Error('Formula render failed');
      const blob = await res.blob();
      setFormulaImg(URL.createObjectURL(blob));
      setSuccess('Rendered math equation to high-res PNG!');
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleValidateBibtex = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await postForm('/api/latex/validate-bibtex', { bibtex: bibtexCode });
      if (!res.ok) throw new Error('BibTeX validation failed');
      const data = await res.json();
      setBibResult(data);
      setSuccess('BibTeX validated!');
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="border-b border-white/10 pb-4">
        <h3 className="text-xl font-bold text-white flex items-center gap-2">📝 TeXPublish</h3>
        <p className="text-sm text-zinc-400">LaTeX to Word & PDF converter, standalone formula rendering, and BibTeX validator.</p>
      </div>

      <div className="flex gap-2 p-1 bg-zinc-900 rounded-xl border border-white/10">
        {(['convert', 'math', 'bibtex'] as const).map((tab) => (
          <button
            key={tab}
            onClick={() => setSub(tab)}
            className={`flex-1 py-2 text-xs md:text-sm font-medium rounded-lg capitalize transition-all ${
              sub === tab ? 'bg-purple-600 text-white shadow-md' : 'text-zinc-400 hover:text-white'
            }`}
          >
            {tab === 'convert' ? 'Convert LaTeX' : tab === 'math' ? 'Equation Renderer' : 'BibTeX Validator'}
          </button>
        ))}
      </div>

      {sub === 'convert' && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <label className="text-xs text-zinc-400">LaTeX Source Code</label>
            <div className="flex items-center gap-2">
              <span className="text-xs text-zinc-400">Target:</span>
              <select
                value={targetFmt}
                onChange={(e) => setTargetFmt(e.target.value)}
                className="bg-zinc-900 border border-white/20 rounded-lg px-2 py-1 text-xs text-white"
              >
                <option value="docx">Microsoft Word (.docx)</option>
                <option value="pdf">Adobe PDF (.pdf)</option>
              </select>
            </div>
          </div>
          <textarea
            rows={8}
            value={latexCode}
            onChange={(e) => setLatexCode(e.target.value)}
            className="w-full bg-zinc-950 border border-white/10 rounded-xl p-3 font-mono text-xs text-zinc-200"
          />
          <button
            onClick={handleConvertLatex}
            disabled={loading}
            className="w-full py-3.5 rounded-xl font-medium text-white bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 disabled:opacity-50 transition-all shadow-lg shadow-purple-900/30 flex items-center justify-center gap-2"
          >
            {loading ? <Spinner /> : `Convert & Download ${targetFmt.toUpperCase()}`}
          </button>
        </div>
      )}

      {sub === 'math' && (
        <div className="space-y-4">
          <div>
            <label className="text-xs text-zinc-400 block mb-1">{"LaTeX Math Formula (e.g. \\int_0^\\infty e^{-x^2} dx)"}</label>
            <input
              type="text"
              value={formula}
              onChange={(e) => setFormula(e.target.value)}
              className="w-full bg-zinc-900 border border-white/20 rounded-xl px-3 py-2 text-sm text-white font-mono"
            />
          </div>
          <button
            onClick={handleRenderFormula}
            disabled={loading}
            className="w-full py-3 rounded-xl font-medium text-white bg-purple-600 hover:bg-purple-500"
          >
            {loading ? <Spinner /> : 'Render Equation'}
          </button>
          {formulaImg && (
            <div className="p-6 bg-zinc-950 rounded-2xl border border-white/10 flex flex-col items-center gap-4">
              <img src={formulaImg} alt="Rendered equation" className="max-h-28" />
              <a href={formulaImg} download="equation.png" className="text-xs text-purple-400 hover:underline">
                💾 Download Transparent PNG
              </a>
            </div>
          )}
        </div>
      )}

      {sub === 'bibtex' && (
        <div className="space-y-4">
          <label className="text-xs text-zinc-400 block">BibTeX Entry</label>
          <textarea
            rows={6}
            value={bibtexCode}
            onChange={(e) => setBibtexCode(e.target.value)}
            className="w-full bg-zinc-950 border border-white/10 rounded-xl p-3 font-mono text-xs text-zinc-200"
          />
          <button
            onClick={handleValidateBibtex}
            disabled={loading}
            className="w-full py-3 rounded-xl font-medium text-white bg-purple-600 hover:bg-purple-500"
          >
            {loading ? <Spinner /> : 'Validate Entry'}
          </button>
          {bibResult && (
            <div className={`p-4 rounded-xl border ${bibResult.valid ? 'bg-emerald-900/20 border-emerald-500/40 text-emerald-300' : 'bg-red-900/20 border-red-500/40 text-red-300'} text-xs space-y-1`}>
              <p className="font-semibold">{bibResult.valid ? '✅ Valid BibTeX Entry' : '❌ Validation Issues'}</p>
              {bibResult.type && <p>Type: {bibResult.type}</p>}
              {bibResult.citation_key && <p>Key: {bibResult.citation_key}</p>}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

// ---------------------------------------------------------------------------
// 11. OMNICONVERT (UNIVERSAL CONVERTER & RENAMER)
// ---------------------------------------------------------------------------
function DocMorphWorkspace({ setLoading, loading, setError, setSuccess }: any) {
  const [mode, setMode] = useState<'pdf2word' | 'word2pdf' | 'pdf2pdf'>('pdf2word');
  const [file, setFile] = useState<File | null>(null);
  const [customFilename, setCustomFilename] = useState<string>('');
  const [pdfMode, setPdfMode] = useState<string>('clean_flatten');
  const [lastConverted, setLastConverted] = useState<{ name: string; url: string; ext: string } | null>(null);

  // Auto-populate rename field when file is uploaded or mode changes
  useEffect(() => {
    if (file) {
      const base = file.name.replace(/\.[^/.]+$/, '');
      if (mode === 'pdf2word') setCustomFilename(`${base}_converted`);
      else if (mode === 'word2pdf') setCustomFilename(`${base}_converted`);
      else setCustomFilename(`${base}_clean`);
    } else {
      setCustomFilename('');
    }
  }, [file, mode]);

  const switchMode = (newMode: 'pdf2word' | 'word2pdf' | 'pdf2pdf') => {
    setMode(newMode);
    setFile(null);
    setLastConverted(null);
  };

  const targetExt = mode === 'pdf2word' ? 'docx' : 'pdf';
  const effectiveFilename = (customFilename.trim() ? customFilename.trim().replace(/\.[^/.]+$/, '') : 'document') + '.' + targetExt;

  const handleConvert = async () => {
    if (!file) {
      setError('Please select a file to convert.');
      return;
    }
    setLoading(true);
    setError(null);
    try {
      let endpoint = '';
      const extra: Record<string, string> = {
        output_filename: customFilename.trim() || file.name.replace(/\.[^/.]+$/, ''),
      };

      if (mode === 'pdf2word') {
        endpoint = '/api/convert/pdf-to-docx';
      } else if (mode === 'word2pdf') {
        endpoint = '/api/convert/docx-to-pdf';
      } else {
        endpoint = '/api/convert/pdf-to-pdf';
        extra.mode = pdfMode;
      }

      const res = await uploadFile(endpoint, file, extra);
      if (!res.ok) {
        const errData = await res.json().catch(() => ({ detail: 'Conversion failed' }));
        throw new Error(errData.detail || 'Conversion failed');
      }

      const blob = await res.blob();
      const disposition = res.headers.get('Content-Disposition');
      let outName = effectiveFilename;
      if (disposition) {
        const match = disposition.match(/filename="?([^"]+)"?/);
        if (match) outName = match[1];
      }

      const downloadUrl = URL.createObjectURL(blob);
      setLastConverted({
        name: outName,
        url: downloadUrl,
        ext: targetExt,
      });

      // Automatically trigger download
      const a = document.createElement('a');
      a.href = downloadUrl;
      a.download = outName;
      document.body.appendChild(a);
      a.click();
      a.remove();

      setSuccess(`File processed successfully and saved as "${outName}"!`);
    } catch (err: any) {
      setError(err.message || 'Conversion encountered an error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="border-b border-white/10 pb-4">
        <h3 className="text-xl font-bold text-white flex items-center gap-2">
          🔄 OmniConvert
          <span className="text-xs px-2.5 py-0.5 rounded-full bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
            PDF ⇄ WORD & RENAMER
          </span>
        </h3>
        <p className="text-xs text-zinc-400 mt-1">
          Seamlessly convert PDF documents to editable Microsoft Word (.docx), Word documents to PDF, or re-process & sanitize PDFs with custom file renaming.
        </p>
      </div>

      {/* Mode Selector Tabs */}
      <div className="flex flex-wrap gap-2 p-1.5 bg-black/40 border border-white/10 rounded-2xl">
        <button
          onClick={() => switchMode('pdf2word')}
          className={`flex-1 min-w-[140px] py-2.5 px-4 rounded-xl text-xs font-semibold transition-all flex items-center justify-center gap-2 ${
            mode === 'pdf2word'
              ? 'bg-gradient-to-r from-emerald-600 to-teal-600 text-white shadow-lg shadow-emerald-900/30'
              : 'text-zinc-400 hover:text-white hover:bg-white/5'
          }`}
        >
          📄 PDF ➔ Word (.docx)
        </button>
        <button
          onClick={() => switchMode('word2pdf')}
          className={`flex-1 min-w-[140px] py-2.5 px-4 rounded-xl text-xs font-semibold transition-all flex items-center justify-center gap-2 ${
            mode === 'word2pdf'
              ? 'bg-gradient-to-r from-blue-600 to-indigo-600 text-white shadow-lg shadow-blue-900/30'
              : 'text-zinc-400 hover:text-white hover:bg-white/5'
          }`}
        >
          📝 Word (.docx) ➔ PDF
        </button>
        <button
          onClick={() => switchMode('pdf2pdf')}
          className={`flex-1 min-w-[140px] py-2.5 px-4 rounded-xl text-xs font-semibold transition-all flex items-center justify-center gap-2 ${
            mode === 'pdf2pdf'
              ? 'bg-gradient-to-r from-purple-600 to-pink-600 text-white shadow-lg shadow-purple-900/30'
              : 'text-zinc-400 hover:text-white hover:bg-white/5'
          }`}
        >
          🛡️ Same PDF ➔ PDF
        </button>
      </div>

      {/* Upload Zone */}
      <div className="space-y-3">
        <label className="text-xs font-semibold text-zinc-300 flex items-center justify-between">
          <span>
            {mode === 'pdf2word' && 'Select PDF Document to Convert:'}
            {mode === 'word2pdf' && 'Select Microsoft Word (.docx) Document to Convert:'}
            {mode === 'pdf2pdf' && 'Select PDF Document to Re-Process / Standardize:'}
          </span>
          {file && (
            <span className="text-zinc-500 text-[11px]">
              {(file.size / 1024).toFixed(1)} KB
            </span>
          )}
        </label>
        <FileDropZone
          accept={mode === 'word2pdf' ? '.docx,.doc' : '.pdf'}
          onFiles={(files: File[]) => {
            if (files.length > 0) setFile(files[0]);
          }}
          label={
            mode === 'word2pdf'
              ? 'Drop a Word .docx document here, or click to browse'
              : 'Drop a PDF document here, or click to browse'
          }
        />
        {file && (
          <div className="p-3 bg-white/[0.04] border border-white/10 rounded-xl flex items-center justify-between text-xs">
            <div className="flex items-center gap-2 text-zinc-200 truncate">
              <span>{mode === 'word2pdf' ? '📝' : '📄'}</span>
              <span className="font-medium truncate">{file.name}</span>
            </div>
            <button
              onClick={() => setFile(null)}
              className="text-zinc-500 hover:text-red-400 ml-2"
            >
              ✕ Remove
            </button>
          </div>
        )}
      </div>

      {/* PDF to PDF Options */}
      {mode === 'pdf2pdf' && (
        <div className="p-4 bg-purple-950/20 border border-purple-500/20 rounded-2xl space-y-3">
          <label className="text-xs font-semibold text-purple-300 block">PDF Standardization Mode</label>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-2">
            {[
              { id: 'clean_flatten', label: '🛡️ Clean & Flatten', desc: 'Sanitizes syntax & flattens form fields' },
              { id: 'optimize', label: '⚡ Optimize Streams', desc: 'Compresses internal PDF data streams' },
              { id: 'flatten', label: '📄 Flatten Annotations', desc: 'Locks stamps & comments to page' },
            ].map((opt) => (
              <button
                key={opt.id}
                type="button"
                onClick={() => setPdfMode(opt.id)}
                className={`p-3 rounded-xl border text-left transition-all ${
                  pdfMode === opt.id
                    ? 'bg-purple-600/30 border-purple-400 text-white shadow-md shadow-purple-950/50'
                    : 'bg-black/30 border-white/5 text-zinc-400 hover:border-white/20'
                }`}
              >
                <p className="text-xs font-semibold">{opt.label}</p>
                <p className="text-[10px] text-zinc-400 mt-1">{opt.desc}</p>
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Custom File Rename Box */}
      <div className="p-4 bg-zinc-900/60 border border-white/10 rounded-2xl space-y-3">
        <div className="flex items-center justify-between">
          <label className="text-xs font-semibold text-zinc-200 flex items-center gap-1.5">
            ✏️ Custom Output File Name
            <span className="text-[10px] px-2 py-0.5 rounded-full bg-blue-500/20 text-blue-300 border border-blue-500/30">
              RENAME FEATURE
            </span>
          </label>
          <span className="text-[11px] text-zinc-400">
            Target extension: <span className="font-mono text-emerald-400 font-bold">.{targetExt}</span>
          </span>
        </div>

        <div className="relative flex items-center">
          <input
            type="text"
            value={customFilename}
            onChange={(e) => setCustomFilename(e.target.value)}
            placeholder={file ? file.name.replace(/\.[^/.]+$/, '') : 'Enter custom filename...'}
            className="w-full bg-zinc-950/80 border border-white/15 focus:border-purple-400 rounded-xl px-4 py-2.5 text-xs text-white placeholder-zinc-500 focus:outline-none transition-all pr-20 font-mono"
          />
          <span className="absolute right-3 text-xs font-mono font-bold text-zinc-400 bg-white/5 px-2 py-1 rounded">
            .{targetExt}
          </span>
        </div>

        {/* Live File Preview Badge */}
        <div className="flex items-center gap-2 text-[11px] text-zinc-400 bg-black/30 p-2.5 rounded-xl border border-white/5">
          <span className="text-zinc-500">Preview:</span>
          <span className="font-mono text-white font-medium bg-emerald-500/10 border border-emerald-500/20 px-2 py-0.5 rounded">
            {effectiveFilename}
          </span>
          <span className="text-zinc-500 text-[10px] ml-auto">
            Will automatically download with this exact name
          </span>
        </div>
      </div>

      {/* Action Button */}
      <button
        onClick={handleConvert}
        disabled={loading || !file}
        className={`w-full py-3.5 rounded-xl font-medium text-white transition-all shadow-lg flex items-center justify-center gap-2 disabled:opacity-40 disabled:cursor-not-allowed ${
          mode === 'pdf2word'
            ? 'bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 shadow-emerald-950/40'
            : mode === 'word2pdf'
            ? 'bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 shadow-blue-950/40'
            : 'bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-500 hover:to-pink-500 shadow-purple-950/40'
        }`}
      >
        {loading ? (
          <Spinner />
        ) : mode === 'pdf2word' ? (
          '🚀 Convert PDF to Word (.docx)'
        ) : mode === 'word2pdf' ? (
          '📄 Convert Word to PDF (.pdf)'
        ) : (
          '🛡️ Re-process & Save PDF'
        )}
      </button>

      {/* Download Result Card */}
      {lastConverted && (
        <div className="p-4 rounded-2xl bg-emerald-950/20 border border-emerald-500/30 flex items-center justify-between gap-4">
          <div className="space-y-1 truncate">
            <p className="text-xs font-semibold text-emerald-300 flex items-center gap-1.5">
              <span>✅</span> File Ready for Download
            </p>
            <p className="font-mono text-xs text-white truncate">{lastConverted.name}</p>
          </div>
          <a
            href={lastConverted.url}
            download={lastConverted.name}
            className="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white rounded-xl text-xs font-medium shrink-0 transition-all flex items-center gap-1.5 shadow-md shadow-emerald-900/40"
          >
            ⬇️ Download Again
          </a>
        </div>
      )}
    </div>
  );
}

function Spinner() {
  return (
    <svg className="animate-spin h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
    </svg>
  );
}
