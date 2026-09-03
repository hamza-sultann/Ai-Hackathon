import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { AppShell } from '../components/common/AppShell';
import { PriorityBadge, CaseStatusBadge } from '../components/common/StatusBadge';
import { investigationApi } from '../services/investigationApi';
import { Investigation, Priority } from '../types';
import { ROUTES } from '../config/routes';
import { Search, Filter, ArrowRight, ShieldCheck, Cpu } from 'lucide-react';

export const InvestigationQueuePage: React.FC = () => {
  const navigate = useNavigate();
  const [investigations, setInvestigations] = useState<Investigation[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [priorityFilter, setPriorityFilter] = useState<string>('All');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      try {
        const data = await investigationApi.getInvestigations();
        setInvestigations(data);
      } catch (err) {
        console.error('Failed to load investigation queue', err);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  const filteredItems = investigations.filter((item) => {
    const matchesSearch =
      item.consumerId.toLowerCase().includes(searchTerm.toLowerCase()) ||
      item.meterId.toLowerCase().includes(searchTerm.toLowerCase()) ||
      item.feederId.toLowerCase().includes(searchTerm.toLowerCase()) ||
      item.pmtId.toLowerCase().includes(searchTerm.toLowerCase());

    const matchesPriority = priorityFilter === 'All' || item.priority === priorityFilter;

    return matchesSearch && matchesPriority;
  });

  return (
    <AppShell currentRole="analyst">
      <div className="flex items-center justify-between p-5 rounded-xl bg-[#101512] border border-[#263129]">
        <div>
          <h1 className="text-xl font-extrabold text-[#F3F7F4] font-heading flex items-center gap-2">
            <Search className="w-5 h-5 text-[#B6F542]" /> Inspection Prioritization Queue
          </h1>
          <p className="text-xs text-[#9BA8A0] mt-0.5">
            Evidence-backed candidate connections recommended for field verification
          </p>
        </div>
      </div>

      {/* Filter & Search Bar */}
      <div className="p-4 rounded-xl bg-[#101512] border border-[#263129] flex flex-col sm:flex-row items-center justify-between gap-4">
        <div className="relative w-full sm:w-80">
          <Search className="w-4 h-4 text-[#9BA8A0] absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Filter by Consumer (C-08124), Meter, PMT..."
            className="w-full pl-9 pr-4 py-2 bg-[#0C110E] border border-[#263129] rounded-lg text-xs text-[#F3F7F4] placeholder-[#9BA8A0]/60 focus:outline-none focus:border-[#B6F542] font-mono-tech"
          />
        </div>

        <div className="flex items-center gap-3 w-full sm:w-auto">
          <div className="flex items-center gap-2 text-xs text-[#9BA8A0]">
            <Filter className="w-4 h-4 text-[#B6F542]" />
            <span>Priority:</span>
          </div>
          <div className="flex gap-1 bg-[#0C110E] p-1 rounded-lg border border-[#263129]">
            {['All', 'High', 'Medium', 'Low'].map((p) => (
              <button
                key={p}
                onClick={() => setPriorityFilter(p)}
                className={`px-3 py-1 rounded-md text-xs font-semibold transition-all ${
                  priorityFilter === p
                    ? 'bg-[#B6F542] text-[#070A09]'
                    : 'text-[#9BA8A0] hover:text-[#F3F7F4]'
                }`}
              >
                {p}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Queue Table */}
      <div className="p-5 rounded-xl bg-[#101512] border border-[#263129] space-y-4">
        {loading ? (
          <div className="p-12 text-center text-xs text-[#9BA8A0] animate-pulse">
            Loading investigation queue...
          </div>
        ) : filteredItems.length === 0 ? (
          <div className="p-12 text-center text-xs text-[#9BA8A0]">
            No candidate connections match your search parameters.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-[#0C110E] text-[#9BA8A0] uppercase font-mono-tech border-b border-[#263129]">
                <tr>
                  <th className="p-3">Consumer ID</th>
                  <th className="p-3">Feeder / PMT</th>
                  <th className="p-3">Inspection Priority</th>
                  <th className="p-3">Calibrated Risk</th>
                  <th className="p-3">Est. Impact</th>
                  <th className="p-3">Pattern</th>
                  <th className="p-3">Evidence Source</th>
                  <th className="p-3">Safeguards</th>
                  <th className="p-3">Status</th>
                  <th className="p-3">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#263129]/60">
                {filteredItems.map((item) => (
                  <tr
                    key={item.id}
                    onClick={() => navigate(ROUTES.ANALYST.CONSUMER_INVESTIGATION(item.consumerId))}
                    className="hover:bg-[#161D19] cursor-pointer transition-colors"
                  >
                    <td className="p-3">
                      <div className="font-mono-tech text-[#F3F7F4] font-bold">{item.consumerId}</div>
                      <div className="text-[11px] text-[#9BA8A0] font-mono-tech">{item.meterId}</div>
                    </td>
                    <td className="p-3 text-[#9BA8A0] font-mono-tech">
                      {item.feederId} / {item.pmtId}
                    </td>
                    <td className="p-3">
                      <PriorityBadge priority={item.priority} />
                    </td>
                    <td className="p-3 font-mono-tech font-bold text-[#FF6262]">
                      {item.calibratedRiskPercentage}% calibrated anomaly risk
                    </td>
                    <td className="p-3 font-mono-tech text-[#F3F7F4]">
                      {item.estimatedImpactKWhMonth} kWh/mo
                    </td>
                    <td className="p-3 text-[#9BA8A0]">{item.patternName}</td>
                    <td className="p-3 font-mono-tech text-[#40D9E8]">{item.evidenceSource}</td>
                    <td className="p-3">
                      <span className="inline-flex items-center gap-1 text-[11px] text-[#63D98A]">
                        <ShieldCheck className="w-3.5 h-3.5" /> {item.safeguardStatus}
                      </span>
                    </td>
                    <td className="p-3">
                      <CaseStatusBadge status={item.caseStatus} />
                    </td>
                    <td className="p-3">
                      <span className="inline-flex items-center gap-1 text-[#B6F542] font-semibold hover:underline">
                        Review <ArrowRight className="w-3.5 h-3.5" />
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </AppShell>
  );
};
