import { Modal } from '../ui/Overlay';
import { Button } from '../ui/Primitives';

export default function VerifyModal({ open, onClose }) {
  return (
    <Modal open={open} onClose={onClose} width={460}>
      <div className="text-center border border-white/20 bg-[#0a0a0a] shadow-[0_20px_50px_rgba(0,0,0,0.9)] -m-8 p-9">
        <div className="mono text-[10px] tracking-[3px] text-green font-bold uppercase">PUBLIC VERIFICATION</div>
        <div className="h-display text-2xl mt-3 text-white">RUDRANT JOSHI</div>
        <div className="mono text-xs mt-1 text-textDim">BACKEND & DISTRIBUTED SYSTEMS DEVELOPER</div>
        <div className="h-display text-green text-5xl mt-6 drop-shadow-[0_0_12px_rgba(57,255,20,0.3)]">82%</div>
        <div className="eyebrow mt-1 text-textDim">SKILL CONFIDENCE</div>
        <div className="badge strong mt-5">◆ VERIFIED BY SKILLGRAPH</div>
        <div className="mt-7">
          <Button tone="secondary" className="w-full justify-center" onClick={onClose}>
            CLOSE PREVIEW
          </Button>
        </div>
      </div>
    </Modal>
  );
}
