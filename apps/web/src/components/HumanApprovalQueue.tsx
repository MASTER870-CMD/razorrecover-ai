import React from "react";
import { Check, X, UserCheck, ArrowUpRight } from "lucide-react";

interface ApprovalCase {
  id: string;
  customer_name: string;
  customer_email: string;
  amount: number;
  risk_level: string;
  recoverability_score: number;
  recommended_action: string;
  expected_recovery: number;
  failure_reason: string;
  current_state: string;
}

interface HumanApprovalQueueProps {
  cases: ApprovalCase[];
  onApprove: (caseId: string) => void;
  onReject: (caseId: string) => void;
  onSelectCase: (caseId: string) => void;
}

export const HumanApprovalQueue: React.FC<HumanApprovalQueueProps> = ({
  cases,
  onApprove,
  onReject,
  onSelectCase,
}) => {
  const pendingCases = cases.filter((c) => c.current_state === "PENDING_APPROVAL");

  return (
    <div className="space-y-4">
      {/* Header Banner */}
      <div className="p-4 rounded-xl bg-amber-50 border border-amber-200 flex items-start space-x-3 shadow-sm">
        <UserCheck className="w-5 h-5 text-amber-700 shrink-0 mt-0.5" />
        <div>
          <h2 className="text-sm font-bold text-amber-900">Human-In-The-Loop Approval Center</h2>
          <p className="text-xs text-amber-700 mt-0.5 leading-relaxed">
            RazorRecover AI's deterministic safety engine halts actions exceeding automated thresholds (e.g. transaction amount &gt; ₹25,000, critical risk, or low AI confidence). Explicit merchant authorization is required before recovery link creation.
          </p>
        </div>
      </div>

      {pendingCases.length === 0 ? (
        <div className="p-12 rounded-xl bg-white border border-slate-200 text-center shadow-sm">
          <Check className="w-10 h-10 text-emerald-600 mx-auto mb-2 opacity-80" />
          <h3 className="text-sm font-bold text-slate-900">Approval Queue Clear</h3>
          <p className="text-xs text-slate-500 mt-1">
            No transactions currently require manual merchant authorization.
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {pendingCases.map((c) => (
            <div
              key={c.id}
              className="p-5 rounded-xl bg-white border border-slate-200 hover:border-amber-400 transition flex flex-col justify-between shadow-sm"
            >
              <div>
                <div className="flex items-center justify-between mb-3">
                  <div>
                    <span className="text-sm font-bold text-slate-900 truncate block max-w-[220px]">
                      {c.customer_name}
                    </span>
                    <span className="text-[11px] text-slate-400 truncate block">
                      {c.customer_email}
                    </span>
                  </div>
                  <span className="text-base font-bold text-slate-900">
                    ₹{c.amount?.toLocaleString("en-IN")}
                  </span>
                </div>

                <div className="space-y-2 mb-4 text-xs">
                  <div className="flex justify-between text-slate-600">
                    <span>Failure Reason:</span>
                    <span className="text-slate-900 font-medium capitalize">{c.failure_reason?.replace(/_/g, " ")}</span>
                  </div>
                  <div className="flex justify-between text-slate-600">
                    <span>Risk Level:</span>
                    <span className="font-bold text-red-600">{c.risk_level}</span>
                  </div>
                  <div className="flex justify-between text-slate-600">
                    <span>AI Recommended Action:</span>
                    <span className="font-mono text-slate-900 font-bold bg-slate-100 px-2 py-0.5 rounded">{c.recommended_action}</span>
                  </div>
                  <div className="flex justify-between text-slate-600">
                    <span>Recoverability / Expected:</span>
                    <span className="text-emerald-700 font-semibold">
                      {(c.recoverability_score || 0).toFixed(0)}% (₹{c.expected_recovery?.toLocaleString("en-IN")})
                    </span>
                  </div>
                  <div className="p-2.5 rounded-lg bg-amber-50/60 border border-amber-200 text-[11px] text-amber-900">
                    <span className="font-bold">Policy Trigger: </span>
                    {c.amount > 25000
                      ? `Transaction value exceeds automated limit of ₹25,000.`
                      : `Risk scoring flags transaction for manual review.`}
                  </div>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="flex items-center space-x-2 pt-3 border-t border-slate-100">
                <button
                  onClick={() => onApprove(c.id)}
                  className="flex-1 flex items-center justify-center space-x-1.5 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-semibold transition shadow-sm"
                >
                  <Check className="w-3.5 h-3.5" />
                  <span>APPROVE</span>
                </button>
                <button
                  onClick={() => onReject(c.id)}
                  className="flex-1 flex items-center justify-center space-x-1.5 py-2 rounded-lg bg-red-50 hover:bg-red-100 text-red-700 border border-red-200 text-xs font-semibold transition"
                >
                  <X className="w-3.5 h-3.5" />
                  <span>REJECT</span>
                </button>
                <button
                  onClick={() => onSelectCase(c.id)}
                  className="p-2 rounded-lg bg-slate-50 hover:bg-slate-100 text-slate-500 hover:text-slate-800 border border-slate-200 transition"
                  title="Inspect Full Timeline"
                >
                  <ArrowUpRight className="w-4 h-4" />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
