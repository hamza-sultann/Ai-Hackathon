import React from 'react';
import { TrendingUp, TrendingDown, HelpCircle, Info } from 'lucide-react';
import { GLOSSARY_HELPERS } from '../../config/tokens';

interface MetricCardProps {
  label: string;
  value: string | number;
  unit?: string;
  subtext?: string;
  tooltipText?: string;
  trend?: 'up' | 'down' | 'neutral';
  trendLabel?: string;
  glossaryKey?: keyof typeof GLOSSARY_HELPERS;
  accentColor?: string;
  highlighted?: boolean;
}

export const MetricCard: React.FC<MetricCardProps> = ({
  label,
  value,
  unit,
  subtext,
  tooltipText,
  trend,
  trendLabel,
  glossaryKey,
  accentColor = '#B6F542',
  highlighted = false,
}) => {
  const fullTooltip = tooltipText || (glossaryKey && GLOSSARY_HELPERS[glossaryKey]) || subtext;

  return (
    <div
      className={`holo-card holo-shimmer relative p-5 rounded-xl border ${
        highlighted
          ? 'bg-[#161D19] border-[#B6F542]/40 shadow-lg shadow-[#B6F542]/5'
          : 'bg-[#101512] border-[#263129]'
      }`}
    >
      {/* Content sits above the holo pseudo-elements */}
      <div className="relative z-10">
        <div className="flex items-center justify-between gap-2 mb-2">
          <span className="text-label-caps text-[#9BA8A0] flex items-center gap-1.5">
            {label}
            {glossaryKey && GLOSSARY_HELPERS[glossaryKey] && !tooltipText && (
              <span className="group relative cursor-help inline-flex items-center">
                <HelpCircle className="w-3.5 h-3.5 text-[#9BA8A0]/70 group-hover:text-[#B6F542] transition-colors" />
                <span className="pointer-events-none absolute bottom-full left-1/2 -translate-x-1/2 mb-2 hidden group-hover:block w-56 p-2.5 bg-[#161D19] border border-[#263129] rounded-lg text-xs font-normal normal-case text-[#F3F7F4] shadow-xl z-50">
                  {GLOSSARY_HELPERS[glossaryKey]}
                </span>
              </span>
            )}
          </span>
          {trend && (
            <span
              className={`inline-flex items-center gap-1 text-xs font-semibold ${
                trend === 'up' ? 'text-[#FF6262]' : trend === 'down' ? 'text-[#63D98A]' : 'text-[#9BA8A0]'
              }`}
            >
              {trend === 'up' && <TrendingUp className="w-3.5 h-3.5" />}
              {trend === 'down' && <TrendingDown className="w-3.5 h-3.5" />}
              {trendLabel}
            </span>
          )}
        </div>

        <div className="flex items-baseline gap-2">
          <span
            className="text-3xl font-extrabold font-mono-tech tracking-tight text-[#F3F7F4]"
            style={{ color: highlighted ? accentColor : undefined }}
          >
            {value}
          </span>
          {unit && <span className="text-data-md text-[#9BA8A0]">{unit}</span>}
        </div>

        {subtext && (
          <div className="mt-2 flex items-center justify-between text-xs text-[#9BA8A0]">
            <span className="truncate whitespace-nowrap">{subtext}</span>
            <span className="group relative cursor-help inline-flex items-center shrink-0 ml-1.5">
              <Info className="w-3 h-3 text-[#9BA8A0]/70 group-hover:text-[#B6F542] transition-colors" />
              {fullTooltip && (
                <span className="pointer-events-none absolute bottom-full right-0 mb-2 hidden group-hover:block w-56 p-2.5 bg-[#161D19] border border-[#263129] rounded-lg text-xs font-normal normal-case text-[#F3F7F4] shadow-xl z-50 whitespace-normal leading-relaxed">
                  {fullTooltip}
                </span>
              )}
            </span>
          </div>
        )}
      </div>
    </div>
  );
};
