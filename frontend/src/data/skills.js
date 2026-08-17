export const skills = [
  { name: 'Python', pct: 87, status: 'Strong Evidence', badge: 'strong', projects: 3, evidence: 8, cat: 'lang' },
  { name: 'React', pct: 82, status: 'Strong Evidence', badge: 'strong', projects: 2, evidence: 6, cat: 'lang' },
  { name: 'FastAPI', pct: 79, status: 'Strong Evidence', badge: 'strong', projects: 2, evidence: 5, cat: 'fw' },
  { name: 'SQL', pct: 71, status: 'Developing', badge: 'warn', projects: 3, evidence: 5, cat: 'db' },
  { name: 'Git', pct: 91, status: 'Strong Evidence', badge: 'strong', projects: 4, evidence: 10, cat: 'tool' },
  { name: 'Docker', pct: 43, status: 'Needs Improvement', badge: 'gap', projects: 1, evidence: 2, cat: 'tool' },
  { name: 'Testing', pct: 48, status: 'Needs Improvement', badge: 'gap', projects: 1, evidence: 2, cat: 'concept' },
  { name: 'System Design', pct: 51, status: 'Developing', badge: 'warn', projects: 2, evidence: 3, cat: 'concept' },
];

export const projects = [
  { name: 'E-Commerce API', tech: ['Python', 'FastAPI', 'PostgreSQL', 'Docker'], health: 82, skills: 8, ago: '2 hours ago' },
  { name: 'AI Assistant', tech: ['Python', 'OpenAI', 'FastAPI'], health: 76, skills: 6, ago: '1 day ago' },
  { name: 'Expense Manager', tech: ['React', 'Node.js', 'MongoDB'], health: 69, skills: 5, ago: '4 days ago' },
  { name: 'College Management System', tech: ['Java', 'MySQL'], health: 58, skills: 4, ago: '2 weeks ago' },
];

export const gaps = [
  { name: 'Docker', current: 31, target: 70, priority: 'High Priority', cls: 'gap' },
  { name: 'Testing', current: 43, target: 75, priority: 'High Priority', cls: 'gap' },
  { name: 'Redis', current: 18, target: 65, priority: 'High Priority', cls: 'gap' },
  { name: 'System Design', current: 51, target: 75, priority: 'Medium', cls: 'warn' },
  { name: 'SQL', current: 71, target: 75, priority: 'Low', cls: 'warn' },
];

export const roadmap = [
  { n: '01', title: 'Testing Fundamentals', why: 'Testing is currently one of your biggest skill gaps.', task: 'Add unit and integration tests to E-Commerce API.', status: 'NOT STARTED' },
  { n: '02', title: 'Docker', why: 'Containers are expected for backend deployment roles.', task: 'Containerize your API.', status: 'IN PROGRESS' },
  { n: '03', title: 'Redis', why: 'Caching demonstrates production-readiness.', task: 'Add API caching layer.', status: 'LOCKED' },
  { n: '04', title: 'System Design', why: 'Needed for mid-to-senior backend roles.', task: 'Improve service architecture.', status: 'LOCKED' },
];

export const beforeAfterData = [
  { name: 'Testing', before: 42, after: 81 },
  { name: 'Security', before: 61, after: 84 },
  { name: 'Docker', before: 18, after: 73 },
  { name: 'Documentation', before: 54, after: 79 },
];

export const badgesForPassport = ['SQL Verified', 'Python Verified', 'Docker Improved'];

export const apStepsData = [
  'Validating repository…', 'Connecting to GitHub…', 'Repository detected', 'Scanning files…',
  'Detecting technologies…', 'Analyzing architecture…', 'Evaluating code quality…',
  'Extracting skills…', 'Generating SkillGraph…', 'Analysis complete',
];
