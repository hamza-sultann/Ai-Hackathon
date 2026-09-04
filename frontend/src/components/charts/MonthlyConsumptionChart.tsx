import React from 'react';
import ReactECharts from 'echarts-for-react';
import { MonthlyReading } from '../../types';
import { CHART_COLORS } from '../../config/tokens';

interface MonthlyConsumptionChartProps {
  readings: MonthlyReading[];
}

export const MonthlyConsumptionChart: React.FC<MonthlyConsumptionChartProps> = ({ readings }) => {
  const months = readings.map((r) => r.monthYear);
  const billed = readings.map((r) => r.billedKWh);
  const expected = readings.map((r) => r.expectedKWh);
  const peerMedian = readings.map((r) => r.peerMedianKWh);

  const option = {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'axis',
      formatter: (params: any[]) => {
        let res = `<div style="font-family: monospace; font-size: 11px; padding: 4px;"><strong>Period: ${params[0].name}</strong><br/>`;
        params.forEach((p) => {
          res += `${p.marker} ${p.seriesName}: <strong>${p.value} kWh</strong><br/>`;
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
      data: months,
      axisLine: { lineStyle: { color: '#263129' } },
      axisLabel: { color: '#9BA8A0', fontSize: 10, rotate: 45 },
    },
    yAxis: {
      type: 'value',
      name: 'Monthly kWh',
      splitLine: { lineStyle: { color: '#161D19', type: 'dashed' } },
      axisLabel: { color: '#9BA8A0', fontSize: 11 },
    },
    series: [
      {
        name: 'Billed Consumption',
        type: 'line',
        smooth: true,
        data: billed,
        itemStyle: { color: CHART_COLORS.monthlyPipeline },
        lineStyle: { width: 2.5 },
      },
      {
        name: 'Expected Baseline',
        type: 'line',
        smooth: true,
        data: expected,
        itemStyle: { color: '#9BA8A0' },
        lineStyle: { type: 'dashed', width: 1.5 },
      },
      {
        name: 'Peer Group Median',
        type: 'line',
        smooth: true,
        data: peerMedian,
        itemStyle: { color: '#63D98A' },
        lineStyle: { type: 'dotted', width: 1.5 },
      },
    ],
  };

  return (
    <div className="p-5 rounded-xl bg-[#101512] border border-[#263129]">
      <div className="flex items-center justify-between mb-2">
        <div>
          <h3 className="text-sm font-bold text-[#F3F7F4] font-heading">36-Month Historical Consumption Trend</h3>
          <p className="text-xs text-[#9BA8A0]">
            Comparing monthly billed consumption vs historical baseline and peer-group median
          </p>
        </div>
      </div>
      <ReactECharts option={option} style={{ height: '320px', width: '100%' }} />
    </div>
  );
};
