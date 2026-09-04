import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { AppShell } from '../components/common/AppShell';
import { fieldApi } from '../services/fieldApi';
import { FieldSquad, FieldTeamMember } from '../types';
import { ROUTES } from '../config/routes';
import {
  Users,
  HardHat,
  Truck,
  Phone,
  MapPin,
  CheckCircle2,
  Clock,
  Shield,
  Activity,
  ArrowRight,
  Sparkles,
} from 'lucide-react';

export const FieldTeamPage: React.FC = () => {
  const navigate = useNavigate();
  const [squads, setSquads] = useState<FieldSquad[]>([]);
  const [teamMembers, setTeamMembers] = useState<FieldTeamMember[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedSquadId, setSelectedSquadId] = useState<string>('all');

  useEffect(() => {
    async function loadData() {
      try {
        const [sqData, tmData] = await Promise.all([
          fieldApi.getFieldSquads(),
          fieldApi.getTeamMembers(),
        ]);
        setSquads(sqData);
        setTeamMembers(tmData);
      } catch (err) {
        console.error('Failed to load team data', err);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  const filteredMembers = teamMembers.filter((m) => {
    if (selectedSquadId === 'all') return true;
    return m.squadId === selectedSquadId;
  });

  return (
    <AppShell
      currentRole="field"
      hidePrototypeBanner
      compactBanner
      breadcrumbsItems={[
        { label: 'Field Workspace', href: ROUTES.FIELD.ROOT },
        { label: 'Team Queue & Rosters' },
      ]}
    >
      {/* Header */}
      <div className="holo-card p-6 rounded-2xl bg-[#101512] border border-[#263129] flex flex-col md:flex-row md:items-center justify-between gap-4">
        <h1 className="text-xl lg:text-2xl font-bold text-[#F3F7F4] font-heading tracking-tight flex items-center gap-2.5">
          <Users className="w-5 h-5 text-[#63D98A]" /> Field Squads & Personnel Roster
        </h1>
        <div className="flex items-center gap-3">
          <div className="px-3.5 py-2 rounded-xl bg-[#0C110E] border border-[#263129] text-xs font-mono-tech text-[#9BA8A0] flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-[#63D98A] animate-pulse" />
            <span>3 Squads In Field</span>
          </div>
        </div>
      </div>

      {/* Squad Overview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {squads.map((sq) => {
          const isSelected = selectedSquadId === sq.id;
          return (
            <div
              key={sq.id}
              onClick={() => setSelectedSquadId(selectedSquadId === sq.id ? 'all' : sq.id)}
              className={`p-5 rounded-2xl border transition-all cursor-pointer flex flex-col justify-between space-y-4 ${
                isSelected
                  ? 'bg-[#161D19] border-[#63D98A] shadow-lg shadow-[#63D98A]/10'
                  : 'bg-[#101512] border-[#263129] hover:border-[#63D98A]/50 hover:bg-[#161D19]/60'
              }`}
            >
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-mono-tech text-[#63D98A] font-bold">
                    {sq.division}
                  </span>
                  <span className="px-2 py-0.5 rounded text-[10px] font-mono-tech bg-[#63D98A]/10 text-[#63D98A] border border-[#63D98A]/20 font-bold">
                    {sq.status}
                  </span>
                </div>
                <h3 className="text-base font-bold text-[#F3F7F4] font-heading">{sq.name}</h3>
                <p className="text-xs text-[#9BA8A0]">
                  Lead: <strong className="text-[#F3F7F4]">{sq.leaderName}</strong>
                </p>
              </div>

              <div className="grid grid-cols-3 gap-2 p-3 rounded-xl bg-[#0C110E] border border-[#263129]/60 text-center text-xs">
                <div>
                  <span className="text-[10px] text-[#9BA8A0] block">Assigned</span>
                  <span className="font-mono-tech font-bold text-[#F3F7F4]">{sq.assignedJobsCount}</span>
                </div>
                <div>
                  <span className="text-[10px] text-[#9BA8A0] block">Done</span>
                  <span className="font-mono-tech font-bold text-[#63D98A]">{sq.completedJobsCount}</span>
                </div>
                <div>
                  <span className="text-[10px] text-[#9BA8A0] block">Efficiency</span>
                  <span className="font-mono-tech font-bold text-[#40D9E8]">{sq.efficiencyRate}%</span>
                </div>
              </div>

              <div className="pt-2 border-t border-[#263129] flex items-center justify-between text-xs text-[#9BA8A0]">
                <span className="flex items-center gap-1.5 font-mono-tech">
                  <Truck className="w-3.5 h-3.5 text-[#B6F542]" />
                  <span>{sq.vehiclePlate}</span>
                </span>
                <span className="text-[11px] text-[#63D98A] font-semibold">
                  {isSelected ? 'Viewing Roster' : 'Filter Roster →'}
                </span>
              </div>
            </div>
          );
        })}
      </div>

      {/* Team Member Roster Table */}
      <div className="p-6 rounded-2xl bg-[#101512] border border-[#263129] space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
          <div>
            <h2 className="text-base font-bold text-[#F3F7F4] font-heading flex items-center gap-2">
              <HardHat className="w-4 h-4 text-[#63D98A]" /> Field Inspectors Active Roster
            </h2>
            <p className="text-xs text-[#9BA8A0] mt-0.5">
              {selectedSquadId === 'all' ? 'Showing all inspectors across squads' : `Filtered by selected squad`}
            </p>
          </div>

          {selectedSquadId !== 'all' && (
            <button
              onClick={() => setSelectedSquadId('all')}
              className="text-xs text-[#63D98A] hover:underline font-semibold"
            >
              Clear Filter (Show All)
            </button>
          )}
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-[#0C110E] text-[#9BA8A0] uppercase font-mono-tech border-b border-[#263129]">
              <tr>
                <th className="p-3.5">Inspector Name</th>
                <th className="p-3.5">Designation</th>
                <th className="p-3.5">Squad</th>
                <th className="p-3.5">Current Status</th>
                <th className="p-3.5">Assigned Location</th>
                <th className="p-3.5">Active Job</th>
                <th className="p-3.5">Phone</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#263129]/60">
              {filteredMembers.map((tm) => (
                <tr key={tm.id} className="hover:bg-[#161D19] transition-colors">
                  <td className="p-3.5">
                    <div className="font-bold text-[#F3F7F4]">{tm.name}</div>
                    <span className="text-[10px] font-mono-tech text-[#9BA8A0]">{tm.id}</span>
                  </td>
                  <td className="p-3.5 text-[#9BA8A0]">{tm.designation}</td>
                  <td className="p-3.5 font-mono-tech text-[#63D98A] font-semibold">{tm.squadName}</td>
                  <td className="p-3.5">
                    <span
                      className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs font-semibold ${
                        tm.currentStatus === 'On-Site Inspection'
                          ? 'bg-[#FF6262]/10 text-[#FF6262] border border-[#FF6262]/30'
                          : tm.currentStatus === 'En Route'
                          ? 'bg-[#40D9E8]/10 text-[#40D9E8] border border-[#40D9E8]/30'
                          : tm.currentStatus === 'Reviewing Findings'
                          ? 'bg-[#FF9F43]/10 text-[#FF9F43] border border-[#FF9F43]/30'
                          : 'bg-[#63D98A]/10 text-[#63D98A] border border-[#63D98A]/30'
                      }`}
                    >
                      <span className="w-1.5 h-1.5 rounded-full bg-current" />
                      {tm.currentStatus}
                    </span>
                  </td>
                  <td className="p-3.5 text-[#F3F7F4] flex items-center gap-1.5">
                    <MapPin className="w-3.5 h-3.5 text-[#9BA8A0] shrink-0" />
                    <span className="truncate max-w-xs">{tm.assignedLocation}</span>
                  </td>
                  <td className="p-3.5">
                    {tm.activeJobId ? (
                      <button
                        onClick={() => navigate(ROUTES.FIELD.JOB_DETAIL(tm.activeJobId!))}
                        className="font-mono-tech text-[#40D9E8] font-bold hover:underline"
                      >
                        {tm.activeJobId}
                      </button>
                    ) : (
                      <span className="text-[#9BA8A0] font-mono-tech">—</span>
                    )}
                  </td>
                  <td className="p-3.5 font-mono-tech text-[#9BA8A0]">{tm.phone}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </AppShell>
  );
};
