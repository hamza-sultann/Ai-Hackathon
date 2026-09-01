import React, { useEffect, useState } from 'react';
import { AppShell } from '../components/common/AppShell';
import { adminApi } from '../services/adminApi';
import { SystemConfig } from '../types';
import { ROUTES } from '../config/routes';
import {
  Settings,
  Save,
  CheckCircle2,
  Sliders,
  ShieldCheck,
  Zap,
  Clock,
  Bell,
  RefreshCw,
} from 'lucide-react';

export const AdminConfigPage: React.FC = () => {
  const [config, setConfig] = useState<SystemConfig | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);

  useEffect(() => {
    async function loadConfig() {
      try {
        const data = await adminApi.getConfig();
        setConfig(data);
      } catch (err) {
        console.error('Failed to load system configuration', err);
      } finally {
        setLoading(false);
      }
    }
    loadConfig();
  }, []);

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!config) return;
    setSaving(true);
    try {
      const res = await adminApi.updateConfig(config);
      setConfig(res.config);
      setSaveSuccess(true);
      setTimeout(() => setSaveSuccess(false), 3500);
    } catch (err) {
      console.error('Failed to save configuration', err);
    } finally {
      setSaving(false);
    }
  };

  if (loading || !config) {
    return (
      <AppShell currentRole="admin" hidePrototypeBanner compactBanner>
        <div className="p-16 text-center text-xs text-[#9BA8A0] animate-pulse">
          Loading System Configuration & Anomaly Parameters...
        </div>
      </AppShell>
    );
  }

  return (
    <AppShell
      currentRole="admin"
      hidePrototypeBanner
      compactBanner
      breadcrumbsItems={[
        { label: 'Admin Ops', href: ROUTES.ADMIN.ROOT },
        { label: 'System Configuration' },
      ]}
    >
      {/* Header */}
      <div className="holo-card p-6 rounded-2xl bg-[#101512] border border-[#263129] flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl lg:text-2xl font-bold text-[#F3F7F4] font-heading tracking-tight flex items-center gap-2.5">
            <Settings className="w-5 h-5 text-[#F5B942]" /> System Configuration & AI Parameters
          </h1>
          <p className="text-xs text-[#9BA8A0] mt-1">
            Fine-tune machine learning thresholds, TreeSHAP feature depth, safeguard enforcement, and batch orchestration.
          </p>
        </div>
      </div>

      {saveSuccess && (
        <div className="p-4 rounded-2xl bg-[#63D98A]/10 border border-[#63D98A]/30 text-xs text-[#63D98A] flex items-center gap-2 animate-fadeIn">
          <CheckCircle2 className="w-4 h-4 shrink-0" />
          <span>System configuration parameters updated and applied across inference engines.</span>
        </div>
      )}

      <form onSubmit={handleSave} className="space-y-6">
        {/* ML Anomaly Thresholds */}
        <div className="p-6 rounded-2xl bg-[#101512] border border-[#263129] space-y-6">
          <h2 className="text-base font-bold text-[#F3F7F4] font-heading flex items-center gap-2">
            <Sliders className="w-4 h-4 text-[#B6F542]" /> Machine Learning & Physics Thresholds
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Calibrated Risk */}
            <div className="p-4 rounded-xl bg-[#0C110E] border border-[#263129] space-y-3">
              <div className="flex items-center justify-between">
                <label className="text-xs font-bold text-[#F3F7F4]">
                  Calibrated Risk High-Priority Cutoff
                </label>
                <span className="font-mono-tech text-sm font-bold text-[#B6F542]">
                  {config.calibratedRiskThreshold}%
                </span>
              </div>
              <input
                type="range"
                min="50"
                max="95"
                step="1"
                value={config.calibratedRiskThreshold}
                onChange={(e) =>
                  setConfig({ ...config, calibratedRiskThreshold: Number(e.target.value) })
                }
                className="w-full accent-[#B6F542] cursor-pointer"
              />
              <p className="text-[11px] text-[#9BA8A0]">
                Connections with calibrated probability above this threshold trigger High Priority investigation job-cards.
              </p>
            </div>

            {/* TreeSHAP Top Features */}
            <div className="p-4 rounded-xl bg-[#0C110E] border border-[#263129] space-y-3">
              <div className="flex items-center justify-between">
                <label className="text-xs font-bold text-[#F3F7F4]">
                  TreeSHAP Top Explanatory Features
                </label>
                <span className="font-mono-tech text-sm font-bold text-[#40D9E8]">
                  {config.treeShapTopFeaturesCount} Features
                </span>
              </div>
              <input
                type="range"
                min="2"
                max="8"
                step="1"
                value={config.treeShapTopFeaturesCount}
                onChange={(e) =>
                  setConfig({ ...config, treeShapTopFeaturesCount: Number(e.target.value) })
                }
                className="w-full accent-[#40D9E8] cursor-pointer"
              />
              <p className="text-[11px] text-[#9BA8A0]">
                Number of top feature contributions included in the forensic explainability summary.
              </p>
            </div>

            {/* PMT Loss Tolerance */}
            <div className="p-4 rounded-xl bg-[#0C110E] border border-[#263129] space-y-3">
              <div className="flex items-center justify-between">
                <label className="text-xs font-bold text-[#F3F7F4]">
                  PMT Unaccounted Residual Flagging Rate
                </label>
                <span className="font-mono-tech text-sm font-bold text-[#FF6262]">
                  {config.pmtLossAlertThresholdPercentage}%
                </span>
              </div>
              <input
                type="range"
                min="5"
                max="25"
                step="1"
                value={config.pmtLossAlertThresholdPercentage}
                onChange={(e) =>
                  setConfig({ ...config, pmtLossAlertThresholdPercentage: Number(e.target.value) })
                }
                className="w-full accent-[#FF6262] cursor-pointer"
              />
              <p className="text-[11px] text-[#9BA8A0]">
                Transformers with non-technical loss exceeding this percentage are flagged as High-Priority PMTs.
              </p>
            </div>

            {/* Safeguard Strictness */}
            <div className="p-4 rounded-xl bg-[#0C110E] border border-[#263129] space-y-3">
              <label className="text-xs font-bold text-[#F3F7F4] block">
                Responsible AI Safeguard Enforcement
              </label>
              <div className="grid grid-cols-3 gap-2">
                {(['Strict', 'Standard', 'Permissive'] as const).map((mode) => (
                  <button
                    type="button"
                    key={mode}
                    onClick={() => setConfig({ ...config, safeguardMode: mode })}
                    className={`py-2 px-3 rounded-lg text-xs font-semibold transition-all ${
                      config.safeguardMode === mode
                        ? 'bg-[#F5B942] text-[#070A09] font-bold'
                        : 'bg-[#161D19] text-[#9BA8A0] hover:text-[#F3F7F4]'
                    }`}
                  >
                    {mode}
                  </button>
                ))}
              </div>
              <p className="text-[11px] text-[#9BA8A0]">
                Strict mode mandates all 6 automated sanity checks (solar prosumer, feeder outages, data packet health).
              </p>
            </div>
          </div>
        </div>

        {/* Batch Scheduling & Notifications */}
        <div className="p-6 rounded-2xl bg-[#101512] border border-[#263129] space-y-4">
          <h2 className="text-base font-bold text-[#F3F7F4] font-heading flex items-center gap-2">
            <Clock className="w-4 h-4 text-[#40D9E8]" /> Pipeline Execution & Alerts
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
            <div>
              <label className="text-[#9BA8A0] block mb-1">Batch Run Cron Schedule</label>
              <input
                type="text"
                value={config.batchScheduleCron}
                onChange={(e) => setConfig({ ...config, batchScheduleCron: e.target.value })}
                className="w-full p-2.5 bg-[#0C110E] border border-[#263129] rounded-xl text-[#F3F7F4] font-mono-tech focus:outline-none focus:border-[#40D9E8]"
              />
            </div>

            <div className="flex items-center justify-between p-3.5 rounded-xl bg-[#0C110E] border border-[#263129]">
              <div>
                <span className="font-bold text-[#F3F7F4] block">High Residual Alerts</span>
                <span className="text-[11px] text-[#9BA8A0]">Push notifications on PMT deficit surge</span>
              </div>
              <input
                type="checkbox"
                checked={config.notifyOnHighPriorityResidual}
                onChange={(e) =>
                  setConfig({ ...config, notifyOnHighPriorityResidual: e.target.checked })
                }
                className="w-4 h-4 accent-[#B6F542] cursor-pointer"
              />
            </div>
          </div>
        </div>

        {/* Save Bar */}
        <div className="flex justify-end gap-3">
          <button
            type="submit"
            disabled={saving}
            className="flex items-center gap-2 px-6 py-2.5 bg-[#B6F542] hover:bg-[#CAFF69] text-[#070A09] text-xs font-bold rounded-xl transition-all shadow-md active:scale-95 disabled:opacity-50"
          >
            <Save className="w-4 h-4" />
            <span>{saving ? 'Saving System Parameters...' : 'Save Configuration Changes'}</span>
          </button>
        </div>
      </form>
    </AppShell>
  );
};
