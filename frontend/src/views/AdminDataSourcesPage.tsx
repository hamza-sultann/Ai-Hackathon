import React, { useEffect, useState } from 'react';
import { AppShell } from '../components/common/AppShell';
import { adminApi } from '../services/adminApi';
import { DataSourceStatus } from '../types';
import { ROUTES } from '../config/routes';
import {
  Database,
  RefreshCw,
  CheckCircle2,
  AlertCircle,
  Activity,
  Layers,
  Zap,
  Server,
  Sparkles,
} from 'lucide-react';

export const AdminDataSourcesPage: React.FC = () => {
  const [dataSources, setDataSources] = useState<DataSourceStatus[]>([]);
  const [loading, setLoading] = useState(true);
  const [syncingId, setSyncingId] = useState<string | null>(null);
  const [notification, setNotification] = useState<string | null>(null);

  useEffect(() => {
    async function loadData() {
      try {
        const ds = await adminApi.getDataSources();
        setDataSources(ds);
      } catch (err) {
        console.error('Failed to load data sources', err);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  const handleTriggerSync = async (sourceId: string) => {
    setSyncingId(sourceId);
    try {
      const res = await adminApi.triggerDataSourceSync(sourceId);
      setDataSources((prev) =>
        prev.map((ds) => (ds.id === sourceId ? { ...ds, lastIngestedAt: `Just now (${res.timestamp})` } : ds))
      );
      setNotification(res.message);
      setTimeout(() => setNotification(null), 4000);
    } catch (err) {
      console.error('Sync failed', err);
    } finally {
      setSyncingId(null);
    }
  };

  return (
    <AppShell
      currentRole="admin"
      hidePrototypeBanner
      compactBanner
      breadcrumbsItems={[
        { label: 'Admin Ops', href: ROUTES.ADMIN.ROOT },
        { label: 'Data Ingestion Sources' },
      ]}
    >
      {/* Header */}
      <div className="holo-card p-6 rounded-2xl bg-[#101512] border border-[#263129] flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl lg:text-2xl font-bold text-[#F3F7F4] font-heading tracking-tight flex items-center gap-2.5">
            <Database className="w-5 h-5 text-[#40D9E8]" /> Data Telemetry Ingestion Streams
          </h1>
          <p className="text-xs text-[#9BA8A0] mt-1">
            Real-time change data capture (CDC), Kafka high-throughput event buses, Modbus PMT loggers, and GIS sync connectors.
          </p>
        </div>
        <div className="flex items-center gap-2 font-mono-tech text-xs text-[#9BA8A0] px-3.5 py-2 rounded-xl bg-[#0C110E] border border-[#263129]">
          <span className="w-2 h-2 rounded-full bg-[#63D98A] animate-pulse" />
          <span>All 5 Sources Active</span>
        </div>
      </div>

      {notification && (
        <div className="p-4 rounded-2xl bg-[#63D98A]/10 border border-[#63D98A]/30 text-xs text-[#63D98A] flex items-center gap-2 animate-fadeIn">
          <CheckCircle2 className="w-4 h-4 shrink-0" />
          <span>{notification}</span>
        </div>
      )}

      {/* Sources Table */}
      <div className="p-6 rounded-2xl bg-[#101512] border border-[#263129] space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-base font-bold text-[#F3F7F4] font-heading flex items-center gap-2">
            <Layers className="w-4 h-4 text-[#40D9E8]" /> Connected Ingestion Connectors
          </h2>
        </div>

        {loading ? (
          <div className="p-16 text-center text-xs text-[#9BA8A0] animate-pulse">
            Loading Ingestion Pipeline Statuses...
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-[#0C110E] text-[#9BA8A0] uppercase font-mono-tech border-b border-[#263129]">
                <tr>
                  <th className="p-3.5">Source Name</th>
                  <th className="p-3.5">Integration Type</th>
                  <th className="p-3.5">Last Ingested</th>
                  <th className="p-3.5">Record Count</th>
                  <th className="p-3.5">Ingestion Latency</th>
                  <th className="p-3.5">Status</th>
                  <th className="p-3.5 text-right">Manual Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#263129]/60">
                {dataSources.map((ds) => (
                  <tr key={ds.id} className="hover:bg-[#161D19] transition-colors">
                    <td className="p-3.5">
                      <div className="font-bold text-[#F3F7F4]">{ds.name}</div>
                      <span className="text-[10px] font-mono-tech text-[#9BA8A0]">{ds.id}</span>
                    </td>
                    <td className="p-3.5 text-[#9BA8A0]">{ds.type}</td>
                    <td className="p-3.5 font-mono-tech text-[#B6F542]">{ds.lastIngestedAt}</td>
                    <td className="p-3.5 font-mono-tech text-[#F3F7F4] font-bold">
                      {ds.recordCount.toLocaleString()}
                    </td>
                    <td className="p-3.5 font-mono-tech text-[#40D9E8]">{ds.latencyMs} ms</td>
                    <td className="p-3.5">
                      <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-md text-xs font-semibold bg-[#63D98A]/10 text-[#63D98A] border border-[#63D98A]/30">
                        <Activity className="w-3 h-3" /> Active
                      </span>
                    </td>
                    <td className="p-3.5 text-right">
                      <button
                        onClick={() => handleTriggerSync(ds.id)}
                        disabled={syncingId === ds.id}
                        className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-[#161D19] hover:bg-[#40D9E8] hover:text-[#070A09] text-[#40D9E8] border border-[#40D9E8]/30 text-xs font-semibold transition-colors disabled:opacity-50"
                      >
                        <RefreshCw className={`w-3.5 h-3.5 ${syncingId === ds.id ? 'animate-spin' : ''}`} />
                        <span>{syncingId === ds.id ? 'Syncing...' : 'Trigger Sync'}</span>
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* CDC & Kafka Technical Architecture */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="p-5 rounded-2xl bg-[#101512] border border-[#263129] space-y-3">
          <div className="flex items-center gap-2 text-xs font-bold text-[#F3F7F4] font-heading">
            <Zap className="w-4 h-4 text-[#B6F542]" /> Stream Buffer & Partitioning
          </div>
          <p className="text-xs text-[#9BA8A0] leading-relaxed">
            Telemetry from 6,840 smart meters streams directly via Apache Kafka with 4 partitions mapped by feeder identifier. Modbus PMT balance aggregators buffer readings every 15 minutes.
          </p>
        </div>

        <div className="p-5 rounded-2xl bg-[#101512] border border-[#263129] space-y-3">
          <div className="flex items-center gap-2 text-xs font-bold text-[#F3F7F4] font-heading">
            <Server className="w-4 h-4 text-[#40D9E8]" /> Batch CDC Synchronization Schedule
          </div>
          <p className="text-xs text-[#9BA8A0] leading-relaxed">
            SAP IS-U database change logs sync on a daily schedule (18:00 PKT) with automated schema validation and outlier sanitization before model scoring.
          </p>
        </div>
      </div>
    </AppShell>
  );
};
