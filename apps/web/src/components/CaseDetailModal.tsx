"use client";

import React, { useState } from "react";
import {
  X,
  ShieldCheck,
  Cpu,
  CheckCircle2,
  AlertTriangle,
  History,
  Clock,
  ExternalLink,
  Copy,
  Check,
  Lock,
  Zap,
  Loader2,
} from "lucide-react";

interface CaseDetailModalProps {
  caseData: any;
  analyzingCaseId?: string | null;
  executingCaseId?: string | null;
  verifyingCaseId?: string | null;
  onClose: () => void;
  onAnalyze: (id: string) => void;
  onApprove: (id: string) => void;
  onReject: (id: string) => void;
  onExecute: (id: string) => void;
  onVerify: (id: string) => void;
}

export const CaseDetailModal: React.FC<CaseDetailModalProps> = ({
  caseData,
  analyzingCaseId,
  executingCaseId,
  verifyingCaseId,
  onClose,
  onAnalyze,
  onApprove,
  onReject,
  onExecute,
  onVerify,
}) => {
  const [copied, setCopied] = useState<boolean>(false);

  // Escape key close handler MUST run unconditionally at top level
  React.useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        onClose();
      }
    };
    if (caseData) {
      window.addEventListener("keydown", handleKeyDown);
    }
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [caseData, onClose]);

  if (!caseData) return null;

  const {
    case: c,
    customer,
    payment,
    agent_decisions,
    policy_decisions,
    actions,
    audit_logs,
    payment_link,
  } = caseData;

  const latestAgentDecision = agent_decisions?.[0];
  const latestPolicyDecision = policy_decisions?.[0];
  const executedAction = actions?.find(
    (a: any) => a.status === "EXECUTED" || a.status === "VERIFIED" || a.status === "SUCCESS"
  ) || actions?.[0];

  // Derive Payment Link details from explicit object or action execution
  const activePaymentLink = payment_link || (executedAction?.parameters?.payment_link_url ? {
    short_url: executedAction.parameters.payment_link_url,
    id: executedAction.parameters.payment_link_id,
    mode: executedAction.parameters.mode,
  } : null);

  const handleCopyLink = () => {
    if (activePaymentLink?.short_url) {
      navigator.clipboard.writeText(activePaymentLink.short_url);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const caseReference = c?.id ? `RC-${c.id.slice(0, 8).toUpperCase()}` : "RC-CASE";

  return (
    <div
      onClick={onClose}
      className="fixed inset-0 z-50 bg-slate-900/40 backdrop-blur-sm flex items-center justify-center p-3 sm:p-4 overflow-y-auto"
    >
      <div
        onClick={(e) => e.stopPropagation()}
        className="bg-white border border-slate-200 rounded-2xl w-full max-w-4xl max-h-[90vh] overflow-y-auto shadow-2xl flex flex-col animate-in fade-in zoom-in-95 duration-150"
      >
        {/* Modal Header */}
        <div className="flex items-center justify-between p-6 border-b border-slate-200 sticky top-0 bg-white/95 backdrop-blur z-10">
          <div>
            <div className="flex items-center space-x-3 flex-wrap gap-y-1">
              <h2 className="text-xl font-bold text-slate-900">Recovery Case #{caseReference}</h2>
              <span className="text-xs px-2.5 py-0.5 rounded font-mono bg-slate-100 text-slate-700 border border-slate-200">
                {c?.id?.slice(0, 13)}
              </span>
              <span className="text-xs px-2.5 py-0.5 rounded-full font-bold bg-brand-50 text-brand-700 border border-brand-200">
                {c?.current_state?.replace(/_/g, " ")}
              </span>
            </div>
            <p className="text-xs text-slate-500 mt-1">
              Customer: <span className="text-slate-900 font-semibold">{customer?.name}</span> ({customer?.email}) • 
              Amount: <span className="text-slate-900 font-bold">₹{c?.amount?.toLocaleString("en-IN")} INR</span>
            </p>
          </div>
          <button
            onClick={onClose}
            className="p-2 rounded-lg text-slate-400 hover:text-slate-800 hover:bg-slate-100 transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="p-6 space-y-6">
          {/* Top Quick Status Row */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 p-4 rounded-xl bg-slate-50 border border-slate-200">
            <div>
              <span className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider">Risk Score</span>
              <div className="text-lg font-bold text-slate-900 mt-0.5">
                {c?.risk_score?.toFixed(0)} <span className="text-xs font-bold text-red-600">({c?.risk_level})</span>
              </div>
            </div>
            <div>
              <span className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider">Recoverability</span>
              <div className="text-lg font-bold text-emerald-700 mt-0.5">
                {c?.recoverability_score?.toFixed(0)}%
              </div>
            </div>
            <div>
              <span className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider">Expected Recovery</span>
              <div className="text-lg font-bold text-slate-900 mt-0.5">
                ₹{c?.expected_recovery?.toLocaleString("en-IN")}
              </div>
            </div>
            <div>
              <span className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider">Verified Recovery</span>
              <div className="text-lg font-bold text-emerald-700 mt-0.5">
                ₹{c?.actual_recovery?.toLocaleString("en-IN")}
              </div>
            </div>
          </div>

          {/* 1. WHY IS THIS AT RISK? */}
          <div className="p-5 rounded-xl bg-white border border-slate-200 shadow-sm space-y-2">
            <h3 className="text-xs font-bold text-slate-900 uppercase tracking-wider flex items-center gap-2">
              <AlertTriangle className="w-4 h-4 text-red-600" />
              <span>Why is this at risk?</span>
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-2 text-xs">
              <div className="p-3 rounded-lg bg-slate-50 border border-slate-200">
                <span className="text-slate-500 block mb-1 font-medium">Failure Reason</span>
                <span className="font-bold text-slate-900 capitalize text-sm">
                  {payment?.failure_reason?.replace(/_/g, " ") || c?.failure_reason?.replace(/_/g, " ") || "Insufficient Funds"}
                </span>
                <p className="text-[11px] text-slate-500 mt-1">Gateway error reported during checkout capture attempt.</p>
              </div>
              <div className="p-3 rounded-lg bg-slate-50 border border-slate-200">
                <span className="text-slate-500 block mb-1 font-medium">Customer Payment History</span>
                <span className="font-bold text-slate-900 text-sm">
                  {customer?.successful_payments || 0} Successful / {customer?.total_payments || 0} Total
                </span>
                <p className="text-[11px] text-slate-500 mt-1">
                  Lifetime value ₹{(customer?.total_spent || 0).toLocaleString("en-IN")}.
                </p>
              </div>
              <div className="p-3 rounded-lg bg-slate-50 border border-slate-200">
                <span className="text-slate-500 block mb-1 font-medium">Time Elapsed & Decay</span>
                <span className="font-bold text-slate-900 text-sm">Active Decay Window</span>
                <p className="text-[11px] text-slate-500 mt-1">High probability recovery window is open (0-48 hours).</p>
              </div>
            </div>
          </div>

          {/* 2. AI ANALYSIS & REASONING */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Agent Analysis */}
            <div className="p-5 rounded-xl bg-white border border-slate-200 shadow-sm space-y-3">
              <div className="flex items-center space-x-2 text-xs font-bold text-slate-900 uppercase tracking-wider">
                <Cpu className="w-4 h-4 text-brand-600" />
                <span>AI Reasoning Layer (Gemini / Expert)</span>
              </div>
              {latestAgentDecision ? (
                <div className="space-y-2.5 text-xs">
                  <div>
                    <span className="text-slate-500">Diagnosis: </span>
                    <span className="font-semibold text-slate-900">{latestAgentDecision.diagnosis}</span>
                  </div>
                  <div>
                    <span className="text-slate-500">Confidence Score: </span>
                    <span className="font-bold text-emerald-700">{(latestAgentDecision.confidence * 100).toFixed(0)}%</span>
                  </div>
                  <div className="p-3 rounded-lg bg-slate-50 border border-slate-200 text-slate-700 italic text-[11px] leading-relaxed">
                    "{latestAgentDecision.reasoning_summary}"
                  </div>
                </div>
              ) : (
                <div className="py-4 text-center text-slate-500 text-xs">
                  Click "Analyze with AI Agent" to generate diagnosis.
                </div>
              )}
            </div>

            {/* 3. SAFETY DECISION */}
            <div className="p-5 rounded-xl bg-white border border-slate-200 shadow-sm space-y-3">
              <div className="flex items-center space-x-2 text-xs font-bold text-slate-900 uppercase tracking-wider">
                <Lock className="w-4 h-4 text-emerald-700" />
                <span>Deterministic Safety Decision</span>
              </div>
              {latestPolicyDecision ? (
                <div className="space-y-2.5 text-xs">
                  <div className="flex items-center justify-between">
                    <span className="text-slate-500">Safety Verdict:</span>
                    <span
                      className={`font-bold px-2 py-0.5 rounded text-[11px] ${
                        latestPolicyDecision.decision === "ALLOW"
                          ? "bg-emerald-50 text-emerald-700 border border-emerald-200"
                          : latestPolicyDecision.decision === "REQUIRE_HUMAN_APPROVAL"
                          ? "bg-amber-50 text-amber-800 border border-amber-200"
                          : "bg-red-50 text-red-700 border border-red-200"
                      }`}
                    >
                      {latestPolicyDecision.decision}
                    </span>
                  </div>
                  <div>
                    <span className="text-slate-500">Enforced Guardrail: </span>
                    <span className="font-mono text-slate-900 font-semibold">{latestPolicyDecision.policy_name}</span>
                  </div>
                  <div className="p-3 rounded-lg bg-slate-50 border border-slate-200 text-slate-700 text-[11px] leading-relaxed">
                    {latestPolicyDecision.reason}
                  </div>
                </div>
              ) : (
                <div className="py-4 text-center text-slate-500 text-xs">
                  Safety policy check runs automatically during analysis.
                </div>
              )}
            </div>
          </div>

          {/* 4. EXECUTION — REAL SUPPORTED RECOVERY ACTION (PAYMENT LINK) */}
          <div className="p-5 rounded-xl bg-white border border-slate-200 shadow-sm space-y-3">
            <div className="flex items-center justify-between">
              <h3 className="text-xs font-bold text-slate-900 uppercase tracking-wider flex items-center gap-2">
                <Zap className="w-4 h-4 text-brand-600" />
                <span>Execution: Supported Recovery Action</span>
              </h3>
              <span className="text-[11px] font-bold px-2.5 py-0.5 rounded bg-emerald-50 text-emerald-700 border border-emerald-200">
                RAZORPAY TEST MODE
              </span>
            </div>

            {activePaymentLink ? (
              <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 space-y-3">
                <div className="flex items-center justify-between flex-wrap gap-2">
                  <div>
                    <span className="text-[11px] font-semibold text-slate-500 uppercase">Razorpay Payment Link URL</span>
                    <div className="font-mono text-xs font-bold text-slate-900 break-all select-all">
                      {activePaymentLink.short_url}
                    </div>
                    {activePaymentLink.id && (
                      <span className="text-[10px] text-slate-400 font-mono">
                        Link ID: {activePaymentLink.id}
                      </span>
                    )}
                  </div>
                  <div className="flex items-center space-x-2">
                    <button
                      onClick={handleCopyLink}
                      className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-white border border-slate-300 hover:bg-slate-50 text-slate-700 text-xs font-semibold shadow-sm transition"
                    >
                      {copied ? <Check className="w-3.5 h-3.5 text-emerald-600" /> : <Copy className="w-3.5 h-3.5" />}
                      <span>{copied ? "COPIED" : "COPY PAYMENT LINK"}</span>
                    </button>
                    <a
                      href={activePaymentLink.short_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex items-center space-x-1.5 px-3.5 py-1.5 rounded-lg bg-brand-600 hover:bg-brand-700 text-white text-xs font-semibold shadow-sm transition"
                    >
                      <ExternalLink className="w-3.5 h-3.5" />
                      <span>OPEN PAYMENT LINK</span>
                    </a>
                  </div>
                </div>
                <p className="text-[11px] text-slate-500 leading-relaxed border-t border-slate-200 pt-2">
                  The customer receives this link via SMS/email. You can click <strong>OPEN PAYMENT LINK</strong> to simulate or execute a test checkout. When the test transaction completes, Razorpay webhook or server verification captures the funds.
                </p>
              </div>
            ) : (
              <div className="p-4 rounded-lg bg-slate-50 border border-slate-200 text-xs text-slate-600 flex items-center justify-between">
                <span>Recommended Action: <strong>{c?.recommended_action || "CREATE PAYMENT LINK"}</strong></span>
                {c?.current_state === "APPROVED" && (
                  <button
                    onClick={() => onExecute(c.id)}
                    disabled={executingCaseId === c?.id}
                    className="px-3.5 py-1.5 rounded-lg bg-brand-600 text-white text-xs font-semibold hover:bg-brand-700 transition shadow-sm flex items-center gap-1.5 disabled:opacity-60 disabled:cursor-not-allowed"
                  >
                    {executingCaseId === c?.id ? (
                      <>
                        <Loader2 className="w-3.5 h-3.5 animate-spin" />
                        <span>Creating Link...</span>
                      </>
                    ) : (
                      "Create Payment Link Now"
                    )}
                  </button>
                )}
              </div>
            )}
          </div>

          {/* 5. VERIFICATION & RECOVERY OUTCOME */}
          <div className="p-5 rounded-xl bg-white border border-slate-200 shadow-sm space-y-3">
            <h3 className="text-xs font-bold text-slate-900 uppercase tracking-wider flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-700" />
              <span>Verification & Recovery Result</span>
            </h3>
            {c?.current_state === "RECOVERED" ? (
              <div className="p-4 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-900 flex items-center justify-between">
                <div>
                  <div className="text-base font-bold flex items-center gap-2">
                    <CheckCircle2 className="w-5 h-5 text-emerald-600" />
                    ₹{c?.actual_recovery?.toLocaleString("en-IN")} Captured & Verified
                  </div>
                  <p className="text-xs text-emerald-700 mt-0.5">
                    Customer payment verified via Razorpay Test Mode event. Revenue successfully added to recovered pool.
                  </p>
                </div>
                <span className="text-xs font-bold px-3 py-1 rounded bg-emerald-100 text-emerald-800 border border-emerald-300">
                  VERIFIED
                </span>
              </div>
            ) : (
              <div className="flex items-center justify-between p-3 rounded-lg bg-slate-50 border border-slate-200 text-xs">
                <span className="text-slate-600">
                  Status: <strong className="text-slate-900">{c?.current_state?.replace(/_/g, " ")}</strong>. Verification required before counting as recovered.
                </span>
                {(c?.current_state === "WAITING_FOR_PAYMENT" || c?.current_state === "EXECUTING" || c?.current_state === "APPROVED") && (
                  <button
                    onClick={() => onVerify(c.id)}
                    disabled={verifyingCaseId === c?.id || executingCaseId === c?.id}
                    className="px-3.5 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-semibold transition shadow-sm flex items-center gap-1.5 disabled:opacity-60 disabled:cursor-not-allowed"
                  >
                    {verifyingCaseId === c?.id ? (
                      <>
                        <Loader2 className="w-3.5 h-3.5 animate-spin" />
                        <span>Verifying...</span>
                      </>
                    ) : (
                      "Verify Test Payment"
                    )}
                  </button>
                )}
              </div>
            )}
          </div>

          {/* 6. IMMUTABLE AUDIT LOG TABLE */}
          <div className="p-5 rounded-xl bg-white border border-slate-200 shadow-sm">
            <h3 className="text-xs font-bold text-slate-900 uppercase tracking-wider mb-3 flex items-center gap-2">
              <History className="w-4 h-4 text-slate-600" />
              <span>Audit Trail (Chronological)</span>
            </h3>
            <div className="space-y-2 max-h-44 overflow-y-auto pr-2">
              {audit_logs?.map((l: any) => (
                <div key={l.id} className="p-2.5 rounded-lg bg-slate-50 border border-slate-200 text-xs flex items-center justify-between">
                  <div>
                    <span className="font-mono font-bold text-slate-800">{l.actor}</span>
                    <span className="mx-2 text-slate-400">•</span>
                    <span className="text-slate-700 font-semibold">{l.event_type}</span>
                    <span className="mx-2 text-slate-400">•</span>
                    <span className="text-slate-600">{l.action || l.decision || l.reason}</span>
                  </div>
                  <div className="text-[10px] text-slate-400">
                    {new Date(l.created_at).toLocaleTimeString()}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Bottom Action Bar */}
          <div className="flex items-center justify-end space-x-3 pt-4 border-t border-slate-200">
            {c?.current_state === "AT_RISK" && (
              <button
                onClick={() => onAnalyze(c.id)}
                disabled={analyzingCaseId === c.id}
                className="px-4 py-2 rounded-lg bg-brand-600 hover:bg-brand-700 text-white text-xs font-semibold transition shadow-sm flex items-center gap-2 disabled:opacity-60 disabled:cursor-not-allowed"
              >
                {analyzingCaseId === c.id ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    <span>AI Agent Analyzing...</span>
                  </>
                ) : (
                  "Analyze with AI Agent"
                )}
              </button>
            )}
            {c?.current_state === "PENDING_APPROVAL" && (
              <>
                <button
                  onClick={() => onApprove(c.id)}
                  className="px-4 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-semibold transition shadow-sm"
                >
                  APPROVE
                </button>
                <button
                  onClick={() => onReject(c.id)}
                  className="px-4 py-2 rounded-lg bg-red-50 hover:bg-red-100 text-red-700 border border-red-200 text-xs font-semibold transition"
                >
                  REJECT
                </button>
              </>
            )}
            {c?.current_state === "APPROVED" && (
              <button
                onClick={() => onExecute(c.id)}
                disabled={executingCaseId === c?.id}
                className="px-4 py-2 rounded-lg bg-brand-600 hover:bg-brand-700 text-white text-xs font-semibold transition shadow-sm flex items-center gap-2 disabled:opacity-60 disabled:cursor-not-allowed"
              >
                {executingCaseId === c?.id ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    <span>Creating Link...</span>
                  </>
                ) : (
                  "Create Payment Link"
                )}
              </button>
            )}
            {(c?.current_state === "WAITING_FOR_PAYMENT" || c?.current_state === "EXECUTING") && (
              <button
                onClick={() => onVerify(c.id)}
                disabled={verifyingCaseId === c?.id || executingCaseId === c?.id}
                className="px-4 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-semibold transition shadow-sm flex items-center gap-2 disabled:opacity-60 disabled:cursor-not-allowed"
              >
                {verifyingCaseId === c?.id ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    <span>Verifying...</span>
                  </>
                ) : (
                  "Verify Payment"
                )}
              </button>
            )}
            <button
              onClick={onClose}
              className="px-4 py-2 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-semibold transition border border-slate-200"
            >
              Close
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
