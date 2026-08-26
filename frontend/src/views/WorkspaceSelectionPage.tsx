import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Cpu, HardHat, Shield, ArrowRight, Zap, Info } from 'lucide-react';
import { ROUTES } from '../config/routes';

export const WorkspaceSelectionPage: React.FC = () => {
  const navigate = useNavigate();

  const roles = [
    {
      key: 'analyst',
      icon: <Cpu className="w-6 h-6" />,
      title: 'Operator / Analyst',
      desc: 'Full access to PMT mass balance, monthly & smart-meter telemetry comparison, TreeSHAP explanations, investigation queues, and job-card creation.',
      color: '#B6F542',
      holoClass: 'holo-card',
      cta: 'Launch Analyst View',
      route: ROUTES.ANALYST.ROOT,
    },
    {
      key: 'field',
      icon: <HardHat className="w-6 h-6" />,
      title: 'Field Inspector / Supervisor',
      desc: 'Access assigned job-cards, site verification checklists, meter seal condition recording, clamp load testing, findings submission, and supervisor review.',
      color: '#40D9E8',
      holoClass: 'holo-card holo-card-cyan',
      cta: 'Launch Field View',
      route: ROUTES.FIELD.ROOT,
    },
    {
      key: 'admin',
      icon: <Shield className="w-6 h-6" />,
      title: 'Admin & System Ops',
      desc: 'Monitor data telemetry ingestion, model service health (PAI-EAS / Isolation Forest / TreeSHAP), prototype access controls, and audit trails.',
      color: '#F5B942',
      holoClass: 'holo-card holo-card-amber',
      cta: 'Launch Admin View',
      route: ROUTES.ADMIN.ROOT,
    },
  ];

  return (
    <div className="min-h-screen bg-[#070A09] text-[#F3F7F4] flex flex-col justify-between">
      {/* Header */}
      <header className="h-16 border-b border-[#263129] px-6 flex items-center">
        <div className="flex items-center gap-2">
          <Zap className="w-5 h-5 text-[#B6F542]" />
          <span className="text-headline-sm tracking-tight text-[#F3F7F4]">Istikshaf</span>
        </div>
      </header>

      {/* Main Selection Area */}
      <main className="max-w-5xl mx-auto px-6 py-12 w-full space-y-8">
        {/* Prototype Warning Banner */}
        <div className="holo-card p-4 rounded-xl bg-[#161D19] border border-[#B6F542]/40 text-xs text-[#9BA8A0] flex items-start gap-3">
          <Info className="w-5 h-5 text-[#B6F542] shrink-0 mt-0.5" />
          <div className="relative z-10">
            <span className="font-bold text-[#F3F7F4] block text-sm mb-0.5">Prototype Access Enabled</span>
            Prototype access — authentication is disabled for this demonstration. Select a role below to launch its workspace.
          </div>
        </div>

        <div className="text-center space-y-2">
          <h1 className="text-headline-lg text-[#F3F7F4]">Select Workspace Role</h1>
          <p className="text-sm text-[#9BA8A0]">Choose an operational interface to proceed into the system.</p>
        </div>

        {/* 3 Role Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {roles.map((role) => (
            <div
              key={role.key}
              onClick={() => navigate(role.route)}
              className={`${role.holoClass} holo-shimmer holo-scanlines group cursor-pointer p-6 rounded-2xl bg-[#101512] border border-[#263129] flex flex-col justify-between space-y-6`}
            >
              <div className="relative z-10 space-y-4">
                <div
                  className="w-12 h-12 rounded-xl flex items-center justify-center transition-all duration-300"
                  style={{
                    backgroundColor: `${role.color}15`,
                    color: role.color,
                  }}
                >
                  {role.icon}
                </div>
                <h2 className="text-headline-sm text-[#F3F7F4]">{role.title}</h2>
                <p className="text-xs text-[#9BA8A0] leading-relaxed">{role.desc}</p>
              </div>
              <div
                className="relative z-10 flex items-center justify-between text-xs font-semibold pt-4 border-t border-[#263129]"
                style={{ color: role.color }}
              >
                <span>{role.cta}</span>
                <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
              </div>
            </div>
          ))}
        </div>
      </main>

      {/* Footer */}
      <footer className="py-6 border-t border-[#263129] text-center text-label-caps text-[#9BA8A0]">
        Istikshaf Electricity Distribution Companies Prototype • Responsible AI Framework
      </footer>
    </div>
  );
};
