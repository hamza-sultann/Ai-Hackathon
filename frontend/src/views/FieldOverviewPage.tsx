import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { AppShell } from '../components/common/AppShell';
import { MetricCard } from '../components/common/MetricCard';
import { PriorityBadge, JobCardStatusBadge } from '../components/common/StatusBadge';
import { fieldApi } from '../services/fieldApi';
import { JobCard } from '../types';
import { ROUTES } from '../config/routes';
import {
  HardHat,
  ArrowRight,
  MapPin,
  ShieldAlert,
  AlertTriangle,
  Info,
} from 'lucide-react';

export const FieldOverviewPage: React.FC = () => {
  const navigate = useNavigate();
  const [stats, setStats] = useState<any>(null);
  const [assignedJobs, setAssignedJobs] = useState<JobCard[]>([]);
  const [loading, setLoading] = useState(true);
  const [showSquadDetails, setShowSquadDetails] = useState(false);

  useEffect(() => {
    async function loadData() {
      try {
        const [stData, jobsData] = await Promise.all([
          fieldApi.getFieldOverviewStats(),
          fieldApi.getAssignedJobs(),
        ]);
        setStats(stData);
        setAssignedJobs(jobsData);
      } catch (err) {
        console.error('Failed to load field overview', err);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  if (loading || !stats) {
    return (
      <AppShell currentRole="field" hidePrototypeBanner compactBanner>
        <div className="p-16 text-center text-xs text-[#9BA8A0] animate-pulse">
          Loading Field Squad Telemetry & Route Operations...
        </div>
      </AppShell>
    );
  }

  return (
    <AppShell currentRole="field" hidePrototypeBanner compactBanner>
      {/* Top Squad & Operational Status Header */}
      <div className="holo-card p-6 rounded-2xl bg-[#101512] border border-[#263129] flex flex-col lg:flex-row lg:items-center justify-between gap-6">
        <div className="space-y-1.5">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-xl bg-[#40D9E8]/10 border border-[#40D9E8]/30 flex items-center justify-center text-[#40D9E8]">
              <HardHat className="w-5 h-5" />
            </div>
            <h1 className="text-xl lg:text-2xl font-bold text-[#F3F7F4] font-heading tracking-tight">
              Field Inspector & Supervisor Command
            </h1>
          </div>
          <div className="text-xs text-[#9BA8A0] flex items-center gap-2 relative">
            <span>Squad: <strong className="text-[#F3F7F4] font-mono-tech">Squad Alpha (Faisalabad West)</strong></span>
            <span>•</span>
            <button
              onClick={() => setShowSquadDetails(!showSquadDetails)}
              className="text-[#40D9E8] hover:underline font-semibold flex items-center gap-1 cursor-pointer"
            >
              <span>Squad Details</span>
              <Info className="w-3.5 h-3.5" />
            </button>

            {showSquadDetails && (
              <div className="absolute left-48 top-full mt-2 w-64 p-3.5 bg-[#161D19] border border-[#263129] rounded-xl text-xs text-[#F3F7F4] shadow-2xl z-50 animate-fadeIn space-y-2">
                <div className="font-bold text-[#40D9E8] border-b border-[#263129] pb-1.5 font-mono-tech flex items-center justify-between">
                  <span>Squad Alpha Metadata</span>
                  <button onClick={() => setShowSquadDetails(false)} className="text-[#9BA8A0] hover:text-[#F3F7F4]">✕</button>
                </div>
                <div className="space-y-1.5 text-[11px] text-[#9BA8A0]">
                  <div>Lead: <strong className="text-[#F3F7F4]">Engr. Tariq Mahmood</strong></div>
                  <div>Vehicle: <strong className="text-[#F3F7F4] font-mono-tech">FBD-7001</strong></div>
                  <div className="flex items-center gap-1.5 pt-1.5 border-t border-[#263129]/60">
                    <MapPin className="w-3.5 h-3.5 text-[#63D98A]" />
                    <span>GPS Geofence: <strong className="text-[#63D98A]">Sector G-2 Active</strong></span>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>

        <div className="flex items-center gap-2.5">
          <button
            onClick={() => navigate(ROUTES.FIELD.JOBS)}
            className="flex items-center gap-1.5 px-4 py-2 bg-[#40D9E8] hover:bg-[#68E3EE] text-[#070A09] rounded-xl text-xs font-bold transition-all shadow-sm active:scale-95"
          >
            <span>View All Assigned Jobs</span>
            <ArrowRight className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Field Performance KPI Cards */}
      <div className="grid grid-cols-2 sm:grid-cols-5 gap-4">
        <MetricCard label="Assigned Today" value={stats.assignedToday} unit="Jobs" />
        <MetricCard label="High Priority" value={stats.highPriority} unit="Jobs" accentColor="#FF6262" />
        <MetricCard label="In Progress" value={stats.inProgress} unit="Jobs" accentColor="#40D9E8" />
        <MetricCard label="Awaiting Review" value={stats.awaitingReview} unit="Jobs" accentColor="#FF9F43" />
        <MetricCard label="Completed Today" value={stats.completedToday} unit="Jobs" accentColor="#63D98A" />
      </div>

      {/* Urgent Field Dispatches Table */}
      <div className="p-6 rounded-2xl bg-[#101512] border border-[#263129] space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-base font-bold text-[#F3F7F4] font-heading flex items-center gap-2">
              <AlertTriangle className="w-4 h-4 text-[#FF6262]" /> Urgent Priority Dispatches
            </h2>
            <p className="text-xs text-[#9BA8A0] mt-0.5">
              High-priority anomalous connections requiring immediate physical verification.
            </p>
          </div>
          <button
            onClick={() => navigate(ROUTES.FIELD.JOBS)}
            className="text-xs font-semibold text-[#40D9E8] hover:underline flex items-center gap-1"
          >
            <span>Full Job Queue</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-[#0C110E] text-[#9BA8A0] uppercase font-mono-tech border-b border-[#263129]">
              <tr>
                <th className="p-3.5">Job ID</th>
                <th className="p-3.5">Consumer ID</th>
                <th className="p-3.5">Service Area</th>
                <th className="p-3.5">Priority</th>
                <th className="p-3.5">Scheduled Date</th>
                <th className="p-3.5">Status</th>
                <th className="p-3.5 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#263129]/60">
              {assignedJobs.map((job) => (
                <tr
                  key={job.id}
                  onClick={() => navigate(ROUTES.FIELD.JOB_DETAIL(job.id))}
                  className="hover:bg-[#161D19] cursor-pointer transition-colors"
                >
                  <td className="p-3.5 font-mono-tech text-[#40D9E8] font-bold">{job.id}</td>
                  <td className="p-3.5 font-mono-tech text-[#F3F7F4] font-bold">{job.consumerId}</td>
                  <td className="p-3.5 text-[#9BA8A0]">{job.serviceArea}</td>
                  <td className="p-3.5">
                    <PriorityBadge priority={job.priority} />
                  </td>
                  <td className="p-3.5 font-mono-tech text-[#9BA8A0]">{job.scheduledDate}</td>
                  <td className="p-3.5">
                    <JobCardStatusBadge status={job.status} />
                  </td>
                  <td className="p-3.5 text-right">
                    <span className="inline-flex items-center gap-1 px-3 py-1 rounded-lg bg-[#40D9E8]/10 text-[#40D9E8] border border-[#40D9E8]/30 font-semibold hover:bg-[#40D9E8] hover:text-[#070A09] transition-colors">
                      Record Findings <ArrowRight className="w-3.5 h-3.5" />
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Field Inspection Protocol & Safety Checklist */}
      <div className="p-5 rounded-2xl bg-[#0C110E] border border-[#263129] flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="flex items-start gap-3">
          <div className="w-8 h-8 rounded-lg bg-[#B6F542]/10 border border-[#B6F542]/30 flex items-center justify-center text-[#B6F542] shrink-0 mt-0.5">
            <ShieldAlert className="w-4 h-4" />
          </div>
          <div>
            <h4 className="text-xs font-bold text-[#F3F7F4]">Mandatory Field Verification Protocol</h4>
            <p className="text-xs text-[#9BA8A0] mt-0.5">
              Always record clamp-meter load before opening meter enclosure. Photograph intact seals and terminal blocks prior to seal breaking.
            </p>
          </div>
        </div>
        <div className="shrink-0 flex items-center gap-2">
          <span className="text-[11px] font-mono-tech text-[#63D98A] bg-[#63D98A]/10 px-3 py-1.5 rounded-lg border border-[#63D98A]/20">
            Standard SOP 4.2 Active
          </span>
        </div>
      </div>
    </AppShell>
  );
};

