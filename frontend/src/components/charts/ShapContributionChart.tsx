import React from 'react';
import ReactECharts from 'echarts-for-react';
import { ShapFeatureContribution } from '../../types';

interface ShapContributionChartProps {
  contributions: ShapFeatureContribution[];
}

export const ShapContributionChart: React.FC<ShapContributionChartProps> = ({ contributions }) => {
  const names = contributions.map((c) => c.featureName);
  const values = contributions.map((c) => c.contributionValue);

  const option = {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      formatter: (params: any[]) => {
        const item = params[0];
        const obj = contributions[item.dataIndex];
        return `<div style="font-family: monospace; font-size: 11px; padding: 4px; max-width: 260px;">
          <strong>${obj.featureName}</strong><br/>
          SHAP Value: <strong>${obj.contributionValue > 0 ? '+' : ''}${obj.contributionValue}</strong><br/>
          <span style="color: #9BA8A0;">${obj.description}</span>
        </div>`;
      },
    },
    grid: {
      left: '3%',
      right: '8%',
      bottom: '5%',
      top: '5%',
      containLabel: true,
    },
    xAxis: {
      type: 'value',
      name: 'Risk Impact',
      splitLine: { lineStyle: { color: '#161D19', type: 'dashed' } },
      axisLabel: { color: '#9BA8A0', fontSize: 11 },
    },
    yAxis: {
      type: 'category',
      data: names,
      axisLine: { lineStyle: { color: '#263129' } },
      axisLabel: { color: '#F3F7F4', fontSize: 11 },
    },
    series: [
      {
        name: 'SHAP Value',
        type: 'bar',
        barWidth: '45%',
        data: values.map((v) => ({
          value: v,
          itemStyle: {
            color: v > 0 ? '#FF6262' : '#63D98A',
            borderRadius: v > 0 ? [0, 4, 4, 0] : [4, 0, 0, 4],
          },
        })),
      },
    ],
  };

  return (
    <div className="p-5 rounded-xl bg-[#101512] border border-[#263129]">
      <div className="mb-2">
        <h3 className="text-sm font-bold text-[#F3F7F4] font-heading">TreeSHAP Feature Contribution</h3>
        <p className="text-xs text-[#9BA8A0]">
          Positive values (coral) increase calibrated anomaly risk. Negative values (green) reduce risk.
        </p>
      </div>
      <ReactECharts option={option} style={{ height: '260px', width: '100%' }} />
    </div>
  );
};
