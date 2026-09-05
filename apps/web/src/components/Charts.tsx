"use client";

import React from "react";
import {
  AreaChart,
  Area,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

interface ChartsProps {
  riskOverTime: Array<{ date: string; amount: number }>;
  recoveredOverTime: Array<{ date: string; amount: number }>;
  failureBreakdown: Array<{ reason: string; count: number }>;
  actionBreakdown: Array<{ action: string; count: number }>;
}

export const ChartsSection: React.FC<ChartsProps> = ({
  riskOverTime,
  recoveredOverTime,
  failureBreakdown,
  actionBreakdown,
}) => {
  // Combine time series data
  const combinedTimeData = riskOverTime.map((item, idx) => ({
    date: item.date,
    atRisk: item.amount,
    recovered: recoveredOverTime[idx]?.amount || 0,
  }));

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
      {/* 1. Main Time Series Area Chart */}
      <div className="lg:col-span-2 p-5 rounded-xl bg-white border border-slate-200 shadow-sm">
        <div className="flex items-center justify-between mb-4 flex-wrap gap-2">
          <div>
            <h3 className="text-sm font-bold text-slate-900">Revenue at Risk vs. Recovered Over Time</h3>
            <p className="text-xs text-slate-500">7-day performance trajectory in INR (Dual-Scale)</p>
          </div>
          <div className="flex items-center space-x-4 text-xs font-semibold">
            <span className="flex items-center gap-1.5 text-red-600">
              <span className="w-2.5 h-2.5 rounded-sm bg-red-600" /> At Risk (Left Axis)
            </span>
            <span className="flex items-center gap-1.5 text-emerald-700">
              <span className="w-2.5 h-2.5 rounded-sm bg-emerald-600" /> Recovered (Right Axis)
            </span>
          </div>
        </div>
        <div className="h-64 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={combinedTimeData} margin={{ top: 10, right: 10, left: -10, bottom: 0 }}>
              <defs>
                <linearGradient id="colorRisk" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#DC2626" stopOpacity={0.15} />
                  <stop offset="95%" stopColor="#DC2626" stopOpacity={0.0} />
                </linearGradient>
                <linearGradient id="colorRecovered" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#059669" stopOpacity={0.25} />
                  <stop offset="95%" stopColor="#059669" stopOpacity={0.02} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#F1F5F9" vertical={false} />
              <XAxis dataKey="date" stroke="#94A3B8" fontSize={11} tickLine={false} />
              <YAxis
                yAxisId="risk"
                orientation="left"
                stroke="#DC2626"
                fontSize={10}
                tickLine={false}
                tickFormatter={(val) => `₹${val >= 1000 ? `${(val / 1000).toFixed(0)}k` : val}`}
              />
              <YAxis
                yAxisId="recovered"
                orientation="right"
                stroke="#059669"
                fontSize={10}
                tickLine={false}
                tickFormatter={(val) => `₹${val >= 1000 ? `${(val / 1000).toFixed(0)}k` : val}`}
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: "#FFFFFF",
                  borderColor: "#E2E8F0",
                  borderRadius: "8px",
                  fontSize: "12px",
                  boxShadow: "0 4px 6px -1px rgb(0 0 0 / 0.1)",
                  color: "#0F172A",
                }}
                formatter={(value: any, name: string) => [
                  `₹${Number(value).toLocaleString("en-IN")}`,
                  name === "atRisk" ? "At Risk" : "Recovered",
                ]}
              />
              <Area
                yAxisId="risk"
                type="monotone"
                dataKey="atRisk"
                name="atRisk"
                stroke="#DC2626"
                strokeWidth={2}
                fillOpacity={1}
                fill="url(#colorRisk)"
              />
              <Area
                yAxisId="recovered"
                type="monotone"
                dataKey="recovered"
                name="recovered"
                stroke="#059669"
                strokeWidth={2.5}
                fillOpacity={1}
                fill="url(#colorRecovered)"
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* 2. Failure Category Breakdown */}
      <div className="p-5 rounded-xl bg-white border border-slate-200 shadow-sm">
        <div className="mb-4">
          <h3 className="text-sm font-bold text-slate-900">Failure Root Cause Distribution</h3>
          <p className="text-xs text-slate-500">Categorized by deterministic risk engine</p>
        </div>
        <div className="h-64 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart
              data={failureBreakdown}
              layout="vertical"
              margin={{ top: 5, right: 20, left: 10, bottom: 5 }}
            >
              <CartesianGrid strokeDasharray="3 3" stroke="#F1F5F9" horizontal={false} />
              <XAxis type="number" stroke="#94A3B8" fontSize={11} tickLine={false} />
              <YAxis dataKey="reason" type="category" stroke="#64748B" fontSize={10} width={95} tickLine={false} />
              <Tooltip
                contentStyle={{
                  backgroundColor: "#FFFFFF",
                  borderColor: "#E2E8F0",
                  borderRadius: "8px",
                  fontSize: "12px",
                  boxShadow: "0 4px 6px -1px rgb(0 0 0 / 0.1)",
                  color: "#0F172A",
                }}
              />
              <Bar dataKey="count" name="Cases" fill="#DC2626" radius={[0, 4, 4, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
};
