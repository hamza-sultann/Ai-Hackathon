import React, { useEffect, useState } from 'react';
import { AppShell } from '../components/common/AppShell';
import { adminApi } from '../services/adminApi';
import { DataSourceStatus, ModelServiceStatus, AuditEvent } from '../types';
import { Shield, Cpu, Database, UserCheck, FileText, Activity } from 'lucide-react';

export const AdminPage: React.FC = () => {
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

  return (
    <AppShell currentRole="admin">
      <div className="flex items-center justify-between p-5 rounded-xl bg-[#101512] border border-[#263129]">
        <div>
          <h1 className="text-xl font-extrabold text-[#F3F7F4] font-heading flex items-center gap-2">
            <Shield className="w-5 h-5 text-[#F5B942]" /> Admin System Health & Model Telemetry
          </h1>
          <p className="text-xs text-[#9BA8A0] mt-0.5">
            Ingestion Pipelines • Alibaba Cloud PAI-EAS Endpoint Health • Prototype User Access
          </p>
        </div>
      </div>

      {/* Model Services Health */}
      <div className="p-5 rounded-xl bg-[#101512] border border-[#263129] space-y-4">
        <h2 className="text-base font-bold text-[#F3F7F4] font-heading flex items-center gap-2">
          <Cpu className="w-4 h-4 text-[#B6F542]" /> AI Model Microservice Endpoints
        </h2>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-[#0C110E] text-[#9BA8A0] uppercase font-mono-tech border-b border-[#263129]">
              <tr>
                <th className="p-3">Model Service</th>
                <th className="p-3">Technology Stack</th>
                <th className="p-3">Version</th>
                <th className="p-3">P95 Latency</th>
                <th className="p-3">Endpoint URL</th>
                <th className="p-3">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#263129]/60">
              {modelServices.map((ms) => (
                <tr key={ms.id} className="hover:bg-[#161D19]">
                  <td className="p-3 font-semibold text-[#F3F7F4]">{ms.name}</td>
                  <td className="p-3 text-[#9BA8A0]">{ms.technology}</td>
                  <td className="p-3 font-mono-tech text-[#B6F542]">{ms.version}</td>
                  <td className="p-3 font-mono-tech text-[#40D9E8]">{ms.p95LatencyMs} ms</td>
                  <td className="p-3 font-mono-tech text-[#9BA8A0]">{ms.endpoint}</td>
                  <td className="p-3">
                    <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs font-semibold bg-[#63D98A]/10 text-[#63D98A] border border-[#63D98A]/30">
                      <Activity className="w-3.5 h-3.5" /> Healthy
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Data Ingestion Sources */}
      <div className="p-5 rounded-xl bg-[#101512] border border-[#263129] space-y-4">
        <h2 className="text-base font-bold text-[#F3F7F4] font-heading flex items-center gap-2">
          <Database className="w-4 h-4 text-[#40D9E8]" /> Data Telemetry Sources
        </h2>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-[#0C110E] text-[#9BA8A0] uppercase font-mono-tech border-b border-[#263129]">
              <tr>
                <th className="p-3">Source Name</th>
                <th className="p-3">Integration Type</th>
                <th className="p-3">Last Ingested</th>
                <th className="p-3">Record Count</th>
                <th className="p-3">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#263129]/60">
              {dataSources.map((ds) => (
                <tr key={ds.id} className="hover:bg-[#161D19]">
                  <td className="p-3 font-semibold text-[#F3F7F4]">{ds.name}</td>
                  <td className="p-3 text-[#9BA8A0]">{ds.type}</td>
                  <td className="p-3 font-mono-tech text-[#B6F542]">{ds.lastIngestedAt}</td>
                  <td className="p-3 font-mono-tech text-[#F3F7F4]">{ds.recordCount.toLocaleString()}</td>
                  <td className="p-3">
                    <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs font-semibold bg-[#63D98A]/10 text-[#63D98A] border border-[#63D98A]/30">
                      Active
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* User Access Table */}
      <div className="p-5 rounded-xl bg-[#101512] border border-[#263129] space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-base font-bold text-[#F3F7F4] font-heading flex items-center gap-2">
            <UserCheck className="w-4 h-4 text-[#F5B942]" /> User Access Controls
          </h2>
          <span className="text-xs font-mono-tech text-[#F5B942] bg-[#F5B942]/10 px-3 py-1 rounded-md border border-[#F5B942]/30">
            Access controls shown for prototype demonstration only.
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-[#0C110E] text-[#9BA8A0] uppercase font-mono-tech border-b border-[#263129]">
              <tr>
                <th className="p-3">User Email</th>
                <th className="p-3">Role</th>
                <th className="p-3">Division</th>
                <th className="p-3">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#263129]/60">
              <tr className="hover:bg-[#161D19]">
                <td className="p-3 font-mono-tech text-[#F3F7F4]">analyst.hamza@disco.gov.pk</td>
                <td className="p-3 text-[#B6F542] font-semibold">Operator / Analyst</td>
                <td className="p-3 text-[#9BA8A0]">Faisalabad West</td>
                <td className="p-3 text-[#63D98A]">Active</td>
              </tr>
              <tr className="hover:bg-[#161D19]">
                <td className="p-3 font-mono-tech text-[#F3F7F4]">field.tariq@disco.gov.pk</td>
                <td className="p-3 text-[#40D9E8] font-semibold">Field Inspector</td>
                <td className="p-3 text-[#9BA8A0]">Squad Alpha</td>
                <td className="p-3 text-[#63D98A]">Active</td>
              </tr>
              <tr className="hover:bg-[#161D19]">
                <td className="p-3 font-mono-tech text-[#F3F7F4]">admin.system@disco.gov.pk</td>
                <td className="p-3 text-[#F5B942] font-semibold">Admin Ops</td>
                <td className="p-3 text-[#9BA8A0]">Headquarters</td>
                <td className="p-3 text-[#63D98A]">Active</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      {/* Audit Activity */}
      <div className="p-5 rounded-xl bg-[#101512] border border-[#263129] space-y-4">
        <h2 className="text-base font-bold text-[#F3F7F4] font-heading flex items-center gap-2">
          <FileText className="w-4 h-4 text-[#9BA8A0]" /> System Audit Log
        </h2>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-[#0C110E] text-[#9BA8A0] uppercase font-mono-tech border-b border-[#263129]">
              <tr>
                <th className="p-3">Audit ID</th>
                <th className="p-3">Actor</th>
                <th className="p-3">Timestamp</th>
                <th className="p-3">Action</th>
                <th className="p-3">Object ID</th>
                <th className="p-3">Result</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#263129]/60">
              {auditEvents.map((aud) => (
                <tr key={aud.id} className="hover:bg-[#161D19]">
                  <td className="p-3 font-mono-tech text-[#9BA8A0]">{aud.id}</td>
                  <td className="p-3 font-mono-tech text-[#F3F7F4]">{aud.actor}</td>
                  <td className="p-3 font-mono-tech text-[#B6F542]">{aud.timestamp}</td>
                  <td className="p-3 font-semibold text-[#F3F7F4]">{aud.action}</td>
                  <td className="p-3 font-mono-tech text-[#40D9E8]">{aud.objectId}</td>
                  <td className="p-3 text-[#63D98A] font-semibold">{aud.result}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </AppShell>
  );
};
