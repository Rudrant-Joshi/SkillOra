import { Modal } from '../ui/Overlay';

export default function VerifyModal({ open, onClose }) {
  return (
    <Modal open={open} onClose={onClose} width={460}>
      <div className="text-center border-2 border-green -m-8 p-9">
        <div className="mono dim text-[10px] tracking-[3px] text-textDim">PUBLIC VERIFICATION</div>
        <div className="h-display text-2xl mt-3">RUDRANT JOSHI</div>
        <div className="mono dim text-xs mt-1 text-textDim">BACKEND DEVELOPER</div>
        <div className="h-display text-green text-5xl mt-6">82%</div>
        <div className="eyebrow mt-1">SKILL CONFIDENCE</div>
        <div className="badge strong mt-5">◆ VERIFIED BY SKILLGRAPH</div>
        <button className="btn-secondary w-full justify-center mt-7" onClick={onClose}>
          CLOSE PREVIEW
        </button>
      </div>
    </Modal>
  );
}
