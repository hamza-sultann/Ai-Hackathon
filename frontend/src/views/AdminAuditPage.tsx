import React, { useEffect, useState } from 'react';
import { AppShell } from '../components/common/AppShell';
import { adminApi } from '../services/adminApi';
import { AuditEvent } from '../types';
import { ROUTES } from '../config/routes';
import {
  FileText,
  Search,
  Filter,
  Download,
  CheckCircle2,
  AlertTriangle,
  Clock,
  Shield,
  X,
  Layers,
} from 'lucide-react';

export const AdminAuditPage: React.FC = () => {
  const [auditEvents, setAuditEvents] = useState<AuditEvent[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [actionFilter, setActionFilter] = useState('All');
  const [selectedAudit, setSelectedAudit] = useState<AuditEvent | null>(null);
  const [exportNotification, setExportNotification] = useState<string | null>(null);

  useEffect(() => {
    async function loadData() {
      try {
        const aud = await adminApi.getAuditActivity();
        setAuditEvents(aud);
      } catch (err) {
        console.error('Failed to load audit activity', err);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  const filteredEvents = auditEvents.filter((aud) => {
    const matchesSearch =
      aud.id.toLowerCase().includes(searchQuery.toLowerCase()) ||
      aud.actor.toLowerCase().includes(searchQuery.toLowerCase()) ||
      aud.objectId.toLowerCase().includes(searchQuery.toLowerCase()) ||
      aud.action.toLowerCase().includes(searchQuery.toLowerCase());

    const matchesAction = actionFilter === 'All' || aud.action === actionFilter;

    return matchesSearch && matchesAction;
  });

  const handleExportCSV = () => {
    setExportNotification('System audit stream exported to CSV successfully.');
    setTimeout(() => setExportNotification(null), 3500);
  };

  return (
    <AppShell
      currentRole="admin"
      hidePrototypeBanner
      compactBanner
      breadcrumbsItems={[
        { label: 'Admin Ops', href: ROUTES.ADMIN.ROOT },
        { label: 'System Audit Trail' },
      ]}
    >
      {/* Header */}
      <div className="holo-card p-6 rounded-2xl bg-[#101512] border border-[#263129] flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl lg:text-2xl font-bold text-[#F3F7F4] font-heading tracking-tight flex items-center gap-2.5">
            <FileText className="w-5 h-5 text-[#63D98A]" /> Enterprise System Audit Trail
          </h1>
          <p className="text-xs text-[#9BA8A0] mt-1">
            Immutable, timestamped event stream capturing user actions, automated model executions, and job-card state transitions.
          </p>
        </div>
        <button
          onClick={handleExportCSV}
          className="flex items-center gap-2 px-4 py-2 rounded-xl bg-[#161D19] hover:bg-[#263129] text-[#63D98A] border border-[#63D98A]/30 text-xs font-semibold transition-all shrink-0"
        >
          <Download className="w-4 h-4" />
          <span>Export Audit Log (CSV)</span>
        </button>
      </div>

      {exportNotification && (
        <div className="p-4 rounded-2xl bg-[#63D98A]/10 border border-[#63D98A]/30 text-xs text-[#63D98A] flex items-center gap-2 animate-fadeIn">
          <CheckCircle2 className="w-4 h-4 shrink-0" />
          <span>{exportNotification}</span>
        </div>
      )}

      {/* Filter & Search Bar */}
      <div className="p-4 rounded-2xl bg-[#101512] border border-[#263129] space-y-3">
        <div className="flex flex-col md:flex-row gap-3">
          <div className="relative flex-1">
            <Search className="w-4 h-4 text-[#9BA8A0] absolute left-3.5 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search by Audit ID, Actor email, Action, or Object ID..."
              className="w-full pl-10 pr-4 py-2 bg-[#0C110E] border border-[#263129] rounded-xl text-xs text-[#F3F7F4] placeholder-[#9BA8A0]/60 focus:outline-none focus:border-[#63D98A] transition-colors font-mono-tech"
            />
          </div>

          <div className="flex items-center gap-1 bg-[#0C110E] p-1 rounded-xl border border-[#263129] text-xs overflow-x-auto">
            <span className="px-2 text-[11px] text-[#9BA8A0] font-mono-tech">Action:</span>
            {['All', 'CREATE_JOB_CARD', 'BATCH_GRID_ANALYSIS', 'ASSIGN_JOB_CARD', 'SUBMIT_FINDING'].map((act) => (
              <button
                key={act}
                onClick={() => setActionFilter(act)}
                className={`px-3 py-1 rounded-lg text-xs font-semibold whitespace-nowrap transition-all ${
                  actionFilter === act
                    ? 'bg-[#63D98A] text-[#070A09]'
                    : 'text-[#9BA8A0] hover:text-[#F3F7F4] hover:bg-[#161D19]'
                }`}
              >
                {act}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Audit Log Table */}
      <div className="p-6 rounded-2xl bg-[#101512] border border-[#263129] space-y-4">
        {loading ? (
          <div className="p-16 text-center text-xs text-[#9BA8A0] animate-pulse">
            Loading System Audit Stream...
          </div>
        ) : filteredEvents.length === 0 ? (
          <div className="p-12 text-center text-xs text-[#9BA8A0]">
            No audit records found matching your filters.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-[#0C110E] text-[#9BA8A0] uppercase font-mono-tech border-b border-[#263129]">
                <tr>
                  <th className="p-3.5">Audit ID</th>
                  <th className="p-3.5">Actor Identity</th>
                  <th className="p-3.5">Action Executed</th>
                  <th className="p-3.5">Target Entity ID</th>
                  <th className="p-3.5">Timestamp</th>
                  <th className="p-3.5">Execution Result</th>
                  <th className="p-3.5 text-right">Details</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#263129]/60">
                {filteredEvents.map((aud) => (
                  <tr key={aud.id} className="hover:bg-[#161D19] transition-colors">
                    <td className="p-3.5 font-mono-tech font-bold text-[#63D98A]">{aud.id}</td>
                    <td className="p-3.5 font-mono-tech text-[#F3F7F4]">{aud.actor}</td>
                    <td className="p-3.5">
                      <span className="px-2.5 py-1 rounded-md text-[11px] font-mono-tech font-bold bg-[#161D19] text-[#B6F542] border border-[#B6F542]/30">
                        {aud.action}
                      </span>
                    </td>
                    <td className="p-3.5 font-mono-tech text-[#40D9E8] font-bold">{aud.objectId}</td>
                    <td className="p-3.5 font-mono-tech text-[#9BA8A0]">{aud.timestamp}</td>
                    <td className="p-3.5">
                      <span
                        className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded-md text-xs font-semibold ${
                          aud.result === 'Success'
                            ? 'bg-[#63D98A]/10 text-[#63D98A] border border-[#63D98A]/30'
                            : 'bg-[#FF6262]/10 text-[#FF6262] border border-[#FF6262]/30'
                        }`}
                      >
                        {aud.result}
                      </span>
                    </td>
                    <td className="p-3.5 text-right">
                      <button
                        onClick={() => setSelectedAudit(aud)}
                        className="px-3 py-1 rounded-lg bg-[#161D19] hover:bg-[#63D98A] hover:text-[#070A09] text-[#63D98A] border border-[#63D98A]/30 text-xs font-semibold transition-colors"
                      >
                        Inspect
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Audit Detail Modal */}
      {selectedAudit && (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4 z-50 animate-fadeIn">
          <div className="w-full max-w-lg rounded-2xl bg-[#101512] border border-[#263129] shadow-2xl p-6 space-y-4 animate-slideUp">
            <div className="flex items-center justify-between border-b border-[#263129] pb-4">
              <div>
                <h3 className="text-base font-bold text-[#F3F7F4] font-heading font-mono-tech">
                  {selectedAudit.id} • Audit Record
                </h3>
                <p className="text-xs text-[#9BA8A0]">{selectedAudit.timestamp}</p>
              </div>
              <button
                onClick={() => setSelectedAudit(null)}
                className="p-1.5 rounded-lg text-[#9BA8A0] hover:text-[#F3F7F4] hover:bg-[#161D19]"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="space-y-3 text-xs">
              <div className="p-3 rounded-xl bg-[#0C110E] border border-[#263129]">
                <span className="text-[#9BA8A0] block text-[11px]">Actor</span>
                <span className="font-mono-tech text-[#F3F7F4] font-bold">{selectedAudit.actor}</span>
              </div>
              <div className="p-3 rounded-xl bg-[#0C110E] border border-[#263129]">
                <span className="text-[#9BA8A0] block text-[11px]">Action</span>
                <span className="font-mono-tech text-[#B6F542] font-bold">{selectedAudit.action}</span>
              </div>
              <div className="p-3 rounded-xl bg-[#0C110E] border border-[#263129]">
                <span className="text-[#9BA8A0] block text-[11px]">Target Object</span>
                <span className="font-mono-tech text-[#40D9E8] font-bold">{selectedAudit.objectId}</span>
              </div>
            </div>

            <div className="pt-2 flex justify-end">
              <button
                onClick={() => setSelectedAudit(null)}
                className="px-4 py-2 rounded-xl bg-[#161D19] hover:bg-[#263129] text-xs font-semibold text-[#F3F7F4]"
              >
                Close Audit Inspector
              </button>
            </div>
          </div>
        </div>
      )}
    </AppShell>
  );
};
