import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { AppShell } from '../components/common/AppShell';
import { PriorityBadge, JobCardStatusBadge } from '../components/common/StatusBadge';
import { jobCardsApi } from '../services/jobCardsApi';
import { JobCard } from '../types';
import { RESPONSIBLE_TERMINOLOGY } from '../config/tokens';
import { ROUTES } from '../config/routes';
import { Printer, Zap, CheckCircle2 } from 'lucide-react';

export const JobCardDetailPage: React.FC = () => {
  const { jobCardId } = useParams<{ jobCardId: string }>();
  const [jobCard, setJobCard] = useState<JobCard | undefined>(undefined);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      if (jobCardId) {
        try {
          const card = await jobCardsApi.getJobCardById(jobCardId);
          setJobCard(card);
        } catch (err) {
          console.error('Failed to load job card details', err);
        } finally {
          setLoading(false);
        }
      }
    }
    loadData();
  }, [jobCardId]);

  if (loading || !jobCard) {
    return (
      <AppShell currentRole="analyst">
        <div className="p-12 text-center text-xs text-[#9BA8A0] animate-pulse">
          Loading Job Card Details...
        </div>
      </AppShell>
    );
  }

  const breadcrumbs = [
    { label: 'Job-Cards', href: ROUTES.ANALYST.JOB_CARDS },
    { label: jobCard.id },
  ];

  return (
    <AppShell currentRole="analyst" breadcrumbsItems={breadcrumbs}>
      {/* Action Bar */}
      <div className="no-print flex items-center justify-between p-4 rounded-xl bg-[#101512] border border-[#263129]">
        <div>
          <h1 className="text-lg font-bold text-[#F3F7F4] font-heading font-mono-tech">{jobCard.id}</h1>
          <p className="text-xs text-[#9BA8A0]">Official Physical Inspection Job-Card</p>
        </div>

        <button
          onClick={() => window.print()}
          className="px-5 py-2.5 rounded-lg bg-[#B6F542] hover:bg-[#CAFF69] text-[#070A09] font-bold text-xs transition-all shadow-md flex items-center gap-2"
        >
          <Printer className="w-4 h-4" />
          <span>Print / Save as PDF</span>
        </button>
      </div>

      {/* Official Printable Area */}
      <div className="print-area p-8 rounded-2xl bg-[#101512] border border-[#263129] space-y-6 text-sm text-[#F3F7F4]">
        {/* Document Header */}
        <div className="flex items-center justify-between border-b border-[#263129] pb-6">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-[#B6F542] text-[#070A09] flex items-center justify-center font-extrabold">
              <Zap className="w-6 h-6 fill-[#070A09]" />
            </div>
            <div>
              <h2 className="text-xl font-extrabold font-heading">ISTIKSHAF GRID INSPECTION JOB-CARD</h2>
              <p className="text-xs font-mono-tech text-[#9BA8A0]">
                Pakistan Electricity Distribution Companies • AI Telemetry Work-Order
              </p>
            </div>
          </div>
          <div className="text-right font-mono-tech">
            <span className="text-lg font-extrabold text-[#B6F542] block">{jobCard.id}</span>
            <span className="text-xs text-[#9BA8A0]">Issued: {jobCard.createdAt}</span>
          </div>
        </div>

        {/* Responsible Use Disclaimer */}
        <div className="p-4 bg-[#161D19] border border-[#263129] rounded-xl text-xs text-[#9BA8A0]">
          <span className="font-bold text-[#F3F7F4] block mb-1">MANDATORY INSPECTION DISCLAIMER:</span>
          {RESPONSIBLE_TERMINOLOGY.JOB_CARD_DISCLAIMER}
        </div>

        {/* Section 1: Consumer & Grid Meta */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-6 p-4 rounded-xl bg-[#0C110E] border border-[#263129]">
          <div>
            <span className="text-xs text-[#9BA8A0] uppercase block">Consumer ID</span>
            <span className="font-mono-tech font-bold text-[#F3F7F4]">{jobCard.consumerId}</span>
          </div>
          <div>
            <span className="text-xs text-[#9BA8A0] uppercase block">Meter ID</span>
            <span className="font-mono-tech font-bold text-[#F3F7F4]">{jobCard.meterId}</span>
          </div>
          <div>
            <span className="text-xs text-[#9BA8A0] uppercase block">Service Area</span>
            <span className="font-semibold text-[#F3F7F4]">{jobCard.serviceArea}</span>
          </div>
          <div>
            <span className="text-xs text-[#9BA8A0] uppercase block">Feeder / PMT</span>
            <span className="font-mono-tech font-semibold text-[#F3F7F4]">
              {jobCard.feederId} / {jobCard.pmtId}
            </span>
          </div>
        </div>

        {/* Section 2: Priority & Assignment */}
        <div className="grid grid-cols-3 gap-6 p-4 rounded-xl bg-[#0C110E] border border-[#263129]">
          <div>
            <span className="text-xs text-[#9BA8A0] uppercase block mb-1">Priority Level</span>
            <PriorityBadge priority={jobCard.priority} />
          </div>
          <div>
            <span className="text-xs text-[#9BA8A0] uppercase block">Assigned Squad</span>
            <span className="font-semibold text-[#F3F7F4]">{jobCard.assignedTeam}</span>
          </div>
          <div>
            <span className="text-xs text-[#9BA8A0] uppercase block">Scheduled Date</span>
            <span className="font-mono-tech text-[#F3F7F4]">{jobCard.scheduledDate}</span>
          </div>
        </div>

        {/* Section 3: Evidence Summary & Relevant Periods */}
        <div className="space-y-4">
          <div>
            <h3 className="text-xs font-bold text-[#9BA8A0] uppercase tracking-wider mb-1">
              AI Telemetry Evidence Summary
            </h3>
            <p className="p-4 bg-[#0C110E] border border-[#263129] rounded-xl text-xs leading-relaxed font-mono-tech text-[#F3F7F4]">
              {jobCard.evidenceSummary}
            </p>
          </div>

          <div>
            <h3 className="text-xs font-bold text-[#9BA8A0] uppercase tracking-wider mb-1">
              Relevant Target Windows
            </h3>
            <p className="p-3 bg-[#0C110E] border border-[#263129] rounded-xl text-xs font-mono-tech text-[#40D9E8]">
              {jobCard.relevantPeriodsText}
            </p>
          </div>

          {(jobCard.fieldAlert || jobCard.fieldAlertUrdu) && (
            <div>
              <h3 className="text-xs font-bold text-[#9BA8A0] uppercase tracking-wider mb-1">
                Field Alert (English / اردو)
              </h3>
              <div className="p-4 bg-[#0C110E] border border-[#263129] rounded-xl text-xs space-y-2">
                {jobCard.fieldAlert && (
                  <p className="font-mono-tech text-[#F3F7F4]">{jobCard.fieldAlert}</p>
                )}
                {jobCard.fieldAlertUrdu && (
                  <p dir="rtl" lang="ur" className="text-sm leading-loose text-right text-[#F3F7F4] pt-2 border-t border-[#263129]">
                    {jobCard.fieldAlertUrdu}
                  </p>
                )}
              </div>
            </div>
          )}
        </div>

        {/* Section 4: Recommended Physical Checks */}
        <div>
          <h3 className="text-xs font-bold text-[#9BA8A0] uppercase tracking-wider mb-2">
            Recommended Physical Site Checks
          </h3>
          <ul className="space-y-2">
            {jobCard.recommendedChecks.map((check, idx) => (
              <li
                key={idx}
                className="flex items-start gap-2 p-3 bg-[#0C110E] border border-[#263129] rounded-lg text-xs"
              >
                <CheckCircle2 className="w-4 h-4 text-[#B6F542] shrink-0 mt-0.5" />
                <span>{check}</span>
              </li>
            ))}
          </ul>
        </div>

        {/* Section 5: Analyst Notes */}
        <div>
          <h3 className="text-xs font-bold text-[#9BA8A0] uppercase tracking-wider mb-1">Analyst Notes</h3>
          <p className="p-3 bg-[#0C110E] border border-[#263129] rounded-xl text-xs text-[#9BA8A0]">
            {jobCard.analystNotes}
          </p>
        </div>

        {/* Section 6: Field Sign-off Blocks */}
        <div className="pt-8 border-t border-[#263129] grid grid-cols-2 gap-8 text-xs font-mono-tech">
          <div className="space-y-6">
            <span>Inspector Signature: _______________________</span>
            <span>Date & Time: _____________________________</span>
          </div>
          <div className="space-y-6">
            <span>Supervisor Approval: ____________________</span>
            <span>Outcome Code: _____________________________</span>
          </div>
        </div>
      </div>
    </AppShell>
  );
};
