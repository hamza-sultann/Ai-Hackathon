import React from 'react';
import { AlertTriangle, AlertCircle, CheckCircle2, Clock, ShieldCheck, HelpCircle } from 'lucide-react';
import { Priority, DataQuality, CaseStatus, JobCardStatus } from '../../types';

interface PriorityBadgeProps {
  priority: Priority;
}

export const PriorityBadge: React.FC<PriorityBadgeProps> = ({ priority }) => {
  switch (priority) {
    case 'High':
      return (
        <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs font-semibold bg-[#FF6262]/10 border border-[#FF6262]/30 text-[#FF6262]">
          <AlertTriangle className="w-3.5 h-3.5" /> High Priority
        </span>
      );
    case 'Medium':
      return (
        <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs font-semibold bg-[#FF9F43]/10 border border-[#FF9F43]/30 text-[#FF9F43]">
          <AlertCircle className="w-3.5 h-3.5" /> Medium Priority
        </span>
      );
    case 'Low':
    default:
      return (
        <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs font-semibold bg-[#63D98A]/10 border border-[#63D98A]/30 text-[#63D98A]">
          <CheckCircle2 className="w-3.5 h-3.5" /> Low Priority
        </span>
      );
  }
};

interface DataQualityBadgeProps {
  quality: DataQuality;
}

export const DataQualityBadge: React.FC<DataQualityBadgeProps> = ({ quality }) => {
  switch (quality) {
    case 'Adequate':
      return (
        <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[11px] font-medium bg-[#63D98A]/10 text-[#63D98A] border border-[#63D98A]/20">
          <ShieldCheck className="w-3 h-3" /> Adequate Data
        </span>
      );
    case 'Partial':
      return (
        <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[11px] font-medium bg-[#F5B942]/10 text-[#F5B942] border border-[#F5B942]/20">
          <Clock className="w-3 h-3" /> Partial Data
        </span>
      );
    case 'Degraded':
    case 'Unavailable':
      return (
        <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[11px] font-medium bg-[#FF6262]/10 text-[#FF6262] border border-[#FF6262]/20">
          <AlertCircle className="w-3 h-3" /> {quality} Data
        </span>
      );
    default:
      return <span className="text-xs text-[#9BA8A0]">{quality}</span>;
  }
};

export const CaseStatusBadge: React.FC<{ status: CaseStatus }> = ({ status }) => {
  return (
    <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-md text-xs font-medium bg-[#161D19] text-[#F3F7F4] border border-[#263129]">
      <span className="w-1.5 h-1.5 rounded-full bg-[#B6F542]" />
      {status}
    </span>
  );
};

export const JobCardStatusBadge: React.FC<{ status: JobCardStatus }> = ({ status }) => {
  const getColors = () => {
    switch (status) {
      case 'Closed':
      case 'Submitted':
        return 'bg-[#63D98A]/10 text-[#63D98A] border-[#63D98A]/30';
      case 'Inspection Started':
      case 'En Route':
      case 'In Progress' as any:
        return 'bg-[#40D9E8]/10 text-[#40D9E8] border-[#40D9E8]/30';
      case 'Supervisor Review':
        return 'bg-[#FF9F43]/10 text-[#FF9F43] border-[#FF9F43]/30';
      default:
        return 'bg-[#161D19] text-[#9BA8A0] border-[#263129]';
    }
  };

  return (
    <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs font-semibold border ${getColors()}`}>
      <HelpCircle className="w-3.5 h-3.5" /> {status}
    </span>
  );
};
