import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { AppShell } from '../components/common/AppShell';
import { DataQualityBadge } from '../components/common/StatusBadge';
import { gridApi } from '../services/gridApi';
import { investigationApi } from '../services/investigationApi';
import { Feeder, PMT, Consumer, Investigation } from '../types';
import { ROUTES } from '../config/routes';
import { Grid, Zap, Cpu, MapPin, Layers, ArrowRight, Activity, TrendingUp, TrendingDown } from 'lucide-react';

export const GridExplorerPage: React.FC = () => {
  const { feederId, pmtId } = useParams<{ feederId?: string; pmtId?: string }>();
  const navigate = useNavigate();

  const [feeders, setFeeders] = useState<Feeder[]>([]);
  const [selectedFeeder, setSelectedFeeder] = useState<Feeder | undefined>(undefined);
  const [pmts, setPmts] = useState<PMT[]>([]);
  const [selectedPmt, setSelectedPmt] = useState<PMT | undefined>(undefined);
  const [consumers, setConsumers] = useState<Consumer[]>([]);
  const [investigations, setInvestigations] = useState<Investigation[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      setLoading(true);
      try {
        const allFeeders = await gridApi.getFeeders();
        setFeeders(allFeeders);

        // Fetch investigations queue to match consumer risk percentages
        const allInvs = await investigationApi.getInvestigations();
        setInvestigations(allInvs);

        if (pmtId) {
          // Consumer Level: PMT is selected
          const p = await gridApi.getPmtById(pmtId);
          setSelectedPmt(p);

          if (p) {
            const f = await gridApi.getFeederById(p.feederId);
            setSelectedFeeder(f);

            const consList = await gridApi.getConsumersByPmt(pmtId);
            setConsumers(consList);
          }
        } else if (feederId) {
          // PMT Level: Feeder is selected
          const f = await gridApi.getFeederById(feederId);
          setSelectedFeeder(f);
          setSelectedPmt(undefined);

          const pmtList = await gridApi.getPmtsByFeeder(feederId);
          setPmts(pmtList);
        } else {
          // Feeder Level: Grid root explorer
          setSelectedFeeder(undefined);
          setSelectedPmt(undefined);
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

  if (loading) {
    return (
      <AppShell currentRole="analyst" breadcrumbsItems={breadcrumbs}>
        <div className="p-12 text-center text-xs text-[#9BA8A0] animate-pulse">
          Retrieving Grid Topology Hierarchy...
        </div>
      </AppShell>
    );
  }

  // Determine current active level
  const isConsumerLevel = !!selectedPmt;
  const isPmtLevel = !selectedPmt && !!selectedFeeder;
  const isFeederLevel = !selectedPmt && !selectedFeeder;

  return (
    <AppShell currentRole="analyst" breadcrumbsItems={breadcrumbs}>
      {/* Page Title Block */}
      <div className="flex flex-col md:flex-row md:items-center justify-between p-5 rounded-xl bg-[#101512] border border-[#263129] gap-4">
        <div>
          <h1 className="text-xl font-extrabold text-[#F3F7F4] font-heading flex items-center gap-2">
            <Grid className="w-5 h-5 text-[#B6F542]" /> Grid Topology Explorer
          </h1>
          <p className="text-xs text-[#9BA8A0] mt-0.5">
            Operator-level spatial tree navigation. Use breadcrumbs above to traverse levels.
          </p>
        </div>
      </div>

      {/* LEVEL 3: Connected Consumers / Meters */}
      {isConsumerLevel && selectedPmt && (
        <div className="space-y-6">
          {/* PMT Details Header Box */}
          <div className="p-6 rounded-xl bg-[#161D19] border border-[#40D9E8]/30 space-y-4">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-[#263129]/60 pb-4">
              <div>
                <span className="text-[10px] font-mono-tech text-[#40D9E8] uppercase tracking-wider font-semibold">
                  Selected Pole-Mounted Transformer (PMT)
                </span>
                <h2 className="text-lg font-bold text-[#F3F7F4] font-heading mt-0.5">
                  {selectedPmt.id} — Feeder: {selectedPmt.feederName}
                </h2>
                <p className="text-xs text-[#9BA8A0] flex items-center gap-1.5 mt-1">
                  <MapPin className="w-3.5 h-3.5 text-[#9BA8A0]" /> {selectedPmt.location}
                </p>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-xs text-[#9BA8A0] font-mono-tech">Capacity: {selectedPmt.capacityKVA} kVA</span>
                <DataQualityBadge quality={selectedPmt.dataQuality} />
              </div>
            </div>

            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
              <div className="p-3 bg-[#101512] rounded-lg border border-[#263129]">
                <span className="text-[10px] text-[#9BA8A0] uppercase block">Injected Energy</span>
                <span className="text-base font-extrabold font-mono-tech text-[#40D9E8]">
                  {selectedPmt.injectedEnergyKWh.toLocaleString()} kWh
                </span>
              </div>
              <div className="p-3 bg-[#101512] rounded-lg border border-[#263129]">
                <span className="text-[10px] text-[#9BA8A0] uppercase block">Billed Energy</span>
                <span className="text-base font-extrabold font-mono-tech text-[#63D98A]">
                  {selectedPmt.billedEnergyKWh.toLocaleString()} kWh
                </span>
              </div>
              <div className="p-3 bg-[#101512] rounded-lg border border-[#263129]">
                <span className="text-[10px] text-[#9BA8A0] uppercase block">Technical Loss</span>
                <span className="text-base font-extrabold font-mono-tech text-[#F5B942]">
                  {selectedPmt.estimatedTechnicalLossKWh.toLocaleString()} kWh
                </span>
              </div>
              <div className="p-3 bg-[#101512] rounded-lg border border-[#263129]">
                <span className="text-[10px] text-[#9BA8A0] uppercase block">Residual Loss</span>
                <span className="text-base font-extrabold font-mono-tech text-[#FF6262]">
                  {selectedPmt.unaccountedResidualKWh.toLocaleString()} kWh
                </span>
              </div>
            </div>
          </div>

          {/* Consumer Grid */}
          <div className="space-y-4">
            <h3 className="text-base font-bold text-[#F3F7F4] font-heading flex items-center gap-2">
              <Cpu className="w-4.5 h-4.5 text-[#B6F542]" /> Connected Meters / Consumers ({consumers.length})
            </h3>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
              {consumers.map((c) => {
                const inv = investigations.find((i) => i.consumerId === c.id);
                const risk = inv ? inv.calibratedRiskPercentage : undefined;

                return (
                  <div
                    key={c.id}
                    onClick={() => navigate(ROUTES.ANALYST.CONSUMER_INVESTIGATION(c.id))}
                    className="holo-card p-5 rounded-xl bg-[#101512] border border-[#263129] hover:border-[#B6F542]/30 cursor-pointer transition-all duration-200 flex flex-col justify-between h-48"
                  >
                    <div className="space-y-2">
                      <div className="flex items-start justify-between gap-2">
                        <div>
                          <span className="text-[9px] font-mono-tech text-[#9BA8A0] uppercase tracking-wider block">Consumer ID</span>
                          <span className="text-sm font-bold font-mono-tech text-[#F3F7F4]">{c.id}</span>
                        </div>

                        {risk !== undefined ? (
                          <span className={`px-2 py-0.5 rounded text-[10px] font-bold font-mono-tech ${
                            risk >= 85 ? 'bg-[#FF6262]/10 text-[#FF6262] border border-[#FF6262]/20' : 'bg-[#F5B942]/10 text-[#F5B942] border border-[#F5B942]/20'
                          }`}>
                            {risk}% Risk
                          </span>
                        ) : (
                          <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-[#63D98A]/10 text-[#63D98A] border border-[#63D98A]/20">
                            Stable Profile
                          </span>
                        )}
                      </div>

                      <div className="text-[11px] text-[#9BA8A0] leading-relaxed">
                        <div className="flex justify-between">
                          <span>Meter ID:</span>
                          <span className="font-mono-tech text-[#F3F7F4]">{c.meterId}</span>
                        </div>
                        <div className="flex justify-between">
                          <span>Tariff Category:</span>
                          <span className="text-[#F3F7F4]">{c.tariffCategory}</span>
                        </div>
                        <div className="flex justify-between">
                          <span>Sanctioned Load:</span>
                          <span className="font-mono-tech text-[#F3F7F4]">{c.sanctionedLoadKW} kW</span>
                        </div>
                      </div>
                    </div>

                    <div className="flex items-center justify-between border-t border-[#263129]/40 pt-3 text-[10px]">
                      <div className="flex gap-2">
                        <span className={`px-1.5 py-0.5 rounded text-[9px] font-medium ${c.hasSmartMeter ? 'bg-[#40D9E8]/10 text-[#40D9E8]' : 'bg-[#9BA8A0]/10 text-[#9BA8A0]'}`}>
                          {c.hasSmartMeter ? 'AMI Smart' : 'Conventional'}
                        </span>
                        {c.isRegisteredSolarProsumer && (
                          <span className="px-1.5 py-0.5 rounded text-[9px] font-medium bg-[#B6F542]/10 text-[#B6F542]">
                            Solar Prosumer
                          </span>
                        )}
                      </div>
                      <span className="text-[#B6F542] hover:underline flex items-center gap-1 font-semibold">
                        Investigate <ArrowRight className="w-3 h-3" />
                      </span>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      )}

      {/* LEVEL 2: PMTs */}
      {isPmtLevel && selectedFeeder && (
        <div className="space-y-6">
          {/* Feeder Details Header Box */}
          <div className="p-6 rounded-xl bg-[#161D19] border border-[#B6F542]/30 space-y-4">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-[#263129]/60 pb-4">
              <div>
                <span className="text-[10px] font-mono-tech text-[#B6F542] uppercase tracking-wider font-semibold">
                  Selected Feeder
                </span>
                <h2 className="text-lg font-bold text-[#F3F7F4] font-heading mt-0.5">
                  {selectedFeeder.id} — {selectedFeeder.name}
                </h2>
                <p className="text-xs text-[#9BA8A0] mt-1">
                  Service Area: {selectedFeeder.serviceArea} • Substation: {selectedFeeder.substation}
                </p>
              </div>
              <div className="flex items-center gap-3">
                <div className="text-right">
                  <span className="text-[10px] text-[#9BA8A0] block">Uptime</span>
                  <span className="text-sm font-bold font-mono-tech text-[#63D98A]">{selectedFeeder.uptimePercentage}%</span>
                </div>
              </div>
            </div>

            <div className="grid grid-cols-2 sm:grid-cols-3 gap-4">
              <div className="p-3 bg-[#101512] rounded-lg border border-[#263129]">
                <span className="text-[10px] text-[#9BA8A0] uppercase block">Injected Energy</span>
                <span className="text-base font-extrabold font-mono-tech text-[#40D9E8]">
                  {selectedFeeder.injectedEnergyKWh.toLocaleString()} kWh
                </span>
              </div>
              <div className="p-3 bg-[#101512] rounded-lg border border-[#263129]">
                <span className="text-[10px] text-[#9BA8A0] uppercase block">Accounted Energy</span>
                <span className="text-base font-extrabold font-mono-tech text-[#63D98A]">
                  {selectedFeeder.accountedEnergyKWh.toLocaleString()} kWh
                </span>
              </div>
              <div className="p-3 bg-[#101512] rounded-lg border border-[#263129]">
                <span className="text-[10px] text-[#9BA8A0] uppercase block">Residual Loss</span>
                <span className="text-base font-extrabold font-mono-tech text-[#FF6262]">
                  {selectedFeeder.unaccountedResidualKWh.toLocaleString()} kWh
                </span>
              </div>
            </div>
          </div>

          {/* PMT Grid */}
          <div className="space-y-4">
            <h3 className="text-base font-bold text-[#F3F7F4] font-heading flex items-center gap-2">
              <Zap className="w-4.5 h-4.5 text-[#40D9E8]" /> Pole-Mounted Transformers ({pmts.length})
            </h3>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
              {pmts.map((p) => (
                <div
                  key={p.id}
                  onClick={() => navigate(ROUTES.ANALYST.PMT(p.id))}
                  className="holo-card p-5 rounded-xl bg-[#101512] border border-[#263129] hover:border-[#40D9E8]/30 cursor-pointer transition-all duration-200 flex flex-col justify-between h-48"
                >
                  <div className="space-y-2">
                    <div className="flex items-start justify-between gap-2">
                      <div>
                        <span className="text-[9px] font-mono-tech text-[#9BA8A0] uppercase tracking-wider block">Transformer</span>
                        <span className="text-sm font-bold font-mono-tech text-[#F3F7F4]">{p.id}</span>
                      </div>

                      {p.unaccountedResidualKWh > 12000 ? (
                        <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-[#FF6262]/10 text-[#FF6262] border border-[#FF6262]/20">
                          Critical Spike
                        </span>
                      ) : p.unaccountedResidualKWh > 5000 ? (
                        <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-[#F5B942]/10 text-[#F5B942] border border-[#F5B942]/20">
                          Elevated Loss
                        </span>
                      ) : (
                        <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-[#63D98A]/10 text-[#63D98A] border border-[#63D98A]/20">
                          Stable Balance
                        </span>
                      )}
                    </div>

                    <div className="text-[11px] text-[#9BA8A0] leading-relaxed">
                      <div className="flex justify-between">
                        <span>Location:</span>
                        <span className="text-[#F3F7F4] text-right truncate max-w-[140px]">{p.location}</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Capacity:</span>
                        <span className="font-mono-tech text-[#F3F7F4]">{p.capacityKVA} kVA</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Connected Meters:</span>
                        <span className="font-mono-tech text-[#F3F7F4]">{p.connectedConsumerCount}</span>
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center justify-between border-t border-[#263129]/40 pt-3 text-[10px]">
                    <div>
                      <span className="text-[#9BA8A0] mr-1.5">Residual Loss:</span>
                      <span className="font-mono-tech font-bold text-[#FF6262]">
                        {p.unaccountedResidualKWh.toLocaleString()} kWh
                      </span>
                    </div>
                    <span className="text-[#40D9E8] hover:underline flex items-center gap-1 font-semibold">
                      Explore Meters <ArrowRight className="w-3 h-3" />
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* LEVEL 1: Feeders (Root) */}
      {isFeederLevel && (
        <div className="space-y-4">
          <h3 className="text-base font-bold text-[#F3F7F4] font-heading flex items-center gap-2">
            <Layers className="w-4.5 h-4.5 text-[#B6F542]" /> Substation Feeders ({feeders.length})
          </h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {feeders.map((f) => (
              <div
                key={f.id}
                onClick={() => navigate(ROUTES.ANALYST.FEEDER(f.id))}
                className="holo-card p-5 rounded-xl bg-[#101512] border border-[#263129] hover:border-[#B6F542]/30 cursor-pointer transition-all duration-200 flex flex-col justify-between h-48"
              >
                <div className="space-y-2">
                  <div className="flex items-start justify-between gap-2">
                    <div>
                      <span className="text-[9px] font-mono-tech text-[#9BA8A0] uppercase tracking-wider block">Feeder Line</span>
                      <span className="text-sm font-bold font-mono-tech text-[#F3F7F4]">{f.id}</span>
                    </div>

                    {f.priorityPmtCount >= 4 ? (
                      <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-[#FF6262]/10 text-[#FF6262] border border-[#FF6262]/20">
                        High NTL Risk
                      </span>
                    ) : f.priorityPmtCount >= 1 ? (
                      <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-[#F5B942]/10 text-[#F5B942] border border-[#F5B942]/20">
                        Medium NTL Risk
                      </span>
                    ) : (
                      <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-[#63D98A]/10 text-[#63D98A] border border-[#63D98A]/20">
                        Low NTL Risk
                      </span>
                    )}
                  </div>

                  <div className="text-[11px] text-[#9BA8A0] leading-relaxed">
                    <div className="flex justify-between">
                      <span>Service Area:</span>
                      <span className="text-[#F3F7F4] truncate max-w-[150px]">{f.serviceArea}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Uptime:</span>
                      <span className="font-mono-tech text-[#63D98A]">{f.uptimePercentage}%</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Priority PMTs:</span>
                      <span className="font-mono-tech text-[#F5B942] font-semibold">
                        {f.priorityPmtCount} / {f.totalPmtCount}
                      </span>
                    </div>
                  </div>
                </div>

                <div className="flex items-center justify-between border-t border-[#263129]/40 pt-3 text-[10px]">
                  <div>
                    <span className="text-[#9BA8A0] mr-1.5">Unaccounted:</span>
                    <span className="font-mono-tech font-bold text-[#FF6262]">
                      {f.unaccountedResidualKWh.toLocaleString()} kWh
                    </span>
                  </div>
                  <span className="text-[#B6F542] hover:underline flex items-center gap-1 font-semibold">
                    Explore PMTs <ArrowRight className="w-3 h-3" />
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </AppShell>
  );
};
