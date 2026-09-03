import React, { useEffect, useState } from 'react';
import { AppShell } from '../components/common/AppShell';
import { PipelineOverlapChart } from '../components/charts/PipelineOverlapChart';
import { comparisonApi } from '../services/comparisonApi';
import { PipelineComparison } from '../types';
import { GitCompare, Layers, Info } from 'lucide-react';

export const PipelineComparisonPage: React.FC = () => {
  const [comparison, setComparison] = useState<PipelineComparison | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      try {
        const data = await comparisonApi.getPipelineComparison();
        setComparison(data);
      } catch (err) {
        console.error('Failed to load pipeline comparison', err);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  if (loading || !comparison) {
    return (
      <AppShell currentRole="analyst">
        <div className="p-12 text-center text-xs text-[#9BA8A0] animate-pulse">
          Loading Pipeline Telemetry Comparison...
        </div>
      </AppShell>
    );
  }

  return (
    <AppShell currentRole="analyst">
      <div className="flex items-center justify-between p-5 rounded-xl bg-[#101512] border border-[#263129]">
        <div>
          <h1 className="text-xl font-extrabold text-[#F3F7F4] font-heading flex items-center gap-2">
            <GitCompare className="w-5 h-5 text-[#B6F542]" /> Pipeline Telemetry Comparison
          </h1>
          <p className="text-xs text-[#9BA8A0] mt-0.5">
            Benchmarking monthly billing pipeline against hourly smart-meter telemetry
          </p>
        </div>
      </div>

      {/* Unavailable Smart Meter Data Notice Box Requirement */}
      <div className="p-4 rounded-xl bg-[#161D19] border border-[#F5B942]/30 text-xs text-[#9BA8A0] flex items-start gap-3">
        <Info className="w-5 h-5 text-[#F5B942] shrink-0 mt-0.5" />
        <div>
          <span className="font-bold text-[#F3F7F4] block mb-0.5">Smart-Meter Coverage Telemetry</span>
          Smart-meter data is active on 68.4% of connections (6,840 / 10,000). For meters without AMI telemetry:
          <span className="text-[#F5B942] font-semibold ml-1">
            "Smart-meter data is unavailable for this connection. Monthly analysis remains active."
          </span>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        <div className="lg:col-span-6">
          <PipelineOverlapChart comparison={comparison} />
        </div>

        {/* Anomaly Breakdown */}
        <div className="lg:col-span-6 p-5 rounded-xl bg-[#101512] border border-[#263129] space-y-4">
          <h2 className="text-base font-bold text-[#F3F7F4] font-heading flex items-center gap-2">
            <Layers className="w-4 h-4 text-[#40D9E8]" /> Anomaly Type Distribution
          </h2>

          <div className="space-y-3">
            {comparison.anomalyTypeBreakdown.map((item, idx) => (
              <div key={idx} className="space-y-1">
                <div className="flex justify-between text-xs font-semibold">
                  <span className="text-[#F3F7F4]">{item.type}</span>
                  <span className="font-mono-tech text-[#B6F542]">{item.count} connections</span>
                </div>
                <div className="w-full h-2 rounded-full bg-[#0C110E] overflow-hidden border border-[#263129]">
                  <div
                    className="h-full bg-[#40D9E8]"
                    style={{ width: `${(item.count / 200) * 100}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </AppShell>
  );
};
