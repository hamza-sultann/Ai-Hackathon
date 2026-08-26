import React from 'react';
import { Search, RefreshCw, Bell, Activity, User } from 'lucide-react';
import { RoleSwitcher } from './RoleSwitcher';
import { UserRole } from '../../types';

interface TopBarProps {
  currentRole: UserRole;
  onOpenAnalysisDrawer?: () => void;
  lastRefresh?: string;
  dataHealthStatus?: 'Healthy' | 'Degraded' | 'Syncing';
}

export const TopBar: React.FC<TopBarProps> = ({
  currentRole,
  onOpenAnalysisDrawer,
  lastRefresh = '18:30 PKT',
  dataHealthStatus = 'Healthy',
}) => {
  return (
    <header className="no-print h-14 bg-[#0C110E] border-b border-[#263129] px-6 flex items-center justify-between gap-4 sticky top-0 z-30">
      {/* Left: Global Search */}
      <div className="flex items-center gap-4 flex-1 max-w-md">
        <div className="relative w-full">
          <Search className="w-4 h-4 text-[#9BA8A0] absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Search Feeders (FDR-08), PMTs (PMT-081), Consumer IDs (C-08124)..."
            className="w-full pl-9 pr-4 py-1.5 bg-[#101512] border border-[#263129] rounded-lg text-xs text-[#F3F7F4] placeholder-[#9BA8A0]/60 focus:outline-none focus:border-[#B6F542] transition-colors font-mono-tech"
          />
        </div>
      </div>

      {/* Right: Refresh, Health, Role Switcher, Notifications, Avatar */}
      <div className="flex items-center gap-3 shrink-0">
        {/* Data Health & Refresh */}
        <div className="flex items-center gap-2 px-3 py-1 bg-[#101512] border border-[#263129] rounded-lg text-xs text-[#9BA8A0]">
          <span className="flex items-center gap-1.5">
            <Activity className="w-3.5 h-3.5 text-[#63D98A]" />
            <span className="font-semibold text-[#F3F7F4]">{dataHealthStatus}</span>
          </span>
          <span className="text-[#263129]">|</span>
          <span className="font-mono-tech text-[11px]">Synced {lastRefresh}</span>
        </div>

        {/* Run Analysis CTA */}
        {onOpenAnalysisDrawer && (
          <button
            onClick={onOpenAnalysisDrawer}
            className="flex items-center gap-1.5 px-3 py-1.5 bg-[#B6F542] hover:bg-[#CAFF69] text-[#070A09] rounded-lg text-xs font-semibold transition-all shadow-sm"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            <span>Run New Analysis</span>
          </button>
        )}

        {/* Role Switcher */}
        <RoleSwitcher currentRole={currentRole} />

        {/* Notifications */}
        <button
          aria-label="Notifications"
          className="relative p-2 text-[#9BA8A0] hover:text-[#F3F7F4] bg-[#101512] border border-[#263129] rounded-lg transition-colors"
        >
          <Bell className="w-4 h-4" />
          <span className="absolute top-1 right-1 w-2 h-2 rounded-full bg-[#B6F542]" />
        </button>

        {/* Prototype Avatar */}
        <div className="flex items-center gap-2 pl-2 border-l border-[#263129]">
          <div className="w-8 h-8 rounded-full bg-[#161D19] border border-[#B6F542]/40 flex items-center justify-center text-[#B6F542] font-semibold text-xs">
            <User className="w-4 h-4" />
          </div>
        </div>
      </div>
    </header>
  );
};
