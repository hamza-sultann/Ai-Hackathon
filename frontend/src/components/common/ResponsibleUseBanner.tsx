import React from 'react';
import { ShieldAlert, Info } from 'lucide-react';
import { RESPONSIBLE_TERMINOLOGY } from '../../config/tokens';

interface ResponsibleUseBannerProps {
  message?: string;
  variant?: 'info' | 'warning';
}

export const ResponsibleUseBanner: React.FC<ResponsibleUseBannerProps> = ({
  message = RESPONSIBLE_TERMINOLOGY.SYSTEM_DISCLAIMER,
  variant = 'info',
}) => {
  const isWarning = variant === 'warning';
  return (
    <div
      className={`flex items-start gap-3 p-3.5 rounded-lg border ${
        isWarning
          ? 'bg-amber-950/20 border-amber-500/30 text-amber-200'
          : 'bg-[#101512] border-[#263129] text-[#9BA8A0]'
      } text-xs leading-relaxed transition-all`}
    >
      {isWarning ? (
        <ShieldAlert className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
      ) : (
        <Info className="w-4 h-4 text-[#B6F542] shrink-0 mt-0.5" />
      )}
      <div>
        <span className="font-semibold text-[#F3F7F4] mr-1.5">Inspection Support System:</span>
        {message}
      </div>
    </div>
  );
};
