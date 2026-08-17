export const assessmentsData = [
  { id: 'a1', title: 'Backend Engineer Assessment', company: 'TechCorp', duration: 90, qcount: 25, skills: ['Backend', 'SQL', 'Algorithms', 'System Design'], status: 'NOT STARTED' },
  { id: 'a2', title: 'Python Skill Assessment', company: 'Self-Verify', duration: 45, qcount: 15, skills: ['Python'], status: 'NOT STARTED' },
  { id: 'a3', title: 'SQL Assessment', company: 'CloudForge', duration: 30, qcount: 12, skills: ['SQL'], status: 'COMPLETED', score: 91 },
  { id: 'a4', title: 'System Design Assessment', company: 'AI Labs', duration: 60, qcount: 8, skills: ['System Design'], status: 'EXPIRED' },
];

export const examQuestions = [
  { type: 'MCQ', q: 'Which HTTP status code indicates a successful resource creation?', options: ['200 OK', '201 Created', '204 No Content', '302 Found'], answer: 1 },
  { type: 'MCQ', q: 'In PostgreSQL, which command creates an index?', options: ['MAKE INDEX', 'CREATE INDEX', 'ADD INDEX', 'NEW INDEX'], answer: 1 },
  { type: 'SQL', q: 'Write a query to select all users who signed up in the last 7 days.', code: "SELECT * FROM users\nWHERE created_at >= NOW() - INTERVAL '7 days';" },
  { type: 'CODING', q: 'Implement a function that returns the two indices of numbers in an array that add up to a target value.', code: 'def two_sum(nums, target):\n    seen = {}\n    for i, n in enumerate(nums):\n        if target - n in seen:\n            return [seen[target-n], i]\n        seen[n] = i\n    return []' },
  { type: 'MCQ', q: 'Which of the following best describes idempotency in REST APIs?', options: ['Response is cached', 'Multiple identical requests have the same effect as one', 'Request always returns 200', 'Request cannot be repeated'], answer: 1 },
];

export const questionBankData = [
  { q: 'Explain the difference between INNER JOIN and LEFT JOIN.', type: 'Short Answer', topic: 'Database', diff: 'Easy', skill: 'SQL' },
  { q: 'Two Sum — return indices of two numbers that add to target.', type: 'Coding Problem', topic: 'Algorithms', diff: 'Easy', skill: 'Python' },
  { q: 'Design a URL shortener service.', type: 'System Design', topic: 'System Design', diff: 'Hard', skill: 'System Design' },
  { q: 'Find and fix the bug in the given FastAPI route handler.', type: 'Debugging', topic: 'Backend', diff: 'Medium', skill: 'FastAPI' },
  { q: 'What will this Python snippet output?', type: 'Output Prediction', topic: 'Language-specific', diff: 'Medium', skill: 'Python' },
];

export const campaignsData = [
  { name: 'Backend Engineer — Q3 Hiring', job: 'Backend Engineer', state: 'Active', invited: 180, started: 142, completed: 91, shortlisted: 34, interview: 14, selected: 3 },
  { name: 'AI Engineer — Founding Team', job: 'AI Engineer', state: 'Active', invited: 60, started: 41, completed: 22, shortlisted: 9, interview: 5, selected: 1 },
  { name: 'DevOps Contract Batch', job: 'DevOps Engineer', state: 'Draft', invited: 0, started: 0, completed: 0, shortlisted: 0, interview: 0, selected: 0 },
  { name: 'Full Stack — Spring Cohort', job: 'Full Stack Developer', state: 'Completed', invited: 120, started: 98, completed: 88, shortlisted: 20, interview: 11, selected: 4 },
];

export const candidatesData = [
  { name: 'Rudrant Joshi', score: 84, skills: 'Python, FastAPI, SQL', status: 'Assessment Complete', time: '82m', coding: '8/10', ai: '86%' },
  { name: 'Devesh Kumar', score: 79, skills: 'Java, Spring, SQL', status: 'Assessment Complete', time: '88m', coding: '7/10', ai: '81%' },
  { name: 'Priya Nair', score: 71, skills: 'React, Node.js', status: 'In Progress', time: '—', coding: '—', ai: '—' },
  { name: 'Rohan Verma', score: 66, skills: 'Python, Security', status: 'Invited', time: '—', coding: '—', ai: '—' },
];

export const interviewsData = [
  { candidate: 'Rudrant Joshi', position: 'Backend Engineer', type: 'Technical', date: 'Aug 18', time: '3:00 PM', interviewers: 'Sarah Mehta', status: 'Scheduled' },
  { candidate: 'Devesh Kumar', position: 'Backend Engineer', type: 'Technical', date: 'Aug 19', time: '11:00 AM', interviewers: 'Arjun Shah', status: 'Upcoming' },
  { candidate: 'Ananya Rao', position: 'AI Engineer', type: 'System Design', date: 'Aug 14', time: '2:00 PM', interviewers: 'Sarah Mehta', status: 'Completed' },
];

export const teamData = [
  { name: 'Sarah Mehta', role: 'Recruiter', email: 'sarah@techcorp.io' },
  { name: 'Arjun Shah', role: 'Admin', email: 'arjun@techcorp.io' },
  { name: 'Neha Patel', role: 'Hiring Manager', email: 'neha@techcorp.io' },
];
