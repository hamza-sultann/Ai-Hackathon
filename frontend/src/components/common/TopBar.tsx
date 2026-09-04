import React, { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Search,
  RefreshCw,
  Bell,
  Activity,
  User,
  CheckCheck,
  ExternalLink,
  Shield,
  Zap,
  HardHat,
  Settings,
  LogOut,
  Sliders,
  Sparkles,
  X,
  AlertTriangle,
  Radio,
} from 'lucide-react';
import { RoleSwitcher } from './RoleSwitcher';
import { UserRole, AppNotification } from '../../types';
import { adminApi } from '../../services/adminApi';
import { ROUTES } from '../../config/routes';

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
  const navigate = useNavigate();
  const [notificationsOpen, setNotificationsOpen] = useState(false);
  const [profileOpen, setProfileOpen] = useState(false);
  const [notifications, setNotifications] = useState<AppNotification[]>([]);
  const [notificationFilter, setNotificationFilter] = useState<'all' | 'anomaly' | 'field' | 'system'>('all');
  const [toastMessage, setToastMessage] = useState<string | null>(null);

  const notifRef = useRef<HTMLDivElement>(null);
  const profileRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    adminApi.getNotifications().then((data) => setNotifications(data));
  }, []);

  // Close dropdowns when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (notifRef.current && !notifRef.current.contains(event.target as Node)) {
        setNotificationsOpen(false);
      }
      if (profileRef.current && !profileRef.current.contains(event.target as Node)) {
        setProfileOpen(false);
      }
    };

    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        setNotificationsOpen(false);
        setProfileOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    document.addEventListener('keydown', handleKeyDown);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
      document.removeEventListener('keydown', handleKeyDown);
    };
  }, []);

  const unreadCount = notifications.filter((n) => !n.read).length;

  const handleMarkAllRead = () => {
    adminApi.markNotificationsRead();
    setNotifications((prev) => prev.map((n) => ({ ...n, read: true })));
    showToast('All notifications marked as read.');
  };

  const handleNotificationClick = (notif: AppNotification) => {
    setNotifications((prev) =>
      prev.map((n) => (n.id === notif.id ? { ...n, read: true } : n))
    );
    setNotificationsOpen(false);
    if (notif.targetUrl) {
      navigate(notif.targetUrl);
    }
  };

  const showToast = (msg: string) => {
    setToastMessage(msg);
    setTimeout(() => setToastMessage(null), 3000);
  };

  const filteredNotifications = notifications.filter((n) => {
    if (notificationFilter === 'all') return true;
    return n.category === notificationFilter;
  });

  return (
    <>
      <header className="no-print h-14 bg-[#0C110E] border-b border-[#263129] px-4 sm:px-6 flex items-center justify-between gap-2 sm:gap-4 sticky top-0 z-30">
        {/* Left: Global Search */}
        <div className="flex items-center gap-3 flex-1 min-w-0 max-w-xs md:max-w-sm xl:max-w-md">
          <div className="relative w-full">
            <Search className="w-4 h-4 text-[#9BA8A0] absolute left-3 top-1/2 -translate-y-1/2 shrink-0 pointer-events-none" />
            <input
              type="text"
              placeholder="Search Feeders, PMTs, Consumers..."
              className="w-full pl-9 pr-4 py-1.5 bg-[#101512] border border-[#263129] rounded-lg text-xs text-[#F3F7F4] placeholder-[#9BA8A0]/60 focus:outline-none focus:border-[#B6F542] transition-colors font-mono-tech"
            />
          </div>
        </div>

        {/* Right: Refresh, Health, Role Switcher, Notifications, Avatar */}
        <div className="flex items-center gap-2 sm:gap-3 shrink-0">
          {/* Data Health & Refresh */}
          <div className="hidden md:flex items-center gap-2 px-2.5 py-1 bg-[#101512] border border-[#263129] rounded-lg text-xs text-[#9BA8A0]">
            <span className="flex items-center gap-1.5">
              <Activity className="w-3.5 h-3.5 text-[#63D98A]" />
              <span className="font-semibold text-[#F3F7F4]">{dataHealthStatus}</span>
            </span>
            <span className="text-[#263129] hidden xl:inline">|</span>
            <span className="font-mono-tech text-[11px] hidden xl:inline">Synced {lastRefresh}</span>
          </div>

          {/* Run Analysis CTA */}
          {onOpenAnalysisDrawer && (
            <button
              onClick={onOpenAnalysisDrawer}
              className="flex items-center gap-1.5 px-2.5 sm:px-3 py-1.5 bg-[#B6F542] hover:bg-[#CAFF69] text-[#070A09] rounded-lg text-xs font-semibold transition-all shadow-sm active:scale-95 shrink-0"
              title="Run New Analysis"
            >
              <RefreshCw className="w-3.5 h-3.5" />
              <span className="hidden xl:inline">Run New Analysis</span>
              <span className="hidden sm:inline xl:hidden">Analyze</span>
            </button>
          )}

          {/* Prototype Access Badge (only on ultra-wide screens to prevent overflow) */}
          <div className="hidden 2xl:flex items-center px-2.5 h-[24px] rounded-full border border-[#263129] text-[#9BA8A0] text-[11px] font-medium shrink-0">
            Prototype access — auth disabled
          </div>

          {/* Role Switcher */}
          <RoleSwitcher currentRole={currentRole} />


          {/* Notifications Popover */}
          <div className="relative" ref={notifRef}>
            <button
              onClick={() => {
                setNotificationsOpen(!notificationsOpen);
                setProfileOpen(false);
              }}
              aria-label="Notifications"
              className={`relative p-2 rounded-lg border transition-all ${
                notificationsOpen
                  ? 'bg-[#161D19] text-[#F3F7F4] border-[#B6F542]'
                  : 'bg-[#101512] text-[#9BA8A0] hover:text-[#F3F7F4] border-[#263129]'
              }`}
            >
              <Bell className="w-4 h-4" />
              {unreadCount > 0 && (
                <span className="absolute -top-1 -right-1 min-w-[18px] h-[18px] px-1 rounded-full bg-[#B6F542] text-[#070A09] text-[10px] font-mono-tech font-extrabold flex items-center justify-center shadow-md animate-pulse">
                  {unreadCount}
                </span>
              )}
            </button>

            {/* Notification Dropdown Panel */}
            {notificationsOpen && (
              <div className="absolute right-0 mt-2 w-80 sm:w-96 rounded-xl bg-[#101512] border border-[#263129] shadow-2xl shadow-black/80 z-50 overflow-hidden animate-fadeIn">
                {/* Panel Header */}
                <div className="p-3.5 bg-[#0C110E] border-b border-[#263129] flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-bold text-[#F3F7F4] font-heading">Telemetry & Grid Alerts</span>
                    {unreadCount > 0 && (
                      <span className="px-1.5 py-0.5 rounded text-[10px] font-mono-tech bg-[#B6F542]/10 text-[#B6F542] border border-[#B6F542]/20 font-bold">
                        {unreadCount} unread
                      </span>
                    )}
                  </div>
                  {unreadCount > 0 && (
                    <button
                      onClick={handleMarkAllRead}
                      className="text-[11px] text-[#B6F542] hover:underline flex items-center gap-1 font-semibold"
                    >
                      <CheckCheck className="w-3 h-3" /> Mark all read
                    </button>
                  )}
                </div>

                {/* Filter Tabs */}
                <div className="flex items-center gap-1 px-3 py-2 bg-[#161D19]/60 border-b border-[#263129] text-[11px]">
                  {(['all', 'anomaly', 'field', 'system'] as const).map((tab) => (
                    <button
                      key={tab}
                      onClick={() => setNotificationFilter(tab)}
                      className={`px-2.5 py-1 rounded-md capitalize font-medium transition-all ${
                        notificationFilter === tab
                          ? 'bg-[#B6F542] text-[#070A09] font-bold'
                          : 'text-[#9BA8A0] hover:text-[#F3F7F4] hover:bg-[#101512]'
                      }`}
                    >
                      {tab}
                    </button>
                  ))}
                </div>

                {/* Notifications List */}
                <div className="max-h-80 overflow-y-auto divide-y divide-[#263129]/60">
                  {filteredNotifications.length === 0 ? (
                    <div className="p-8 text-center text-xs text-[#9BA8A0]">
                      No notifications in this category.
                    </div>
                  ) : (
                    filteredNotifications.map((notif) => (
                      <div
                        key={notif.id}
                        onClick={() => handleNotificationClick(notif)}
                        className={`p-3.5 cursor-pointer transition-all hover:bg-[#161D19] flex items-start gap-3 ${
                          !notif.read ? 'bg-[#101512]' : 'bg-[#0C110E]/50 opacity-75'
                        }`}
                      >
                        <div className="mt-0.5 shrink-0">
                          {notif.category === 'anomaly' && (
                            <div className="w-6 h-6 rounded bg-[#FF6262]/10 border border-[#FF6262]/30 text-[#FF6262] flex items-center justify-center">
                              <AlertTriangle className="w-3.5 h-3.5" />
                            </div>
                          )}
                          {notif.category === 'field' && (
                            <div className="w-6 h-6 rounded bg-[#40D9E8]/10 border border-[#40D9E8]/30 text-[#40D9E8] flex items-center justify-center">
                              <HardHat className="w-3.5 h-3.5" />
                            </div>
                          )}
                          {notif.category === 'system' && (
                            <div className="w-6 h-6 rounded bg-[#63D98A]/10 border border-[#63D98A]/30 text-[#63D98A] flex items-center justify-center">
                              <Radio className="w-3.5 h-3.5" />
                            </div>
                          )}
                          {notif.category === 'model' && (
                            <div className="w-6 h-6 rounded bg-[#B6F542]/10 border border-[#B6F542]/30 text-[#B6F542] flex items-center justify-center">
                              <Zap className="w-3.5 h-3.5" />
                            </div>
                          )}
                        </div>

                        <div className="flex-1 min-w-0">
                          <div className="flex items-center justify-between gap-1 mb-0.5">
                            <h4 className="text-xs font-bold text-[#F3F7F4] truncate">{notif.title}</h4>
                            <span className="text-[10px] font-mono-tech text-[#9BA8A0] shrink-0">
                              {notif.timestamp}
                            </span>
                          </div>
                          <p className="text-[11px] text-[#9BA8A0] leading-snug line-clamp-2">
                            {notif.message}
                          </p>
                        </div>
                        {!notif.read && (
                          <span className="w-2 h-2 rounded-full bg-[#B6F542] shrink-0 mt-1" />
                        )}
                      </div>
                    ))
                  )}
                </div>

                {/* Panel Footer */}
                <div className="p-2.5 bg-[#0C110E] border-t border-[#263129] text-center">
                  <button
                    onClick={() => {
                      setNotificationsOpen(false);
                      navigate(ROUTES.ADMIN.AUDIT);
                    }}
                    className="text-[11px] text-[#9BA8A0] hover:text-[#F3F7F4] transition-colors"
                  >
                    View Complete System Audit Stream →
                  </button>
                </div>
              </div>
            )}
          </div>

          {/* User Profile Avatar Popover */}
          <div className="relative" ref={profileRef}>
            <button
              onClick={() => {
                setProfileOpen(!profileOpen);
                setNotificationsOpen(false);
              }}
              aria-label="User Account Menu"
              className="flex items-center gap-2 pl-2 border-l border-[#263129] group cursor-pointer focus:outline-none"
            >
              <div
                className={`w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold transition-all ${
                  profileOpen
                    ? 'bg-[#B6F542] text-[#070A09] shadow-md shadow-[#B6F542]/20 ring-2 ring-[#B6F542]'
                    : 'bg-[#161D19] border border-[#B6F542]/40 text-[#B6F542] group-hover:border-[#B6F542]'
                }`}
              >
                HS
              </div>
            </button>

            {/* Profile Dropdown Panel */}
            {profileOpen && (
              <div className="absolute right-0 mt-2 w-72 rounded-xl bg-[#101512] border border-[#263129] shadow-2xl shadow-black/80 z-50 overflow-hidden animate-fadeIn">
                {/* User Info Header */}
                <div className="p-4 bg-[#0C110E] border-b border-[#263129]">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-full bg-[#161D19] border border-[#B6F542] text-[#B6F542] font-bold text-sm flex items-center justify-center shrink-0">
                      HS
                    </div>
                    <div className="min-w-0">
                      <h3 className="text-xs font-bold text-[#F3F7F4] truncate">Engr. Hamza Sultan</h3>
                      <p className="text-[11px] font-mono-tech text-[#9BA8A0] truncate">
                        analyst.hamza@disco.gov.pk
                      </p>
                      <span className="inline-block mt-1 px-2 py-0.5 rounded text-[10px] font-semibold bg-[#B6F542]/10 text-[#B6F542] border border-[#B6F542]/20">
                        Lead Grid Intelligence Operator
                      </span>
                    </div>
                  </div>
                  <div className="mt-3 pt-2.5 border-t border-[#263129]/60 text-[10px] text-[#9BA8A0]">
                    Division: <span className="text-[#F3F7F4] font-semibold">Faisalabad West / HQ</span>
                  </div>
                </div>

                {/* Quick Workspace Switcher */}
                <div className="p-2 border-b border-[#263129] bg-[#161D19]/40 space-y-1">
                  <span className="px-2 text-[10px] uppercase font-mono-tech text-[#9BA8A0] font-bold block">
                    Switch Active Workspace
                  </span>
                  <button
                    onClick={() => {
                      setProfileOpen(false);
                      navigate(ROUTES.ANALYST.ROOT);
                    }}
                    className={`w-full flex items-center justify-between px-2.5 py-1.5 rounded-lg text-xs transition-colors ${
                      currentRole === 'analyst'
                        ? 'bg-[#B6F542] text-[#070A09] font-bold'
                        : 'text-[#9BA8A0] hover:text-[#F3F7F4] hover:bg-[#101512]'
                    }`}
                  >
                    <span className="flex items-center gap-2">
                      <Zap className="w-3.5 h-3.5" /> Operator / Analyst
                    </span>
                    {currentRole === 'analyst' && <span className="text-[10px]">Active</span>}
                  </button>

                  <button
                    onClick={() => {
                      setProfileOpen(false);
                      navigate(ROUTES.FIELD.ROOT);
                    }}
                    className={`w-full flex items-center justify-between px-2.5 py-1.5 rounded-lg text-xs transition-colors ${
                      currentRole === 'field'
                        ? 'bg-[#B6F542] text-[#070A09] font-bold'
                        : 'text-[#9BA8A0] hover:text-[#F3F7F4] hover:bg-[#101512]'
                    }`}
                  >
                    <span className="flex items-center gap-2">
                      <HardHat className="w-3.5 h-3.5" /> Field Inspector
                    </span>
                    {currentRole === 'field' && <span className="text-[10px]">Active</span>}
                  </button>

                  <button
                    onClick={() => {
                      setProfileOpen(false);
                      navigate(ROUTES.ADMIN.ROOT);
                    }}
                    className={`w-full flex items-center justify-between px-2.5 py-1.5 rounded-lg text-xs transition-colors ${
                      currentRole === 'admin'
                        ? 'bg-[#B6F542] text-[#070A09] font-bold'
                        : 'text-[#9BA8A0] hover:text-[#F3F7F4] hover:bg-[#101512]'
                    }`}
                  >
                    <span className="flex items-center gap-2">
                      <Shield className="w-3.5 h-3.5" /> Admin System Ops
                    </span>
                    {currentRole === 'admin' && <span className="text-[10px]">Active</span>}
                  </button>
                </div>

                {/* Account Actions */}
                <div className="p-2 space-y-0.5">
                  <button
                    onClick={() => {
                      setProfileOpen(false);
                      navigate(ROUTES.ADMIN.CONFIGURATION);
                    }}
                    className="w-full flex items-center gap-2.5 px-3 py-2 rounded-lg text-xs text-[#9BA8A0] hover:text-[#F3F7F4] hover:bg-[#161D19] transition-colors"
                  >
                    <Settings className="w-3.5 h-3.5 text-[#B6F542]" />
                    <span>System Preferences & Thresholds</span>
                  </button>

                  <button
                    onClick={() => {
                      setProfileOpen(false);
                      showToast('Session refreshed in prototype mode.');
                    }}
                    className="w-full flex items-center gap-2.5 px-3 py-2 rounded-lg text-xs text-[#9BA8A0] hover:text-[#F3F7F4] hover:bg-[#161D19] transition-colors"
                  >
                    <Sparkles className="w-3.5 h-3.5 text-[#40D9E8]" />
                    <span>Prototype Environment Info</span>
                  </button>

                  <button
                    onClick={() => {
                      setProfileOpen(false);
                      navigate(ROUTES.WORKSPACES);
                    }}
                    className="w-full flex items-center gap-2.5 px-3 py-2 rounded-lg text-xs text-[#FF6262] hover:bg-[#FF6262]/10 transition-colors"
                  >
                    <LogOut className="w-3.5 h-3.5" />
                    <span>Exit to Workspace Selector</span>
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      </header>

      {/* Floating Action Toast */}
      {toastMessage && (
        <div className="fixed bottom-6 right-6 z-50 px-4 py-2.5 rounded-xl bg-[#161D19] border border-[#B6F542]/40 text-xs text-[#F3F7F4] shadow-2xl flex items-center gap-2 animate-slideUp">
          <Sparkles className="w-4 h-4 text-[#B6F542]" />
          <span>{toastMessage}</span>
        </div>
      )}
    </>
  );
};

