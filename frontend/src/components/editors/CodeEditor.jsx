import { useRef, useState } from 'react';
import Editor from '@monaco-editor/react';
import { Copy, RotateCcw, Check } from 'lucide-react';
import { monacoLangMap } from '../../data/code';

/**
 * Reusable Monaco editor used by Snippets, Problem Solver, and Exam coding
 * questions. Handles its own dispose lifecycle via @monaco-editor/react
 * (which unmounts/remounts safely — no manual editor.dispose() bookkeeping
 * needed like the vanilla-JS version had to do by hand).
 */
export default function CodeEditor({
  value,
  onChange,
  language = 'JavaScript',
  height = 320,
  originalValue,
  readOnly = false,
  showToolbar = true,
}) {
  const editorRef = useRef(null);
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(editorRef.current?.getValue() ?? value ?? '');
      setCopied(true);
      setTimeout(() => setCopied(false), 1200);
    } catch {
      /* clipboard may be unavailable in sandboxed iframes — fail silently */
    }
  };

  const handleReset = () => onChange?.(originalValue ?? '');

  return (
    <div className="border border-borderDim bg-surface mt-1.5">
      {showToolbar && (
        <div className="flex justify-between items-center px-3 py-2 border-b border-borderDim text-[10px] text-textDim tracking-widest uppercase">
          <span>{language} · MONACO EDITOR</span>
          <div className="flex gap-3">
            <button onClick={handleCopy} className="flex items-center gap-1 hover:text-white transition-colors" type="button">
              {copied ? <Check size={12} /> : <Copy size={12} />} {copied ? 'COPIED' : 'COPY'}
            </button>
            {onChange && (
              <button onClick={handleReset} className="flex items-center gap-1 hover:text-white transition-colors" type="button">
                <RotateCcw size={12} /> RESET
              </button>
            )}
          </div>
        </div>
      )}
      <Editor
        height={height}
        language={monacoLangMap[language] || 'javascript'}
        theme="vs-dark"
        value={value}
        onChange={(v) => onChange?.(v ?? '')}
        onMount={(editor) => (editorRef.current = editor)}
        options={{
          readOnly,
          fontFamily: '"Space Mono", monospace',
          fontSize: 13,
          minimap: { enabled: height > 240 },
          wordWrap: 'on',
          folding: true,
          bracketPairColorization: { enabled: true },
          automaticLayout: true,
          scrollBeyondLastLine: false,
        }}
      />
    </div>
  );
}
