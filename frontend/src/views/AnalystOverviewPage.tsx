import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { AppShell } from '../components/common/AppShell';
import { MetricCard } from '../components/common/MetricCard';
import { EnergyBalanceChart } from '../components/charts/EnergyBalanceChart';
import { overviewApi } from '../services/overviewApi';
import { gridApi } from '../services/gridApi';
import { SystemOverview, Feeder } from '../types';
import { ROUTES } from '../config/routes';
import {
  ArrowRight,
  Layers,
  Grid,
  Search,
  GitCompare,
  TrendingUp,
  TrendingDown,
  Minus,
  ShieldCheck,
  Zap,
  Activity,
  ChevronRight,
  Cpu,
  BarChart3,
  Info,
} from 'lucide-react';

export const AnalystOverviewPage: React.FC = () => {
  const navigate = useNavigate();
  const [overview, setOverview] = useState<SystemOverview | null>(null);
  const [feeders, setFeeders] = useState<Feeder[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      try {
        const [ovData, feedersData] = await Promise.all([
          overviewApi.getOverview(),
          gridApi.getFeeders(),
        ]);
        setOverview(ovData);
        setFeeders(feedersData);
      } catch (err) {
        console.error('Failed to load analyst overview data', err);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  if (loading || !overview) {
    return (
      <AppShell currentRole="analyst" hidePrototypeBanner compactBanner>
        <div className="p-16 text-center text-xs text-[#9BA8A0] animate-pulse">
          Loading Operator Telemetry & Grid Balance Data...
        </div>
      </AppShell>
    );
  }

  // Calculate high-level energy ratios
  const deliveryEfficiency = ((overview.billedEnergyMWh / overview.injectedEnergyMWh) * 100).toFixed(1);
  const technicalLossRatio = ((overview.estimatedTechnicalLossMWh / overview.injectedEnergyMWh) * 100).toFixed(1);
  const residualLossRatio = ((overview.unaccountedResidualMWh / overview.injectedEnergyMWh) * 100).toFixed(1);

  return (
    <AppShell currentRole="analyst" hidePrototypeBanner compactBanner>
      {/* Top Header Summary Bar */}
      <div className="holo-card p-6 rounded-2xl bg-[#101512] border border-[#263129] flex flex-col lg:flex-row lg:items-center justify-between gap-6">
        <div className="space-y-1.5">
          <div className="flex items-center gap-2.5">
            <h1 className="text-xl lg:text-2xl font-bold text-[#F3F7F4] font-heading tracking-tight">
              Grid-Loss Operations Overview
            </h1>
            <span className="px-2.5 py-0.5 rounded-full text-[10px] font-mono-tech bg-[#B6F542]/10 text-[#B6F542] border border-[#B6F542]/30 font-bold">
              LIVE TELEMETRY
            </span>
          </div>
          <p className="text-xs text-[#9BA8A0]">
            Analysis Period: <span className="font-mono-tech text-[#F3F7F4] font-semibold">{overview.analysisPeriod}</span>
          </p>
        </div>

        {/* Quick Action Navigation Buttons */}
        <div className="flex flex-wrap items-center gap-2.5">
          <button
            onClick={() => navigate(ROUTES.ANALYST.GRID)}
            className="flex items-center gap-2 px-3.5 py-2 rounded-xl bg-[#161D19] hover:bg-[#1E2722] text-[#F3F7F4] border border-[#263129] text-xs font-semibold transition-all hover:border-[#B6F542]/40"
          >
            <Grid className="w-3.5 h-3.5 text-[#B6F542]" />
            <span>Grid Explorer</span>
          </button>

          <button
            onClick={() => navigate(ROUTES.ANALYST.INVESTIGATIONS)}
            className="flex items-center gap-2 px-3.5 py-2 rounded-xl bg-[#161D19] hover:bg-[#1E2722] text-[#F3F7F4] border border-[#263129] text-xs font-semibold transition-all hover:border-[#FF6262]/40"
          >
            <Search className="w-3.5 h-3.5 text-[#FF6262]" />
            <span>Investigation Queue ({overview.connectionsRecommendedForReview})</span>
          </button>

          <button
            onClick={() => navigate(ROUTES.ANALYST.COMPARISON)}
            className="flex items-center gap-2 px-3.5 py-2 rounded-xl bg-[#161D19] hover:bg-[#1E2722] text-[#F3F7F4] border border-[#263129] text-xs font-semibold transition-all hover:border-[#40D9E8]/40"
          >
            <GitCompare className="w-3.5 h-3.5 text-[#40D9E8]" />
            <span>Pipeline Comparison</span>
          </button>
        </div>
      </div>

      {/* Primary Grid Physics Metric Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
        <MetricCard
          label="Injected Grid Energy"
          value={overview.injectedEnergyMWh.toLocaleString()}
          unit="MWh"
          subtext="Upstream feeder input"
          tooltipText="Total upstream feeder injection"
        />

        <MetricCard
          label="Billed Consumption"
          value={overview.billedEnergyMWh.toLocaleString()}
          unit="MWh"
          accentColor="#63D98A"
          subtext={`${deliveryEfficiency}% of injected load`}
          tooltipText={`Accounts for ${deliveryEfficiency}% of injected load`}
        />

        <MetricCard
          label="Estimated Technical Loss"
          value={overview.estimatedTechnicalLossMWh.toLocaleString()}
          unit="MWh"
          subtext={`${technicalLossRatio}% physics-modeled`}
          tooltipText={`Physics-modeled line resistance (${technicalLossRatio}%)`}
        />

        <MetricCard
          label="Unaccounted Residual"
          value={overview.unaccountedResidualMWh.toLocaleString()}
          unit="MWh"
          glossaryKey="UNACCOUNTED_RESIDUAL"
          accentColor="#FF6262"
          highlighted
          subtext={`${residualLossRatio}% primary NTL target`}
          tooltipText={`Primary target non-technical loss (${residualLossRatio}%)`}
        />

        <MetricCard
          label="High-Priority PMTs"
          value={overview.highPriorityPmtCount}
          unit="PMTs"
          glossaryKey="PMT"
          accentColor="#FF9F43"
          subtext="Anomalous deficit"
          tooltipText="Transformers exhibiting anomalous deficit"
        />

        <MetricCard
          label="Recommended for Review"
          value={overview.connectionsRecommendedForReview}
          unit="Connections"
          glossaryKey="CALIBRATED_ANOMALY_RISK"
          accentColor="#B6F542"
          subtext="Risk ≥75% confirmed"
          tooltipText="Calibrated risk ≥ 75% requiring verification"
        />
      </div>

      {/* Energy Balance Breakdown & Ratios */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        <div className="lg:col-span-3">
          <EnergyBalanceChart
            injectedMWh={overview.injectedEnergyMWh}
            billedMWh={overview.billedEnergyMWh}
            technicalLossMWh={overview.estimatedTechnicalLossMWh}
            unaccountedResidualMWh={overview.unaccountedResidualMWh}
          />
        </div>

        {/* Efficiency Indicators Panel */}
        <div className="p-6 rounded-2xl bg-[#101512] border border-[#263129] flex flex-col justify-between space-y-6">
          <div>
            <h3 className="text-xs font-bold uppercase tracking-wider text-[#9BA8A0] font-mono-tech flex items-center gap-2 mb-4">
              <BarChart3 className="w-4 h-4 text-[#B6F542]" /> System Efficiency Key Rates
            </h3>

            <div className="space-y-4">
              <div className="p-3.5 rounded-xl bg-[#0C110E] border border-[#263129]/80">
                <span className="text-[11px] text-[#9BA8A0] block">Grid Delivery Efficiency</span>
                <span className="text-xl font-extrabold text-[#63D98A] font-mono-tech">{deliveryEfficiency}%</span>
                <div className="w-full bg-[#161D19] h-1.5 rounded-full mt-2 overflow-hidden">
                  <div className="bg-[#63D98A] h-full rounded-full" style={{ width: `${deliveryEfficiency}%` }} />
                </div>
              </div>

              <div className="p-3.5 rounded-xl bg-[#0C110E] border border-[#263129]/80">
                <span className="text-[11px] text-[#9BA8A0] block">Unaccounted Loss Rate</span>
                <span className="text-xl font-extrabold text-[#FF6262] font-mono-tech">{residualLossRatio}%</span>
                <div className="w-full bg-[#161D19] h-1.5 rounded-full mt-2 overflow-hidden">
                  <div className="bg-[#FF6262] h-full rounded-full" style={{ width: `${residualLossRatio}%` }} />
                </div>
              </div>
            </div>
          </div>

          <div className="pt-4 border-t border-[#263129] flex items-center justify-between text-xs text-[#9BA8A0]">
            <span className="flex items-center gap-1.5 text-[#B6F542]">
              <ShieldCheck className="w-4 h-4" /> 6 Safeguards Active
            </span>
            <span className="font-mono-tech text-[11px]">Zero False-Positives Mode</span>
          </div>
        </div>
      </div>

      {/* Feeder Loss Hotspots Overview Grid */}
      <div className="p-6 rounded-2xl bg-[#101512] border border-[#263129] space-y-5">
        <div className="flex items-center justify-between">
          <h2 className="text-base font-bold text-[#F3F7F4] font-heading flex items-center gap-2">
            <Activity className="w-4 h-4 text-[#B6F542]" /> High-Level Feeder Loss Hotspots
          </h2>

          <button
            onClick={() => navigate(ROUTES.ANALYST.GRID)}
            className="flex items-center gap-1.5 text-xs font-semibold text-[#B6F542] hover:underline"
          >
            <span>Open 3D Grid Topology</span>
            <ChevronRight className="w-4 h-4" />
          </button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-4">
          {feeders.map((fdr) => {
            const residualPct = ((fdr.unaccountedResidualKWh / fdr.injectedEnergyKWh) * 100).toFixed(1);
            return (
              <div
                key={fdr.id}
                onClick={() => navigate(ROUTES.ANALYST.FEEDER(fdr.id))}
                className="p-4 rounded-xl bg-[#0C110E] border border-[#263129] hover:border-[#B6F542]/50 hover:bg-[#161D19] transition-all cursor-pointer group flex flex-col justify-between space-y-4"
              >
                <div>
                  <div className="flex items-center justify-between mb-1.5">
                    <span className="font-mono-tech text-xs font-bold text-[#B6F542] group-hover:text-[#CAFF69]">
                      {fdr.id}
                    </span>
                    <span className="flex items-center gap-1 text-[11px] font-mono-tech text-[#9BA8A0]">
                      {fdr.trend === 'increasing' && <TrendingUp className="w-3.5 h-3.5 text-[#FF6262]" />}
                      {fdr.trend === 'decreasing' && <TrendingDown className="w-3.5 h-3.5 text-[#63D98A]" />}
                      {fdr.trend === 'stable' && <Minus className="w-3.5 h-3.5 text-[#9BA8A0]" />}
                      <span className="capitalize">{fdr.trend}</span>
                    </span>
                  </div>
                  <h3 className="text-xs font-bold text-[#F3F7F4] line-clamp-1">{fdr.name}</h3>
                  <p className="text-[11px] text-[#9BA8A0] mt-0.5">{fdr.substation}</p>
                </div>

                <div className="space-y-2 pt-3 border-t border-[#263129]/60 text-xs">
                  <div className="flex items-center justify-between">
                    <span className="text-[#9BA8A0]">Unaccounted Residual</span>
                    <span className="font-mono-tech font-bold text-[#FF6262]">{residualPct}%</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-[#9BA8A0]">Priority PMTs</span>
                    <span className="font-mono-tech font-bold text-[#F3F7F4]">
                      {fdr.priorityPmtCount} / {fdr.totalPmtCount}
                    </span>
                  </div>
                </div>

                <div className="pt-2 flex items-center justify-between text-[11px] text-[#B6F542] font-semibold">
                  <span>Inspect Feeder PMTs</span>
                  <ArrowRight className="w-3.5 h-3.5 transform group-hover:translate-x-1 transition-transform" />
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* AI Dual-Pipeline & Safeguard Compliance Summary */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Monthly Billing Pipeline */}
        <div className="p-4 rounded-xl bg-[#101512] border border-[#263129] h-[110px] flex flex-col justify-between">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2 text-xs font-bold text-[#F3F7F4] font-heading">
              <Layers className="w-4 h-4 text-[#F5B942]" />
              <span>Monthly Billing Pipeline</span>
            </div>
            <div className="group relative cursor-help flex items-center">
              <Info className="w-3.5 h-3.5 text-[#9BA8A0] group-hover:text-[#F5B942] transition-colors" />
              <div className="pointer-events-none absolute bottom-full right-0 mb-2 hidden group-hover:block w-64 p-2.5 bg-[#161D19] border border-[#263129] rounded-lg text-xs normal-case text-[#F3F7F4] shadow-xl z-50 whitespace-normal leading-relaxed">
                Covers 100% of consumer connections (10,000 records). 142 anomalies flagged via step-down consumption trends & historical variance models.
              </div>
            </div>
          </div>

          <div className="text-[24px] font-extrabold font-mono-tech leading-none text-[#F5B942]">
            100%
          </div>

          <div className="text-xs text-[#9BA8A0]">
            142 flagged
          </div>
        </div>

        {/* AMI Smart Meter Pipeline */}
        <div className="p-4 rounded-xl bg-[#101512] border border-[#263129] h-[110px] flex flex-col justify-between">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2 text-xs font-bold text-[#F3F7F4] font-heading">
              <Zap className="w-4 h-4 text-[#40D9E8]" />
              <span>AMI Smart Meter Pipeline</span>
            </div>
            <div className="group relative cursor-help flex items-center">
              <Info className="w-3.5 h-3.5 text-[#9BA8A0] group-hover:text-[#40D9E8] transition-colors" />
              <div className="pointer-events-none absolute bottom-full right-0 mb-2 hidden group-hover:block w-64 p-2.5 bg-[#161D19] border border-[#263129] rounded-lg text-xs normal-case text-[#F3F7F4] shadow-xl z-50 whitespace-normal leading-relaxed">
                Covers 68.4% of consumer connections (6,840 smart meters). 215 anomalies flagged via hourly load profiles & peak-tariff deviation models.
              </div>
            </div>
          </div>

          <div className="text-[24px] font-extrabold font-mono-tech leading-none text-[#40D9E8]">
            68.4%
          </div>

          <div className="text-xs text-[#9BA8A0]">
            215 flagged
          </div>
        </div>

        {/* TreeSHAP & Corroboration */}
        <div className="p-4 rounded-xl bg-[#101512] border border-[#263129] h-[110px] flex flex-col justify-between">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2 text-xs font-bold text-[#F3F7F4] font-heading">
              <Cpu className="w-4 h-4 text-[#B6F542]" />
              <span>TreeSHAP & Corroboration</span>
            </div>
            <div className="group relative cursor-help flex items-center">
              <Info className="w-3.5 h-3.5 text-[#9BA8A0] group-hover:text-[#B6F542] transition-colors" />
              <div className="pointer-events-none absolute bottom-full right-0 mb-2 hidden group-hover:block w-64 p-2.5 bg-[#161D19] border border-[#263129] rounded-lg text-xs normal-case text-[#F3F7F4] shadow-xl z-50 whitespace-normal leading-relaxed">
                38.6% dual-pipeline agreement rate with PMT transformer balance corroboration and 6 automated safeguards to ensure zero false positives.
              </div>
            </div>
          </div>

          <div className="text-[24px] font-extrabold font-mono-tech leading-none text-[#B6F542]">
            38.6%
          </div>

          <div className="text-xs text-[#9BA8A0]">
            6 safeguards passed
          </div>
        </div>
      </div>
    </AppShell>
  );
};

