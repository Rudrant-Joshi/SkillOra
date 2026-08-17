import { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { PageHeader } from '../../components/ui/Primitives';
import CodeEditor from '../../components/editors/CodeEditor';
import { useDemoState } from '../../context/DemoStateContext';
import { useToast } from '../../context/ToastContext';
import { useConfirm } from '../../context/ConfirmContext';

const LANGS = ['JavaScript', 'Python', 'Java', 'C++', 'C', 'HTML', 'CSS', 'SQL'];

export default function SnippetForm() {
  const { id } = useParams();
  const { snippets, saveSnippet } = useDemoState();
  const navigate = useNavigate();
  const { showToast } = useToast();
  const confirm = useConfirm();
  const editing = id ? snippets.find((s) => s.id === id) : null;

  const [title, setTitle] = useState(editing?.title || '');
  const [desc, setDesc] = useState(editing?.desc || '');
  const [lang, setLang] = useState(editing?.lang || 'JavaScript');
  const [isPublic, setIsPublic] = useState(editing?.isPublic ?? true);
  const [code, setCode] = useState(editing?.code || '// start typing…\n');
  const [dirty, setDirty] = useState(false);

  useEffect(() => {
    setDirty(true);
  }, [title, desc, lang, isPublic, code]);

  const handleSave = () => {
    if (!title.trim()) {
      showToast('Give the snippet a title first', 'error');
      return;
    }
    const snippet = editing
      ? { ...editing, title, desc, lang, isPublic, code, updated: 'just now', versions: [{ v: (editing.versions[0]?.v || 0) + 1, msg: 'Updated snippet', time: 'just now' }, ...editing.versions] }
      : { id: `s${Date.now()}`, title, desc, lang, isPublic, code, created: 'just now', updated: 'just now', versions: [{ v: 1, msg: 'Initial version', time: 'just now' }] };
    saveSnippet(snippet);
    showToast(editing ? 'Snippet updated' : 'Snippet created');
    navigate(`/app/code/snippets/${snippet.id}`);
  };

  const handleCancel = async () => {
    if (dirty) {
      const ok = await confirm({ title: 'Discard changes?', message: 'Unsaved changes to this snippet will be lost.', confirmLabel: 'DISCARD' });
      if (!ok) return;
    }
    navigate('/app/code');
  };

  return (
    <div>
      <PageHeader title={editing ? 'Edit Snippet' : 'Create Snippet'} subtitle="Reusable code editor component — also used by Problem Solver." />
      <div className="grid grid-cols-1 lg:grid-cols-[1fr_260px] gap-6">
        <div>
          <div className="field-label">Title</div>
          <input className="field-input" value={title} onChange={(e) => setTitle(e.target.value)} placeholder="e.g. REST API Authentication" />
          <div className="field-label">Description</div>
          <input className="field-input" value={desc} onChange={(e) => setDesc(e.target.value)} placeholder="What does this snippet do?" />
          <CodeEditor value={code} onChange={setCode} language={lang} originalValue={editing?.code} />
        </div>
        <div className="card-flat h-fit">
          <div className="eyebrow">Language</div>
          <select className="field-input mt-2" value={lang} onChange={(e) => setLang(e.target.value)}>
            {LANGS.map((l) => (
              <option key={l}>{l}</option>
            ))}
          </select>
          <div className="divider-dim" />
          <div className="eyebrow">Visibility</div>
          <div className="flex gap-2 mt-2">
            <button
              className={`btn-small flex-1 justify-center ${isPublic ? 'active' : ''}`}
              onClick={() => setIsPublic(true)}
              type="button"
            >
              PUBLIC
            </button>
            <button
              className={`btn-small flex-1 justify-center ${!isPublic ? 'active' : ''}`}
              onClick={() => setIsPublic(false)}
              type="button"
            >
              PRIVATE
            </button>
          </div>
          <div className="mono dim text-[10px] mt-2.5 leading-relaxed text-textDim">
            {isPublic ? 'Public snippets appear on your profile and in the activity feed.' : 'Private snippets are only visible to you.'}
          </div>
          <div className="divider-dim" />
          <button className="btn-primary w-full justify-center" onClick={handleSave} type="button">
            SAVE SNIPPET
          </button>
          <button className="btn-secondary w-full justify-center mt-2.5" onClick={handleCancel} type="button">
            CANCEL
          </button>
        </div>
      </div>
    </div>
  );
}
