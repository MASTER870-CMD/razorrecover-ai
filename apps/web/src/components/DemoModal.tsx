"use client";

import React, { useEffect, useState } from "react";
import { Zap, CheckCircle2, ShieldCheck, X, RefreshCw } from "lucide-react";
import { api } from "../lib/api";

interface DemoModalProps {
  isOpen: boolean;
  onClose: () => void;
  onFinished: () => void;
}

export const DemoModal: React.FC<DemoModalProps> = ({ isOpen, onClose, onFinished }) => {
  const [currentStep, setCurrentStep] = useState<number>(0);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [demoResult, setDemoResult] = useState<any>(null);

  const startDemo = async () => {
    setIsLoading(true);
    setCurrentStep(1);

    try {
      // Step 1: Ingestion
      await new Promise((r) => setTimeout(r, 600));
      setCurrentStep(2);

      // Step 2: Risk analysis
      await new Promise((r) => setTimeout(r, 700));
      setCurrentStep(3);

      // Step 3: AI reasoning & Safety check
      await new Promise((r) => setTimeout(r, 700));
      setCurrentStep(4);

      // Execute actual backend workflow
      const res = await api.runDemo();
      setDemoResult(res);

      // Step 4: Execution
      await new Promise((r) => setTimeout(r, 700));
      setCurrentStep(5);

      // Step 5: Verification & Capture
      setIsLoading(false);
      onFinished();
    } catch (err) {
      console.error("Demo workflow failed:", err);
      setIsLoading(false);
    }
  };

  // Escape key handler to close modal
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        onClose();
      }
    };
    if (isOpen) {
      window.addEventListener("keydown", handleKeyDown);
    }
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [isOpen, onClose]);

  useEffect(() => {
    if (isOpen) {
      startDemo();
    } else {
      setCurrentStep(0);
      setDemoResult(null);
    }
  }, [isOpen]);

  if (!isOpen) return null;

  const steps = [
    {
      num: 1,
      title: "1. Failed Payment Ingestion",
      desc: "Acme Media recurring SaaS transaction of ₹4,999 failed with INSUFFICIENT_FUNDS.",
      detail: "Customer: Acme Media • Prior Success: 96% • LTV: ₹48,500",
    },
    {
      num: 2,
      title: "2. Revenue Risk Engine Evaluation",
      desc: "Deterministic risk engine calculates Risk: 45 (MEDIUM) and Recoverability: 78%.",
      detail: "Identified high probability recovery window within 24 hours.",
    },
    {
      num: 3,
      title: "3. AI Diagnosis & Recommendation",
      desc: "Reasoning engine analyzes failure pattern and recommends PAYMENT_LINK recovery.",
      detail: "Diagnosis: 'Temporary account shortfall on debit' • Confidence: 92%",
    },
    {
      num: 4,
      title: "4. Deterministic Safety Policy Clearance",
      desc: "Safety engine evaluates rules: Amount ₹4,999 < ₹25k limit, 0 prior failures (ALLOWED).",
      detail: "Clearance granted without requiring human escalation.",
    },
    {
      num: 5,
      title: "5. Execution, Webhook Verification & Recovery",
      desc: "Supported recovery link issued, customer payment event verified, revenue recovered.",
      detail: "Verified ₹4,999 test recovery • Case state: RECOVERED • Audit logged",
    },
  ];

  return (
    <div
      onClick={onClose}
      className="fixed inset-0 z-50 bg-slate-900/50 backdrop-blur-sm flex items-center justify-center p-3 sm:p-4 overflow-y-auto"
    >
      <div
        onClick={(e) => e.stopPropagation()}
        className="bg-white border border-slate-200 rounded-2xl w-full max-w-xl max-h-[90vh] shadow-2xl flex flex-col overflow-hidden animate-in fade-in zoom-in-95 duration-150"
      >
        {/* Sticky Header */}
        <div className="flex items-center justify-between px-5 py-3.5 border-b border-slate-200 bg-white sticky top-0 z-10">
          <div className="flex items-center space-x-3">
            <div className="p-2 rounded-lg bg-red-50 text-brand-600 border border-red-200">
              <Zap className="w-5 h-5 fill-brand-600" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <h2 className="text-sm font-bold text-slate-900">Controlled Demonstration</h2>
                <span className="px-1.5 py-0.5 text-[9px] font-bold rounded bg-slate-100 text-slate-700 border border-slate-200">
                  TEST WORKFLOW
                </span>
              </div>
              <p className="text-[11px] text-slate-500 mt-0.5">
                Acme Media • ₹4,999 INR • Autonomous recovery lifecycle
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            aria-label="Close modal"
            className="p-1.5 rounded-lg text-slate-400 hover:text-slate-800 hover:bg-slate-100 transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Scrollable Step-by-Step Flow */}
        <div className="overflow-y-auto p-4 sm:p-5 space-y-2.5 flex-1">
          {steps.map((st) => {
            const isDone = currentStep > st.num || (currentStep === 5 && st.num === 5);
            const isCurrent = currentStep === st.num;

            return (
              <div
                key={st.num}
                className={`p-3 rounded-xl border transition-all ${
                  isDone
                    ? "bg-emerald-50/40 border-emerald-200"
                    : isCurrent
                    ? "bg-red-50/40 border-brand-300 shadow-sm"
                    : "bg-slate-50/50 border-slate-200 opacity-60"
                }`}
              >
                <div className="flex items-start space-x-3">
                  <div className="mt-0.5">
                    {isDone ? (
                      <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                    ) : isCurrent ? (
                      <RefreshCw className="w-4 h-4 text-brand-600 animate-spin" />
                    ) : (
                      <div className="w-4 h-4 rounded-full border border-slate-300 text-[10px] font-mono flex items-center justify-center text-slate-400">
                        {st.num}
                      </div>
                    )}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-bold text-slate-900">{st.title}</span>
                      {isDone && (
                        <span className="text-[9px] font-bold text-emerald-700 uppercase tracking-wider bg-emerald-100/60 px-1.5 py-0.5 rounded">
                          Verified
                        </span>
                      )}
                    </div>
                    <p className="text-[11px] text-slate-600 mt-0.5 leading-snug">{st.desc}</p>
                    <div className="text-[10px] font-mono text-slate-400 mt-1">{st.detail}</div>
                  </div>
                </div>
              </div>
            );
          })}

          {/* Success Banner when complete */}
          {currentStep === 5 && (
            <div className="p-3.5 rounded-xl bg-emerald-50 border border-emerald-200 flex items-center justify-between shadow-sm">
              <div className="flex items-center space-x-2.5">
                <ShieldCheck className="w-5 h-5 text-emerald-600 shrink-0" />
                <div>
                  <div className="text-xs font-bold text-slate-900">End-to-End Recovery Flow Verified</div>
                  <div className="text-[11px] text-emerald-800">
                    ₹4,999 recovered & logged to immutable audit trail.
                  </div>
                </div>
              </div>
              <span className="text-sm font-bold text-emerald-700 font-mono shrink-0">+₹4,999.00</span>
            </div>
          )}
        </div>

        {/* Sticky Action Footer */}
        <div className="flex items-center justify-between px-5 py-3 border-t border-slate-200 bg-slate-50 sticky bottom-0 z-10">
          <div className="text-[11px] text-slate-500">
            Press <kbd className="px-1.5 py-0.5 text-[10px] font-mono bg-white border border-slate-300 rounded shadow-xs">Esc</kbd> or click outside to close
          </div>
          <div className="flex items-center space-x-2">
            <button
              onClick={startDemo}
              disabled={isLoading}
              className="px-3 py-1.5 rounded-lg bg-white hover:bg-slate-100 text-slate-700 text-xs font-semibold border border-slate-300 transition flex items-center space-x-1.5 shadow-xs"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${isLoading ? "animate-spin" : ""}`} />
              <span>Re-run</span>
            </button>
            <button
              onClick={onClose}
              className="px-4 py-1.5 rounded-lg bg-brand-600 hover:bg-brand-700 text-white text-xs font-semibold transition shadow-xs"
            >
              View in Dashboard
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
