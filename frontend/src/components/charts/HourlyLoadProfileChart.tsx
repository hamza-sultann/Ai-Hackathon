import React from 'react';
import ReactECharts from 'echarts-for-react';
import { HourlyReading } from '../../types';
import { CHART_COLORS } from '../../config/tokens';

interface HourlyLoadProfileChartProps {
  readings: HourlyReading[];
}

export const HourlyLoadProfileChart: React.FC<HourlyLoadProfileChartProps> = ({ readings }) => {
  const hours = readings.map((r) => `${String(r.hourOfDay).padStart(2, '0')}:00`);
  const actuals = readings.map((r) => r.actualUsageKWh);
  const expecteds = readings.map((r) => r.expectedUsageKWh);
  const residuals = readings.map((r) => r.pmtResidualKWh);

  const option = {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'axis',
      formatter: (params: any[]) => {
        let res = `<div style="font-family: monospace; font-size: 11px; padding: 4px;"><strong>Hour ${params[0].name}</strong><br/>`;
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
      data: hours,
      axisLine: { lineStyle: { color: '#263129' } },
      axisLabel: { color: '#9BA8A0', fontSize: 11 },
    },
    yAxis: [
      {
        type: 'value',
        name: 'Consumer kWh',
        splitLine: { lineStyle: { color: '#161D19', type: 'dashed' } },
        axisLabel: { color: '#9BA8A0', fontSize: 11 },
      },
      {
        type: 'value',
        name: 'PMT Residual kWh',
        splitLine: { show: false },
        axisLabel: { color: '#9BA8A0', fontSize: 11 },
      },
    ],
    // MarkArea for 6 PM - 10 PM Peak Tariff Window
    series: [
      {
        name: 'Actual Hourly Load',
        type: 'line',
        smooth: true,
        data: actuals,
        itemStyle: { color: CHART_COLORS.smartMeterPipeline },
        lineStyle: { width: 3 },
        markArea: {
          itemStyle: { color: 'rgba(255, 98, 98, 0.12)' },
          data: [
            [
              { name: 'Peak Tariff (6 PM–10 PM)', xAxis: '18:00' },
              { xAxis: '22:00' },
            ],
          ],
        },
      },
      {
        name: 'Expected Usage Baseline',
        type: 'line',
        smooth: true,
        data: expecteds,
        itemStyle: { color: '#9BA8A0' },
        lineStyle: { type: 'dashed', width: 2 },
      },
      {
        name: 'PMT Residual Spike',
        type: 'bar',
        yAxisIndex: 1,
        data: residuals,
        itemStyle: { color: 'rgba(255, 159, 67, 0.45)', borderRadius: [2, 2, 0, 0] },
      },
    ],
  };

  return (
    <div className="p-5 rounded-xl bg-[#101512] border border-[#263129]">
      <div className="flex items-center justify-between mb-2">
        <div>
          <h3 className="text-sm font-bold text-[#F3F7F4] font-heading">24-Hour Smart Meter Telemetry Profile</h3>
          <p className="text-xs text-[#9BA8A0]">
            Comparing actual usage vs expected baseline & PMT residual co-occurrence (Peak Tariff 18:00–22:00 PKT highlighted)
          </p>
        </div>
      </div>
      <ReactECharts option={option} style={{ height: '320px', width: '100%' }} />
    </div>
  );
};
