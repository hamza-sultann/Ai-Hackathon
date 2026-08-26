import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ROUTES } from './config/routes';

// Import Views
import { LandingPage } from './views/LandingPage';
import { WorkspaceSelectionPage } from './views/WorkspaceSelectionPage';
import { AnalystOverviewPage } from './views/AnalystOverviewPage';
import { GridExplorerPage } from './views/GridExplorerPage';
import { InvestigationQueuePage } from './views/InvestigationQueuePage';
import { ConsumerInvestigationPage } from './views/ConsumerInvestigationPage';
import { PipelineComparisonPage } from './views/PipelineComparisonPage';
import { JobCardsPage } from './views/JobCardsPage';
import { JobCardDetailPage } from './views/JobCardDetailPage';
import { FieldOverviewPage } from './views/FieldOverviewPage';
import { FieldJobDetailPage } from './views/FieldJobDetailPage';
import { AdminPage } from './views/AdminPage';
import { NotFoundPage } from './views/NotFoundPage';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      staleTime: 1000 * 60 * 5, // 5 minutes
    },
  },
});

export const App: React.FC = () => {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          {/* Public Routes */}
          <Route path={ROUTES.HOME} element={<LandingPage />} />
          <Route path={ROUTES.WORKSPACES} element={<WorkspaceSelectionPage />} />

          {/* Operator / Analyst Workspace Routes */}
          <Route path={ROUTES.ANALYST.ROOT} element={<AnalystOverviewPage />} />
          <Route path={ROUTES.ANALYST.GRID} element={<GridExplorerPage />} />
          <Route path={ROUTES.ANALYST.FEEDER_PARAM} element={<GridExplorerPage />} />
          <Route path={ROUTES.ANALYST.PMT_PARAM} element={<GridExplorerPage />} />
          <Route path={ROUTES.ANALYST.INVESTIGATIONS} element={<InvestigationQueuePage />} />
          <Route path={ROUTES.ANALYST.CONSUMER_INVESTIGATION_PARAM} element={<ConsumerInvestigationPage />} />
          <Route path={ROUTES.ANALYST.COMPARISON} element={<PipelineComparisonPage />} />
          <Route path={ROUTES.ANALYST.JOB_CARDS} element={<JobCardsPage />} />
          <Route path={ROUTES.ANALYST.JOB_CARD_DETAIL_PARAM} element={<JobCardDetailPage />} />

          {/* Field Inspector / Supervisor Workspace Routes */}
          <Route path={ROUTES.FIELD.ROOT} element={<FieldOverviewPage />} />
          <Route path={ROUTES.FIELD.JOBS} element={<FieldOverviewPage />} />
          <Route path={ROUTES.FIELD.JOB_DETAIL_PARAM} element={<FieldJobDetailPage />} />
          <Route path={ROUTES.FIELD.TEAM} element={<FieldOverviewPage />} />
          <Route path={ROUTES.FIELD.HISTORY} element={<FieldOverviewPage />} />

          {/* Admin Workspace Routes */}
          <Route path={ROUTES.ADMIN.ROOT} element={<AdminPage />} />
          <Route path={ROUTES.ADMIN.DATA_SOURCES} element={<AdminPage />} />
          <Route path={ROUTES.ADMIN.MODELS} element={<AdminPage />} />
          <Route path={ROUTES.ADMIN.USERS} element={<AdminPage />} />
          <Route path={ROUTES.ADMIN.AUDIT} element={<AdminPage />} />
          <Route path={ROUTES.ADMIN.CONFIGURATION} element={<AdminPage />} />

          {/* Fallback 404 Route */}
          <Route path="*" element={<NotFoundPage />} />
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  );
};

export default App;
