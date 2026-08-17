export const navGroups = {
  developer: [
    { label: 'MVP', items: [
      { t: 'dashboard', l: 'Dashboard' }, { t: 'code', l: 'Code / Snippets' }, { t: 'problems', l: 'Problems' },
      { t: 'network', l: 'Network' }, { t: 'feed', l: 'Feed' },
    ]},
    { label: 'SkillGraph', items: [
      { t: 'projects', l: 'Projects' }, { t: 'skillgraph', l: 'SkillGraph' },
      { t: 'skills', l: 'Skills' }, { t: 'gaps', l: 'Skill Gaps' }, { t: 'roadmap', l: 'Roadmap' },
    ]},
    { label: 'Career', items: [{ t: 'jobs', l: 'Jobs' }, { t: 'applications', l: 'Applications' }] },
    { label: 'Verification', items: [{ t: 'verify', l: 'Verification' }, { t: 'passport', l: 'Skill Passport' }] },
    { label: '', items: [{ t: 'messages', l: 'Messages' }, { t: 'assessments', l: 'Assessments' }, { t: 'profile', l: 'Profile' }] },
  ],
  recruiter: [
    { label: 'Company', items: [
      { t: 'companyDashboard', l: 'Dashboard' }, { t: 'companyJobs', l: 'Jobs' },
      { t: 'companyCampaigns', l: 'Hiring Campaigns' }, { t: 'companyQuestions', l: 'Question Bank' },
    ]},
    { label: 'Hiring', items: [{ t: 'companyCandidates', l: 'Candidates' }, { t: 'companyInterviews', l: 'Interviews' }] },
    { label: 'Insights', items: [{ t: 'companyAnalytics', l: 'Analytics' }] },
    { label: '', items: [{ t: 'messages', l: 'Messages' }, { t: 'profile', l: 'Profile' }] },
  ],
  company: [
    { label: 'Company', items: [
      { t: 'companyDashboard', l: 'Dashboard' }, { t: 'companyJobs', l: 'Jobs' },
      { t: 'companyCampaigns', l: 'Hiring Campaigns' }, { t: 'companyQuestions', l: 'Question Bank' },
    ]},
    { label: 'Hiring', items: [{ t: 'companyCandidates', l: 'Candidates' }, { t: 'companyInterviews', l: 'Interviews' }] },
    { label: 'Insights', items: [{ t: 'companyAnalytics', l: 'Analytics' }] },
    { label: 'Admin', items: [{ t: 'companyTeam', l: 'Team' }] },
    { label: '', items: [{ t: 'messages', l: 'Messages' }, { t: 'profile', l: 'Profile' }] },
  ],
};

// route each nav "t" key maps to, per role
export const routeFor = {
  dashboard: '/app/dashboard', code: '/app/code', problems: '/app/problems',
  network: '/app/network', feed: '/app/feed', projects: '/app/projects',
  skillgraph: '/app/skillgraph', skills: '/app/skills', gaps: '/app/skill-gaps',
  roadmap: '/app/roadmap', jobs: '/app/jobs', applications: '/app/applications',
  verify: '/app/verify', passport: '/app/passport', messages: '/app/messages',
  assessments: '/app/assessments', profile: '/app/profile',
  companyDashboard: '/recruiter/dashboard', companyJobs: '/recruiter/jobs',
  companyCampaigns: '/recruiter/campaigns', companyQuestions: '/recruiter/questions',
  companyCandidates: '/recruiter/candidates', companyInterviews: '/recruiter/interviews',
  companyAnalytics: '/recruiter/analytics', companyTeam: '/recruiter/team',
};

export const roleHome = { developer: '/app/dashboard', recruiter: '/recruiter/dashboard', company: '/recruiter/dashboard' };
export const roleTitle = { developer: 'BACKEND DEVELOPER', recruiter: 'RECRUITER · TECHCORP', company: 'COMPANY ADMIN · TECHCORP' };
export const roleName = { developer: 'Rudrant Joshi', recruiter: 'Sarah Mehta', company: 'Arjun Shah' };
export const roleInitials = { developer: 'RJ', recruiter: 'SM', company: 'AS' };

export const companies = ['TechCorp', 'Nova Systems', 'CloudForge', 'AI Labs'];
