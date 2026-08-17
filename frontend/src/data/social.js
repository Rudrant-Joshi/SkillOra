export const jobsData = [
  { id: 'j1', title: 'Backend Engineer', company: 'TechCorp', loc: 'Remote', type: 'Full-time', match: 82, salary: '₹18–26L', posted: '2 days ago',
    req: [{ s: 'Python', have: 87, need: 70 }, { s: 'FastAPI', have: 82, need: 70 }, { s: 'PostgreSQL', have: 71, need: 60 }, { s: 'Docker', have: 43, need: 65 }, { s: 'Redis', have: 18, need: 50 }] },
  { id: 'j2', title: 'Full Stack Developer', company: 'Nova Systems', loc: 'Bengaluru · Hybrid', type: 'Full-time', match: 71, salary: '₹14–20L', posted: '5 days ago',
    req: [{ s: 'React', have: 82, need: 70 }, { s: 'Python', have: 87, need: 60 }, { s: 'SQL', have: 71, need: 60 }, { s: 'System Design', have: 51, need: 65 }] },
  { id: 'j3', title: 'AI Engineer', company: 'AI Labs', loc: 'Remote', type: 'Full-time', match: 64, salary: '₹22–30L', posted: '1 week ago',
    req: [{ s: 'Python', have: 87, need: 80 }, { s: 'System Design', have: 51, need: 70 }, { s: 'Testing', have: 48, need: 60 }] },
  { id: 'j4', title: 'DevOps Engineer', company: 'CloudForge', loc: 'Remote', type: 'Contract', match: 39, salary: '₹16–22L', posted: '3 days ago',
    req: [{ s: 'Docker', have: 43, need: 80 }, { s: 'Git', have: 91, need: 70 }, { s: 'System Design', have: 51, need: 60 }] },
];

export const applicationsData = [
  { job: 'Backend Engineer', company: 'TechCorp', applied: 'Aug 12', stage: 'Technical Assessment' },
  { job: 'Full Stack Developer', company: 'Nova Systems', applied: 'Aug 8', stage: 'Applied' },
  { job: 'AI Engineer', company: 'AI Labs', applied: 'Aug 2', stage: 'Interview' },
];

export const networkSeed = [
  { name: 'Priya Nair', role: 'Frontend Developer', skills: ['React', 'TypeScript', 'Next.js'], conf: 79, verified: 14, status: 'CONNECT', following: false },
  { name: 'Karan Mehta', role: 'DevOps Engineer', skills: ['Docker', 'Kubernetes', 'AWS'], conf: 85, verified: 20, status: 'PENDING', following: false },
  { name: 'Ananya Rao', role: 'AI/ML Engineer', skills: ['Python', 'PyTorch', 'MLOps'], conf: 88, verified: 22, status: 'CONNECTED', following: true },
  { name: 'Devesh Kumar', role: 'Backend Developer', skills: ['Java', 'Spring', 'SQL'], conf: 74, verified: 11, status: 'CONNECT', following: false },
  { name: 'Ishita Shah', role: 'Full Stack Developer', skills: ['React', 'Node.js', 'MongoDB'], conf: 81, verified: 16, status: 'CONNECT', following: true },
  { name: 'Rohan Verma', role: 'Security Engineer', skills: ['Python', 'Security', 'Networking'], conf: 77, verified: 13, status: 'CONNECT', following: false },
];

export const feedSeed = [
  { id: 'f1', name: 'Rudrant Joshi', role: 'Backend Developer', text: 'Improved automated testing coverage in my E-Commerce API.', before: 42, after: 81, skill: 'Testing', likes: 34, comments: 6 },
  { id: 'f2', name: 'Ananya Rao', role: 'AI/ML Engineer', text: 'Shipped a new MLOps pipeline project — CI/CD for model deployment.', likes: 58, comments: 12, project: 'ML Deploy Pipeline' },
  { id: 'f3', name: 'TechCorp', role: 'Company', text: 'We just opened a Backend Engineer role — evidence-backed applicants preferred.', likes: 21, comments: 3, job: 'Backend Engineer' },
  { id: 'f4', name: 'Karan Mehta', role: 'DevOps Engineer', text: 'Earned a Verified Docker badge after completing the CloudForge assessment.', badge: 'Docker · 88%', likes: 47, comments: 9 },
];

export const conversationsData = [
  { id: 'c1', name: 'Sarah Mehta', sub: 'Recruiter · TechCorp', type: 'RECRUITING', context: 'Backend Engineer · Application #APP-1028', online: true,
    msgs: [{ me: false, t: 'Hi Rudrant — thanks for applying to Backend Engineer.' }, { me: false, t: "We'd like to send you a technical assessment." }, { me: true, t: 'Sounds good, happy to take it this week.' }] },
  { id: 'c2', name: 'Ananya Rao', sub: 'AI/ML Engineer', type: 'DIRECT', context: null, online: false,
    msgs: [{ me: false, t: 'Nice improvement on the testing score 👀' }, { me: true, t: 'Thanks! Docker is next on my roadmap.' }] },
  { id: 'c3', name: '#backend-community', sub: 'Community · 412 members', type: 'COMMUNITY', context: null, online: false,
    msgs: [{ me: false, t: 'Anyone using Redis for API caching in FastAPI?' }, { me: true, t: 'Yep, works great with aioredis.' }] },
];

export const notificationsData = [
  { t: 'TechCorp invited you to Backend Engineer Assessment', sub: '2 hours ago', cta: 'View' },
  { t: 'Your Docker skill improvement was verified', sub: '5 hours ago', cta: 'View' },
  { t: 'Ananya Rao accepted your connection request', sub: '1 day ago', cta: 'View' },
  { t: 'Interview scheduled — AI Engineer @ AI Labs', sub: '2 days ago', cta: 'View' },
  { t: 'Roadmap updated: Redis added as new gap', sub: '3 days ago', cta: 'View' },
];
