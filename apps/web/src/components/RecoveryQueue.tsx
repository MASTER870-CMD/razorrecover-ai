"use client";

import React, { useState } from "react";
import { Search, Eye, Loader2 } from "lucide-react";

interface CaseItem {
  id: string;
  customer_name: string;
  customer_email: string;
  amount: number;
  currency: string;
  risk_score: number;
  risk_level: string;
  recoverability_score: number;
  recommended_action: string;
  current_state: string;
  expected_recovery: number;
  actual_recovery: number;
  failure_reason: string;
  payment_method: string;
}

interface RecoveryQueueProps {
  cases: CaseItem[];
  analyzingCaseId?: string | null;
  approvingCaseId?: string | null;
  executingCaseId?: string | null;
  verifyingCaseId?: string | null;
  onSelectCase: (caseId: string) => void;
  onAnalyzeCase: (caseId: string) => void;
  onApproveCase: (caseId: string) => void;
  onExecuteCase: (caseId: string) => void;
  onVerifyCase?: (caseId: string) => void;
}

export const RecoveryQueue: React.FC<RecoveryQueueProps> = ({
  cases,
  analyzingCaseId,
  approvingCaseId,
  executingCaseId,
  verifyingCaseId,
  onSelectCase,
  onAnalyzeCase,
  onApproveCase,
  onExecuteCase,
  onVerifyCase,
}) => {
  const [filterRisk, setFilterRisk] = useState<string>("ALL");
  const [filterState, setFilterState] = useState<string>("ALL");
  const [search, setSearch] = useState<string>("");

  const filteredCases = cases.filter((c) => {
    if (filterRisk !== "ALL" && c.risk_level !== filterRisk) return false;
    if (filterState !== "ALL" && c.current_state !== filterState) return false;
    if (search) {
      const q = search.toLowerCase();
      return (
        c.customer_name?.toLowerCase().includes(q) ||
        c.customer_email?.toLowerCase().includes(q) ||
        c.failure_reason?.toLowerCase().includes(q) ||
        c.recommended_action?.toLowerCase().includes(q) ||
        c.id?.toLowerCase().includes(q)
      );
    }
    return true;
  });

  const getRiskBadge = (level: string) => {
    switch (level) {
      case "LOW":
        return <span className="px-2 py-0.5 text-[10px] font-bold rounded bg-emerald-50 text-emerald-700 border border-emerald-200">LOW</span>;
      case "MEDIUM":
        return <span className="px-2 py-0.5 text-[10px] font-bold rounded bg-blue-50 text-blue-700 border border-blue-200">MEDIUM</span>;
      case "HIGH":
        return <span className="px-2 py-0.5 text-[10px] font-bold rounded bg-amber-50 text-amber-700 border border-amber-200">HIGH</span>;
      case "CRITICAL":
        return <span className="px-2 py-0.5 text-[10px] font-bold rounded bg-red-50 text-red-700 border border-red-200">CRITICAL</span>;
      default:
        return <span className="px-2 py-0.5 text-[10px] font-medium rounded bg-slate-100 text-slate-600">UNKNOWN</span>;
    }
  };

  const getStateBadge = (state: string) => {
    switch (state) {
      case "RECOVERED":
        return <span className="px-2.5 py-0.5 text-[10px] font-bold rounded-full bg-emerald-50 text-emerald-700 border border-emerald-200">RECOVERED</span>;
      case "WAITING_FOR_PAYMENT":
        return <span className="px-2.5 py-0.5 text-[10px] font-bold rounded-full bg-amber-50 text-amber-700 border border-amber-200 animate-pulse">WAITING FOR PAYMENT</span>;
      case "APPROVED":
      case "READY":
        return <span className="px-2.5 py-0.5 text-[10px] font-bold rounded-full bg-blue-50 text-blue-700 border border-blue-200">READY</span>;
      case "PENDING_APPROVAL":
      case "PENDING_REVIEW":
        return <span className="px-2.5 py-0.5 text-[10px] font-bold rounded-full bg-amber-100 text-amber-800 border border-amber-300">PENDING REVIEW</span>;
      case "BLOCKED":
        return <span className="px-2.5 py-0.5 text-[10px] font-bold rounded-full bg-slate-100 text-slate-700 border border-slate-300">BLOCKED</span>;
      case "EXECUTING":
        return <span className="px-2.5 py-0.5 text-[10px] font-bold rounded-full bg-slate-100 text-slate-800 border border-slate-300">EXECUTING</span>;
      case "AT_RISK":
        return <span className="px-2.5 py-0.5 text-[10px] font-bold rounded-full bg-red-50 text-red-700 border border-red-200">AT RISK</span>;
      case "FAILED":
        return <span className="px-2.5 py-0.5 text-[10px] font-bold rounded-full bg-red-100 text-red-800 border border-red-300">FAILED</span>;
      default:
        return <span className="px-2.5 py-0.5 text-[10px] font-medium rounded-full bg-slate-100 text-slate-700 border border-slate-200">{state?.replace(/_/g, " ")}</span>;
    }
  };

  return (
    <div className="p-5 rounded-xl bg-white border border-slate-200 shadow-sm">
      {/* Filters Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-4">
        <div className="flex items-center space-x-3 flex-wrap gap-y-2">
          <div className="relative">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
            <input
              type="text"
              placeholder="Search customer, failure, or action..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="pl-9 pr-3 py-1.5 rounded-lg bg-slate-50 border border-slate-200 text-xs text-slate-900 placeholder-slate-400 focus:outline-none focus:border-brand-600 w-64"
            />
          </div>

          {/* Risk Filter */}
          <select
            value={filterRisk}
            onChange={(e) => setFilterRisk(e.target.value)}
            className="px-2.5 py-1.5 rounded-lg bg-slate-50 border border-slate-200 text-xs text-slate-700 focus:outline-none focus:border-brand-600"
          >
            <option value="ALL">All Risk Levels</option>
            <option value="LOW">Low Risk</option>
            <option value="MEDIUM">Medium Risk</option>
            <option value="HIGH">High Risk</option>
            <option value="CRITICAL">Critical Risk</option>
          </select>

          {/* State Filter */}
          <select
            value={filterState}
            onChange={(e) => setFilterState(e.target.value)}
            className="px-2.5 py-1.5 rounded-lg bg-slate-50 border border-slate-200 text-xs text-slate-700 focus:outline-none focus:border-brand-600"
          >
            <option value="ALL">All States</option>
            <option value="AT_RISK">At Risk</option>
            <option value="PENDING_APPROVAL">Pending Review</option>
            <option value="APPROVED">Ready / Approved</option>
            <option value="WAITING_FOR_PAYMENT">Waiting For Payment</option>
            <option value="RECOVERED">Recovered</option>
            <option value="BLOCKED">Blocked</option>
          </select>
        </div>

        <div className="text-xs text-slate-500">
          Showing <span className="font-semibold text-slate-900">{filteredCases.length}</span> cases
        </div>
      </div>

      {/* Table */}
      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs text-slate-700">
          <thead className="bg-slate-50 text-slate-500 uppercase text-[10px] font-semibold tracking-wider border-b border-slate-200">
            <tr>
              <th className="py-3 px-3">Customer</th>
              <th className="py-3 px-3">Amount</th>
              <th className="py-3 px-3">Failure Reason</th>
              <th className="py-3 px-3">Risk</th>
              <th className="py-3 px-3">Recoverability</th>
              <th className="py-3 px-3">AI Recommendation</th>
              <th className="py-3 px-3">Status</th>
              <th className="py-3 px-3 text-right">Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {filteredCases.map((c) => (
              <tr
                key={c.id}
                onClick={() => onSelectCase(c.id)}
                className="hover:bg-slate-50/80 cursor-pointer transition group"
              >
                <td className="py-3 px-3">
                  <div className="font-semibold text-slate-900 group-hover:text-brand-600 transition">{c.customer_name}</div>
                  <div className="text-[10px] text-slate-400 truncate max-w-[140px]">{c.customer_email}</div>
                </td>
                <td className="py-3 px-3 font-semibold text-slate-900">
                  ₹{c.amount?.toLocaleString("en-IN")}
                </td>
                <td className="py-3 px-3">
                  <span className="text-slate-700 capitalize font-medium">{c.failure_reason?.replace(/_/g, " ")}</span>
                  <div className="text-[10px] text-slate-400">{c.payment_method}</div>
                </td>
                <td className="py-3 px-3">{getRiskBadge(c.risk_level)}</td>
                <td className="py-3 px-3">
                  <div className="flex items-center space-x-2">
                    <div className="w-12 bg-slate-100 h-1.5 rounded-full overflow-hidden border border-slate-200">
                      <div
                        className="bg-brand-600 h-full rounded-full"
                        style={{ width: `${Math.min(100, c.recoverability_score || 0)}%` }}
                      />
                    </div>
                    <span className="text-[11px] font-medium text-slate-700">{(c.recoverability_score || 0).toFixed(0)}%</span>
                  </div>
                </td>
                <td className="py-3 px-3">
                  {c.current_state === "AT_RISK" ? (
                    <span className="text-slate-400 italic text-[11px] font-medium">Pending AI Diagnosis</span>
                  ) : c.recommended_action ? (
                    <span className="inline-block px-2 py-0.5 rounded font-mono text-[11px] font-semibold bg-slate-100 text-slate-800 border border-slate-200">
                      {c.recommended_action}
                    </span>
                  ) : (
                    <span className="text-slate-400 italic text-[11px]">—</span>
                  )}
                </td>
                <td className="py-3 px-3">{getStateBadge(c.current_state)}</td>
                <td className="py-3 px-3 text-right" onClick={(e) => e.stopPropagation()}>
                  <div className="flex items-center justify-end space-x-1.5">
                    {c.current_state === "AT_RISK" && (
                      <button
                        onClick={() => onAnalyzeCase(c.id)}
                        disabled={analyzingCaseId === c.id}
                        className="px-2.5 py-1 text-[11px] font-medium rounded bg-red-50 text-red-700 hover:bg-red-100 border border-red-200 transition flex items-center gap-1 disabled:opacity-50 disabled:cursor-not-allowed"
                      >
                        {analyzingCaseId === c.id ? (
                          <>
                            <Loader2 className="w-3 h-3 animate-spin" />
                            <span>Analyzing...</span>
                          </>
                        ) : (
                          "Analyze"
                        )}
                      </button>
                    )}
                    {c.current_state === "PENDING_APPROVAL" && (
                      <button
                        onClick={() => onApproveCase(c.id)}
                        disabled={approvingCaseId === c.id}
                        className="px-2.5 py-1 text-[11px] font-medium rounded bg-amber-50 text-amber-800 hover:bg-amber-100 border border-amber-300 transition flex items-center gap-1 disabled:opacity-60 disabled:cursor-not-allowed"
                      >
                        {approvingCaseId === c.id ? (
                          <>
                            <Loader2 className="w-3 h-3 animate-spin" />
                            <span>Approving...</span>
                          </>
                        ) : (
                          "Approve"
                        )}
                      </button>
                    )}
                    {c.current_state === "APPROVED" && (
                      <button
                        onClick={() => onExecuteCase(c.id)}
                        disabled={executingCaseId === c.id}
                        className="px-2.5 py-1 text-[11px] font-semibold rounded bg-brand-600 text-white hover:bg-brand-700 transition shadow-sm flex items-center gap-1 disabled:opacity-60 disabled:cursor-not-allowed"
                      >
                        {executingCaseId === c.id ? (
                          <>
                            <Loader2 className="w-3 h-3 animate-spin" />
                            <span>Creating...</span>
                          </>
                        ) : (
                          "Create Link"
                        )}
                      </button>
                    )}
                    {(c.current_state === "EXECUTING" || c.current_state === "WAITING_FOR_PAYMENT") && onVerifyCase && (
                      <button
                        onClick={() => onVerifyCase(c.id)}
                        disabled={verifyingCaseId === c.id}
                        className="px-2.5 py-1 text-[11px] font-semibold rounded bg-emerald-600 text-white hover:bg-emerald-700 transition shadow-sm flex items-center gap-1 disabled:opacity-60 disabled:cursor-not-allowed"
                      >
                        {verifyingCaseId === c.id ? (
                          <>
                            <Loader2 className="w-3 h-3 animate-spin" />
                            <span>Verifying...</span>
                          </>
                        ) : (
                          "Verify Payment"
                        )}
                      </button>
                    )}
                    {c.current_state === "RECOVERED" && (
                      <span className="text-[11px] font-medium text-emerald-600 px-2 py-0.5 rounded bg-emerald-50 border border-emerald-200">
                        Recovered
                      </span>
                    )}
                    <button
                      onClick={() => onSelectCase(c.id)}
                      className="p-1 rounded text-slate-400 hover:text-slate-800 hover:bg-slate-100 transition"
                      title="View Case Timeline"
                    >
                      <Eye className="w-4 h-4" />
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};
