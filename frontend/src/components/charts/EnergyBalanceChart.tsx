import React from 'react';
import ReactECharts from 'echarts-for-react';
import { CHART_COLORS } from '../../config/tokens';

interface EnergyBalanceChartProps {
  injectedMWh: number;
  billedMWh: number;
  technicalLossMWh: number;
  unaccountedResidualMWh: number;
}

export const EnergyBalanceChart: React.FC<EnergyBalanceChartProps> = ({
  injectedMWh,
  billedMWh,
  technicalLossMWh,
  unaccountedResidualMWh,
}) => {
  const option = {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      formatter: (params: any[]) => {
        let res = `<div style="font-family: monospace; font-size: 12px; padding: 4px;"><strong>Energy Mass Balance</strong><br/>`;
        params.forEach((item) => {
          res += `${item.marker} ${item.seriesName}: <strong>${item.value} MWh</strong><br/>`;
        });
        res += `</div>`;
        return res;
      },
    },
    legend: {
      top: '0%',
      textStyle: { color: '#9BA8A0', fontSize: 11 },
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '10%',
      top: '15%',
      containLabel: true,
    },
    xAxis: {
      type: 'category',
      data: ['Injected Energy', 'Mass Balance Accounting'],
      axisLine: { lineStyle: { color: '#263129' } },
      axisLabel: { color: '#9BA8A0', fontSize: 12 },
    },
    yAxis: {
      type: 'value',
      name: 'MWh',
      nameTextStyle: { color: '#9BA8A0' },
      splitLine: { lineStyle: { color: '#161D19', type: 'dashed' } },
      axisLabel: { color: '#9BA8A0', fontSize: 11 },
    },
    series: [
      {
        name: 'Injected Grid Energy',
        type: 'bar',
        barWidth: '40%',
        data: [injectedMWh, 0],
        itemStyle: { color: CHART_COLORS.injected, borderRadius: [4, 4, 0, 0] },
      },
      {
        name: 'Billed Consumption',
        type: 'bar',
        stack: 'balance',
        barWidth: '40%',
        data: [0, billedMWh],
        itemStyle: { color: CHART_COLORS.billed },
      },
      {
        name: 'Estimated Technical Loss',
        type: 'bar',
        stack: 'balance',
        barWidth: '40%',
        data: [0, technicalLossMWh],
        itemStyle: { color: CHART_COLORS.technicalLoss },
      },
      {
        name: 'Unaccounted Residual',
        type: 'bar',
        stack: 'balance',
        barWidth: '40%',
        data: [0, unaccountedResidualMWh],
        itemStyle: { color: CHART_COLORS.residual, borderRadius: [4, 4, 0, 0] },
      },
    ],
  };

  return (
    <div className="p-5 rounded-xl bg-[#101512] border border-[#263129]">
      <div className="flex items-center justify-between mb-2">
        <div>
          <h3 className="text-sm font-bold text-[#F3F7F4] font-heading">PMT Grid Energy Mass Balance</h3>
          <p className="text-xs text-[#9BA8A0]">
            Injected Energy = Billed Energy + Estimated Technical Loss + Unaccounted Residual
          </p>
        </div>
      </div>
      <ReactECharts option={option} style={{ height: '320px', width: '100%' }} />
    </div>
  );
};
