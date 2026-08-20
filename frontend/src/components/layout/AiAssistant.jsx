import { useEffect, useRef, useState } from 'react';
import { AnimatePresence, motion } from 'framer-motion';
import { Bot, Send, Sparkles, X } from 'lucide-react';
import { press, ease } from '../../lib/motion';
import { useReducedMotion } from '../../hooks/useReducedMotion';

const GREETING = {
  role: 'ai',
  text: "Hey, I'm your SkillGraph copilot. Ask me about your skills, projects, roadmap or job matches.",
};

/**
 * Canned/local response engine. No backend is wired yet — this keeps the
 * widget fully functional on the frontend while the real assistant API
 * is connected later. Swap `getReply` for a real API call when ready.
 */
function getReply(input) {
  const q = input.toLowerCase();
  if (/skill|gap/.test(q)) {
    return "Head to Skill Gaps to see where you're behind the roles you're targeting, and Roadmap for a suggested learning order.";
  }
  if (/project/.test(q)) {
    return 'You can import a repo from Projects → Import, or open X-Ray on an existing project to see its detected stack and depth score.';
  }
  if (/job|application|interview/.test(q)) {
    return 'Check the Jobs tab for matches ranked against your SkillGraph, and Applications to track where each one stands.';
  }
  if (/code|snippet|problem/.test(q)) {
    return 'The Code and Problems sections let you save snippets and practice problems with the built-in editor and runner.';
  }
  if (/passport|verify/.test(q)) {
    return 'Verify lets peers or mentors confirm specific skills, and Passport bundles your verified skills into a shareable profile.';
  }
  if (/hi|hello|hey/.test(q)) {
    return "Hey! What are you working on right now — skills, projects, or job search?";
  }
  return "Got it — I'm still a lightweight demo assistant, so I can point you to the right part of SkillGraph rather than reason deeply yet. Try asking about skills, projects, jobs, or your roadmap.";
}

export default function AiAssistant() {
  const [open, setOpen] = useState(false);
  const [messages, setMessages] = useState([GREETING]);
  const [input, setInput] = useState('');
  const [typing, setTyping] = useState(false);
  const scrollRef = useRef(null);
  const inputRef = useRef(null);
  const reduced = useReducedMotion();

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, typing]);

  useEffect(() => {
    if (open) {
      const t = setTimeout(() => inputRef.current?.focus(), 250);
      return () => clearTimeout(t);
    }
  }, [open]);

  function send() {
    const text = input.trim();
    if (!text) return;
    setMessages((m) => [...m, { role: 'user', text }]);
    setInput('');
    setTyping(true);
    const delay = 500 + Math.random() * 500;
    setTimeout(() => {
      setTyping(false);
      setMessages((m) => [...m, { role: 'ai', text: getReply(text) }]);
    }, delay);
  }

  function onKeyDown(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      send();
    }
  }

  return (
    <div className="fixed bottom-[22px] right-5 sm:bottom-[22px] sm:right-8 z-[110] flex flex-col items-end">
      <AnimatePresence>
        {open && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 8 }}
            transition={{ duration: 0.18, ease: ease.out }}
            className="mb-4 w-[92vw] max-w-[360px] h-[480px] max-h-[70vh] bg-black border border-zinc-700 flex flex-col shadow-[0_24px_48px_-12px_rgba(0,0,0,0.9),0_0_36px_-4px_rgba(57,255,20,0.2)] overflow-hidden"
          >
            {/* Header */}
            <div className="flex items-center justify-between px-4 py-3.5 border-b border-zinc-800 shrink-0 bg-surface/40">
              <div className="flex items-center gap-2.5 min-w-0">
                <motion.div
                  className="w-8 h-8 border border-green bg-black flex items-center justify-center shrink-0"
                  whileHover={{ rotate: [0, -10, 10, 0], scale: 1.15 }}
                  transition={{ duration: 0.3 }}
                >
                  <Bot size={16} className="text-green" />
                </motion.div>
                <div className="min-w-0">
                  <div className="text-[11px] tracking-[2px] uppercase text-white font-medium flex items-center gap-2">
                    AI Assistant
                    <motion.span
                      className="w-1.5 h-1.5 bg-green rounded-full inline-block"
                      animate={{ scale: [1, 1.4, 1], opacity: [0.6, 1, 0.6] }}
                      transition={{ duration: 1.5, repeat: Infinity }}
                    />
                  </div>
                  <div className="text-[10px] text-textDim tracking-wide truncate">SkillGraph Copilot</div>
                </div>
              </div>
              <motion.button
                type="button"
                aria-label="Close AI assistant"
                onClick={() => setOpen(false)}
                whileHover={{ rotate: 90, scale: 1.18, borderColor: '#fff', color: '#fff' }}
                whileTap={{ scale: 0.9 }}
                className="w-8 h-8 border border-borderDim flex items-center justify-center text-textDim hover:text-white shrink-0 transition-colors"
              >
                <X size={15} />
              </motion.button>
            </div>

            {/* Messages */}
            <div ref={scrollRef} className="flex-1 overflow-y-auto scrollbar-thin px-4 py-4 space-y-3">
              {messages.map((m, i) => (
                <motion.div
                  key={i}
                  initial={{ opacity: 0, y: 8, scale: 0.98 }}
                  animate={{ opacity: 1, y: 0, scale: 1 }}
                  transition={{ duration: 0.2 }}
                  className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <motion.div
                    whileHover={{ scale: 1.01 }}
                    className={`max-w-[85%] px-3 py-2 text-[12px] leading-relaxed transition-all ${
                      m.role === 'user'
                        ? 'bg-surface2 border border-borderDim text-white'
                        : 'bg-surface border border-green/40 hover:border-green/80 text-white shadow-[0_0_12px_rgba(57,255,20,0.1)]'
                    }`}
                  >
                    {m.role === 'ai' && (
                      <div className="text-green text-[9px] tracking-[1.5px] uppercase mb-1 font-semibold flex items-center gap-1.5">
                        <Sparkles size={11} className="text-green" /> AI
                      </div>
                    )}
                    {m.text}
                  </motion.div>
                </motion.div>
              ))}
              {typing && (
                <motion.div
                  initial={{ opacity: 0, y: 4 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="flex justify-start"
                >
                  <div className="bg-surface border border-green/40 px-3.5 py-2.5 flex items-center gap-1.5 shadow-[0_0_10px_rgba(57,255,20,0.15)]">
                    {[0, 1, 2].map((d) => (
                      <motion.span
                        key={d}
                        className="w-1.5 h-1.5 bg-green inline-block rounded-full"
                        animate={reduced ? {} : { y: [0, -4, 0], opacity: [0.3, 1, 0.3] }}
                        transition={{ duration: 0.8, repeat: Infinity, delay: d * 0.16 }}
                      />
                    ))}
                  </div>
                </motion.div>
              )}
            </div>

            {/* Input */}
            <div className="border-t border-borderDim p-3 flex items-center gap-2 shrink-0 bg-surface/30">
              <input
                ref={inputRef}
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={onKeyDown}
                type="text"
                placeholder="Ask the AI..."
                className="flex-1 bg-surface2 border border-borderDim px-3 py-2.5 text-[12px] text-white placeholder:text-textMute focus:outline-none focus:border-green focus:shadow-[0_0_10px_rgba(57,255,20,0.2)] transition-all"
              />
              <motion.button
                type="button"
                aria-label="Send message"
                onClick={() => {
                  if (input.trim()) {
                    send();
                  } else {
                    inputRef.current?.focus();
                  }
                }}
                whileHover={{ scale: 1.05, boxShadow: '0 0 16px rgba(57,255,20,0.75)' }}
                whileTap={{ scale: 0.95 }}
                className="w-10 h-10 bg-green text-black flex items-center justify-center shrink-0 shadow-[0_0_12px_rgba(57,255,20,0.4)] transition-all cursor-pointer font-bold select-none"
              >
                <Send size={16} strokeWidth={2.4} className="translate-x-[1px]" />
              </motion.button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Bubble toggle with continuous floating and hover animation */}
      <motion.button
        type="button"
        aria-label={open ? 'Close AI assistant' : 'Open AI assistant'}
        onClick={() => setOpen((o) => !o)}
        animate={
          reduced
            ? undefined
            : {
                y: [0, -3, 0],
                boxShadow: [
                  '0 10px 25px -4px rgba(57,255,20,0.45)',
                  '0 12px 35px -2px rgba(57,255,20,0.75)',
                  '0 10px 25px -4px rgba(57,255,20,0.45)',
                ],
              }
        }
        transition={{ duration: 3.4, repeat: Infinity, ease: 'easeInOut' }}
        whileHover={
          reduced
            ? undefined
            : {
                y: -6,
                boxShadow: '0 18px 36px -4px rgba(57,255,20,0.9), 0 0 50px rgba(57,255,20,0.5)',
                transition: { type: 'spring', stiffness: 450, damping: 18 },
              }
        }
        whileTap={{ y: -1, scale: 0.96 }}
        className={`relative w-14 h-14 rounded-full bg-green text-black flex items-center justify-center shrink-0 cursor-pointer outline-none focus:outline-none focus-visible:outline-none focus:ring-0 active:outline-none select-none transition-colors ${
          open ? 'border-0 border-transparent' : 'border-2 border-green'
        }`}
      >
        {/* Subtle radar wave pulse rings */}
        {!open && !reduced && (
          <>
            <motion.span
              className="absolute inset-0 rounded-full border border-green/35 pointer-events-none"
              animate={{ scale: [1, 1.45], opacity: [0.35, 0] }}
              transition={{ duration: 2.4, repeat: Infinity, ease: 'easeOut' }}
            />
            <motion.span
              className="absolute inset-0 rounded-full border border-green/20 pointer-events-none"
              animate={{ scale: [1, 1.65], opacity: [0.2, 0] }}
              transition={{ duration: 2.4, repeat: Infinity, ease: 'easeOut', delay: 1.2 }}
            />
          </>
        )}
        <AnimatePresence initial={false}>
          {open ? (
            <motion.div
              key="close"
              initial={{ opacity: 0, rotate: -45 }}
              animate={{ opacity: 1, rotate: 0 }}
              exit={{ opacity: 0, rotate: 45 }}
              transition={{ duration: 0.15 }}
              className="absolute inset-0 flex items-center justify-center text-black"
            >
              <X size={24} strokeWidth={2.5} />
            </motion.div>
          ) : (
            <motion.div
              key="open"
              initial={{ opacity: 0, rotate: 45 }}
              animate={{ opacity: 1, rotate: 0 }}
              exit={{ opacity: 0, rotate: -45 }}
              transition={{ duration: 0.15 }}
              className="absolute inset-0 flex items-center justify-center text-black"
            >
              <motion.div
                animate={{ rotate: [0, 8, -8, 0] }}
                transition={{ duration: 3.5, repeat: Infinity, ease: 'easeInOut' }}
                className="flex items-center justify-center"
              >
                <Sparkles size={24} strokeWidth={2.2} />
              </motion.div>
            </motion.div>
          )}
        </AnimatePresence>
      </motion.button>
    </div>
  );
}
