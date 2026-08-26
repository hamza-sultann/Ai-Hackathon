import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { UserCheck, Shield, Cpu, HardHat } from 'lucide-react';
import { UserRole } from '../../types';
import { ROUTES } from '../../config/routes';

interface RoleSwitcherProps {
  currentRole: UserRole;
}

export const RoleSwitcher: React.FC<RoleSwitcherProps> = ({ currentRole }) => {
  const navigate = useNavigate();

  const handleRoleChange = (role: UserRole) => {
    switch (role) {
      case 'analyst':
        navigate(ROUTES.ANALYST.ROOT);
        break;
      case 'field':
        navigate(ROUTES.FIELD.ROOT);
        break;
      case 'admin':
        navigate(ROUTES.ADMIN.ROOT);
        break;
    }
  };

  return (
    <div className="flex items-center gap-1.5 bg-[#0C110E] border border-[#263129] p-1 rounded-lg">
      <button
        onClick={() => handleRoleChange('analyst')}
        className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-semibold transition-all ${
          currentRole === 'analyst'
            ? 'bg-[#B6F542] text-[#070A09] shadow-sm'
            : 'text-[#9BA8A0] hover:text-[#F3F7F4] hover:bg-[#161D19]'
        }`}
        title="Operator / Analyst Workspace"
      >
        <Cpu className="w-3.5 h-3.5" />
        <span>Analyst</span>
      </button>

      <button
        onClick={() => handleRoleChange('field')}
        className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-semibold transition-all ${
          currentRole === 'field'
            ? 'bg-[#40D9E8] text-[#070A09] shadow-sm'
            : 'text-[#9BA8A0] hover:text-[#F3F7F4] hover:bg-[#161D19]'
        }`}
        title="Field Inspector / Supervisor Workspace"
      >
        <HardHat className="w-3.5 h-3.5" />
        <span>Field</span>
      </button>

      <button
        onClick={() => handleRoleChange('admin')}
        className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-semibold transition-all ${
          currentRole === 'admin'
            ? 'bg-[#F5B942] text-[#070A09] shadow-sm'
            : 'text-[#9BA8A0] hover:text-[#F3F7F4] hover:bg-[#161D19]'
        }`}
        title="Admin Workspace"
      >
        <Shield className="w-3.5 h-3.5" />
        <span>Admin</span>
      </button>
    </div>
  );
};
