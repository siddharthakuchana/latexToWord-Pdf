'use client';

import { useCallback, useRef, useState } from 'react';

interface FileDropZoneProps {
  accept?: string;
  multiple?: boolean;
  label?: string;
  sublabel?: string;
  onFiles: (files: File[]) => void;
  children?: React.ReactNode;
}

export default function FileDropZone({
  accept = '.pdf',
  multiple = false,
  label = 'Drop your file here',
  sublabel = 'or click to browse',
  onFiles,
  children,
}: FileDropZoneProps) {
  const [dragging, setDragging] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragging(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragging(false);
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragging(false);
    const files = Array.from(e.dataTransfer.files);
    if (files.length > 0) onFiles(files);
  }, [onFiles]);

  const handleClick = () => inputRef.current?.click();

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || []);
    if (files.length > 0) onFiles(files);
    e.target.value = '';
  };

  return (
    <div
      onClick={handleClick}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
      className={`
        relative cursor-pointer rounded-2xl border-2 border-dashed p-8
        flex flex-col items-center justify-center gap-3
        transition-all duration-300 min-h-[180px]
        ${dragging
          ? 'border-purple-500 bg-purple-500/10 scale-[1.02]'
          : 'border-white/10 bg-white/[0.02] hover:border-white/20 hover:bg-white/[0.04]'
        }
      `}
    >
      <input
        ref={inputRef}
        type="file"
        accept={accept}
        multiple={multiple}
        onChange={handleChange}
        className="hidden"
      />

      {children || (
        <>
          <div className={`text-4xl transition-transform duration-300 ${dragging ? 'scale-125' : ''}`}>
            📄
          </div>
          <div className="text-center">
            <p className="text-sm font-semibold text-white/80">{label}</p>
            <p className="text-xs text-white/40 mt-1">{sublabel}</p>
          </div>
        </>
      )}
    </div>
  );
}
