import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { AppShell } from '../components/common/AppShell';
import { DataQualityBadge } from '../components/common/StatusBadge';
import { MetricCard } from '../components/common/MetricCard';
import { gridApi } from '../services/gridApi';
import { Feeder, PMT, Consumer } from '../types';
import { ROUTES } from '../config/routes';
import { ArrowRight, Grid, Zap, Cpu } from 'lucide-react';

export const GridExplorerPage: React.FC = () => {
  const { feederId, pmtId } = useParams<{ feederId?: string; pmtId?: string }>();
  const navigate = useNavigate();

  const [feeders, setFeeders] = useState<Feeder[]>([]);
  const [selectedFeeder, setSelectedFeeder] = useState<Feeder | undefined>(undefined);
  const [pmts, setPmts] = useState<PMT[]>([]);
  const [selectedPmt, setSelectedPmt] = useState<PMT | undefined>(undefined);
  const [consumers, setConsumers] = useState<Consumer[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      setLoading(true);
      try {
        const allFeeders = await gridApi.getFeeders();
        setFeeders(allFeeders);

        const currentFeederId = feederId || 'FDR-08';
        const f = await gridApi.getFeederById(currentFeederId);
        setSelectedFeeder(f);

        if (currentFeederId) {
          const pmtList = await gridApi.getPmtsByFeeder(currentFeederId);
          setPmts(pmtList);

          const currentPmtId = pmtId || 'PMT-081';
          const p = await gridApi.getPmtById(currentPmtId);
          setSelectedPmt(p);

          if (currentPmtId) {
            const consList = await gridApi.getConsumersByPmt(currentPmtId);
            setConsumers(consList);
          }
        }
      } catch (err) {
        console.error('Failed to load grid hierarchy data', err);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, [feederId, pmtId]);

  const breadcrumbs = [
    { label: 'Grid Explorer', href: ROUTES.ANALYST.GRID },
    ...(selectedFeeder ? [{ label: selectedFeeder.id, href: ROUTES.ANALYST.FEEDER(selectedFeeder.id) }] : []),
    ...(selectedPmt ? [{ label: selectedPmt.id, href: ROUTES.ANALYST.PMT(selectedPmt.id) }] : []),
  ];

  return (
    <AppShell currentRole="analyst" breadcrumbsItems={breadcrumbs}>
      {/* Header */}
      <div className="flex items-center justify-between p-5 rounded-xl bg-[#101512] border border-[#263129]">
        <div>
          <h1 className="text-xl font-extrabold text-[#F3F7F4] font-heading flex items-center gap-2">
            <Grid className="w-5 h-5 text-[#B6F542]" /> Grid Topology Explorer
          </h1>
          <p className="text-xs text-[#9BA8A0] mt-0.5">
            Navigating Substation Feeders → Pole-Mounted Transformers (PMTs) → Connected Meters
          </p>
        </div>
      </div>

      {/* Selected PMT Balance Summary */}
      {selectedPmt && (
        <div className="p-5 rounded-xl bg-[#161D19] border border-[#B6F542]/40 space-y-4">
          <div className="flex items-center justify-between border-b border-[#263129] pb-3">
            <div>
              <span className="text-xs font-mono-tech text-[#B6F542] uppercase tracking-wider block">
                Target PMT Selected
              </span>
              <h2 className="text-lg font-bold text-[#F3F7F4] font-heading">
                {selectedPmt.id} — {selectedPmt.feederName}
              </h2>
              <p className="text-xs text-[#9BA8A0]">{selectedPmt.location}</p>
            </div>
            <DataQualityBadge quality={selectedPmt.dataQuality} />
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            <div className="p-3 bg-[#101512] rounded-lg border border-[#263129]">
              <span className="text-[11px] text-[#9BA8A0] uppercase block">Injected Energy</span>
              <span className="text-lg font-extrabold font-mono-tech text-[#40D9E8]">
                {selectedPmt.injectedEnergyKWh.toLocaleString()} kWh
              </span>
            </div>
            <div className="p-3 bg-[#101512] rounded-lg border border-[#263129]">
              <span className="text-[11px] text-[#9BA8A0] uppercase block">= Billed Energy</span>
              <span className="text-lg font-extrabold font-mono-tech text-[#63D98A]">
                {selectedPmt.billedEnergyKWh.toLocaleString()} kWh
              </span>
            </div>
            <div className="p-3 bg-[#101512] rounded-lg border border-[#263129]">
              <span className="text-[11px] text-[#9BA8A0] uppercase block">+ Est. Technical Loss</span>
              <span className="text-lg font-extrabold font-mono-tech text-[#F5B942]">
                {selectedPmt.estimatedTechnicalLossKWh.toLocaleString()} kWh
              </span>
            </div>
            <div className="p-3 bg-[#101512] rounded-lg border border-[#B6F542]/40">
              <span className="text-[11px] text-[#9BA8A0] uppercase block">+ Unaccounted Residual</span>
              <span className="text-lg font-extrabold font-mono-tech text-[#FF6262]">
                {selectedPmt.unaccountedResidualKWh.toLocaleString()} kWh
              </span>
            </div>
          </div>
        </div>
      )}

      {/* Feeder Table */}
      <div className="p-5 rounded-xl bg-[#101512] border border-[#263129] space-y-4">
        <h2 className="text-base font-bold text-[#F3F7F4] font-heading">Feeders Summary</h2>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-[#0C110E] text-[#9BA8A0] uppercase font-mono-tech border-b border-[#263129]">
              <tr>
                <th className="p-3">Feeder ID & Name</th>
                <th className="p-3">Service Area</th>
                <th className="p-3">Uptime</th>
                <th className="p-3">Injected Energy</th>
                <th className="p-3">Accounted Energy</th>
                <th className="p-3">Residual</th>
                <th className="p-3">Priority PMTs</th>
                <th className="p-3">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#263129]/60">
              {feeders.map((f) => (
                <tr
                  key={f.id}
                  onClick={() => navigate(ROUTES.ANALYST.FEEDER(f.id))}
                  className={`hover:bg-[#161D19] cursor-pointer transition-colors ${
                    f.id === selectedFeeder?.id ? 'bg-[#161D19]/60 font-semibold' : ''
                  }`}
                >
                  <td className="p-3">
                    <div className="font-mono-tech text-[#F3F7F4] font-bold">{f.id}</div>
                    <div className="text-[11px] text-[#9BA8A0]">{f.name}</div>
                  </td>
                  <td className="p-3 text-[#9BA8A0]">{f.serviceArea}</td>
                  <td className="p-3 font-mono-tech text-[#63D98A]">{f.uptimePercentage}%</td>
                  <td className="p-3 font-mono-tech text-[#40D9E8]">{f.injectedEnergyKWh.toLocaleString()} kWh</td>
                  <td className="p-3 font-mono-tech text-[#63D98A]">{f.accountedEnergyKWh.toLocaleString()} kWh</td>
                  <td className="p-3 font-mono-tech text-[#FF6262] font-bold">
                    {f.unaccountedResidualKWh.toLocaleString()} kWh
                  </td>
                  <td className="p-3 font-mono-tech text-[#F5B942] font-bold">
                    {f.priorityPmtCount} / {f.totalPmtCount}
                  </td>
                  <td className="p-3">
                    <span className="inline-flex items-center gap-1 text-[#B6F542] hover:underline">
                      Explore PMTs <ArrowRight className="w-3.5 h-3.5" />
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
