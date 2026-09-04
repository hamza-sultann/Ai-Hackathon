import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { AppShell } from '../components/common/AppShell';
import { PriorityBadge, CaseStatusBadge } from '../components/common/StatusBadge';
import { ResponsibleUseBanner } from '../components/common/ResponsibleUseBanner';
import { MonthlyConsumptionChart } from '../components/charts/MonthlyConsumptionChart';
import { HourlyLoadProfileChart } from '../components/charts/HourlyLoadProfileChart';
import { ShapContributionChart } from '../components/charts/ShapContributionChart';
import { JobCardForm } from '../components/forms/JobCardForm';
import { investigationApi } from '../services/investigationApi';
import { jobCardsApi } from '../services/jobCardsApi';
import {
  Investigation,
  RiskExplanation,
  MonthlyReading,
  HourlyReading,
  JobCard,
} from '../types';
import { RESPONSIBLE_TERMINOLOGY } from '../config/tokens';
import { ROUTES } from '../config/routes';
import {
  ShieldCheck,
  Cpu,
  FileCheck,
  Layers,
  Calendar,
  AlertTriangle,
  Clock,
  CheckCircle2,
  X,
  Zap,
} from 'lucide-react';

export const ConsumerInvestigationPage: React.FC = () => {
  const { consumerId } = useParams<{ consumerId: string }>();
  const navigate = useNavigate();

  const targetId = consumerId || 'C-08124';

  const [investigation, setInvestigation] = useState<Investigation | undefined>(undefined);
  const [explanation, setExplanation] = useState<RiskExplanation | null>(null);
  const [monthlyReadings, setMonthlyReadings] = useState<MonthlyReading[]>([]);
  const [hourlyReadings, setHourlyReadings] = useState<HourlyReading[]>([]);
  const [activeTab, setActiveTab] = useState<'monthly' | 'smart_meter' | 'compare'>('compare');
  const [isJobCardModalOpen, setIsJobCardModalOpen] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      setLoading(true);
      try {
        const [inv, exp, monthly, hourly] = await Promise.all([
          investigationApi.getInvestigationByConsumerId(targetId),
          investigationApi.getExplanationByConsumerId(targetId),
          investigationApi.getMonthlyReadings(targetId),
          investigationApi.getHourlyReadings(targetId),
        ]);
        setInvestigation(inv);
        setExplanation(exp);
        setMonthlyReadings(monthly);
        setHourlyReadings(hourly);
      } catch (err) {
        console.error('Failed to load consumer investigation', err);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, [targetId]);

  const breadcrumbs = [
    { label: 'Investigation Queue', href: ROUTES.ANALYST.INVESTIGATIONS },
    { label: targetId },
  ];

  if (loading || !investigation || !explanation) {
    return (
      <AppShell currentRole="analyst">
        <div className="p-12 text-center text-xs text-[#9BA8A0] animate-pulse">
          Loading AI Evidence for Connection {targetId}...
        </div>
      </AppShell>
    );
  }

  const handleCreateJobCardSubmit = async (data: Omit<JobCard, 'id' | 'createdAt' | 'status'>) => {
    try {
      const created = await jobCardsApi.createJobCard(data);
      setIsJobCardModalOpen(false);
      navigate(ROUTES.ANALYST.JOB_CARD_DETAIL(created.id));
    } catch (err) {
      console.error('Failed to issue job card', err);
    }
  };

  return (
    <AppShell currentRole="analyst" breadcrumbsItems={breadcrumbs} showBanner={false}>
      {/* Mandatory Disclaimer */}
      <ResponsibleUseBanner
        message={RESPONSIBLE_TERMINOLOGY.FIELD_VERIFICATION_REQUIRED}
        variant="warning"
      />

      {/* Header Record Summary */}
      <div className="p-6 rounded-xl bg-[#101512] border border-[#263129] space-y-4">
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 border-b border-[#263129] pb-4">
          <div>
            <div className="flex items-center gap-3 mb-1">
              <h1 className="text-2xl font-extrabold text-[#F3F7F4] font-heading font-mono-tech">
                {investigation.consumerId}
              </h1>
              <PriorityBadge priority={investigation.priority} />
              <CaseStatusBadge status={investigation.caseStatus} />
            </div>
            <p className="text-xs text-[#9BA8A0] font-mono-tech">
              Meter ID: <span className="text-[#F3F7F4]">{investigation.meterId}</span> • Feeder:{' '}
              <span className="text-[#F3F7F4]">{investigation.feederId}</span> • PMT:{' '}
              <span className="text-[#F3F7F4]">{investigation.pmtId}</span>
            </p>
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={() => setIsJobCardModalOpen(true)}
              className="px-5 py-2.5 rounded-lg bg-[#B6F542] hover:bg-[#CAFF69] text-[#070A09] font-bold text-xs transition-all shadow-md flex items-center gap-2"
            >
              <FileCheck className="w-4 h-4" />
              <span>Create Inspection Job-Card</span>
            </button>
          </div>
        </div>

        {/* Key Metrics Row */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
          <div className="p-3 bg-[#0C110E] rounded-lg border border-[#FF6262]/30">
            <span className="text-[11px] text-[#9BA8A0] uppercase block">Calibrated Risk</span>
            <span className="text-2xl font-extrabold font-mono-tech text-[#FF6262]">
              {investigation.calibratedRiskPercentage}%
            </span>
            <span className="text-[10px] text-[#9BA8A0] block mt-0.5">calibrated anomaly risk</span>
          </div>

          <div className="p-3 bg-[#0C110E] rounded-lg border border-[#263129]">
            <span className="text-[11px] text-[#9BA8A0] uppercase block">Estimated Impact</span>
            <span className="text-2xl font-extrabold font-mono-tech text-[#F3F7F4]">
              {investigation.estimatedImpactKWhMonth}
            </span>
            <span className="text-[10px] text-[#9BA8A0] block mt-0.5">kWh / month</span>
          </div>

          <div className="p-3 bg-[#0C110E] rounded-lg border border-[#263129]">
            <span className="text-[11px] text-[#9BA8A0] uppercase block">Observed Pattern</span>
            <span className="text-sm font-bold text-[#F5B942] block mt-1">
              {investigation.patternName}
            </span>
          </div>

          <div className="p-3 bg-[#0C110E] rounded-lg border border-[#263129]">
            <span className="text-[11px] text-[#9BA8A0] uppercase block">Evidence Source</span>
            <span className="text-sm font-bold text-[#40D9E8] block mt-1">
              {investigation.evidenceSource}
            </span>
          </div>
        </div>
      </div>

      {/* Tabs Navigation */}
      <div className="flex border-b border-[#263129]">
        <button
          onClick={() => setActiveTab('compare')}
          className={`px-6 py-3 font-bold text-xs border-b-2 transition-all flex items-center gap-2 ${
            activeTab === 'compare'
              ? 'border-[#B6F542] text-[#B6F542] bg-[#161D19]'
              : 'border-transparent text-[#9BA8A0] hover:text-[#F3F7F4]'
          }`}
        >
          <Layers className="w-4 h-4" />
          <span>Evidence Comparison & Synthesis</span>
        </button>

        <button
          onClick={() => setActiveTab('monthly')}
          className={`px-6 py-3 font-bold text-xs border-b-2 transition-all flex items-center gap-2 ${
            activeTab === 'monthly'
              ? 'border-[#F5B942] text-[#F5B942] bg-[#161D19]'
              : 'border-transparent text-[#9BA8A0] hover:text-[#F3F7F4]'
          }`}
        >
          <Calendar className="w-4 h-4" />
          <span>Monthly Billing Pipeline</span>
        </button>

        <button
          onClick={() => setActiveTab('smart_meter')}
          className={`px-6 py-3 font-bold text-xs border-b-2 transition-all flex items-center gap-2 ${
            activeTab === 'smart_meter'
              ? 'border-[#40D9E8] text-[#40D9E8] bg-[#161D19]'
              : 'border-transparent text-[#9BA8A0] hover:text-[#F3F7F4]'
          }`}
        >
          <Zap className="w-4 h-4" />
          <span>Hourly Smart Meter Pipeline</span>
        </button>
      </div>

      {/* Tab Contents */}
      {activeTab === 'compare' && (
        <div className="space-y-6">
          {/* Comparison Cards Grid */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="p-4 rounded-xl bg-[#101512] border border-[#F5B942]/30">
              <span className="text-[11px] text-[#9BA8A0] uppercase block">Monthly Risk</span>
              <span className="text-xl font-extrabold font-mono-tech text-[#F5B942]">
                {investigation.monthlyRiskPercentage}%
              </span>
            </div>
            <div className="p-4 rounded-xl bg-[#101512] border border-[#40D9E8]/30">
              <span className="text-[11px] text-[#9BA8A0] uppercase block">Smart-Meter Risk</span>
              <span className="text-xl font-extrabold font-mono-tech text-[#40D9E8]">
                {investigation.smartMeterRiskPercentage}%
              </span>
            </div>
            <div className="p-4 rounded-xl bg-[#101512] border border-[#63D98A]/30">
              <span className="text-[11px] text-[#9BA8A0] uppercase block">Combined Strength</span>
              <span className="text-xl font-extrabold text-[#63D98A]">
                {investigation.combinedEvidenceStrength}
              </span>
            </div>
            <div className="p-4 rounded-xl bg-[#101512] border border-[#B6F542]/30">
              <span className="text-[11px] text-[#9BA8A0] uppercase block">Pipeline Agreement</span>
              <span className="text-xl font-extrabold text-[#B6F542]">
                {investigation.pipelineAgreement}
              </span>
            </div>
          </div>

          {/* Synthesis Note */}
          <div className="p-5 rounded-xl bg-[#161D19] border border-[#263129] space-y-2">
            <h3 className="text-sm font-bold text-[#F3F7F4] font-heading flex items-center gap-2">
              <Cpu className="w-4 h-4 text-[#B6F542]" /> AI Telemetry Synthesis
            </h3>
            <p className="text-xs text-[#F3F7F4] leading-relaxed font-mono-tech">
              "{explanation.summaryText}"
            </p>
          </div>

          {/* Bilingual Field Warning (English / Urdu) */}
          {(explanation.fieldAlert || explanation.fieldAlertUrdu) && (
            <div className="p-5 rounded-xl bg-[#101512] border border-[#F5B942]/30 space-y-3">
              <h3 className="text-sm font-bold text-[#F3F7F4] font-heading flex items-center gap-2">
                <AlertTriangle className="w-4 h-4 text-[#F5B942]" /> Field Warning (English / اردو)
              </h3>
              {explanation.fieldAlert && (
                <div className="space-y-1">
                  <span className="text-[10px] text-[#9BA8A0] uppercase tracking-wider">English</span>
                  <p className="text-xs text-[#F3F7F4] leading-relaxed font-mono-tech">
                    {explanation.fieldAlert}
                  </p>
                </div>
              )}
              {explanation.fieldAlertUrdu && (
                <div className="space-y-1 pt-2 border-t border-[#263129]">
                  <span className="text-[10px] text-[#9BA8A0] uppercase tracking-wider">اردو</span>
                  <p dir="rtl" lang="ur" className="text-sm text-[#F5B942] leading-loose text-right">
                    {explanation.fieldAlertUrdu}
                  </p>
                </div>
              )}
              <p className="text-[10px] text-[#9BA8A0]">
                Generated by the Urdu localization agent. Inherited by any job-card issued from this investigation.
              </p>
            </div>
          )}

          {/* TreeSHAP Chart & PMT Corroboration */}
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
            <div className="lg:col-span-7">
              <ShapContributionChart contributions={explanation.treeShapContributions} />
            </div>

            {/* Safeguard Checks */}
            <div className="lg:col-span-5 p-5 rounded-xl bg-[#101512] border border-[#263129] space-y-4">
              <h3 className="text-sm font-bold text-[#F3F7F4] font-heading flex items-center gap-2">
                <ShieldCheck className="w-4 h-4 text-[#63D98A]" /> Pre-Inspection Safeguard Checks
              </h3>

              <div className="space-y-3">
                {explanation.safeguards.map((sg) => (
                  <div
                    key={sg.id}
                    className="p-3 rounded-lg bg-[#0C110E] border border-[#263129] text-xs space-y-1"
                  >
                    <div className="flex items-center justify-between font-semibold">
                      <span className="text-[#F3F7F4]">{sg.name}</span>
                      {sg.passed ? (
                        <span className="text-[#63D98A] flex items-center gap-1 text-[11px]">
                          <CheckCircle2 className="w-3.5 h-3.5" /> Passed
                        </span>
                      ) : (
                        <span className="text-[#FF9F43] flex items-center gap-1 text-[11px]">
                          <AlertTriangle className="w-3.5 h-3.5" /> Review
                        </span>
                      )}
                    </div>
                    <p className="text-[11px] text-[#9BA8A0]">{sg.detail}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {activeTab === 'monthly' && (
        <MonthlyConsumptionChart readings={monthlyReadings} />
      )}

      {activeTab === 'smart_meter' && (
        <HourlyLoadProfileChart readings={hourlyReadings} />
      )}

      {/* Modal for Creating Job-Card */}
      {isJobCardModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-xs">
          <div className="bg-[#0C110E] border border-[#263129] rounded-2xl max-w-2xl w-full p-6 space-y-4 shadow-2xl max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between pb-3 border-b border-[#263129]">
              <h2 className="text-lg font-bold text-[#F3F7F4] font-heading">Issue Inspection Job-Card</h2>
              <button
                onClick={() => setIsJobCardModalOpen(false)}
                className="p-1 rounded-lg text-[#9BA8A0] hover:text-[#F3F7F4]"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <JobCardForm
              initialData={{
                consumerId: investigation.consumerId,
                meterId: investigation.meterId,
                feederId: investigation.feederId,
                pmtId: investigation.pmtId,
                priority: investigation.priority,
                estimatedImpactKWhMonth: investigation.estimatedImpactKWhMonth,
                evidenceSummary: explanation.summaryText,
                fieldAlert: explanation.fieldAlert,
                fieldAlertUrdu: explanation.fieldAlertUrdu,
              }}
              onSubmit={handleCreateJobCardSubmit}
              onCancel={() => setIsJobCardModalOpen(false)}
            />
          </div>
        </div>
      )}
    </AppShell>
  );
};
