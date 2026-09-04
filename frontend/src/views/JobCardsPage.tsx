import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { AppShell } from '../components/common/AppShell';
import { PriorityBadge, JobCardStatusBadge } from '../components/common/StatusBadge';
import { jobCardsApi } from '../services/jobCardsApi';
import { JobCard } from '../types';
import { ROUTES } from '../config/routes';
import { FileCheck, ArrowRight, Printer, Plus } from 'lucide-react';

export const JobCardsPage: React.FC = () => {
  const navigate = useNavigate();
  const [jobCards, setJobCards] = useState<JobCard[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      try {
        const data = await jobCardsApi.getJobCards();
        setJobCards(data);
      } catch (err) {
        console.error('Failed to load job cards', err);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  return (
    <AppShell currentRole="analyst">
      <div className="flex items-center justify-between p-5 rounded-xl bg-[#101512] border border-[#263129]">
        <div>
          <h1 className="text-xl font-extrabold text-[#F3F7F4] font-heading flex items-center gap-2">
            <FileCheck className="w-5 h-5 text-[#B6F542]" /> Operational Job-Cards
          </h1>
          <p className="text-xs text-[#9BA8A0] mt-0.5">
            Issued inspection job-cards dispatched to field squads
          </p>
        </div>
      </div>

      <div className="p-5 rounded-xl bg-[#101512] border border-[#263129] space-y-4">
        {loading ? (
          <div className="p-12 text-center text-xs text-[#9BA8A0] animate-pulse">
            Loading operational job-cards...
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-[#0C110E] text-[#9BA8A0] uppercase font-mono-tech border-b border-[#263129]">
                <tr>
                  <th className="p-3">Job-Card ID</th>
                  <th className="p-3">Consumer & Meter</th>
                  <th className="p-3">Feeder / PMT</th>
                  <th className="p-3">Priority</th>
                  <th className="p-3">Assigned Squad</th>
                  <th className="p-3">Scheduled Date</th>
                  <th className="p-3">Status</th>
                  <th className="p-3">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#263129]/60">
                {jobCards.map((jc) => (
                  <tr
                    key={jc.id}
                    onClick={() => navigate(ROUTES.ANALYST.JOB_CARD_DETAIL(jc.id))}
                    className="hover:bg-[#161D19] cursor-pointer transition-colors"
                  >
                    <td className="p-3 font-mono-tech text-[#B6F542] font-bold">{jc.id}</td>
                    <td className="p-3">
                      <div className="font-mono-tech text-[#F3F7F4] font-bold">{jc.consumerId}</div>
                      <div className="text-[11px] text-[#9BA8A0] font-mono-tech">{jc.meterId}</div>
                    </td>
                    <td className="p-3 font-mono-tech text-[#9BA8A0]">
                      {jc.feederId} / {jc.pmtId}
                    </td>
                    <td className="p-3">
                      <PriorityBadge priority={jc.priority} />
                    </td>
                    <td className="p-3 text-[#F3F7F4] font-medium">{jc.assignedTeam}</td>
                    <td className="p-3 font-mono-tech text-[#9BA8A0]">{jc.scheduledDate}</td>
                    <td className="p-3">
                      <JobCardStatusBadge status={jc.status} />
                    </td>
                    <td className="p-3">
                      <span className="inline-flex items-center gap-1 text-[#B6F542] font-semibold hover:underline">
                        View / Print <Printer className="w-3.5 h-3.5" />
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
