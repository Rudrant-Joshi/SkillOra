import { useNavigate, useParams } from 'react-router-dom';
import { PageHeader, Button, EmptyState } from '../../components/ui/Primitives';
import CodeEditor from '../../components/editors/CodeEditor';
import { useDemoState } from '../../context/DemoStateContext';
import { useConfirm } from '../../context/ConfirmContext';
import { useToast } from '../../context/ToastContext';

export default function SnippetDetail() {
  const { id } = useParams();
  const { snippets, deleteSnippet, restoreSnippetVersion } = useDemoState();
  const navigate = useNavigate();
  const confirm = useConfirm();
  const { showToast } = useToast();
  const snippet = snippets.find((s) => s.id === id);

  if (!snippet) {
    return (
      <div>
        <PageHeader title="Snippet Not Found" />
        <EmptyState>This snippet doesn't exist (it may have been deleted).</EmptyState>
      </div>
    );
  }

  const handleDelete = async () => {
    const ok = await confirm({ title: 'Delete snippet?', message: `"${snippet.title}" will be permanently removed from your account.`, confirmLabel: 'DELETE' });
    if (!ok) return;
    deleteSnippet(snippet.id);
    showToast('Snippet deleted');
    navigate('/app/code');
  };

  return (
    <div>
      <PageHeader
        title={snippet.title}
        subtitle={snippet.desc}
        actions={
          <div className="flex gap-2.5">
            <Button to={`/app/code/snippets/${snippet.id}/edit`} tone="secondary">
              EDIT
            </Button>
            <Button tone="secondary" onClick={handleDelete}>
              DELETE
            </Button>
          </div>
        }
      />
      <div className="flex gap-1.5 mb-4">
        <span className="tech-pill">{snippet.lang}</span>
        <span className={`badge ${snippet.isPublic ? 'strong' : ''}`}>{snippet.isPublic ? 'PUBLIC' : 'PRIVATE'}</span>
      </div>

      <CodeEditor value={snippet.code} language={snippet.lang} readOnly height={360} />

      <div className="divider" />
      <div className="text-xs tracking-widest uppercase text-textDim mb-4">Version History</div>
      <div className="flex flex-col gap-2">
        {snippet.versions.map((v) => (
          <div key={v.v} className="skill-row cursor-default">
            <div>
              <div className="skill-name">v{v.v} — {v.msg}</div>
              <div className="text-textDim text-[10px] mt-1">{v.time}</div>
            </div>
            {v.v !== snippet.versions[0].v && (
              <button className="btn-small" onClick={() => restoreSnippetVersion(snippet.id, v.msg)}>
                RESTORE
              </button>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
