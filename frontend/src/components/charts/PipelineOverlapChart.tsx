import React from 'react';
import ReactECharts from 'echarts-for-react';
import { PipelineComparison } from '../../types';
import { CHART_COLORS } from '../../config/tokens';

interface PipelineOverlapChartProps {
  comparison: PipelineComparison;
}

export const PipelineOverlapChart: React.FC<PipelineOverlapChartProps> = ({ comparison }) => {
  const option = {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'item',
      formatter: '{b}: <strong>{c} Connections</strong> ({d}%)',
    },
    legend: {
      bottom: '0%',
      textStyle: { color: '#9BA8A0', fontSize: 11 },
    },
    series: [
      {
        name: 'Pipeline Detections',
        type: 'pie',
        radius: ['45%', '70%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 6,
          borderColor: '#101512',
          borderWidth: 3,
        },
        label: {
          show: true,
          color: '#F3F7F4',
          fontSize: 11,
          formatter: '{b}\n{c} ({d}%)',
        },
        data: [
          { value: comparison.monthlyOnlyCount, name: 'Monthly Billing Only', itemStyle: { color: CHART_COLORS.monthlyPipeline } },
          { value: comparison.smartMeterOnlyCount, name: 'Smart Meter Only', itemStyle: { color: CHART_COLORS.smartMeterPipeline } },
          { value: comparison.bothPipelinesCount, name: 'Both Pipelines (High Confidence)', itemStyle: { color: CHART_COLORS.agreement } },
        ],
      },
    ],
  };

  return (
    <div className="p-5 rounded-xl bg-[#101512] border border-[#263129]">
      <div className="mb-2">
        <h3 className="text-sm font-bold text-[#F3F7F4] font-heading">Pipeline Detection Overlap</h3>
        <p className="text-xs text-[#9BA8A0]">
          Consensus between monthly billing trends and hourly smart-meter telemetry
        </p>
      </div>
      <ReactECharts option={option} style={{ height: '300px', width: '100%' }} />
    </div>
  );
};
