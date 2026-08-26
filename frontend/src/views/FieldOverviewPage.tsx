import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { AppShell } from '../components/common/AppShell';
import { MetricCard } from '../components/common/MetricCard';
import { PriorityBadge, JobCardStatusBadge } from '../components/common/StatusBadge';
import { fieldApi } from '../services/fieldApi';
import { JobCard } from '../types';
import { ROUTES } from '../config/routes';
import { HardHat, ArrowRight, CheckCircle, Clock } from 'lucide-react';

export const FieldOverviewPage: React.FC = () => {
  const navigate = useNavigate();
  const [stats, setStats] = useState<any>(null);
  const [assignedJobs, setAssignedJobs] = useState<JobCard[]>([]);
  const [loading, setLoading] = useState(true);

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
      <AppShell currentRole="field">
        <div className="p-12 text-center text-xs text-[#9BA8A0] animate-pulse">
          Loading Field Squad Workload Telemetry...
        </div>
      </AppShell>
    );
  }

  return (
    <AppShell currentRole="field">
      <div className="flex items-center justify-between p-5 rounded-xl bg-[#101512] border border-[#263129]">
        <div>
          <h1 className="text-xl font-extrabold text-[#F3F7F4] font-heading flex items-center gap-2">
            <HardHat className="w-5 h-5 text-[#40D9E8]" /> Field Inspector & Supervisor Dashboard
          </h1>
          <p className="text-xs text-[#9BA8A0] mt-0.5">
            Active Squad: <span className="font-mono-tech text-[#F3F7F4]">Squad Alpha (Faisalabad)</span> • Supervisor Review Active
          </p>
        </div>
      </div>

      {/* Field Overview Metrics */}
      <div className="grid grid-cols-2 sm:grid-cols-5 gap-4">
        <MetricCard label="Assigned Today" value={stats.assignedToday} unit="Jobs" />
        <MetricCard label="High Priority" value={stats.highPriority} unit="Jobs" accentColor="#FF6262" />
        <MetricCard label="In Progress" value={stats.inProgress} unit="Jobs" accentColor="#40D9E8" />
        <MetricCard label="Awaiting Review" value={stats.awaitingReview} unit="Jobs" accentColor="#FF9F43" />
        <MetricCard label="Completed Today" value={stats.completedToday} unit="Jobs" accentColor="#63D98A" />
      </div>

      {/* Assigned Job Queue Table */}
      <div className="p-5 rounded-xl bg-[#101512] border border-[#263129] space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-base font-bold text-[#F3F7F4] font-heading">Assigned Field Job-Cards</h2>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-[#0C110E] text-[#9BA8A0] uppercase font-mono-tech border-b border-[#263129]">
              <tr>
                <th className="p-3">Job ID</th>
                <th className="p-3">Consumer ID</th>
                <th className="p-3">Service Area</th>
                <th className="p-3">Priority</th>
                <th className="p-3">Scheduled Date</th>
                <th className="p-3">Status</th>
                <th className="p-3">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#263129]/60">
              {assignedJobs.map((job) => (
                <tr
                  key={job.id}
                  onClick={() => navigate(ROUTES.FIELD.JOB_DETAIL(job.id))}
                  className="hover:bg-[#161D19] cursor-pointer transition-colors"
                >
                  <td className="p-3 font-mono-tech text-[#40D9E8] font-bold">{job.id}</td>
                  <td className="p-3 font-mono-tech text-[#F3F7F4] font-bold">{job.consumerId}</td>
                  <td className="p-3 text-[#9BA8A0]">{job.serviceArea}</td>
                  <td className="p-3">
                    <PriorityBadge priority={job.priority} />
                  </td>
                  <td className="p-3 font-mono-tech text-[#9BA8A0]">{job.scheduledDate}</td>
                  <td className="p-3">
                    <JobCardStatusBadge status={job.status} />
                  </td>
                  <td className="p-3">
                    <span className="inline-flex items-center gap-1 text-[#40D9E8] font-semibold hover:underline">
                      Record Findings <ArrowRight className="w-3.5 h-3.5" />
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </AppShell>
  );
};
