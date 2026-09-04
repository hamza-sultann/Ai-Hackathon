import React, { useState, useEffect } from 'react';
import { X, Play, CheckCircle2, AlertCircle, Loader2 } from 'lucide-react';
import { AnalysisScope, AnalysisPipeline, AnalysisJob } from '../../types';
import { analysisApi } from '../../services/analysisApi';

interface AnalysisDrawerProps {
  isOpen: boolean;
  onClose: () => void;
  onAnalysisCompleted?: () => void;
}

export const AnalysisDrawer: React.FC<AnalysisDrawerProps> = ({
  isOpen,
  onClose,
  onAnalysisCompleted,
}) => {
  const [scope, setScope] = useState<AnalysisScope>('Entire Grid');
  const [pipelines, setPipelines] = useState<AnalysisPipeline>('Both');
  const [activeJob, setActiveJob] = useState<AnalysisJob | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    let timer: any;
    if (activeJob && activeJob.status !== 'completed' && activeJob.status !== 'failed') {
      timer = setInterval(async () => {
        const updated = await analysisApi.getAnalysisStatus(activeJob.id);
        setActiveJob(updated);
        if (updated.status === 'completed') {
          clearInterval(timer);
          onAnalysisCompleted?.();
        }
      }, 1500);
    }
    return () => clearInterval(timer);
  }, [activeJob, onAnalysisCompleted]);

  if (!isOpen) return null;

  const handleStartAnalysis = async () => {
    setIsSubmitting(true);
    try {
      const job = await analysisApi.startAnalysis(scope, pipelines);
      setActiveJob(job);
    } catch (err) {
      console.error('Failed to start analysis', err);
    } finally {
      setIsSubmitting(false);
    }
  };

  const stages = [
    { key: 'validating_data', label: '1. Validating Monthly & Hourly Telemetry Data' },
    { key: 'calculating_pmt_balance', label: '2. Calculating PMT Energy Mass Balance' },
    { key: 'scoring_anomalies', label: '3. Running Isolation Forest Anomaly Scoring' },
    { key: 'calibrating_risk', label: '4. Calibrating Probability via Isotonic Model' },
    { key: 'generating_explanations', label: '5. Computing TreeSHAP Feature Contributions' },
    { key: 'completed', label: '6. Finalizing Operational Inspection Queue' },
  ];

  const getStageStatus = (stageKey: string) => {
    if (!activeJob) return 'pending';
    if (activeJob.status === 'completed') return 'done';

    const order = [
      'validating_data',
      'calculating_pmt_balance',
      'scoring_anomalies',
      'calibrating_risk',
      'generating_explanations',
      'completed',
    ];
    const currentIndex = order.indexOf(activeJob.status);
    const stageIndex = order.indexOf(stageKey);

    if (stageIndex < currentIndex) return 'done';
    if (stageIndex === currentIndex) return 'active';
    return 'pending';
  };

  return (
    <div className="fixed inset-0 z-50 flex justify-end bg-black/60 backdrop-blur-xs transition-opacity">
      <div className="w-full max-w-lg bg-[#0C110E] border-l border-[#263129] h-full flex flex-col justify-between p-6 shadow-2xl overflow-y-auto">
        <div>
          {/* Header */}
          <div className="flex items-center justify-between pb-4 border-b border-[#263129] mb-6">
            <div>
              <h2 className="text-lg font-bold text-[#F3F7F4] font-heading">Run New AI Grid Analysis</h2>
              <p className="text-xs text-[#9BA8A0]">
                Batch inference, PMT residual balance, and TreeSHAP explainability pipeline.
              </p>
            </div>
            <button
              onClick={onClose}
              className="p-1.5 rounded-lg text-[#9BA8A0] hover:text-[#F3F7F4] hover:bg-[#161D19] transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {!activeJob ? (
            /* Setup Form */
            <div className="space-y-6">
              {/* Analysis Period */}
              <div>
                <label className="block text-xs font-semibold text-[#9BA8A0] mb-2 uppercase tracking-wider">
                  Analysis Period
                </label>
                <div className="p-3 bg-[#101512] border border-[#263129] rounded-lg text-xs font-mono-tech text-[#F3F7F4]">
                  Current Period: Aug 2026 (Monthly Sync + Hourly Telemetry)
                </div>
              </div>

              {/* Scope Selection */}
              <div>
                <label className="block text-xs font-semibold text-[#9BA8A0] mb-2 uppercase tracking-wider">
                  Analysis Scope
                </label>
                <div className="grid grid-cols-3 gap-2">
                  {(['Entire Grid', 'Feeder', 'PMT'] as AnalysisScope[]).map((s) => (
                    <button
                      key={s}
                      type="button"
                      onClick={() => setScope(s)}
                      className={`py-2 px-3 rounded-lg text-xs font-semibold border transition-all ${
                        scope === s
                          ? 'bg-[#B6F542] text-[#070A09] border-[#B6F542]'
                          : 'bg-[#101512] text-[#9BA8A0] border-[#263129] hover:bg-[#161D19]'
                      }`}
                    >
                      {s}
                    </button>
                  ))}
                </div>
              </div>

              {/* Pipeline Selection */}
              <div>
                <label className="block text-xs font-semibold text-[#9BA8A0] mb-2 uppercase tracking-wider">
                  Telemetry Pipelines
                </label>
                <div className="grid grid-cols-3 gap-2">
                  {(['Monthly', 'Smart Meter', 'Both'] as AnalysisPipeline[]).map((p) => (
                    <button
                      key={p}
                      type="button"
                      onClick={() => setPipelines(p)}
                      className={`py-2 px-3 rounded-lg text-xs font-semibold border transition-all ${
                        pipelines === p
                          ? 'bg-[#40D9E8] text-[#070A09] border-[#40D9E8]'
                          : 'bg-[#101512] text-[#9BA8A0] border-[#263129] hover:bg-[#161D19]'
                      }`}
                    >
                      {p}
                    </button>
                  ))}
                </div>
              </div>

              {/* Data Validation Note */}
              <div className="p-4 rounded-lg bg-[#101512] border border-[#263129] text-xs text-[#9BA8A0] space-y-2">
                <span className="font-semibold text-[#F3F7F4] flex items-center gap-1.5">
                  <CheckCircle2 className="w-4 h-4 text-[#63D98A]" /> Data Quality Safeguards Pre-Check
                </span>
                <p>
                  10,000 monthly billing accounts ready. 6,840 smart-meter telemetries active. Feeder outage log synced.
                </p>
              </div>
            </div>
          ) : (
            /* Running Progress State */
            <div className="space-y-6">
              <div className="p-4 rounded-xl bg-[#101512] border border-[#263129]">
                <div className="flex items-center justify-between text-xs font-semibold text-[#F3F7F4] mb-2">
                  <span>Job ID: {activeJob.id}</span>
                  <span className="font-mono-tech text-[#B6F542]">{activeJob.progressPercentage}%</span>
                </div>
                <div className="w-full h-2 rounded-full bg-[#161D19] overflow-hidden border border-[#263129]">
                  <div
                    className="h-full bg-gradient-to-r from-[#40D9E8] via-[#B6F542] to-[#63D98A] transition-all duration-500"
                    style={{ width: `${activeJob.progressPercentage}%` }}
                  />
                </div>
              </div>

              {/* Pipeline Stages */}
              <div className="space-y-3">
                <span className="text-xs font-semibold text-[#9BA8A0] uppercase tracking-wider block">
                  Execution Stages
                </span>
                {stages.map((st) => {
                  const status = getStageStatus(st.key);
                  return (
                    <div
                      key={st.key}
                      className={`flex items-center justify-between p-3 rounded-lg border text-xs transition-all ${
                        status === 'active'
                          ? 'bg-[#161D19] border-[#B6F542]/50 text-[#F3F7F4]'
                          : status === 'done'
                          ? 'bg-[#101512] border-[#263129] text-[#9BA8A0]'
                          : 'bg-[#101512]/50 border-[#263129]/50 text-[#9BA8A0]/40'
                      }`}
                    >
                      <span>{st.label}</span>
                      {status === 'active' && <Loader2 className="w-4 h-4 text-[#B6F542] animate-spin" />}
                      {status === 'done' && <CheckCircle2 className="w-4 h-4 text-[#63D98A]" />}
                    </div>
                  );
                })}
              </div>

              {activeJob.status === 'completed' && (
                <div className="space-y-3">
                  <div className="p-4 rounded-lg bg-[#63D98A]/10 border border-[#63D98A]/30 text-xs text-[#63D98A] flex items-center gap-2">
                    <CheckCircle2 className="w-5 h-5 shrink-0" />
                    <span>Analysis batch successfully completed! Operational risk scores &amp; TreeSHAP explanations refreshed.</span>
                  </div>

                  {(activeJob.flaggedCount != null || activeJob.agentDecisions) && (
                    <div className="p-4 rounded-xl bg-[#101512] border border-[#263129] space-y-2 text-xs text-[#9BA8A0]">
                      <span className="font-semibold text-[#F3F7F4] uppercase tracking-wider block">
                        Pipeline Result
                      </span>
                      <div className="grid grid-cols-2 gap-x-4 gap-y-1 font-mono-tech">
                        {activeJob.modelScored && (
                          <><span>Model</span><span className="text-[#F3F7F4]">{activeJob.modelScored}</span></>
                        )}
                        {activeJob.analysisMonth && (
                          <><span>Analysis month</span><span className="text-[#F3F7F4]">{activeJob.analysisMonth}</span></>
                        )}
                        {activeJob.flaggedCount != null && (
                          <><span>Consumers flagged</span><span className="text-[#F5B942]">{activeJob.flaggedCount}</span></>
                        )}
                        {activeJob.agentDecisions && (
                          <>
                            <span>Routed to field</span>
                            <span className="text-[#F3F7F4]">{activeJob.agentDecisions.routedToField}</span>
                            <span>Soft-warning SMS</span>
                            <span className="text-[#F3F7F4]">{activeJob.agentDecisions.softWarning}</span>
                            <span>Suppressed (Confounder)</span>
                            <span className="text-[#F3F7F4]">{activeJob.agentDecisions.suppressedConfounder}</span>
                            <span>Consolidated (dedup)</span>
                            <span className="text-[#F3F7F4]">{activeJob.agentDecisions.consolidatedDuplicate}</span>
                            <span>Repeat-offender flags</span>
                            <span className="text-[#F3F7F4]">{activeJob.agentDecisions.recidivist}</span>
                          </>
                        )}
                        {activeJob.auditEventsWritten != null && (
                          <><span>Audit events written</span><span className="text-[#F3F7F4]">{activeJob.auditEventsWritten}</span></>
                        )}
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>
          )}
        </div>

        {/* Footer Actions */}
        <div className="pt-4 border-t border-[#263129] flex items-center justify-end gap-3">
          {!activeJob ? (
            <>
              <button
                type="button"
                onClick={onClose}
                className="px-4 py-2 rounded-lg text-xs font-semibold text-[#9BA8A0] hover:text-[#F3F7F4] hover:bg-[#161D19] transition-colors"
              >
                Cancel
              </button>
              <button
                type="button"
                disabled={isSubmitting}
                onClick={handleStartAnalysis}
                className="flex items-center gap-2 px-5 py-2 rounded-lg text-xs font-semibold bg-[#B6F542] hover:bg-[#CAFF69] text-[#070A09] transition-all disabled:opacity-50"
              >
                {isSubmitting ? <Loader2 className="w-4 h-4 animate-spin" /> : <Play className="w-4 h-4 fill-current" />}
                <span>Execute Analysis Job</span>
              </button>
            </>
          ) : (
            <button
              type="button"
              onClick={() => {
                setActiveJob(null);
                onClose();
              }}
              className="px-5 py-2 rounded-lg text-xs font-semibold bg-[#161D19] hover:bg-[#263129] text-[#F3F7F4] border border-[#263129] transition-colors"
            >
              {activeJob.status === 'completed' ? 'Close & View Results' : 'Dismiss Panel'}
            </button>
          )}
        </div>
      </div>
    </div>
  );
};
