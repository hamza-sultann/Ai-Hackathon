import React, { useEffect, useState } from 'react';
import { AppShell } from '../components/common/AppShell';
import { adminApi } from '../services/adminApi';
import { AdminUser } from '../types';
import { ROUTES } from '../config/routes';
import {
  UserCheck,
  UserPlus,
  Shield,
  CheckCircle2,
  Lock,
  Search,
  Mail,
  Building,
  Key,
  X,
} from 'lucide-react';

export const AdminUsersPage: React.FC = () => {
  const [users, setUsers] = useState<AdminUser[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [addUserModalOpen, setAddUserModalOpen] = useState(false);
  const [newUser, setNewUser] = useState({
    name: '',
    email: '',
    role: 'analyst' as any,
    division: 'Faisalabad West Division',
    status: 'Active' as const,
    permissions: ['VIEW_GRID_TELEMETRY'],
  });
  const [statusMessage, setStatusMessage] = useState<string | null>(null);

  useEffect(() => {
    async function loadData() {
      try {
        const data = await adminApi.getUsers();
        setUsers(data);
      } catch (err) {
        console.error('Failed to load users', err);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  const handleCreateUser = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newUser.name || !newUser.email) return;
    try {
      const created = await adminApi.addUser(newUser);
      setUsers((prev) => [...prev, created]);
      setAddUserModalOpen(false);
      setStatusMessage(`User account for ${created.name} provisioned successfully.`);
      setTimeout(() => setStatusMessage(null), 4000);
      setNewUser({
        name: '',
        email: '',
        role: 'analyst',
        division: 'Faisalabad West Division',
        status: 'Active',
        permissions: ['VIEW_GRID_TELEMETRY'],
      });
    } catch (err) {
      console.error('Failed to create user', err);
    }
  };

  const filteredUsers = users.filter(
    (u) =>
      u.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      u.email.toLowerCase().includes(searchQuery.toLowerCase()) ||
      u.division.toLowerCase().includes(searchQuery.toLowerCase()) ||
      u.role.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <AppShell
      currentRole="admin"
      hidePrototypeBanner
      compactBanner
      breadcrumbsItems={[
        { label: 'Admin Ops', href: ROUTES.ADMIN.ROOT },
        { label: 'User Access & Security' },
      ]}
    >
      {/* Header */}
      <div className="holo-card p-6 rounded-2xl bg-[#101512] border border-[#263129] flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl lg:text-2xl font-bold text-[#F3F7F4] font-heading tracking-tight flex items-center gap-2.5">
            <UserCheck className="w-5 h-5 text-[#F5B942]" /> User Access Controls & RBAC
          </h1>
          <p className="text-xs text-[#9BA8A0] mt-1">
            Manage authenticated grid operators, field supervisors, inspector teams, and enterprise DISCO roles.
          </p>
        </div>
        <button
          onClick={() => setAddUserModalOpen(true)}
          className="flex items-center gap-2 px-4 py-2 rounded-xl bg-[#F5B942] hover:bg-[#FFCA58] text-[#070A09] text-xs font-bold transition-all shadow-md active:scale-95 shrink-0"
        >
          <UserPlus className="w-4 h-4" />
          <span>Provision New User</span>
        </button>
      </div>

      {statusMessage && (
        <div className="p-4 rounded-2xl bg-[#63D98A]/10 border border-[#63D98A]/30 text-xs text-[#63D98A] flex items-center gap-2 animate-fadeIn">
          <CheckCircle2 className="w-4 h-4 shrink-0" />
          <span>{statusMessage}</span>
        </div>
      )}

      {/* Search Bar */}
      <div className="p-4 rounded-2xl bg-[#101512] border border-[#263129]">
        <div className="relative">
          <Search className="w-4 h-4 text-[#9BA8A0] absolute left-3.5 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search by name, email, division, or role..."
            className="w-full pl-10 pr-4 py-2 bg-[#0C110E] border border-[#263129] rounded-xl text-xs text-[#F3F7F4] placeholder-[#9BA8A0]/60 focus:outline-none focus:border-[#F5B942] transition-colors font-mono-tech"
          />
        </div>
      </div>

      {/* User Directory Table */}
      <div className="p-6 rounded-2xl bg-[#101512] border border-[#263129] space-y-4">
        <h2 className="text-base font-bold text-[#F3F7F4] font-heading flex items-center gap-2">
          <Shield className="w-4 h-4 text-[#F5B942]" /> Active User Directory
        </h2>

        {loading ? (
          <div className="p-16 text-center text-xs text-[#9BA8A0] animate-pulse">
            Loading User Directory...
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-[#0C110E] text-[#9BA8A0] uppercase font-mono-tech border-b border-[#263129]">
                <tr>
                  <th className="p-3.5">User Identity</th>
                  <th className="p-3.5">Assigned Role</th>
                  <th className="p-3.5">Division / Department</th>
                  <th className="p-3.5">Last Login</th>
                  <th className="p-3.5">Status</th>
                  <th className="p-3.5 text-right">Permissions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#263129]/60">
                {filteredUsers.map((u) => (
                  <tr key={u.id} className="hover:bg-[#161D19] transition-colors">
                    <td className="p-3.5">
                      <div className="font-bold text-[#F3F7F4]">{u.name}</div>
                      <div className="font-mono-tech text-[11px] text-[#9BA8A0]">{u.email}</div>
                    </td>
                    <td className="p-3.5">
                      <span
                        className={`font-semibold capitalize ${
                          u.role === 'analyst'
                            ? 'text-[#B6F542]'
                            : u.role === 'field'
                            ? 'text-[#40D9E8]'
                            : u.role === 'supervisor'
                            ? 'text-[#FF9F43]'
                            : 'text-[#F5B942]'
                        }`}
                      >
                        {u.role === 'analyst' ? 'Operator / Analyst' : u.role}
                      </span>
                    </td>
                    <td className="p-3.5 text-[#9BA8A0]">{u.division}</td>
                    <td className="p-3.5 font-mono-tech text-[#9BA8A0]">{u.lastLogin}</td>
                    <td className="p-3.5">
                      <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-md text-xs font-semibold bg-[#63D98A]/10 text-[#63D98A] border border-[#63D98A]/30">
                        {u.status}
                      </span>
                    </td>
                    <td className="p-3.5 text-right">
                      <span className="font-mono-tech text-[10px] text-[#9BA8A0] bg-[#0C110E] px-2 py-1 rounded-md border border-[#263129]">
                        {u.permissions.length} policies
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Permissions Matrix */}
      <div className="p-6 rounded-2xl bg-[#101512] border border-[#263129] space-y-4">
        <h3 className="text-sm font-bold text-[#F3F7F4] font-heading flex items-center gap-2">
          <Key className="w-4 h-4 text-[#F5B942]" /> Role Permissions Matrix (RBAC)
        </h3>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs border border-[#263129] rounded-xl overflow-hidden">
            <thead className="bg-[#0C110E] text-[#9BA8A0] font-mono-tech">
              <tr>
                <th className="p-3 border-b border-[#263129]">Action Capability</th>
                <th className="p-3 border-b border-[#263129] text-center text-[#B6F542]">Operator / Analyst</th>
                <th className="p-3 border-b border-[#263129] text-center text-[#40D9E8]">Field Inspector</th>
                <th className="p-3 border-b border-[#263129] text-center text-[#FF9F43]">Supervisor</th>
                <th className="p-3 border-b border-[#263129] text-center text-[#F5B942]">System Admin</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#263129]/60">
              <tr>
                <td className="p-3 font-semibold text-[#F3F7F4]">View 3D Grid Topology & Loss Gauges</td>
                <td className="p-3 text-center text-[#63D98A]">✓</td>
                <td className="p-3 text-center text-[#9BA8A0]">—</td>
                <td className="p-3 text-center text-[#63D98A]">✓</td>
                <td className="p-3 text-center text-[#63D98A]">✓</td>
              </tr>
              <tr>
                <td className="p-3 font-semibold text-[#F3F7F4]">Trigger Batch Grid ML Analysis</td>
                <td className="p-3 text-center text-[#63D98A]">✓</td>
                <td className="p-3 text-center text-[#9BA8A0]">—</td>
                <td className="p-3 text-center text-[#63D98A]">✓</td>
                <td className="p-3 text-center text-[#63D98A]">✓</td>
              </tr>
              <tr>
                <td className="p-3 font-semibold text-[#F3F7F4]">Create & Dispatch Field Job-Cards</td>
                <td className="p-3 text-center text-[#63D98A]">✓</td>
                <td className="p-3 text-center text-[#9BA8A0]">—</td>
                <td className="p-3 text-center text-[#63D98A]">✓</td>
                <td className="p-3 text-center text-[#63D98A]">✓</td>
              </tr>
              <tr>
                <td className="p-3 font-semibold text-[#F3F7F4]">Record Clamp Load & Seal Tamper Proof</td>
                <td className="p-3 text-center text-[#9BA8A0]">—</td>
                <td className="p-3 text-center text-[#63D98A]">✓</td>
                <td className="p-3 text-center text-[#63D98A]">✓</td>
                <td className="p-3 text-center text-[#63D98A]">✓</td>
              </tr>
              <tr>
                <td className="p-3 font-semibold text-[#F3F7F4]">Configure AI Anomaly Thresholds & Models</td>
                <td className="p-3 text-center text-[#9BA8A0]">—</td>
                <td className="p-3 text-center text-[#9BA8A0]">—</td>
                <td className="p-3 text-center text-[#9BA8A0]">—</td>
                <td className="p-3 text-center text-[#63D98A]">✓</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      {/* Add User Modal */}
      {addUserModalOpen && (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4 z-50 animate-fadeIn">
          <div className="w-full max-w-lg rounded-2xl bg-[#101512] border border-[#263129] shadow-2xl p-6 space-y-5 animate-slideUp">
            <div className="flex items-center justify-between border-b border-[#263129] pb-4">
              <div>
                <h3 className="text-base font-bold text-[#F3F7F4] font-heading flex items-center gap-2">
                  <UserPlus className="w-4 h-4 text-[#F5B942]" /> Provision New User Account
                </h3>
                <p className="text-xs text-[#9BA8A0]">Add an operator or field squad member to the DISCO portal.</p>
              </div>
              <button
                onClick={() => setAddUserModalOpen(false)}
                className="p-1.5 rounded-lg text-[#9BA8A0] hover:text-[#F3F7F4] hover:bg-[#161D19]"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleCreateUser} className="space-y-4 text-xs">
              <div>
                <label className="text-[#9BA8A0] block mb-1">Full Name</label>
                <input
                  type="text"
                  required
                  value={newUser.name}
                  onChange={(e) => setNewUser({ ...newUser, name: e.target.value })}
                  placeholder="e.g. Engr. Asad Tariq"
                  className="w-full p-2.5 bg-[#0C110E] border border-[#263129] rounded-xl text-[#F3F7F4] focus:outline-none focus:border-[#F5B942]"
                />
              </div>

              <div>
                <label className="text-[#9BA8A0] block mb-1">Official Email Address</label>
                <input
                  type="email"
                  required
                  value={newUser.email}
                  onChange={(e) => setNewUser({ ...newUser, email: e.target.value })}
                  placeholder="e.g. asad.tariq@disco.gov.pk"
                  className="w-full p-2.5 bg-[#0C110E] border border-[#263129] rounded-xl text-[#F3F7F4] font-mono-tech focus:outline-none focus:border-[#F5B942]"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="text-[#9BA8A0] block mb-1">Primary Role</label>
                  <select
                    value={newUser.role}
                    onChange={(e) => setNewUser({ ...newUser, role: e.target.value as any })}
                    className="w-full p-2.5 bg-[#0C110E] border border-[#263129] rounded-xl text-[#F3F7F4] focus:outline-none focus:border-[#F5B942]"
                  >
                    <option value="analyst">Operator / Analyst</option>
                    <option value="field">Field Inspector</option>
                    <option value="supervisor">Field Supervisor</option>
                    <option value="admin">System Admin</option>
                  </select>
                </div>

                <div>
                  <label className="text-[#9BA8A0] block mb-1">Division / Circle</label>
                  <input
                    type="text"
                    value={newUser.division}
                    onChange={(e) => setNewUser({ ...newUser, division: e.target.value })}
                    className="w-full p-2.5 bg-[#0C110E] border border-[#263129] rounded-xl text-[#F3F7F4] focus:outline-none focus:border-[#F5B942]"
                  />
                </div>
              </div>

              <div className="pt-3 flex justify-end gap-2">
                <button
                  type="button"
                  onClick={() => setAddUserModalOpen(false)}
                  className="px-4 py-2 rounded-xl bg-[#161D19] hover:bg-[#263129] text-xs font-semibold text-[#9BA8A0]"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 rounded-xl bg-[#F5B942] hover:bg-[#FFCA58] text-[#070A09] text-xs font-bold transition-all"
                >
                  Provision Account
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </AppShell>
  );
};
