"use client";

import React, { useEffect, useState } from "react";
import {
  Sparkles,
  TrendingUp,
  ShieldCheck,
  AlertOctagon,
  UserCheck,
  CheckCircle,
  XCircle,
  BarChart2,
  RefreshCw,
} from "lucide-react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from "recharts";
import { api } from "../lib/api";

export const EvaluationDashboard: React.FC = () => {
  const [evalRuns, setEvalRuns] = useState<any[]>([]);
  const [selectedRunDetail, setSelectedRunDetail] = useState<any>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [isRunningEvaluation, setIsRunningEvaluation] = useState<boolean>(false);

  const loadEvaluations = async () => {
    setIsLoading(true);
    try {
      const runs = await api.getEvaluations();
      setEvalRuns(runs);
      if (runs.length > 0) {
        const detail = await api.getEvaluationDetail(runs[0].id);
        setSelectedRunDetail(detail);
      }
    } catch (e) {
      console.error("Failed to load evaluations:", e);
    } finally {
      setIsLoading(false);
    }
  };

  const handleRunEvaluation = async (size: number = 500) => {
    setIsRunningEvaluation(true);
    try {
      const newRun = await api.runEvaluation(size);
      const detail = await api.getEvaluationDetail(newRun.id);
      setEvalRuns((prev) => [newRun, ...prev]);
      setSelectedRunDetail(detail);
    } catch (e) {
      console.error("Failed to run benchmark:", e);
    } finally {
      setIsRunningEvaluation(false);
    }
  };

  useEffect(() => {
    loadEvaluations();
  }, []);

  const latestRun = selectedRunDetail?.run || evalRuns[0];
  const scenarioStats = latestRun?.metrics_breakdown?.scenario_stats || {};

  // Scenario breakdown data
  const scenarioChartData = Object.keys(scenarioStats).map((k) => ({
    scenario: k.replace(/_/g, " ").slice(0, 14),
    aiRecovered: scenarioStats[k].ai_recovered,
    baselineRecovered: scenarioStats[k].baseline_recovered,
  }));

  return (
    <div className="space-y-6">
      {/* Top Action & Summary Banner */}
      <div className="p-6 rounded-2xl bg-white border border-slate-200 shadow-sm flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2.5 flex-wrap gap-y-1">
            <h2 className="text-lg font-bold text-slate-900">Empirical Agent Evaluation Benchmark</h2>
            <span className="px-2.5 py-0.5 text-xs font-bold rounded-full bg-slate-100 text-slate-800 border border-slate-300">
              SYNTHETIC EVALUATION DATASET
            </span>
            <span className="px-2.5 py-0.5 text-xs font-bold rounded-full bg-red-50 text-red-700 border border-red-200">
              500 BENCHMARK CASES
            </span>
          </div>
          <p className="text-xs text-slate-500 mt-1 max-w-2xl leading-relaxed">
            Direct comparison of RazorRecover AI vs. a deterministic naive baseline (single generic retry). All metrics reflect empirical calculations across 12 distinct Indian payment failure topologies on synthetic evaluation data.
          </p>
        </div>

        <button
          onClick={() => handleRunEvaluation(500)}
          disabled={isRunningEvaluation}
          className="flex items-center space-x-2 px-5 py-2.5 rounded-xl bg-brand-600 hover:bg-brand-700 text-white text-xs font-bold transition shadow-sm disabled:opacity-50"
        >
          <Sparkles className={`w-4 h-4 ${isRunningEvaluation ? "animate-spin" : ""}`} />
          <span>{isRunningEvaluation ? "Evaluating 500 Cases..." : "Run 500-Case Evaluation"}</span>
        </button>
      </div>

      {latestRun && (
        <>
          {/* Head-to-Head KPI Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {/* Revenue Recovered vs Baseline */}
            <div className="p-5 rounded-xl bg-white border border-slate-200 shadow-sm">
              <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Evaluation Revenue Recovered</span>
              <div className="text-2xl font-extrabold text-emerald-700 mt-1">
                ₹{latestRun.revenue_recovered?.toLocaleString("en-IN")}
              </div>
              <div className="text-xs text-slate-500 mt-1">
                vs. Baseline: <span className="text-slate-800 font-semibold">₹{latestRun.baseline_recovery?.toLocaleString("en-IN")}</span>
              </div>
            </div>

            {/* Incremental Revenue */}
            <div className="p-5 rounded-xl bg-emerald-50/60 border border-emerald-200 shadow-sm">
              <span className="text-xs font-bold text-emerald-900 flex items-center gap-1.5 uppercase tracking-wider">
                <TrendingUp className="w-3.5 h-3.5 text-emerald-700" /> Incremental Recovery
              </span>
              <div className="text-2xl font-extrabold text-slate-900 mt-1">
                +₹{latestRun.incremental_recovery?.toLocaleString("en-IN")}
              </div>
              <div className="text-xs text-emerald-700 font-bold mt-1">
                +{((latestRun.recovery_rate - latestRun.baseline_recovery_rate)).toFixed(1)}% Higher Recovery Rate
              </div>
            </div>

            {/* Recovery Rate Comparison */}
            <div className="p-5 rounded-xl bg-white border border-slate-200 shadow-sm">
              <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">AI vs Baseline Recovery Rate</span>
              <div className="flex items-baseline space-x-2 mt-1">
                <span className="text-2xl font-extrabold text-brand-600">{latestRun.recovery_rate?.toFixed(1)}%</span>
                <span className="text-sm font-semibold text-slate-400">vs {latestRun.baseline_recovery_rate?.toFixed(1)}%</span>
              </div>
              <div className="text-xs text-slate-500 mt-1">
                From ₹{latestRun.revenue_at_risk?.toLocaleString("en-IN")} at risk in evaluation
              </div>
            </div>

            {/* Safety Metrics */}
            <div className="p-5 rounded-xl bg-white border border-slate-200 shadow-sm">
              <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Deterministic Safety Gating</span>
              <div className="text-2xl font-extrabold text-slate-900 mt-1">
                {latestRun.unsafe_decisions_blocked || 0}
              </div>
              <div className="text-xs text-slate-500 mt-1">
                Unsafe actions blocked • <span className="text-amber-700 font-bold">{latestRun.human_escalations || 0}</span> escalated
              </div>
            </div>
          </div>

          {/* Benchmark Comparison Chart */}
          <div className="p-6 rounded-2xl bg-white border border-slate-200 shadow-sm">
            <h3 className="text-sm font-bold text-slate-900 mb-1">
              Recovered Revenue Comparison Across Scenarios (INR)
            </h3>
            <p className="text-xs text-slate-500 mb-4">
              RazorRecover AI (Razorpay-Red) vs. Naive Baseline (Slate)
            </p>
            <div className="h-72 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={scenarioChartData} margin={{ top: 10, right: 10, left: 10, bottom: 20 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#F1F5F9" vertical={false} />
                  <XAxis dataKey="scenario" stroke="#94A3B8" fontSize={10} angle={-25} textAnchor="end" />
                  <YAxis stroke="#94A3B8" fontSize={11} tickFormatter={(v) => `₹${(v / 1000).toFixed(0)}k`} />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: "#FFFFFF",
                      borderColor: "#E2E8F0",
                      borderRadius: "8px",
                      fontSize: "12px",
                      color: "#0F172A",
                    }}
                    formatter={(val: any) => [`₹${Number(val).toLocaleString("en-IN")}`, ""]}
                  />
                  <Legend />
                  <Bar dataKey="aiRecovered" name="RazorRecover AI" fill="#DC2626" radius={[4, 4, 0, 0]} />
                  <Bar dataKey="baselineRecovered" name="Naive Baseline" fill="#64748B" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Case Inspector Table */}
          <div className="p-6 rounded-2xl bg-white border border-slate-200 shadow-sm">
            <h3 className="text-sm font-bold text-slate-900 mb-1">Detailed Case Evaluation Inspector (Sample 20 of 500)</h3>
            <p className="text-xs text-slate-500 mb-4">
              Inspect decision precision, policy clearance, and simulated execution outcomes across the synthetic dataset.
            </p>
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs text-slate-700">
                <thead className="bg-slate-50 text-slate-500 uppercase text-[10px] font-semibold tracking-wider border-b border-slate-200">
                  <tr>
                    <th className="py-2.5 px-3">Scenario</th>
                    <th className="py-2.5 px-3">Amount</th>
                    <th className="py-2.5 px-3">Expected Action</th>
                    <th className="py-2.5 px-3">Actual AI Action</th>
                    <th className="py-2.5 px-3">Outcome</th>
                    <th className="py-2.5 px-3">Policy Audit Rationale</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {selectedRunDetail?.sample_cases?.slice(0, 20).map((sc: any) => (
                    <tr key={sc.id} className="hover:bg-slate-50 transition">
                      <td className="py-2.5 px-3 font-semibold text-slate-900 capitalize">
                        {sc.scenario.replace(/_/g, " ")}
                      </td>
                      <td className="py-2.5 px-3 font-mono font-medium">₹{sc.amount?.toLocaleString("en-IN")}</td>
                      <td className="py-2.5 px-3 font-mono text-slate-500">{sc.expected_action}</td>
                      <td className="py-2.5 px-3 font-mono text-brand-700 font-bold">{sc.actual_action}</td>
                      <td className="py-2.5 px-3">
                        <span
                          className={`px-2 py-0.5 text-[10px] font-bold rounded-full ${
                            sc.actual_outcome.includes("RECOVERED")
                              ? "bg-emerald-50 text-emerald-700 border border-emerald-200"
                              : sc.actual_outcome.includes("BLOCKED")
                              ? "bg-slate-100 text-slate-700 border border-slate-300"
                              : "bg-red-50 text-red-700 border border-red-200"
                          }`}
                        >
                          {sc.actual_outcome}
                        </span>
                      </td>
                      <td className="py-2.5 px-3 text-slate-500 truncate max-w-[280px]">
                        {sc.reasoning}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </>
      )}
    </div>
  );
};
