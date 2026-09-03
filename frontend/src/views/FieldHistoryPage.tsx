import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { AppShell } from '../components/common/AppShell';
import { fieldApi } from '../services/fieldApi';
import { ROUTES } from '../config/routes';
import {
  History,
  Search,
  Filter,
  CheckCircle2,
  AlertTriangle,
  FileCheck,
  ShieldCheck,
  Zap,
  Calendar,
  X,
} from 'lucide-react';

export const FieldHistoryPage: React.FC = () => {
  const navigate = useNavigate();
  const [history, setHistory] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [outcomeFilter, setOutcomeFilter] = useState<string>('All');
  const [selectedRecord, setSelectedRecord] = useState<any | null>(null);

  useEffect(() => {
    async function loadData() {
      try {
        const data = await fieldApi.getInspectionHistory();
        setHistory(data);
      } catch (err) {
        console.error('Failed to load inspection history', err);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  const filteredHistory = history.filter((rec) => {
    const matchesSearch =
      rec.jobCardId.toLowerCase().includes(searchQuery.toLowerCase()) ||
      rec.consumerId.toLowerCase().includes(searchQuery.toLowerCase()) ||
      rec.meterId.toLowerCase().includes(searchQuery.toLowerCase()) ||
      rec.inspectorName.toLowerCase().includes(searchQuery.toLowerCase()) ||
      rec.serviceArea.toLowerCase().includes(searchQuery.toLowerCase());

    const matchesOutcome = outcomeFilter === 'All' || rec.outcome === outcomeFilter;

    return matchesSearch && matchesOutcome;
  });

  return (
    <AppShell
      currentRole="field"
      hidePrototypeBanner
      compactBanner
      breadcrumbsItems={[
        { label: 'Field Workspace', href: ROUTES.FIELD.ROOT },
        { label: 'Inspection History Logs' },
      ]}
    >
      {/* Header */}
      <div className="holo-card p-6 rounded-2xl bg-[#101512] border border-[#263129] flex flex-col md:flex-row md:items-center justify-between gap-4">
        <h1 className="text-xl lg:text-2xl font-bold text-[#F3F7F4] font-heading tracking-tight flex items-center gap-2.5">
          <History className="w-5 h-5 text-[#B6F542]" /> Field Inspection History & Audit Archives
        </h1>
        <div className="flex items-center gap-2 font-mono-tech text-xs text-[#9BA8A0] px-3.5 py-2 rounded-xl bg-[#0C110E] border border-[#263129]">
          <span>Logged Audits:</span>
          <span className="font-bold text-[#B6F542]">{history.length}</span>
        </div>
      </div>

      {/* Filter & Search Bar */}
      <div className="p-4 rounded-2xl bg-[#101512] border border-[#263129] space-y-3">
        <div className="flex flex-col md:flex-row gap-3">
          {/* Search Box */}
          <div className="relative flex-1">
            <Search className="w-4 h-4 text-[#9BA8A0] absolute left-3.5 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search by Job ID, Consumer ID (C-08092), Inspector name, Meter..."
              className="w-full pl-10 pr-4 py-2 bg-[#0C110E] border border-[#263129] rounded-xl text-xs text-[#F3F7F4] placeholder-[#9BA8A0]/60 focus:outline-none focus:border-[#B6F542] transition-colors font-mono-tech"
            />
          </div>

          {/* Outcome Filter */}
          <div className="flex flex-wrap items-center gap-1 bg-[#0C110E] p-1 rounded-xl border border-[#263129] text-xs">
            <span className="px-2 text-[11px] text-[#9BA8A0] font-mono-tech">Outcome:</span>
            {(['All', 'Irregularity Observed', 'Meter Issue', 'Technical Fault', 'No Irregularity Found'] as const).map(
              (oc) => (
                <button
                  key={oc}
                  onClick={() => setOutcomeFilter(oc)}
                  className={`px-3 py-1 rounded-lg text-xs font-semibold transition-all ${
                    outcomeFilter === oc
                      ? 'bg-[#B6F542] text-[#070A09]'
                      : 'text-[#9BA8A0] hover:text-[#F3F7F4] hover:bg-[#161D19]'
                  }`}
                >
                  {oc}
                </button>
              )
            )}
          </div>
        </div>
      </div>

      {/* History Table */}
      <div className="p-6 rounded-2xl bg-[#101512] border border-[#263129] space-y-4">
        {loading ? (
          <div className="p-16 text-center text-xs text-[#9BA8A0] animate-pulse">
            Loading Inspection History Logs...
          </div>
        ) : filteredHistory.length === 0 ? (
          <div className="p-12 text-center text-xs text-[#9BA8A0]">
            No historical inspection records match your filters.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-[#0C110E] text-[#9BA8A0] uppercase font-mono-tech border-b border-[#263129]">
                <tr>
                  <th className="p-3.5">Audit ID / Job</th>
                  <th className="p-3.5">Consumer ID</th>
                  <th className="p-3.5">Inspector</th>
                  <th className="p-3.5">Seal Status</th>
                  <th className="p-3.5">Wiring Condition</th>
                  <th className="p-3.5">Observed Load</th>
                  <th className="p-3.5">Final Outcome</th>
                  <th className="p-3.5">Timestamp</th>
                  <th className="p-3.5 text-right">Details</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#263129]/60">
                {filteredHistory.map((rec) => (
                  <tr key={rec.id} className="hover:bg-[#161D19] transition-colors">
                    <td className="p-3.5">
                      <div className="font-mono-tech font-bold text-[#B6F542]">{rec.id}</div>
                      <span className="text-[10px] font-mono-tech text-[#9BA8A0]">{rec.jobCardId}</span>
                    </td>
                    <td className="p-3.5 font-mono-tech font-bold text-[#F3F7F4]">{rec.consumerId}</td>
                    <td className="p-3.5">
                      <div className="text-[#F3F7F4] font-medium">{rec.inspectorName}</div>
                      <span className="text-[10px] font-mono-tech text-[#9BA8A0]">{rec.squadName}</span>
                    </td>
                    <td className="p-3.5">
                      <span
                        className={`font-mono-tech font-bold ${
                          rec.meterSealCondition === 'Tampered' ? 'text-[#FF6262]' : 'text-[#63D98A]'
                        }`}
                      >
                        {rec.meterSealCondition}
                      </span>
                    </td>
                    <td className="p-3.5">
                      <span
                        className={`font-mono-tech ${
                          rec.wiringCondition === 'Bypassed' ? 'text-[#FF6262] font-bold' : 'text-[#9BA8A0]'
                        }`}
                      >
                        {rec.wiringCondition}
                      </span>
                    </td>
                    <td className="p-3.5 font-mono-tech font-bold text-[#F3F7F4]">{rec.loadObservedKW} kW</td>
                    <td className="p-3.5">
                      <span
                        className={`inline-flex items-center gap-1 px-2.5 py-1 rounded-md text-xs font-semibold ${
                          rec.outcome === 'Irregularity Observed'
                            ? 'bg-[#FF6262]/10 text-[#FF6262] border border-[#FF6262]/30'
                            : rec.outcome === 'Meter Issue'
                            ? 'bg-[#FF9F43]/10 text-[#FF9F43] border border-[#FF9F43]/30'
                            : rec.outcome === 'Technical Fault'
                            ? 'bg-[#40D9E8]/10 text-[#40D9E8] border border-[#40D9E8]/30'
                            : 'bg-[#63D98A]/10 text-[#63D98A] border border-[#63D98A]/30'
                        }`}
                      >
                        {rec.outcome}
                      </span>
                    </td>
                    <td className="p-3.5 font-mono-tech text-[#9BA8A0]">{rec.submittedAt}</td>
                    <td className="p-3.5 text-right">
                      <button
                        onClick={() => setSelectedRecord(rec)}
                        className="px-3 py-1 rounded-lg bg-[#161D19] hover:bg-[#B6F542] hover:text-[#070A09] text-[#B6F542] border border-[#B6F542]/30 text-xs font-semibold transition-colors"
                      >
                        View Notes
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Record Notes Modal */}
      {selectedRecord && (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4 z-50 animate-fadeIn">
          <div className="w-full max-w-xl rounded-2xl bg-[#101512] border border-[#263129] shadow-2xl p-6 space-y-5 animate-slideUp">
            <div className="flex items-center justify-between border-b border-[#263129] pb-4">
              <div>
                <h3 className="text-base font-bold text-[#F3F7F4] font-heading font-mono-tech">
                  {selectedRecord.id} • {selectedRecord.consumerId}
                </h3>
                <p className="text-xs text-[#9BA8A0]">
                  Concluded by {selectedRecord.inspectorName} ({selectedRecord.squadName}) on {selectedRecord.submittedAt}
                </p>
              </div>
              <button
                onClick={() => setSelectedRecord(null)}
                className="p-1.5 rounded-lg text-[#9BA8A0] hover:text-[#F3F7F4] hover:bg-[#161D19]"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="grid grid-cols-2 gap-3 text-xs">
              <div className="p-3 rounded-xl bg-[#0C110E] border border-[#263129]">
                <span className="text-[#9BA8A0] block text-[11px]">Meter Condition</span>
                <span className="font-mono-tech text-[#F3F7F4] font-bold">{selectedRecord.meterCondition}</span>
              </div>
              <div className="p-3 rounded-xl bg-[#0C110E] border border-[#263129]">
                <span className="text-[#9BA8A0] block text-[11px]">Meter Seal</span>
                <span className="font-mono-tech text-[#F3F7F4] font-bold">{selectedRecord.meterSealCondition}</span>
              </div>
              <div className="p-3 rounded-xl bg-[#0C110E] border border-[#263129]">
                <span className="text-[#9BA8A0] block text-[11px]">Wiring State</span>
                <span className="font-mono-tech text-[#F3F7F4] font-bold">{selectedRecord.wiringCondition}</span>
              </div>
              <div className="p-3 rounded-xl bg-[#0C110E] border border-[#263129]">
                <span className="text-[#9BA8A0] block text-[11px]">Measured Load</span>
                <span className="font-mono-tech text-[#F3F7F4] font-bold">{selectedRecord.loadObservedKW} kW</span>
              </div>
            </div>

            <div className="p-4 rounded-xl bg-[#0C110E] border border-[#263129] space-y-2">
              <span className="text-[10px] font-mono-tech uppercase font-bold text-[#B6F542] block">
                Inspector Recorded Field Notes
              </span>
              <p className="text-xs text-[#F3F7F4] leading-relaxed font-sans">
                {selectedRecord.inspectorNotes}
              </p>
            </div>

            <div className="pt-2 flex justify-end">
              <button
                onClick={() => setSelectedRecord(null)}
                className="px-4 py-2 rounded-xl bg-[#161D19] hover:bg-[#263129] text-xs font-semibold text-[#F3F7F4] transition-colors"
              >
                Close Audit Record
              </button>
            </div>
          </div>
        </div>
      )}
    </AppShell>
  );
};
