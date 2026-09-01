import React, { useState } from 'react';
import { ShieldAlert, Info } from 'lucide-react';
import { RESPONSIBLE_TERMINOLOGY } from '../../config/tokens';

interface ResponsibleUseBannerProps {
  message?: string;
  variant?: 'info' | 'warning';
  compact?: boolean;
}

export const ResponsibleUseBanner: React.FC<ResponsibleUseBannerProps> = ({
  message = RESPONSIBLE_TERMINOLOGY.SYSTEM_DISCLAIMER,
  variant = 'info',
  compact = false,
}) => {
  const isWarning = variant === 'warning';
  const [showTooltip, setShowTooltip] = useState(false);

  const compactText = "Inspection-support system — evidence-backed, not a theft determination.";

  if (compact) {
    return (
      <div className="relative flex items-center justify-between h-[36px] px-4 py-2 rounded-lg bg-[#101512] border border-[#263129] border-l-4 border-l-[#B6F542] text-xs text-[#9BA8A0] transition-all">
        <div className="flex items-center gap-2 truncate">
          <span className="font-semibold text-[#F3F7F4] shrink-0">Inspection Support System:</span>
          <span className="truncate">{compactText}</span>
        </div>

        {/* Info Icon with Hover / Click Tooltip Popover */}
        <div
          className="relative flex items-center shrink-0 ml-2"
          onMouseEnter={() => setShowTooltip(true)}
          onMouseLeave={() => setShowTooltip(false)}
          onClick={() => setShowTooltip(!showTooltip)}
        >
          <Info className="w-4 h-4 text-[#9BA8A0] hover:text-[#B6F542] cursor-pointer transition-colors" />

          {showTooltip && (
            <div className="absolute right-0 top-full mt-2 w-80 p-3 bg-[#161D19] border border-[#263129] rounded-xl text-xs text-[#F3F7F4] shadow-2xl z-50 animate-fadeIn pointer-events-none">
              <div className="font-semibold text-[#B6F542] mb-1 flex items-center gap-1.5">
                <Info className="w-3.5 h-3.5" /> Inspection Support Disclaimer
              </div>
              <p className="text-[#9BA8A0] leading-relaxed text-[11px]">{message}</p>
            </div>
          )}
        </div>
      </div>
    );
  }

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
