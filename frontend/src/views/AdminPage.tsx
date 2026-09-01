import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { AppShell } from '../components/common/AppShell';
import { MetricCard } from '../components/common/MetricCard';
import { adminApi } from '../services/adminApi';
import { DataSourceStatus, ModelServiceStatus, AuditEvent } from '../types';
import { ROUTES } from '../config/routes';
import {
  Shield,
  Cpu,
  Database,
  UserCheck,
  FileText,
  Activity,
  ArrowRight,
  Settings,
  Zap,
  Server,
  Radio,
  CheckCircle2,
  Lock,
} from 'lucide-react';

export const AdminPage: React.FC = () => {
  const navigate = useNavigate();
  const [dataSources, setDataSources] = useState<DataSourceStatus[]>([]);
  const [modelServices, setModelServices] = useState<ModelServiceStatus[]>([]);
  const [auditEvents, setAuditEvents] = useState<AuditEvent[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      try {
        const [ds, ms, aud] = await Promise.all([
          adminApi.getDataSources(),
          adminApi.getModelServices(),
          adminApi.getAuditActivity(),
        ]);
        setDataSources(ds);
        setModelServices(ms);
        setAuditEvents(aud);
      } catch (err) {
        console.error('Failed to load admin data', err);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  if (loading) {
    return (
      <AppShell currentRole="admin" hidePrototypeBanner compactBanner>
        <div className="p-16 text-center text-xs text-[#9BA8A0] animate-pulse">
          Loading Admin Control Plane Telemetry...
        </div>
      </AppShell>
    );
  }

  return (
    <AppShell currentRole="admin" hidePrototypeBanner compactBanner>
      {/* Top Header Summary Bar */}
      <div className="holo-card p-6 rounded-2xl bg-[#101512] border border-[#263129] flex flex-col lg:flex-row lg:items-center justify-between gap-6">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-xl bg-[#F5B942]/10 border border-[#F5B942]/30 flex items-center justify-center text-[#F5B942]">
            <Shield className="w-5 h-5" />
          </div>
          <h1 className="text-xl lg:text-2xl font-bold text-[#F3F7F4] font-heading tracking-tight">
            Admin & System Ops Command Center
          </h1>
        </div>

        <div className="flex flex-wrap items-center gap-2.5">
          <button
            onClick={() => navigate(ROUTES.ADMIN.CONFIGURATION)}
            className="flex items-center gap-2 px-3.5 py-2 rounded-xl bg-[#161D19] hover:bg-[#1E2722] text-[#F3F7F4] border border-[#263129] text-xs font-semibold transition-all hover:border-[#F5B942]/40"
          >
            <Settings className="w-3.5 h-3.5 text-[#F5B942]" />
            <span>Threshold Config</span>
          </button>

          <button
            onClick={() => navigate(ROUTES.ADMIN.AUDIT)}
            className="flex items-center gap-2 px-3.5 py-2 rounded-xl bg-[#161D19] hover:bg-[#1E2722] text-[#F3F7F4] border border-[#263129] text-xs font-semibold transition-all hover:border-[#63D98A]/40"
          >
            <FileText className="w-3.5 h-3.5 text-[#63D98A]" />
            <span>Audit Trail</span>
          </button>
        </div>
      </div>

      {/* Primary System Health KPI Cards */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-6">
        <MetricCard
          label="AI Model Microservices"
          value={modelServices.length}
          unit="Active Endpoints"
          accentColor="#B6F542"
          subtext="PAI-EAS & Function Compute"
        />

        <MetricCard
          label="Ingestion Pipelines"
          value={dataSources.length}
          unit="Active Streams"
          accentColor="#40D9E8"
          subtext="Kafka, Modbus, CDC & GIS"
        />

        <MetricCard
          label="P95 Model Latency"
          value="140"
          unit="ms"
          accentColor="#63D98A"
          subtext="XGBoost & TreeSHAP PAI latency"
        />

        <MetricCard
          label="Safeguard Strictness"
          value="100%"
          unit="Enforced"
          accentColor="#F5B942"
          subtext="6 automated integrity checks"
        />
      </div>

      {/* Infrastructure Health & Recent System Audit Events */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left 1 Col: Infrastructure Health */}
        <div className="p-6 rounded-2xl bg-[#101512] border border-[#263129] flex flex-col justify-between space-y-4">
          <div className="space-y-3">
            <h3 className="text-xs font-bold uppercase tracking-wider text-[#9BA8A0] font-mono-tech flex items-center gap-2">
              <Server className="w-4 h-4 text-[#40D9E8]" /> Infrastructure Health
            </h3>

            <div className="space-y-2.5 text-xs">
              <div className="p-3 rounded-xl bg-[#0C110E] border border-[#263129] flex items-center justify-between">
                <span className="text-[#9BA8A0]">PAI-EAS Cluster</span>
                <span className="text-[#63D98A] font-bold font-mono-tech flex items-center gap-1">
                  <CheckCircle2 className="w-3.5 h-3.5" /> 99.98% Uptime
                </span>
              </div>

              <div className="p-3 rounded-xl bg-[#0C110E] border border-[#263129] flex items-center justify-between">
                <span className="text-[#9BA8A0]">Kafka Event Stream</span>
                <span className="text-[#63D98A] font-bold font-mono-tech flex items-center gap-1">
                  <CheckCircle2 className="w-3.5 h-3.5" /> 0ms Lag
                </span>
              </div>

              <div className="p-3 rounded-xl bg-[#0C110E] border border-[#263129] flex items-center justify-between">
                <span className="text-[#9BA8A0]">PostGIS Spatial Engine</span>
                <span className="text-[#63D98A] font-bold font-mono-tech flex items-center gap-1">
                  <CheckCircle2 className="w-3.5 h-3.5" /> Active
                </span>
              </div>
            </div>
          </div>

          <div className="p-3.5 rounded-xl bg-[#0C110E] border border-[#263129] text-[11px] text-[#9BA8A0]">
            <div className="flex items-center gap-1.5 text-[#F3F7F4] font-semibold mb-1">
              <Lock className="w-3.5 h-3.5 text-[#F5B942]" /> Role-Based Access Enforced
            </div>
            <p className="leading-snug">
              Surveillance and model calibration actions restricted to authorized DISCO operators.
            </p>
          </div>
        </div>

        {/* Right 2 Cols: Recent System Audit Events */}
        <div className="lg:col-span-2 p-6 rounded-2xl bg-[#101512] border border-[#263129] space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-base font-bold text-[#F3F7F4] font-heading flex items-center gap-2">
                <FileText className="w-4 h-4 text-[#63D98A]" /> Recent System Audit Events
              </h2>
              <p className="text-xs text-[#9BA8A0] mt-0.5">
                Cryptographically verifiable audit log of all model actions, job creation, and sync operations.
              </p>
            </div>
            <button
              onClick={() => navigate(ROUTES.ADMIN.AUDIT)}
              className="text-xs text-[#63D98A] hover:underline font-semibold flex items-center gap-1"
            >
              <span>Full Audit Stream</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-[#0C110E] text-[#9BA8A0] uppercase font-mono-tech border-b border-[#263129]">
                <tr>
                  <th className="p-3">Audit ID</th>
                  <th className="p-3">Actor</th>
                  <th className="p-3">Action</th>
                  <th className="p-3">Target ID</th>
                  <th className="p-3">Timestamp</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#263129]/60">
                {auditEvents.slice(0, 2).map((aud) => (
                  <tr key={aud.id} className="hover:bg-[#161D19] transition-colors">
                    <td className="p-3 font-mono-tech text-[#9BA8A0]">{aud.id}</td>
                    <td className="p-3 font-mono-tech text-[#F3F7F4] font-semibold">{aud.actor}</td>
                    <td className="p-3">
                      <span className="font-mono-tech px-2 py-0.5 rounded text-[10px] bg-[#161D19] text-[#63D98A] border border-[#63D98A]/30">
                        {aud.action}
                      </span>
                    </td>
                    <td className="p-3 font-mono-tech text-[#40D9E8]">{aud.objectId}</td>
                    <td className="p-3 font-mono-tech text-[#9BA8A0]">{aud.timestamp}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </AppShell>
  );
};

