import React from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import type { InspectionFinding } from '../../types';

const findingsSchema = z.object({
  jobCardId: z.string().min(1, 'Job Card ID is required'),
  meterSealCondition: z.enum(['Intact', 'Tampered', 'Missing', 'Not Inspected']),
  meterCondition: z.enum(['Normal', 'Damaged', 'Stopped', 'Display Fault']),
  wiringCondition: z.enum(['Standard', 'Irregular', 'Bypassed', 'Unsafe']),
  bypassEvidenceObserved: z.boolean(),
  loadObservedKW: z.number().min(0, 'Observed load must be 0 or greater'),
  siteAccessStatus: z.enum(['Accessible', 'Refused', 'Premises Locked', 'Hazardous']),
  consumerPresent: z.boolean(),
  inspectorNotes: z.string().min(5, 'Provide at least 5 characters of field inspection notes'),
  outcome: z.enum([
    'No Irregularity Found',
    'Technical Fault',
    'Meter Issue',
    'Requires Follow-Up',
    'Irregularity Observed',
    'Unable to Inspect',
  ]),
});

type FindingsFormData = z.infer<typeof findingsSchema>;

interface FindingsFormProps {
  jobCardId: string;
  onSubmit: (finding: InspectionFinding) => void;
  onCancel: () => void;
  isSubmitting?: boolean;
}

export const FindingsForm: React.FC<FindingsFormProps> = ({
  jobCardId,
  onSubmit,
  onCancel,
  isSubmitting = false,
}) => {
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<FindingsFormData>({
    resolver: zodResolver(findingsSchema),
    defaultValues: {
      jobCardId,
      meterSealCondition: 'Intact',
      meterCondition: 'Normal',
      wiringCondition: 'Standard',
      bypassEvidenceObserved: false,
      loadObservedKW: 4.5,
      siteAccessStatus: 'Accessible',
      consumerPresent: true,
      inspectorNotes: 'Checked optical port and meter terminal cover. Load measurement taken with clamp meter.',
      outcome: 'Irregularity Observed',
    },
  });

  const handleFormSubmit = (data: FindingsFormData) => {
    const fullFinding: InspectionFinding = {
      jobCardId: data.jobCardId || jobCardId,
      meterSealCondition: data.meterSealCondition,
      meterCondition: data.meterCondition,
      wiringCondition: data.wiringCondition,
      bypassEvidenceObserved: data.bypassEvidenceObserved,
      loadObservedKW: data.loadObservedKW,
      siteAccessStatus: data.siteAccessStatus,
      consumerPresent: data.consumerPresent,
      attachmentPlaceholders: ['photo_meter_front.jpg', 'photo_terminal_box.jpg'],
      inspectorNotes: data.inspectorNotes,
      outcome: data.outcome,
      submittedAt: new Date().toLocaleString() + ' PKT',
      submittedBy: 'Inspector Tariq (Squad Alpha)',
    };
    onSubmit(fullFinding);
  };

  return (
    <form onSubmit={handleSubmit(handleFormSubmit)} className="space-y-6">
      <input type="hidden" {...register('jobCardId')} />
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-xs font-semibold text-[#9BA8A0] mb-1">Meter Seal Condition</label>
          <select
            {...register('meterSealCondition')}
            className="w-full px-3 py-2 bg-[#101512] border border-[#263129] rounded-lg text-xs text-[#F3F7F4]"
          >
            <option value="Intact">Intact</option>
            <option value="Tampered">Tampered</option>
            <option value="Missing">Missing</option>
            <option value="Not Inspected">Not Inspected</option>
          </select>
        </div>

        <div>
          <label className="block text-xs font-semibold text-[#9BA8A0] mb-1">Meter State</label>
          <select
            {...register('meterCondition')}
            className="w-full px-3 py-2 bg-[#101512] border border-[#263129] rounded-lg text-xs text-[#F3F7F4]"
          >
            <option value="Normal">Normal</option>
            <option value="Damaged">Damaged</option>
            <option value="Stopped">Stopped</option>
            <option value="Display Fault">Display Fault</option>
          </select>
        </div>

        <div>
          <label className="block text-xs font-semibold text-[#9BA8A0] mb-1">Wiring Condition</label>
          <select
            {...register('wiringCondition')}
            className="w-full px-3 py-2 bg-[#101512] border border-[#263129] rounded-lg text-xs text-[#F3F7F4]"
          >
            <option value="Standard">Standard Wiring</option>
            <option value="Irregular">Irregular Loop</option>
            <option value="Bypassed">Bypassed</option>
            <option value="Unsafe">Unsafe Wiring</option>
          </select>
        </div>

        <div>
          <label className="block text-xs font-semibold text-[#9BA8A0] mb-1">Observed Clamp Load (kW)</label>
          <input
            type="number"
            step="0.1"
            {...register('loadObservedKW', { valueAsNumber: true })}
            className="w-full px-3 py-2 bg-[#101512] border border-[#263129] rounded-lg text-xs text-[#F3F7F4] font-mono-tech"
          />
        </div>
      </div>

      <div className="flex items-center gap-6 p-3 bg-[#101512] border border-[#263129] rounded-lg">
        <label className="flex items-center gap-2 text-xs font-medium text-[#F3F7F4] cursor-pointer">
          <input
            type="checkbox"
            {...register('bypassEvidenceObserved')}
            className="w-4 h-4 rounded border-[#263129] text-[#B6F542] focus:ring-0 bg-[#070A09]"
          />
          <span>Bypass / Physical Tap Observed</span>
        </label>

        <label className="flex items-center gap-2 text-xs font-medium text-[#F3F7F4] cursor-pointer">
          <input
            type="checkbox"
            {...register('consumerPresent')}
            className="w-4 h-4 rounded border-[#263129] text-[#B6F542] focus:ring-0 bg-[#070A09]"
          />
          <span>Consumer Present On Site</span>
        </label>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-xs font-semibold text-[#9BA8A0] mb-1">Site Access Status</label>
          <select
            {...register('siteAccessStatus')}
            className="w-full px-3 py-2 bg-[#101512] border border-[#263129] rounded-lg text-xs text-[#F3F7F4]"
          >
            <option value="Accessible">Accessible</option>
            <option value="Refused">Refused Access</option>
            <option value="Premises Locked">Premises Locked</option>
            <option value="Hazardous">Hazardous Condition</option>
          </select>
        </div>

        <div>
          <label className="block text-xs font-semibold text-[#9BA8A0] mb-1">Inspection Outcome</label>
          <select
            {...register('outcome')}
            className="w-full px-3 py-2 bg-[#101512] border border-[#263129] rounded-lg text-xs text-[#F3F7F4]"
          >
            <option value="No Irregularity Found">No Irregularity Found</option>
            <option value="Technical Fault">Technical Fault</option>
            <option value="Meter Issue">Meter Issue</option>
            <option value="Requires Follow-Up">Requires Follow-Up</option>
            <option value="Irregularity Observed">Irregularity Observed</option>
            <option value="Unable to Inspect">Unable to Inspect</option>
          </select>
        </div>
      </div>

      <div>
        <label className="block text-xs font-semibold text-[#9BA8A0] mb-1">Field Inspector Notes</label>
        <textarea
          rows={3}
          {...register('inspectorNotes')}
          className="w-full px-3 py-2 bg-[#101512] border border-[#263129] rounded-lg text-xs text-[#F3F7F4]"
        />
        {errors.inspectorNotes && <span className="text-[11px] text-[#FF6262]">{errors.inspectorNotes.message}</span>}
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
          className="px-5 py-2 rounded-lg text-xs font-semibold bg-[#40D9E8] hover:bg-[#68e2f0] text-[#070A09] transition-all disabled:opacity-50"
        >
          {isSubmitting ? 'Submitting...' : 'Submit Inspection Findings'}
        </button>
      </div>
    </form>
  );
};
