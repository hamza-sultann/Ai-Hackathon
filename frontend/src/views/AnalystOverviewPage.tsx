import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { AppShell } from '../components/common/AppShell';
import { MetricCard } from '../components/common/MetricCard';
import { EnergyBalanceChart } from '../components/charts/EnergyBalanceChart';
import { PriorityBadge, DataQualityBadge } from '../components/common/StatusBadge';
import { overviewApi } from '../services/overviewApi';
import { investigationApi } from '../services/investigationApi';
import { SystemOverview, Investigation } from '../types';
import { ROUTES } from '../config/routes';
import { ArrowRight, RefreshCw, Layers } from 'lucide-react';

export const AnalystOverviewPage: React.FC = () => {
  const navigate = useNavigate();
  const [overview, setOverview] = useState<SystemOverview | null>(null);
  const [recentQueue, setRecentQueue] = useState<Investigation[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      try {
        const [ovData, queueData] = await Promise.all([
          overviewApi.getOverview(),
          investigationApi.getInvestigations(),
        ]);
        setOverview(ovData);
        setRecentQueue(queueData);
      } catch (err) {
        console.error('Failed to load overview data', err);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  if (loading || !overview) {
    return (
      <AppShell currentRole="analyst">
        <div className="p-12 text-center text-xs text-[#9BA8A0] animate-pulse">
          Loading Operator Overview Telemetry...
        </div>
      </AppShell>
    );
  }

  return (
    <AppShell currentRole="analyst">
      {/* Top Header Summary Bar */}
      <div className="holo-card flex flex-col md:flex-row md:items-center justify-between gap-4 p-5 rounded-xl bg-[#101512] border border-[#263129]">
        <div className="relative z-10">
          <h1 className="text-headline-md text-[#F3F7F4]">Grid-Loss Operations Overview</h1>
          <p className="text-xs text-[#9BA8A0] mt-0.5">
            Analysis Period: <span className="font-mono-tech text-[#F3F7F4]">{overview.analysisPeriod}</span> •
            Last Batch Run: <span className="font-mono-tech text-[#B6F542]">{overview.lastAnalysisTimestamp}</span>
          </p>
        </div>

        <div className="relative z-10 flex items-center gap-3">
          <div className="px-3 py-1.5 rounded-lg bg-[#161D19] border border-[#263129] text-data-md text-[#9BA8A0] flex items-center gap-2">
            <Layers className="w-3.5 h-3.5 text-[#40D9E8]" />
            <span>Monthly: 100% | Smart Meter: 68.4%</span>
          </div>
        </div>
      </div>

      {/* Primary Grid Physics Metric Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        <MetricCard
          label="Injected Grid Energy"
          value={overview.injectedEnergyMWh.toLocaleString()}
          unit="MWh"
          subtext="Total energy supplied at substation feeder head-end"
        />

        <MetricCard
          label="Billed Consumption"
          value={overview.billedEnergyMWh.toLocaleString()}
          unit="MWh"
          accentColor="#63D98A"
          subtext="Total energy billed across 10,000 active meters"
        />

        <MetricCard
          label="Estimated Technical Loss"
          value={overview.estimatedTechnicalLossMWh.toLocaleString()}
          unit="MWh"
          subtext="Physics-calculated I²R line & transformer loss (8.5%)"
        />

        <MetricCard
          label="Unaccounted Residual"
          value={overview.unaccountedResidualMWh.toLocaleString()}
          unit="MWh"
          glossaryKey="UNACCOUNTED_RESIDUAL"
          accentColor="#FF6262"
          highlighted
          subtext="Residual energy remaining for prioritized inspection"
        />

        <MetricCard
          label="High-Priority PMTs"
          value={overview.highPriorityPmtCount}
          unit="PMTs"
          glossaryKey="PMT"
          subtext="Transformers exhibiting elevated residual energy spikes"
        />

        <MetricCard
          label="Recommended for Review"
          value={overview.connectionsRecommendedForReview}
          unit="Connections"
          glossaryKey="CALIBRATED_ANOMALY_RISK"
          accentColor="#B6F542"
          subtext="Consumer connections flagged for field inspection review"
        />
      </div>

      {/* Energy Balance Chart */}
      <EnergyBalanceChart
        injectedMWh={overview.injectedEnergyMWh}
        billedMWh={overview.billedEnergyMWh}
        technicalLossMWh={overview.estimatedTechnicalLossMWh}
        unaccountedResidualMWh={overview.unaccountedResidualMWh}
      />

      {/* Priority Recommendations Table */}
      <div className="holo-card p-5 rounded-xl bg-[#101512] border border-[#263129] space-y-4">
        <div className="relative z-10 flex items-center justify-between">
          <div>
            <h2 className="text-headline-sm text-[#F3F7F4]">Recent Priority Recommendations</h2>
            <p className="text-xs text-[#9BA8A0]">
              Connections exhibiting high calibrated anomaly risk requiring field verification.
            </p>
          </div>
          <button
            onClick={() => navigate(ROUTES.ANALYST.INVESTIGATIONS)}
            className="flex items-center gap-1.5 text-xs font-semibold text-[#B6F542] hover:underline"
          >
            <span>View Full Investigation Queue</span>
            <ArrowRight className="w-4 h-4" />
          </button>
        </div>

        <div className="relative z-10 overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-[#0C110E] text-label-caps text-[#9BA8A0] border-b border-[#263129]">
              <tr>
                <th className="p-3">Consumer ID</th>
                <th className="p-3">Feeder / PMT</th>
                <th className="p-3">Priority</th>
                <th className="p-3">Calibrated Anomaly Risk</th>
                <th className="p-3">Est. Impact</th>
                <th className="p-3">Pattern</th>
                <th className="p-3">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#263129]/60">
              {recentQueue.map((inv) => (
                <tr
                  key={inv.id}
                  onClick={() => navigate(ROUTES.ANALYST.CONSUMER_INVESTIGATION(inv.consumerId))}
                  className="hover:bg-[#161D19] cursor-pointer transition-colors"
                >
                  <td className="p-3 font-semibold font-mono-tech text-[#F3F7F4]">{inv.consumerId}</td>
                  <td className="p-3 text-[#9BA8A0] font-mono-tech">
                    {inv.feederId} / {inv.pmtId}
                  </td>
                  <td className="p-3">
                    <PriorityBadge priority={inv.priority} />
                  </td>
                  <td className="p-3 font-mono-tech font-bold text-[#FF6262]">
                    {inv.calibratedRiskPercentage}% calibrated anomaly risk
                  </td>
                  <td className="p-3 font-mono-tech text-[#F3F7F4]">{inv.estimatedImpactKWhMonth} kWh/mo</td>
                  <td className="p-3 text-[#9BA8A0]">{inv.patternName}</td>
                  <td className="p-3">
                    <span className="inline-flex items-center gap-1 text-[#B6F542] font-semibold hover:underline">
                      Investigate <ArrowRight className="w-3.5 h-3.5" />
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
