import { PageHeader, Card } from '../../components/ui/Primitives';
import { StaggerContainer, StaggerItem, Reveal } from '../../components/animations/Reveal';
import { AnimatedNumber } from '../../components/ui/AnimatedNumber';
import { useDemoState } from '../../context/DemoStateContext';
import { problemsData, badgeDefs } from '../../data/code';
import { roleName, roleTitle, roleInitials } from '../../data/roles';
import { useAuth } from '../../context/AuthContext';

export default function Profile() {
  const { snippets, solved, followingCount, network } = useDemoState();
  const { role } = useAuth();
  const solvedProblems = problemsData.filter((p) => solved.includes(p.id));
  const byDiff = { Easy: 0, Medium: 0, Hard: 0 };
  solvedProblems.forEach((p) => (byDiff[p.diff] += 1));
  const langs = [...new Set(snippets.map((s) => s.lang))];
  const publicSnippets = snippets.filter((s) => s.isPublic);
  const followers = network.filter((n) => n.following).length + 128;

  const earnedBadges = badgeDefs.filter((b) => b.check({ solved, snippets }));

  return (
    <div>
      <Reveal>
        <div className="flex items-center gap-4">
          <div className="w-16 h-16 bg-green text-black flex items-center justify-center h-display text-xl flex-shrink-0">{roleInitials[role]}</div>
          <div>
            <div className="h-display text-2xl">{roleName[role]}</div>
            <div className="dim text-xs mt-1 text-textDim">{roleTitle[role]}</div>
          </div>
        </div>
        <div className="divider" />
      </Reveal>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <Card>
          <div className="eyebrow">Problems Solved</div>
          <div className="big-num text-green text-3xl"><AnimatedNumber value={solved.length} /></div>
        </Card>
        <Card>
          <div className="eyebrow">Snippets</div>
          <div className="big-num text-3xl"><AnimatedNumber value={snippets.length} /></div>
        </Card>
        <Card>
          <div className="eyebrow">Followers</div>
          <div className="big-num text-3xl"><AnimatedNumber value={followers} /></div>
        </Card>
        <Card>
          <div className="eyebrow">Following</div>
          <div className="big-num text-3xl"><AnimatedNumber value={followingCount} /></div>
        </Card>
      </div>

      <div className="divider" />
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Reveal>
          <div className="card-flat">
            <div className="eyebrow">Problems By Difficulty</div>
            <div className="flex flex-col gap-2 mt-3">
              {Object.entries(byDiff).map(([k, v]) => (
                <div key={k} className="flex justify-between text-xs">
                  <span>{k}</span>
                  <span className="text-green">{v}</span>
                </div>
              ))}
            </div>
          </div>
        </Reveal>
        <Reveal delay={0.05}>
          <div className="card-flat">
            <div className="eyebrow">Languages</div>
            <div className="flex gap-1.5 flex-wrap mt-3">
              {langs.length ? langs.map((l) => <span key={l} className="tech-pill">{l}</span>) : <span className="dim text-xs text-textDim">No snippets yet</span>}
            </div>
          </div>
        </Reveal>
      </div>

      <div className="divider" />
      <div className="text-xs tracking-widest uppercase text-textDim mb-4">Badges</div>
      <StaggerContainer className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4">
        {badgeDefs.map((b) => {
          const earned = earnedBadges.includes(b);
          return (
            <StaggerItem key={b.id}>
              <div className={`card text-center ${earned ? '' : 'opacity-40'}`}>
                <div className={`text-lg ${earned ? 'text-green' : 'text-textMute'}`}>{earned ? '✓' : '○'}</div>
                <div className="h-display text-[11px] mt-2 leading-tight">{b.name}</div>
                <div className="text-textDim text-[10px] mt-1.5">{b.desc}</div>
              </div>
            </StaggerItem>
          );
        })}
      </StaggerContainer>

      <div className="divider" />
      <div className="text-xs tracking-widest uppercase text-textDim mb-4">Public Snippets</div>
      <StaggerContainer className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        {publicSnippets.length ? publicSnippets.map((s) => (
          <StaggerItem key={s.id}>
            <div className="card">
              <div className="h-display text-sm">{s.title}</div>
              <div className="tech-pill inline-block mt-2">{s.lang}</div>
            </div>
          </StaggerItem>
        )) : <div className="dim text-xs text-textDim">No public snippets yet.</div>}
      </StaggerContainer>
    </div>
  );
}
