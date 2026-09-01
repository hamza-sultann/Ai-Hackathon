import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { AppShell } from '../components/common/AppShell';
import { PriorityBadge, JobCardStatusBadge } from '../components/common/StatusBadge';
import { fieldApi } from '../services/fieldApi';
import { JobCard, Priority, JobCardStatus } from '../types';
import { ROUTES } from '../config/routes';
import {
  HardHat,
  Search,
  ArrowRight,
  Calendar,
  MapPin,
  FileCheck2,
} from 'lucide-react';

export const FieldJobsPage: React.FC = () => {
  const navigate = useNavigate();
  const [jobs, setJobs] = useState<JobCard[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [priorityFilter, setPriorityFilter] = useState<'All' | Priority>('All');
  const [statusFilter, setStatusFilter] = useState<'All' | JobCardStatus>('All');
  const [openEvidenceJobId, setOpenEvidenceJobId] = useState<string | null>(null);

  useEffect(() => {
    async function loadData() {
      try {
        const data = await fieldApi.getAssignedJobs();
        setJobs(data);
      } catch (err) {
        console.error('Failed to load assigned jobs', err);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  const getFieldInstruction = (text: string) => {
    const lower = text.toLowerCase();
    if (lower.includes('peak') || lower.includes('18:00')) {
      return 'Unusual peak-hour drop — check meter and wiring.';
    }
    if (lower.includes('night') || lower.includes('01:00') || lower.includes('off-peak')) {
      return 'Off-peak drop — inspect terminal block and switch.';
    }
    return 'Consumption anomaly — verify meter seals and wiring.';
  };

  const filteredJobs = jobs.filter((job) => {
    const matchesSearch =
      job.id.toLowerCase().includes(searchQuery.toLowerCase()) ||
      job.consumerId.toLowerCase().includes(searchQuery.toLowerCase()) ||
      job.meterId.toLowerCase().includes(searchQuery.toLowerCase()) ||
      job.serviceArea.toLowerCase().includes(searchQuery.toLowerCase());

    const matchesPriority = priorityFilter === 'All' || job.priority === priorityFilter;
    const matchesStatus = statusFilter === 'All' || job.status === statusFilter;

    return matchesSearch && matchesPriority && matchesStatus;
  });

  return (
    <AppShell
      currentRole="field"
      hidePrototypeBanner
      compactBanner
      breadcrumbsItems={[
        { label: 'Field Workspace', href: ROUTES.FIELD.ROOT },
        { label: 'Assigned Job-Cards' },
      ]}
    >
      {/* Header */}
      <div className="holo-card p-6 rounded-2xl bg-[#101512] border border-[#263129] flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl lg:text-2xl font-bold text-[#F3F7F4] font-heading tracking-tight flex items-center gap-2.5">
            <HardHat className="w-5 h-5 text-[#40D9E8]" /> Assigned Field Job-Cards
          </h1>
          <p className="text-xs text-[#9BA8A0] mt-1">
            Active inspection orders assigned to Squad Alpha with physical verification checklists & AI diagnostic evidence.
          </p>
        </div>
        <div className="flex items-center gap-2 font-mono-tech text-xs text-[#9BA8A0] px-3.5 py-2 rounded-xl bg-[#0C110E] border border-[#263129]">
          <span>Total Assigned:</span>
          <span className="font-bold text-[#40D9E8]">{jobs.length}</span>
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
              placeholder="Search by Job ID (JC-2026-081), Consumer (C-08124), Meter, Area..."
              className="w-full pl-10 pr-4 py-2 bg-[#0C110E] border border-[#263129] rounded-xl text-xs text-[#F3F7F4] placeholder-[#9BA8A0]/60 focus:outline-none focus:border-[#40D9E8] transition-colors font-mono-tech"
            />
          </div>

          {/* Priority Filter */}
          <div className="flex items-center gap-1 bg-[#0C110E] p-1 rounded-xl border border-[#263129] text-xs">
            <span className="px-2 text-[11px] text-[#9BA8A0] font-mono-tech">Priority:</span>
            {(['All', 'High', 'Medium', 'Low'] as const).map((p) => (
              <button
                key={p}
                onClick={() => setPriorityFilter(p)}
                className={`px-3 py-1 rounded-lg text-xs font-semibold transition-all ${
                  priorityFilter === p
                    ? 'bg-[#40D9E8] text-[#070A09]'
                    : 'text-[#9BA8A0] hover:text-[#F3F7F4] hover:bg-[#161D19]'
                }`}
              >
                {p}
              </button>
            ))}
          </div>
        </div>

        {/* Status Pills */}
        <div className="flex flex-wrap items-center gap-1.5 pt-2 border-t border-[#263129]/60 text-xs">
          <span className="text-[11px] text-[#9BA8A0] font-mono-tech mr-2">Status:</span>
          {(['All', 'Assigned', 'In Progress', 'Submitted', 'Closed'] as const).map((st) => (
            <button
              key={st}
              onClick={() => setStatusFilter(st as any)}
              className={`px-3 py-1 rounded-lg text-xs font-medium transition-all ${
                statusFilter === st
                  ? 'bg-[#161D19] text-[#40D9E8] border border-[#40D9E8]/40 font-bold'
                  : 'text-[#9BA8A0] hover:text-[#F3F7F4] bg-[#0C110E] border border-[#263129]'
              }`}
            >
              {st}
            </button>
          ))}
        </div>
      </div>

      {/* Jobs List Grid */}
      {loading ? (
        <div className="p-16 text-center text-xs text-[#9BA8A0] animate-pulse">
          Loading Assigned Field Job Cards...
        </div>
      ) : filteredJobs.length === 0 ? (
        <div className="p-16 rounded-2xl bg-[#101512] border border-[#263129] text-center space-y-2">
          <FileCheck2 className="w-8 h-8 text-[#9BA8A0] mx-auto opacity-50" />
          <h3 className="text-sm font-bold text-[#F3F7F4]">No Job Cards Found</h3>
          <p className="text-xs text-[#9BA8A0]">Try adjusting your search query or filter settings.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {filteredJobs.map((job) => (
            <div
              key={job.id}
              onClick={() => navigate(ROUTES.FIELD.JOB_DETAIL(job.id))}
              className="p-5 rounded-2xl bg-[#101512] border border-[#263129] hover:border-[#40D9E8]/50 hover:bg-[#161D19] transition-all cursor-pointer group flex flex-col justify-between space-y-4"
            >
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className="font-mono-tech text-sm font-bold text-[#40D9E8] group-hover:text-[#68E3EE]">
                      {job.id}
                    </span>
                    <PriorityBadge priority={job.priority} />
                  </div>
                  <JobCardStatusBadge status={job.status} />
                </div>

                <div className="grid grid-cols-2 gap-2 text-xs pt-1">
                  <div>
                    <span className="text-[#9BA8A0] text-[11px] block">Consumer ID</span>
                    <span className="font-mono-tech font-bold text-[#F3F7F4]">{job.consumerId}</span>
                  </div>
                  <div>
                    <span className="text-[#9BA8A0] text-[11px] block">Meter Serial</span>
                    <span className="font-mono-tech text-[#F3F7F4]">{job.meterId}</span>
                  </div>
                </div>

                {/* Plain-Language Field Instruction & Evidence Popover */}
                <div className="p-3 rounded-xl bg-[#0C110E] border border-[#263129]/60 text-xs space-y-1.5">
                  <div className="flex items-center justify-between text-[10px] font-mono-tech text-[#40D9E8] font-bold uppercase">
                    <span>Field Instruction</span>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        setOpenEvidenceJobId(openEvidenceJobId === job.id ? null : job.id);
                      }}
                      className="text-[#40D9E8] hover:underline font-semibold flex items-center gap-1 cursor-pointer normal-case text-[11px]"
                    >
                      <span>Full Evidence →</span>
                    </button>
                  </div>
                  <p className="text-[#F3F7F4] font-medium leading-relaxed">
                    {getFieldInstruction(job.evidenceSummary)}
                  </p>

                  {openEvidenceJobId === job.id && (
                    <div
                      onClick={(e) => e.stopPropagation()}
                      className="mt-2 p-2.5 rounded-lg bg-[#161D19] border border-[#40D9E8]/40 text-xs space-y-1 animate-fadeIn"
                    >
                      <div className="flex items-center justify-between text-[10px] font-mono-tech text-[#40D9E8] font-bold uppercase">
                        <span>Supervisor Reference (Full AI Evidence)</span>
                        <button onClick={() => setOpenEvidenceJobId(null)} className="text-[#9BA8A0] hover:text-[#F3F7F4]">✕</button>
                      </div>
                      <p className="text-[#9BA8A0] text-[11px] leading-relaxed font-sans">{job.evidenceSummary}</p>
                    </div>
                  )}
                </div>
              </div>

              <div className="space-y-3 pt-2">
                <div className="flex items-center justify-between text-xs text-[#9BA8A0] font-mono-tech">
                  <span className="flex items-center gap-1.5">
                    <MapPin className="w-3.5 h-3.5 text-[#63D98A]" />
                    <span>{job.serviceArea}</span>
                  </span>
                  <span className="flex items-center gap-1.5">
                    <Calendar className="w-3.5 h-3.5 text-[#B6F542]" />
                    <span>{job.scheduledDate}</span>
                  </span>
                </div>

                <div className="pt-2 border-t border-[#263129] flex items-center justify-between">
                  <span className="text-[11px] text-[#9BA8A0]">
                    Assigned: <strong className="text-[#F3F7F4]">{job.assignedTeam}</strong>
                  </span>
                  <span className="inline-flex items-center gap-1 text-xs font-bold text-[#40D9E8] group-hover:translate-x-1 transition-transform">
                    Inspect & Record <ArrowRight className="w-3.5 h-3.5" />
                  </span>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </AppShell>
  );
};
