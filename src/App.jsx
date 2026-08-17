import { Navigate, Route, Routes } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import { ToastProvider } from './context/ToastContext';
import { ConfirmProvider } from './context/ConfirmContext';
import { DemoStateProvider } from './context/DemoStateContext';
import RequireAuth from './routes/RequireAuth';

import AuthLayout from './layouts/AuthLayout';
import AppShell from './layouts/AppShell';

import Login from './pages/auth/Login';
import Signup from './pages/auth/Signup';

import Dashboard from './pages/developer/Dashboard';

import Projects from './pages/skillgraph/Projects';
import ProjectDetail from './pages/skillgraph/ProjectDetail';
import ProjectsImport from './pages/skillgraph/ProjectsImport';
import Xray from './pages/skillgraph/Xray';
import SkillGraphView from './pages/skillgraph/SkillGraphView';
import Skills from './pages/skillgraph/Skills';
import Gaps from './pages/skillgraph/Gaps';
import Roadmap from './pages/skillgraph/Roadmap';
import Verify from './pages/skillgraph/Verify';
import Passport from './pages/skillgraph/Passport';

import CodeList from './pages/code/CodeList';
import SnippetForm from './pages/code/SnippetForm';
import SnippetDetail from './pages/code/SnippetDetail';

import ProblemsList from './pages/problems/ProblemsList';
import ProblemSolve from './pages/problems/ProblemSolve';

import Profile from './pages/profile/Profile';
import Network from './pages/network/Network';
import Feed from './pages/feed/Feed';
import Messages from './pages/messages/Messages';

import Jobs from './pages/jobs/Jobs';
import JobDetail from './pages/jobs/JobDetail';
import Applications from './pages/jobs/Applications';

import Assessments from './pages/assessments/Assessments';
import ExamTake from './pages/assessments/ExamTake';
import ExamResult from './pages/assessments/ExamResult';

import CompanyDashboard from './pages/recruiter/CompanyDashboard';
import CompanyJobs from './pages/recruiter/CompanyJobs';
import CompanyCampaigns from './pages/recruiter/CompanyCampaigns';
import CompanyQuestions from './pages/recruiter/CompanyQuestions';
import CompanyCandidates from './pages/recruiter/CompanyCandidates';
import Scorecard from './pages/recruiter/Scorecard';
import CompanyInterviews from './pages/recruiter/CompanyInterviews';
import CompanyAnalytics from './pages/recruiter/CompanyAnalytics';
import CompanyTeam from './pages/recruiter/CompanyTeam';

import NotFound from './pages/NotFound';

function RootRedirect() {
  const { isAuthenticated, role } = useAuth();
  if (!isAuthenticated) return <Navigate to="/login" replace />;
  return <Navigate to={role === 'developer' ? '/app/dashboard' : '/recruiter/dashboard'} replace />;
}

export default function App() {
  return (
    <AuthProvider>
      <ToastProvider>
        <ConfirmProvider>
          <DemoStateProvider>
            <Routes>
              <Route path="/" element={<RootRedirect />} />

              <Route element={<AuthLayout />}>
                <Route path="/login" element={<Login />} />
                <Route path="/signup" element={<Signup />} />
              </Route>

              <Route
                element={
                  <RequireAuth>
                    <AppShell />
                  </RequireAuth>
                }
              >
                {/* Developer / MVP routes */}
                <Route path="/app/dashboard" element={<Dashboard />} />
                <Route path="/app/code" element={<CodeList />} />
                <Route path="/app/code/snippets" element={<Navigate to="/app/code" replace />} />
                <Route path="/app/code/snippets/new" element={<SnippetForm />} />
                <Route path="/app/code/snippets/:id" element={<SnippetDetail />} />
                <Route path="/app/code/snippets/:id/edit" element={<SnippetForm />} />
                <Route path="/app/problems" element={<ProblemsList />} />
                <Route path="/app/problems/:id" element={<ProblemSolve />} />
                <Route path="/app/network" element={<Network />} />
                <Route path="/app/feed" element={<Feed />} />
                <Route path="/app/messages" element={<Messages />} />
                <Route path="/app/profile" element={<Profile />} />

                {/* SkillGraph routes */}
                <Route path="/app/projects" element={<Projects />} />
                <Route path="/app/projects-import" element={<ProjectsImport />} />
                <Route path="/app/projects/:name" element={<ProjectDetail />} />
                <Route path="/app/analyze" element={<ProjectsImport />} />
                <Route path="/app/xray" element={<Xray />} />
                <Route path="/app/skillgraph" element={<SkillGraphView />} />
                <Route path="/app/skills" element={<Skills />} />
                <Route path="/app/skill-gaps" element={<Gaps />} />
                <Route path="/app/roadmap" element={<Roadmap />} />
                <Route path="/app/verify" element={<Verify />} />
                <Route path="/app/passport" element={<Passport />} />

                {/* Career routes */}
                <Route path="/app/jobs" element={<Jobs />} />
                <Route path="/app/jobs/:id" element={<JobDetail />} />
                <Route path="/app/applications" element={<Applications />} />
                <Route path="/app/assessments" element={<Assessments />} />
                <Route path="/app/assessments/:id/take" element={<ExamTake />} />
                <Route path="/app/assessments/:id/result" element={<ExamResult />} />
                <Route path="/app/search" element={<Navigate to="/app/dashboard" replace />} />
                <Route path="/app/notifications" element={<Navigate to="/app/dashboard" replace />} />

                {/* Recruiter / Company routes (shared shell + sidebar switches by role) */}
                <Route path="/recruiter/dashboard" element={<CompanyDashboard />} />
                <Route path="/recruiter/jobs" element={<CompanyJobs />} />
                <Route path="/recruiter/campaigns" element={<CompanyCampaigns />} />
                <Route path="/recruiter/questions" element={<CompanyQuestions />} />
                <Route path="/recruiter/candidates" element={<CompanyCandidates />} />
                <Route path="/recruiter/scorecard/:id" element={<Scorecard />} />
                <Route path="/recruiter/interviews" element={<CompanyInterviews />} />
                <Route path="/recruiter/analytics" element={<CompanyAnalytics />} />
                <Route path="/recruiter/team" element={<CompanyTeam />} />
              </Route>

              <Route path="*" element={<NotFound />} />
            </Routes>
          </DemoStateProvider>
        </ConfirmProvider>
      </ToastProvider>
    </AuthProvider>
  );
}
