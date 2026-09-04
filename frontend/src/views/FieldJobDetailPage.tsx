import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { AppShell } from '../components/common/AppShell';
import { PriorityBadge, JobCardStatusBadge } from '../components/common/StatusBadge';
import { ResponsibleUseBanner } from '../components/common/ResponsibleUseBanner';
import { FindingsForm } from '../components/forms/FindingsForm';
import { jobCardsApi } from '../services/jobCardsApi';
import { fieldApi } from '../services/fieldApi';
import { JobCard, InspectionFinding } from '../types';
import { RESPONSIBLE_TERMINOLOGY } from '../config/tokens';
import { ROUTES } from '../config/routes';
import { HardHat, CheckCircle2, AlertCircle, FileCheck, ShieldCheck } from 'lucide-react';

export const FieldJobDetailPage: React.FC = () => {
  const { jobCardId } = useParams<{ jobCardId: string }>();
  const navigate = useNavigate();

  const [jobCard, setJobCard] = useState<JobCard | undefined>(undefined);
  const [existingFinding, setExistingFinding] = useState<InspectionFinding | undefined>(undefined);
  const [loading, setLoading] = useState(true);
  const [submittedMessage, setSubmittedMessage] = useState<string | null>(null);

  useEffect(() => {
    async function loadData() {
      if (jobCardId) {
        try {
          const [card, finding] = await Promise.all([
            jobCardsApi.getJobCardById(jobCardId),
            fieldApi.getFindingByJobCardId(jobCardId),
          ]);
          setJobCard(card);
          setExistingFinding(finding);
        } catch (err) {
          console.error('Failed to load field job details', err);
        } finally {
          setLoading(false);
        }
      }
    }
    loadData();
  }, [jobCardId]);

  if (loading || !jobCard) {
    return (
      <AppShell currentRole="field">
        <div className="p-12 text-center text-xs text-[#9BA8A0] animate-pulse">
          Loading Field Job Details...
        </div>
      </AppShell>
    );
  }

  const breadcrumbs = [
    { label: 'Assigned Jobs', href: ROUTES.FIELD.JOBS },
    { label: jobCard.id },
  ];

  const handleFindingsSubmit = async (finding: InspectionFinding) => {
    try {
      const res = await fieldApi.submitFinding(finding);
      setExistingFinding(finding);
      setSubmittedMessage(res.message);
      await jobCardsApi.updateJobCardStatus(jobCard.id, 'Submitted');
    } catch (err) {
      console.error('Failed to submit inspection findings', err);
    }
  };

  return (
    <AppShell currentRole="field" breadcrumbsItems={breadcrumbs} showBanner={false}>
      <ResponsibleUseBanner message={RESPONSIBLE_TERMINOLOGY.JOB_CARD_DISCLAIMER} />

      {submittedMessage && (
        <div className="p-4 rounded-xl bg-[#63D98A]/10 border border-[#63D98A]/30 text-xs text-[#63D98A] flex items-center gap-2">
          <CheckCircle2 className="w-5 h-5 shrink-0" />
          <span>{submittedMessage}</span>
        </div>
      )}

      {/* Header Info */}
      <div className="p-6 rounded-xl bg-[#101512] border border-[#263129] space-y-4">
        <div className="flex items-center justify-between border-b border-[#263129] pb-4">
          <div>
            <div className="flex items-center gap-3 mb-1">
              <h1 className="text-xl font-extrabold text-[#F3F7F4] font-heading font-mono-tech">
                {jobCard.id}
              </h1>
              <PriorityBadge priority={jobCard.priority} />
              <JobCardStatusBadge status={jobCard.status} />
            </div>
            <p className="text-xs text-[#9BA8A0] font-mono-tech">
              Consumer: <span className="text-[#F3F7F4] font-bold">{jobCard.consumerId}</span> • Meter:{' '}
              <span className="text-[#F3F7F4] font-bold">{jobCard.meterId}</span> • Location:{' '}
              <span className="text-[#F3F7F4]">{jobCard.serviceArea}</span>
            </p>
          </div>
        </div>

        <div className="p-4 bg-[#0C110E] border border-[#263129] rounded-xl text-xs space-y-2">
          <span className="font-bold text-[#40D9E8] block uppercase tracking-wider">
            Evidence Summary for Field Squad
          </span>
          <p className="font-mono-tech text-[#F3F7F4]">{jobCard.evidenceSummary}</p>
        </div>

        {jobCard.fieldAlertUrdu && (
          <div className="p-4 bg-[#0C110E] border border-[#F5B942]/30 rounded-xl text-xs space-y-2">
            <span className="font-bold text-[#F5B942] block uppercase tracking-wider">
              فیلڈ وارننگ (اردو)
            </span>
            <p dir="rtl" lang="ur" className="text-base leading-loose text-right text-[#F3F7F4]">
              {jobCard.fieldAlertUrdu}
            </p>
            {jobCard.fieldAlert && (
              <p className="font-mono-tech text-[#9BA8A0] pt-2 border-t border-[#263129]">
                {jobCard.fieldAlert}
              </p>
            )}
          </div>
        )}
      </div>

      {/* Inspection Findings Submission Form */}
      <div className="p-6 rounded-xl bg-[#101512] border border-[#263129] space-y-4">
        <div className="border-b border-[#263129] pb-3">
          <h2 className="text-base font-bold text-[#F3F7F4] font-heading flex items-center gap-2">
            <HardHat className="w-5 h-5 text-[#40D9E8]" /> Record Field Inspection Findings
          </h2>
          <p className="text-xs text-[#9BA8A0]">
            Complete physical meter seal, wiring, clamp load, and outcome determination.
          </p>
        </div>

        {existingFinding ? (
          <div className="p-4 rounded-xl bg-[#161D19] border border-[#63D98A]/30 space-y-3 text-xs">
            <div className="flex items-center justify-between">
              <span className="font-bold text-[#63D98A] text-sm">Findings Submitted & Locked</span>
              <span className="font-mono-tech text-[#9BA8A0]">{existingFinding.submittedAt}</span>
            </div>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 font-mono-tech text-[#F3F7F4]">
              <div>Seal: {existingFinding.meterSealCondition}</div>
              <div>State: {existingFinding.meterCondition}</div>
              <div>Wiring: {existingFinding.wiringCondition}</div>
              <div>Outcome: {existingFinding.outcome}</div>
            </div>
            <p className="text-[#9BA8A0] pt-2 border-t border-[#263129]">{existingFinding.inspectorNotes}</p>
          </div>
        ) : (
          <FindingsForm
            jobCardId={jobCard.id}
            onSubmit={handleFindingsSubmit}
            onCancel={() => navigate(ROUTES.FIELD.JOBS)}
          />
        )}
      </div>
    </AppShell>
  );
};
