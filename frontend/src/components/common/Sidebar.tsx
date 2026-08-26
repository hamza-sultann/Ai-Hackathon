import React, { useState } from 'react';
import { NavLink } from 'react-router-dom';
import {
  Zap,
  LayoutDashboard,
  Grid,
  Search,
  GitCompare,
  FileCheck,
  HardHat,
  Users,
  History,
  Shield,
  Database,
  Cpu,
  UserCheck,
  FileText,
  Settings,
  ChevronLeft,
  ChevronRight,
  Sparkles,
} from 'lucide-react';
import { UserRole } from '../../types';
import { ROUTES } from '../../config/routes';

interface SidebarProps {
  currentRole: UserRole;
}

export const Sidebar: React.FC<SidebarProps> = ({ currentRole }) => {
  const [collapsed, setCollapsed] = useState(false);

  const getNavItems = () => {
    switch (currentRole) {
      case 'analyst':
        return [
          { label: 'Overview', path: ROUTES.ANALYST.ROOT, icon: LayoutDashboard, end: true },
          { label: 'Grid Explorer', path: ROUTES.ANALYST.GRID, icon: Grid },
          { label: 'Investigation Queue', path: ROUTES.ANALYST.INVESTIGATIONS, icon: Search },
          { label: 'Pipeline Comparison', path: ROUTES.ANALYST.COMPARISON, icon: GitCompare },
          { label: 'Job-Cards', path: ROUTES.ANALYST.JOB_CARDS, icon: FileCheck },
        ];
      case 'field':
        return [
          { label: 'Field Overview', path: ROUTES.FIELD.ROOT, icon: LayoutDashboard, end: true },
          { label: 'Assigned Job-Cards', path: ROUTES.FIELD.JOBS, icon: HardHat },
          { label: 'Team Queue', path: ROUTES.FIELD.TEAM, icon: Users },
          { label: 'Inspection History', path: ROUTES.FIELD.HISTORY, icon: History },
        ];
      case 'admin':
        return [
          { label: 'System Overview', path: ROUTES.ADMIN.ROOT, icon: Shield, end: true },
          { label: 'Data Sources', path: ROUTES.ADMIN.DATA_SOURCES, icon: Database },
          { label: 'Model Services', path: ROUTES.ADMIN.MODELS, icon: Cpu },
          { label: 'User Access', path: ROUTES.ADMIN.USERS, icon: UserCheck },
          { label: 'Audit Activity', path: ROUTES.ADMIN.AUDIT, icon: FileText },
          { label: 'Configuration', path: ROUTES.ADMIN.CONFIGURATION, icon: Settings },
        ];
    }
  };

  const navItems = getNavItems();

  return (
    <aside
      className={`no-print h-screen bg-[#070A09] border-r border-[#263129] flex flex-col justify-between transition-all duration-300 z-40 sticky top-0 ${
        collapsed ? 'w-[72px]' : 'w-[240px]'
      }`}
    >
      {/* Top: Logo & Nav */}
      <div>
        {/* Logo Header */}
        <div className="h-14 flex items-center justify-between px-4 border-b border-[#263129]">
          <NavLink to={ROUTES.HOME} className="flex items-center gap-2.5 overflow-hidden">
            <div className="w-8 h-8 rounded-lg bg-[#B6F542] text-[#070A09] flex items-center justify-center font-bold shrink-0 shadow-md shadow-[#B6F542]/20">
              <Zap className="w-5 h-5 fill-[#070A09]" />
            </div>
            {!collapsed && (
              <div className="flex flex-col">
                <span className="text-headline-sm tracking-tight text-[#F3F7F4]">
                  Istikshaf
                </span>
                <span className="text-label-caps text-[#9BA8A0]">
                  Grid Loss Intelligence
                </span>
              </div>
            )}
          </NavLink>
        </div>

        {/* Workspace Title */}
        {!collapsed && (
          <div className="px-4 py-3 border-b border-[#263129]/50 bg-[#0C110E]">
            <span className="text-label-caps text-[#9BA8A0] block">
              {currentRole === 'analyst' && 'Operator / Analyst Workspace'}
              {currentRole === 'field' && 'Field Inspector Workspace'}
              {currentRole === 'admin' && 'Admin & System Ops Workspace'}
            </span>
          </div>
        )}

        {/* Navigation Links */}
        <nav className="p-2 space-y-1 mt-2">
          {navItems.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              end={item.end}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3 py-2.5 rounded-lg text-xs font-semibold transition-all ${
                  isActive
                    ? 'bg-[#B6F542] text-[#070A09] shadow-sm'
                    : 'text-[#9BA8A0] hover:text-[#F3F7F4] hover:bg-[#161D19]'
                }`
              }
            >
              <item.icon className="w-4 h-4 shrink-0" />
              {!collapsed && <span className="truncate">{item.label}</span>}
            </NavLink>
          ))}
        </nav>
      </div>

      {/* Bottom: Collapse Button & Info */}
      <div className="p-3 border-t border-[#263129] bg-[#0C110E]/60 space-y-2">
        {!collapsed && (
          <div className="p-2.5 rounded-lg bg-[#101512] border border-[#263129] text-[11px] text-[#9BA8A0]">
            <div className="flex items-center gap-1.5 font-semibold text-[#F3F7F4] mb-1">
              <Sparkles className="w-3.5 h-3.5 text-[#B6F542]" />
              <span>DISCO Inspection</span>
            </div>
            <p className="text-[10px] leading-tight">Physics + Smart-Meter + TreeSHAP AI</p>
          </div>
        )}

        <button
          onClick={() => setCollapsed(!collapsed)}
          className="w-full flex items-center justify-center gap-2 py-2 px-3 rounded-lg text-xs font-semibold text-[#9BA8A0] hover:text-[#F3F7F4] hover:bg-[#161D19] transition-colors"
          title={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
        >
          {collapsed ? <ChevronRight className="w-4 h-4" /> : <ChevronLeft className="w-4 h-4" />}
          {!collapsed && <span>Collapse Sidebar</span>}
        </button>
      </div>
    </aside>
  );
};
