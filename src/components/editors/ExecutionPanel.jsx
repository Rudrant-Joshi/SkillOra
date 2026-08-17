import { useState } from 'react';
import { AnimatePresence, motion } from 'framer-motion';
import { evaluateMockSubmission } from '../../data/code';

const STAGES = {
  run: [
    { status: 'QUEUED', delay: 0, text: 'Queued — DEMO EXECUTION…' },
    { status: 'RUNNING', delay: 350, text: 'Running against public tests — DEMO EXECUTION…' },
  ],
  submit: [
    { status: 'QUEUED', delay: 0, text: 'Queued for judging — DEMO EXECUTION (no backend connected)…' },
    { status: 'CHECKING TESTS', delay: 400, text: 'Checking test cases — DEMO EXECUTION…' },
  ],
};

/**
 * Drives the QUEUED -> RUNNING/CHECKING -> COMPLETED mock pipeline and
 * reports a final ExecutionResult. All timers are cleaned up if the
 * component unmounts mid-run.
 */
export function useExecution() {
  const [state, setState] = useState({ status: 'IDLE', result: null, running: false });

  const run = (mode, code) => {
    const stages = STAGES[mode];
    setState({ status: stages[0].status, result: null, running: true, text: stages[0].text });
    const timers = [];
    stages.slice(1).forEach((s) => {
      timers.push(setTimeout(() => setState((prev) => ({ ...prev, status: s.status, text: s.text })), s.delay));
    });
    timers.push(
      setTimeout(() => {
        const r = evaluateMockSubmission(code);
        setState({ status: r.status.toUpperCase().replace('_', ' '), result: r, running: false, text: '' });
      }, mode === 'submit' ? 1000 : 900)
    );
    return () => timers.forEach(clearTimeout);
  };

  return { ...state, run };
}

export function ExecutionResult({ result, status, text, mode = 'run' }) {
  return (
    <div className="min-h-[60px]">
      <AnimatePresence mode="wait">
        {text && (
          <motion.div key="pending" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="mono dim text-xs text-textDim">
            {text}
          </motion.div>
        )}
        {result && (
          <motion.div key="result" initial={{ opacity: 0, y: 6 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.25 }}>
            {result.status === 'accepted' ? (
              <>
                <div className="badge strong">◆ {mode === 'submit' ? 'ACCEPTED — ALL TEST CASES PASSED' : 'PASSED PUBLIC TESTS'} · DEMO EXECUTION</div>
                <div className="flex flex-col gap-1.5 mt-3">
                  <TestRow label="Test 1" pass />
                  <TestRow label="Test 2" pass />
                  {mode === 'submit' && <TestRow label="Hidden Tests" value="3 / 3 PASSED" pass />}
                  {mode === 'submit' && (
                    <>
                      <TestRow label="Runtime" value={result.runtime} />
                      <TestRow label="Memory" value={result.memory} />
                    </>
                  )}
                </div>
              </>
            ) : result.status === 'wrong' ? (
              <>
                <div className="badge" style={{ borderColor: '#fff' }}>✕ WRONG ANSWER · DEMO EXECUTION</div>
                <div className="flex flex-col gap-1.5 mt-3">
                  <TestRow label="Test 1" pass />
                  <TestRow label="Test 2" value="FAILED" />
                  {mode === 'submit' && <TestRow label="Hidden Tests" value="1 / 3 PASSED" />}
                </div>
                <div className="mono dim text-[10px] mt-2 text-textDim">{result.error}</div>
              </>
            ) : (
              <>
                <div className="badge" style={{ borderColor: '#fff' }}>
                  ⚠ {result.status === 'compile_error' ? 'COMPILATION ERROR' : 'RUNTIME ERROR'} · DEMO EXECUTION
                </div>
                <div className="mono dim text-[11px] mt-2.5 whitespace-pre-wrap text-textDim">{result.error}</div>
              </>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

function TestRow({ label, value, pass }) {
  return (
    <div className="test-row">
      <span>{label}</span>
      <span className={pass ? 'text-green' : 'dim text-textDim'}>{value || (pass ? 'PASSED' : '')}</span>
    </div>
  );
}
