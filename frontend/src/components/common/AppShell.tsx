import React, { useState } from 'react';
import { Sidebar } from './Sidebar';
import { TopBar } from './TopBar';
import { Breadcrumbs } from './Breadcrumbs';
import { ResponsibleUseBanner } from './ResponsibleUseBanner';
import { AnalysisDrawer } from './AnalysisDrawer';
import { UserRole } from '../../types';

interface AppShellProps {
  currentRole: UserRole;
  children: React.ReactNode;
  breadcrumbsItems?: Array<{ label: string; href?: string }>;
  showBanner?: boolean;
}

export const AppShell: React.FC<AppShellProps> = ({
  currentRole,
  children,
  breadcrumbsItems,
  showBanner = true,
}) => {
  const [isAnalysisDrawerOpen, setIsAnalysisDrawerOpen] = useState(false);

  return (
    <div className="min-h-screen bg-[#070A09] text-[#F3F7F4] flex flex-row font-sans">
      {/* Left Collapsible Sidebar */}
      <Sidebar currentRole={currentRole} />

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Top Utility Bar */}
        <TopBar
          currentRole={currentRole}
          onOpenAnalysisDrawer={() => setIsAnalysisDrawerOpen(true)}
        />

        {/* Content Container */}
        <main className="flex-1 p-6 max-w-7xl w-full mx-auto space-y-5">
          {/* Prototype Role Warning */}
          <div className="no-print p-2.5 rounded-lg bg-[#161D19] border border-[#263129] flex items-center justify-between text-xs text-[#9BA8A0]">
            <div className="flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-[#B6F542] animate-pulse" />
              <span>Prototype access — authentication is disabled for this demonstration.</span>
            </div>
            <span className="font-mono-tech text-[11px] text-[#B6F542]">Active: {currentRole.toUpperCase()}</span>
          </div>

          {/* Breadcrumbs */}
          <Breadcrumbs customItems={breadcrumbsItems} />

          {/* Responsible Use Banner */}
          {showBanner && <ResponsibleUseBanner />}

          {/* Page Content */}
          <div className="space-y-6">{children}</div>
        </main>
      </div>

      {/* Analysis Drawer */}
      <AnalysisDrawer
        isOpen={isAnalysisDrawerOpen}
        onClose={() => setIsAnalysisDrawerOpen(false)}
      />
    </div>
  );
};
