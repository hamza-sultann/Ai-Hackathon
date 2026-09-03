import React, { useEffect, useState } from 'react';
import { AppShell } from '../components/common/AppShell';
import { adminApi } from '../services/adminApi';
import { ModelServiceStatus } from '../types';
import { ROUTES } from '../config/routes';
import {
  Cpu,
  Activity,
  Play,
  CheckCircle2,
  RefreshCw,
  Code,
  Zap,
  Sliders,
  X,
  Sparkles,
  Server,
} from 'lucide-react';

export const AdminModelsPage: React.FC = () => {
  const [modelServices, setModelServices] = useState<ModelServiceStatus[]>([]);
  const [loading, setLoading] = useState(true);
  const [testModalOpen, setTestModalOpen] = useState(false);
  const [selectedModelId, setSelectedModelId] = useState('ms-2');
  const [testInputs, setTestInputs] = useState({
    peakLoadDropPct: 72,
    offPeakUsageRatio: 0.28,
    pmtResidualDeltaKWh: 14.2,
    sanctionedLoadKW: 15,
  });
  const [testingInference, setTestingInference] = useState(false);
  const [inferenceResult, setInferenceResult] = useState<any | null>(null);

  useEffect(() => {
    async function loadData() {
      try {
        const ms = await adminApi.getModelServices();
        setModelServices(ms);
      } catch (err) {
        console.error('Failed to load model services', err);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  const handleRunInference = async () => {
    setTestingInference(true);
    try {
      const result = await adminApi.testModelInference(selectedModelId, testInputs);
      setInferenceResult(result);
    } catch (err) {
      console.error('Inference test failed', err);
    } finally {
      setTestingInference(false);
    }
  };

  return (
    <AppShell
      currentRole="admin"
      hidePrototypeBanner
      compactBanner
      breadcrumbsItems={[
        { label: 'Admin Ops', href: ROUTES.ADMIN.ROOT },
        { label: 'AI Model Microservices' },
      ]}
    >
      {/* Header */}
      <div className="holo-card p-6 rounded-2xl bg-[#101512] border border-[#263129] flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl lg:text-2xl font-bold text-[#F3F7F4] font-heading tracking-tight flex items-center gap-2.5">
            <Cpu className="w-5 h-5 text-[#B6F542]" /> AI Model Microservice Endpoints
          </h1>
          <p className="text-xs text-[#9BA8A0] mt-1">
            Alibaba Cloud PAI-EAS hosted models: Isolation Forest anomaly scoring, XGBoost risk classifier, and TreeSHAP attribution.
          </p>
        </div>
        <button
          onClick={() => setTestModalOpen(true)}
          className="flex items-center gap-2 px-4 py-2 rounded-xl bg-[#B6F542] hover:bg-[#CAFF69] text-[#070A09] text-xs font-bold transition-all shadow-md active:scale-95 shrink-0"
        >
          <Play className="w-4 h-4 fill-current" />
          <span>Test Live Inference</span>
        </button>
      </div>

      {/* Model Services Table */}
      <div className="p-6 rounded-2xl bg-[#101512] border border-[#263129] space-y-4">
        <h2 className="text-base font-bold text-[#F3F7F4] font-heading flex items-center gap-2">
          <Server className="w-4 h-4 text-[#B6F542]" /> Active Inference Microservice Instances
        </h2>

        {loading ? (
          <div className="p-16 text-center text-xs text-[#9BA8A0] animate-pulse">
            Loading Model Endpoint Telemetry...
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-[#0C110E] text-[#9BA8A0] uppercase font-mono-tech border-b border-[#263129]">
                <tr>
                  <th className="p-3.5">Model Service</th>
                  <th className="p-3.5">Technology Stack</th>
                  <th className="p-3.5">Version</th>
                  <th className="p-3.5">P95 Latency</th>
                  <th className="p-3.5">Endpoint URL</th>
                  <th className="p-3.5">Status</th>
                  <th className="p-3.5 text-right">Inference Tester</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#263129]/60">
                {modelServices.map((ms) => (
                  <tr key={ms.id} className="hover:bg-[#161D19] transition-colors">
                    <td className="p-3.5">
                      <div className="font-bold text-[#F3F7F4]">{ms.name}</div>
                      <span className="text-[10px] font-mono-tech text-[#9BA8A0]">{ms.id}</span>
                    </td>
                    <td className="p-3.5 text-[#9BA8A0]">{ms.technology}</td>
                    <td className="p-3.5 font-mono-tech text-[#B6F542]">{ms.version}</td>
                    <td className="p-3.5 font-mono-tech text-[#40D9E8]">{ms.p95LatencyMs} ms</td>
                    <td className="p-3.5 font-mono-tech text-[#9BA8A0] max-w-xs truncate">{ms.endpoint}</td>
                    <td className="p-3.5">
                      <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs font-semibold bg-[#63D98A]/10 text-[#63D98A] border border-[#63D98A]/30">
                        <Activity className="w-3 h-3" /> Healthy
                      </span>
                    </td>
                    <td className="p-3.5 text-right">
                      <button
                        onClick={() => {
                          setSelectedModelId(ms.id);
                          setTestModalOpen(true);
                        }}
                        className="px-3 py-1.5 rounded-lg bg-[#161D19] hover:bg-[#B6F542] hover:text-[#070A09] text-[#B6F542] border border-[#B6F542]/30 text-xs font-semibold transition-colors"
                      >
                        Test Model
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Model Inference Tester Modal */}
      {testModalOpen && (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4 z-50 animate-fadeIn">
          <div className="w-full max-w-2xl rounded-2xl bg-[#101512] border border-[#263129] shadow-2xl p-6 space-y-5 animate-slideUp">
            <div className="flex items-center justify-between border-b border-[#263129] pb-4">
              <div>
                <h3 className="text-base font-bold text-[#F3F7F4] font-heading flex items-center gap-2">
                  <Play className="w-4 h-4 text-[#B6F542] fill-current" /> Live Model Inference Sandbox
                </h3>
                <p className="text-xs text-[#9BA8A0]">
                  Execute real-time test vectors against Alibaba Cloud PAI-EAS microservice endpoints.
                </p>
              </div>
              <button
                onClick={() => setTestModalOpen(false)}
                className="p-1.5 rounded-lg text-[#9BA8A0] hover:text-[#F3F7F4] hover:bg-[#161D19]"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="space-y-4">
              {/* Select Target Model */}
              <div>
                <label className="text-xs font-bold text-[#9BA8A0] block mb-1.5 uppercase font-mono-tech">
                  Target Microservice Endpoint
                </label>
                <select
                  value={selectedModelId}
                  onChange={(e) => setSelectedModelId(e.target.value)}
                  className="w-full p-2.5 bg-[#0C110E] border border-[#263129] rounded-xl text-xs text-[#F3F7F4] focus:outline-none focus:border-[#B6F542]"
                >
                  {modelServices.map((ms) => (
                    <option key={ms.id} value={ms.id}>
                      {ms.name} ({ms.technology} - {ms.version})
                    </option>
                  ))}
                </select>
              </div>

              {/* Sample Vector Inputs */}
              <div className="grid grid-cols-2 gap-3 text-xs">
                <div>
                  <label className="text-[#9BA8A0] block mb-1">Peak Load Drop (%)</label>
                  <input
                    type="number"
                    value={testInputs.peakLoadDropPct}
                    onChange={(e) =>
                      setTestInputs({ ...testInputs, peakLoadDropPct: Number(e.target.value) })
                    }
                    className="w-full p-2 bg-[#0C110E] border border-[#263129] rounded-lg text-[#F3F7F4] font-mono-tech focus:outline-none focus:border-[#B6F542]"
                  />
                </div>
                <div>
                  <label className="text-[#9BA8A0] block mb-1">Off-Peak Usage Ratio</label>
                  <input
                    type="number"
                    step="0.01"
                    value={testInputs.offPeakUsageRatio}
                    onChange={(e) =>
                      setTestInputs({ ...testInputs, offPeakUsageRatio: Number(e.target.value) })
                    }
                    className="w-full p-2 bg-[#0C110E] border border-[#263129] rounded-lg text-[#F3F7F4] font-mono-tech focus:outline-none focus:border-[#B6F542]"
                  />
                </div>
                <div>
                  <label className="text-[#9BA8A0] block mb-1">PMT Residual Delta (kWh)</label>
                  <input
                    type="number"
                    step="0.1"
                    value={testInputs.pmtResidualDeltaKWh}
                    onChange={(e) =>
                      setTestInputs({ ...testInputs, pmtResidualDeltaKWh: Number(e.target.value) })
                    }
                    className="w-full p-2 bg-[#0C110E] border border-[#263129] rounded-lg text-[#F3F7F4] font-mono-tech focus:outline-none focus:border-[#B6F542]"
                  />
                </div>
                <div>
                  <label className="text-[#9BA8A0] block mb-1">Sanctioned Load (kW)</label>
                  <input
                    type="number"
                    value={testInputs.sanctionedLoadKW}
                    onChange={(e) =>
                      setTestInputs({ ...testInputs, sanctionedLoadKW: Number(e.target.value) })
                    }
                    className="w-full p-2 bg-[#0C110E] border border-[#263129] rounded-lg text-[#F3F7F4] font-mono-tech focus:outline-none focus:border-[#B6F542]"
                  />
                </div>
              </div>

              {/* Run Trigger */}
              <div className="flex justify-end">
                <button
                  onClick={handleRunInference}
                  disabled={testingInference}
                  className="flex items-center gap-2 px-4 py-2 bg-[#B6F542] hover:bg-[#CAFF69] text-[#070A09] text-xs font-bold rounded-xl transition-all disabled:opacity-50"
                >
                  <RefreshCw className={`w-3.5 h-3.5 ${testingInference ? 'animate-spin' : ''}`} />
                  <span>{testingInference ? 'Evaluating Vector...' : 'Execute Test Inference'}</span>
                </button>
              </div>

              {/* Output Display */}
              {inferenceResult && (
                <div className="p-4 rounded-xl bg-[#0C110E] border border-[#B6F542]/40 space-y-2">
                  <div className="flex items-center justify-between text-xs font-mono-tech">
                    <span className="text-[#B6F542] font-bold">PAI-EAS Model Response</span>
                    <span className="text-[#9BA8A0]">Latency: {inferenceResult.latencyMs} ms</span>
                  </div>
                  <pre className="p-3 rounded-lg bg-[#070A09] border border-[#263129] text-[11px] font-mono-tech text-[#63D98A] overflow-x-auto">
                    {JSON.stringify(inferenceResult, null, 2)}
                  </pre>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </AppShell>
  );
};
