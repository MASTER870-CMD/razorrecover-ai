import React, { useEffect, useState } from "react";
import { Cpu, Terminal, RefreshCw, CheckCircle2, ShieldAlert, Lock, UserCheck, AlertCircle } from "lucide-react";
import { api } from "../lib/api";

export const AgentFeed: React.FC = () => {
  const [activities, setActivities] = useState<any[]>([]);
  const [dashboardData, setDashboardData] = useState<any>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);

  const loadData = async () => {
    setIsLoading(true);
    try {
      const [feed, summary] = await Promise.all([
        api.getAgentActivity(),
        api.getDashboard().catch(() => null),
      ]);
      setActivities(feed);
      if (summary) setDashboardData(summary);
    } catch (e) {
      console.error("Failed to load agent activity:", e);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadData();
    const interval = setInterval(loadData, 8000);
    return () => clearInterval(interval);
  }, []);

  const getActorBadge = (actor: string) => {
    switch (actor) {
      case "AGENT":
        return <span className="px-2 py-0.5 text-[10px] font-bold rounded bg-red-50 text-red-700 border border-red-200">AI_AGENT</span>;
      case "POLICY_ENGINE":
        return <span className="px-2 py-0.5 text-[10px] font-bold rounded bg-slate-100 text-slate-800 border border-slate-300">POLICY_GUARD</span>;
      case "HUMAN_OPERATOR":
        return <span className="px-2 py-0.5 text-[10px] font-bold rounded bg-amber-50 text-amber-800 border border-amber-200">HUMAN_OPERATOR</span>;
      default:
        return <span className="px-2 py-0.5 text-[10px] font-bold rounded bg-slate-100 text-slate-700 border border-slate-200">{actor}</span>;
    }
  };

  return (
    <div className="space-y-6">
      {/* Top Header & Status */}
      <div className="p-6 rounded-xl bg-white border border-slate-200 shadow-sm flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div className="flex items-start space-x-3.5">
          <div className="w-10 h-10 rounded-lg bg-red-50 border border-red-200 flex items-center justify-center text-brand-600 shrink-0 mt-0.5">
            <Cpu className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h2 className="text-base font-bold text-slate-900">AI Recovery Agent Engine</h2>
              <span className="text-xs px-2.5 py-0.5 rounded-full font-bold bg-emerald-50 text-emerald-700 border border-emerald-200 flex items-center gap-1.5">
                <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
                ACTIVE
              </span>
            </div>
            <p className="text-xs text-slate-500 mt-1 leading-relaxed">
              Reasoning layer diagnoses failed transactions, suggests recovery actions, and submits recommendations to deterministic policy guardrails.
            </p>
          </div>
        </div>

        <button
          onClick={loadData}
          className="flex items-center space-x-1.5 text-xs font-semibold text-slate-700 hover:text-slate-900 px-3 py-2 rounded-lg bg-white border border-slate-300 hover:bg-slate-50 transition shadow-sm"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${isLoading ? "animate-spin" : ""}`} />
          <span>Refresh Feed</span>
        </button>
      </div>

      {/* KPI Cards Grid */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
        <div className="p-4 rounded-xl bg-white border border-slate-200 shadow-sm">
          <span className="text-[11px] font-semibold text-slate-500 uppercase">Cases Analyzed</span>
          <div className="text-xl font-bold text-slate-900 mt-1">
            {dashboardData?.total_cases || 0}
          </div>
        </div>

        <div className="p-4 rounded-xl bg-white border border-slate-200 shadow-sm">
          <span className="text-[11px] font-semibold text-slate-500 uppercase">Recommendations</span>
          <div className="text-xl font-bold text-brand-600 mt-1">
            {dashboardData?.total_cases || 0}
          </div>
        </div>

        <div className="p-4 rounded-xl bg-white border border-slate-200 shadow-sm">
          <span className="text-[11px] font-semibold text-slate-500 uppercase">Approved Actions</span>
          <div className="text-xl font-bold text-emerald-700 mt-1">
            {((dashboardData?.total_cases || 0) - (dashboardData?.human_review_cases || 0) - (dashboardData?.blocked_actions || 0))}
          </div>
        </div>

        <div className="p-4 rounded-xl bg-white border border-slate-200 shadow-sm">
          <span className="text-[11px] font-semibold text-slate-500 uppercase">Human Escalations</span>
          <div className="text-xl font-bold text-amber-700 mt-1">
            {dashboardData?.human_review_cases || 0}
          </div>
        </div>

        <div className="p-4 rounded-xl bg-white border border-slate-200 shadow-sm">
          <span className="text-[11px] font-semibold text-slate-500 uppercase">Blocked Actions</span>
          <div className="text-xl font-bold text-slate-900 mt-1">
            {dashboardData?.blocked_actions || 0}
          </div>
        </div>
      </div>

      {/* Live Stream of Agent Decisions */}
      <div className="p-6 rounded-xl bg-white border border-slate-200 shadow-sm space-y-4">
        <h3 className="text-xs font-bold text-slate-900 uppercase tracking-wider flex items-center gap-2">
          <Terminal className="w-4 h-4 text-slate-600" />
          <span>Agent Reasoning & Telemetry Log</span>
        </h3>

        <div className="space-y-3 font-mono text-xs">
          {activities.map((act) => (
            <div
              key={act.id}
              className="p-4 rounded-xl bg-slate-50 border border-slate-200 hover:border-slate-300 transition flex flex-col md:flex-row md:items-center justify-between gap-3"
            >
              <div className="flex items-start md:items-center space-x-3">
                <span className="text-slate-400 text-[11px] shrink-0 font-sans">
                  {act.timestamp ? new Date(act.timestamp).toLocaleTimeString() : "--:--:--"}
                </span>
                {getActorBadge(act.actor)}
                <div className="text-slate-700 font-sans">
                  <span className="text-slate-900 font-bold">{act.customer_name}: </span>
                  <span className="text-slate-800 font-medium">{act.action || act.event_type}</span>
                  {act.decision && (
                    <span className="text-slate-500 ml-1.5">
                      → Decision: <span className="text-emerald-700 font-bold">{act.decision}</span>
                    </span>
                  )}
                </div>
              </div>

              <div className="flex items-center space-x-3 text-[11px] text-slate-500 font-sans">
                {act.amount > 0 && (
                  <span className="font-bold text-slate-900">₹{act.amount.toLocaleString("en-IN")}</span>
                )}
                {act.new_state && (
                  <span className="px-2 py-0.5 rounded bg-white text-slate-700 border border-slate-200 font-bold">
                    {act.new_state}
                  </span>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
