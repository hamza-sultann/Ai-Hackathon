import React from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import type { JobCard } from '../../types';
import { RESPONSIBLE_TERMINOLOGY } from '../../config/tokens';

const jobCardSchema = z.object({
  consumerId: z.string().min(1, 'Consumer ID is required'),
  meterId: z.string().min(1, 'Meter ID is required'),
  serviceArea: z.string().min(1, 'Service area is required'),
  feederId: z.string().min(1, 'Feeder ID is required'),
  pmtId: z.string().min(1, 'PMT ID is required'),
  priority: z.enum(['Low', 'Medium', 'High']),
  evidenceSummary: z.string().min(10, 'Provide at least 10 characters of evidence summary'),
  relevantPeriodsText: z.string().min(1, 'Relevant period window is required'),
  estimatedImpactKWhMonth: z.number().min(0, 'Estimated impact must be 0 or greater'),
  safeguardsSummary: z.string().min(1, 'Safeguards summary is required'),
  recommendedChecksText: z.string().min(10, 'Provide recommended physical checks'),
  analystNotes: z.string().min(5, 'Provide analyst notes for the field squad'),
  assignedTeam: z.string().min(1, 'Assigned team is required'),
  scheduledDate: z.string().min(1, 'Scheduled inspection date is required'),
});

type JobCardFormData = z.infer<typeof jobCardSchema>;

interface JobCardFormProps {
  initialData?: Partial<JobCard>;
  onSubmit: (data: Omit<JobCard, 'id' | 'createdAt' | 'status'>) => void;
  onCancel: () => void;
  isSubmitting?: boolean;
}

export const JobCardForm: React.FC<JobCardFormProps> = ({
  initialData,
  onSubmit,
  onCancel,
  isSubmitting = false,
}) => {
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<JobCardFormData>({
    resolver: zodResolver(jobCardSchema),
    defaultValues: {
      consumerId: initialData?.consumerId || 'C-08124',
      meterId: initialData?.meterId || 'MTR-481092',
      serviceArea: initialData?.serviceArea || 'Faisalabad West Division',
      feederId: initialData?.feederId || 'FDR-08',
      pmtId: initialData?.pmtId || 'PMT-081',
      priority: initialData?.priority || 'High',
      evidenceSummary:
        initialData?.evidenceSummary ||
        'Peak-hour usage drop (18:00-22:00 PKT) co-occurring with PMT-081 residual spike. Calibrated anomaly risk 91%.',
      relevantPeriodsText: initialData?.relevantPeriodsText || 'Daily 18:00 - 22:00 PKT (Aug 2026)',
      estimatedImpactKWhMonth: initialData?.estimatedImpactKWhMonth || 184,
      safeguardsSummary:
        initialData?.safeguardsSummary ||
        'All 6 safeguards verified. Solar prosumer excluded. Feeder outages normalized.',
      recommendedChecksText: Array.isArray(initialData?.recommendedChecks)
        ? initialData?.recommendedChecks.join('\n')
        : (initialData?.recommendedChecks as string) ||
          [
            'Inspect physical meter optical port & terminal cover seals.',
            'Check for neutral loop / shunted current transformer (CT) wiring.',
            'Verify incoming secondary cable connection before meter box.',
          ].join('\n'),
      analystNotes:
        initialData?.analystNotes ||
        'Prioritize physical inspection during peak tariff window (18:00 - 20:00). Contact supervisor if meter box is locked.',
      assignedTeam: initialData?.assignedTeam || 'Field Squad Alpha (Faisalabad)',
      scheduledDate: initialData?.scheduledDate || new Date().toISOString().split('T')[0],
    },
  });

  const handleFormSubmit = (data: JobCardFormData) => {
    const checksList = data.recommendedChecksText
      .split('\n')
      .map((line) => line.trim())
      .filter((line) => line.length > 0);

    const payload: Omit<JobCard, 'id' | 'createdAt' | 'status'> = {
      consumerId: data.consumerId,
      meterId: data.meterId,
      serviceArea: data.serviceArea,
      feederId: data.feederId,
      pmtId: data.pmtId,
      priority: data.priority,
      evidenceSummary: data.evidenceSummary,
      relevantPeriodsText: data.relevantPeriodsText,
      estimatedImpactKWhMonth: data.estimatedImpactKWhMonth,
      safeguardsSummary: data.safeguardsSummary,
      recommendedChecks: checksList,
      analystNotes: data.analystNotes,
      assignedTeam: data.assignedTeam,
      scheduledDate: data.scheduledDate,
    };

    onSubmit(payload);
  };

  return (
    <form onSubmit={handleSubmit(handleFormSubmit)} className="space-y-6">
      <div className="p-3 bg-[#161D19] border border-[#263129] rounded-lg text-xs text-[#9BA8A0]">
        <span className="font-semibold text-[#F3F7F4]">Inspection Support Disclaimer:</span>{' '}
        {RESPONSIBLE_TERMINOLOGY.JOB_CARD_DISCLAIMER}
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-xs font-semibold text-[#9BA8A0] mb-1">Consumer ID</label>
          <input
            {...register('consumerId')}
            className="w-full px-3 py-2 bg-[#101512] border border-[#263129] rounded-lg text-xs text-[#F3F7F4] font-mono-tech"
          />
          {errors.consumerId && <span className="text-[11px] text-[#FF6262]">{errors.consumerId.message}</span>}
        </div>

        <div>
          <label className="block text-xs font-semibold text-[#9BA8A0] mb-1">Meter ID</label>
          <input
            {...register('meterId')}
            className="w-full px-3 py-2 bg-[#101512] border border-[#263129] rounded-lg text-xs text-[#F3F7F4] font-mono-tech"
          />
          {errors.meterId && <span className="text-[11px] text-[#FF6262]">{errors.meterId.message}</span>}
        </div>

        <div>
          <label className="block text-xs font-semibold text-[#9BA8A0] mb-1">Feeder ID</label>
          <input
            {...register('feederId')}
            className="w-full px-3 py-2 bg-[#101512] border border-[#263129] rounded-lg text-xs text-[#F3F7F4] font-mono-tech"
          />
        </div>

        <div>
          <label className="block text-xs font-semibold text-[#9BA8A0] mb-1">PMT ID</label>
          <input
            {...register('pmtId')}
            className="w-full px-3 py-2 bg-[#101512] border border-[#263129] rounded-lg text-xs text-[#F3F7F4] font-mono-tech"
          />
        </div>

        <div>
          <label className="block text-xs font-semibold text-[#9BA8A0] mb-1">Inspection Priority</label>
          <select
            {...register('priority')}
            className="w-full px-3 py-2 bg-[#101512] border border-[#263129] rounded-lg text-xs text-[#F3F7F4]"
          >
            <option value="High">High Priority</option>
            <option value="Medium">Medium Priority</option>
            <option value="Low">Low Priority</option>
          </select>
        </div>

        <div>
          <label className="block text-xs font-semibold text-[#9BA8A0] mb-1">Estimated Impact (kWh/month)</label>
          <input
            type="number"
            {...register('estimatedImpactKWhMonth', { valueAsNumber: true })}
            className="w-full px-3 py-2 bg-[#101512] border border-[#263129] rounded-lg text-xs text-[#F3F7F4] font-mono-tech"
          />
        </div>
      </div>

      <div>
        <label className="block text-xs font-semibold text-[#9BA8A0] mb-1">Evidence Summary</label>
        <textarea
          rows={3}
          {...register('evidenceSummary')}
          className="w-full px-3 py-2 bg-[#101512] border border-[#263129] rounded-lg text-xs text-[#F3F7F4]"
        />
        {errors.evidenceSummary && <span className="text-[11px] text-[#FF6262]">{errors.evidenceSummary.message}</span>}
      </div>

      <div>
        <label className="block text-xs font-semibold text-[#9BA8A0] mb-1">Recommended Physical Checks (One per line)</label>
        <textarea
          rows={3}
          {...register('recommendedChecksText')}
          className="w-full px-3 py-2 bg-[#101512] border border-[#263129] rounded-lg text-xs text-[#F3F7F4]"
        />
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-xs font-semibold text-[#9BA8A0] mb-1">Assigned Field Squad</label>
          <input
            {...register('assignedTeam')}
            className="w-full px-3 py-2 bg-[#101512] border border-[#263129] rounded-lg text-xs text-[#F3F7F4]"
          />
        </div>

        <div>
          <label className="block text-xs font-semibold text-[#9BA8A0] mb-1">Scheduled Date</label>
          <input
            type="date"
            {...register('scheduledDate')}
            className="w-full px-3 py-2 bg-[#101512] border border-[#263129] rounded-lg text-xs text-[#F3F7F4]"
          />
        </div>
      </div>

      <div>
        <label className="block text-xs font-semibold text-[#9BA8A0] mb-1">Analyst Notes</label>
        <textarea
          rows={2}
          {...register('analystNotes')}
          className="w-full px-3 py-2 bg-[#101512] border border-[#263129] rounded-lg text-xs text-[#F3F7F4]"
        />
      </div>

      <div className="flex items-center justify-end gap-3 pt-4 border-t border-[#263129]">
        <button
          type="button"
          onClick={onCancel}
          className="px-4 py-2 rounded-lg text-xs font-semibold text-[#9BA8A0] hover:text-[#F3F7F4] hover:bg-[#161D19] transition-colors"
        >
          Cancel
        </button>
        <button
          type="submit"
          disabled={isSubmitting}
          className="px-5 py-2 rounded-lg text-xs font-semibold bg-[#B6F542] hover:bg-[#CAFF69] text-[#070A09] transition-all disabled:opacity-50"
        >
          {isSubmitting ? 'Creating Job-Card...' : 'Issue Official Job-Card'}
        </button>
      </div>
    </form>
  );
};
