import { render, screen, waitFor } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import React from 'react';
import { MemoryRouter, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import App from '../App';
import { WorkspaceSelectionPage } from '../views/WorkspaceSelectionPage';
import { AnalystOverviewPage } from '../views/AnalystOverviewPage';
import { ConsumerInvestigationPage } from '../views/ConsumerInvestigationPage';

const createTestQueryClient = () =>
  new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
      },
    },
  });

describe('Istikshaf Frontend Core Tests', () => {
  it('renders landing page with correct product title and hero headline', () => {
    render(<App />);
    expect(screen.getAllByText(/Istikshaf/i).length).toBeGreaterThan(0);
    expect(screen.getByText(/Find Where the Grid Is/i)).toBeInTheDocument();
    expect(screen.getByText(/Losing Power/i)).toBeInTheDocument();
  });

  it('contains responsible-use disclaimer on landing page', () => {
    render(<App />);
    expect(screen.getByText(/Responsible Use Mandate/i)).toBeInTheDocument();
    expect(screen.getByText(/It does not determine guilt/i)).toBeInTheDocument();
  });

  it('renders workspace selection page with 3 role cards', () => {
    render(
      <MemoryRouter initialEntries={['/workspaces']}>
        <WorkspaceSelectionPage />
      </MemoryRouter>
    );

    expect(screen.getByText(/Prototype Access Enabled/i)).toBeInTheDocument();
    expect(screen.getByText(/Operator \/ Analyst/i)).toBeInTheDocument();
    expect(screen.getByText(/Field Inspector \/ Supervisor/i)).toBeInTheDocument();
    expect(screen.getByText(/Admin & System Ops/i)).toBeInTheDocument();
  });

  it('renders Analyst Overview and PMT Mass Balance metrics', async () => {
    render(
      <QueryClientProvider client={createTestQueryClient()}>
        <MemoryRouter initialEntries={['/analyst']}>
          <AnalystOverviewPage />
        </MemoryRouter>
      </QueryClientProvider>
    );

    await waitFor(() => {
      expect(screen.getByText(/Grid-Loss Operations Overview/i)).toBeInTheDocument();
      expect(screen.getAllByText(/Unaccounted Residual/i).length).toBeGreaterThan(0);
    });
  });

  it('renders Consumer Investigation C-08124 with disclaimer and tabs', async () => {
    render(
      <QueryClientProvider client={createTestQueryClient()}>
        <MemoryRouter initialEntries={['/analyst/investigations/C-08124']}>
          <Routes>
            <Route path="/analyst/investigations/:consumerId" element={<ConsumerInvestigationPage />} />
          </Routes>
        </MemoryRouter>
      </QueryClientProvider>
    );

    await waitFor(() => {
      expect(screen.getAllByText(/C-08124/i).length).toBeGreaterThan(0);
      expect(
        screen.getByText(/This recommendation indicates anomalous behavior and requires field verification/i)
      ).toBeInTheDocument();
      expect(screen.getByText(/Evidence Comparison & Synthesis/i)).toBeInTheDocument();
      expect(screen.getByText(/Monthly Billing Pipeline/i)).toBeInTheDocument();
      expect(screen.getByText(/Hourly Smart Meter Pipeline/i)).toBeInTheDocument();
    });
  });
});
