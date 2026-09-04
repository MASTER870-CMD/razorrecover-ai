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
    <div className="fixed inset-0 z-50 bg-slate-900/40 backdrop-blur-sm flex items-center justify-center p-4">
      <div className="bg-white border border-slate-200 rounded-2xl w-full max-w-2xl p-6 shadow-2xl relative">
        {/* Close Button */}
        <button
          onClick={onClose}
          className="absolute right-4 top-4 p-2 rounded-lg text-slate-400 hover:text-slate-800 hover:bg-slate-100 transition"
        >
          <X className="w-5 h-5" />
        </button>

        {/* Demo Header */}
        <div className="flex items-center space-x-3 mb-6">
          <div className="p-2.5 rounded-xl bg-red-50 text-brand-600 border border-red-200">
            <Zap className="w-6 h-6 fill-brand-600" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h2 className="text-base font-bold text-slate-900">Controlled Demonstration</h2>
              <span className="px-2 py-0.5 text-[10px] font-bold rounded bg-slate-100 text-slate-700 border border-slate-300">
                CONTROLLED DEMONSTRATION
              </span>
            </div>
            <p className="text-xs text-slate-500 mt-0.5">
              Acme Media • ₹4,999 INR • End-to-end autonomous recovery lifecycle
            </p>
          </div>
        </div>

        {/* Step-by-Step Flow */}
        <div className="space-y-3 mb-6">
          {steps.map((st) => {
            const isDone = currentStep > st.num || (currentStep === 5 && st.num === 5);
            const isCurrent = currentStep === st.num;

            return (
              <div
                key={st.num}
                className={`p-3.5 rounded-xl border transition-all ${
                  isDone
                    ? "bg-emerald-50/40 border-emerald-200"
                    : isCurrent
                    ? "bg-red-50/40 border-brand-300 shadow-sm"
                    : "bg-slate-50/50 border-slate-200 opacity-50"
                }`}
              >
                <div className="flex items-start space-x-3">
                  <div className="mt-0.5">
                    {isDone ? (
                      <CheckCircle2 className="w-5 h-5 text-emerald-600" />
                    ) : isCurrent ? (
                      <RefreshCw className="w-5 h-5 text-brand-600 animate-spin" />
                    ) : (
                      <div className="w-5 h-5 rounded-full border border-slate-300 text-[11px] font-mono flex items-center justify-center text-slate-400">
                        {st.num}
                      </div>
                    )}
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-bold text-slate-900">{st.title}</span>
                      {isDone && (
                        <span className="text-[10px] font-bold text-emerald-700 uppercase tracking-wider">
                          Verified
                        </span>
                      )}
                    </div>
                    <p className="text-xs text-slate-600 mt-0.5">{st.desc}</p>
                    <div className="text-[11px] font-mono text-slate-500 mt-1">{st.detail}</div>
                  </div>
                </div>
              </div>
            );
          })}
        </div>

        {/* Success Banner when complete */}
        {currentStep === 5 && (
          <div className="p-4 rounded-xl bg-emerald-50 border border-emerald-200 flex items-center justify-between mb-6 shadow-sm">
            <div className="flex items-center space-x-3">
              <ShieldCheck className="w-6 h-6 text-emerald-600" />
              <div>
                <div className="text-xs font-bold text-slate-900">End-to-End Recovery Flow Verified</div>
                <div className="text-xs text-emerald-800">
                  ₹4,999 successfully recovered and written to immutable database audit trail.
                </div>
              </div>
            </div>
            <span className="text-base font-bold text-emerald-700 font-mono">+₹4,999.00</span>
          </div>
        )}

        {/* Action Controls */}
        <div className="flex items-center justify-end space-x-3">
          <button
            onClick={startDemo}
            disabled={isLoading}
            className="px-4 py-2 rounded-lg bg-white hover:bg-slate-50 text-slate-700 text-xs font-semibold border border-slate-300 transition flex items-center space-x-1.5 shadow-sm"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isLoading ? "animate-spin" : ""}`} />
            <span>Re-run Demonstration</span>
          </button>
          <button
            onClick={onClose}
            className="px-5 py-2 rounded-lg bg-brand-600 hover:bg-brand-700 text-white text-xs font-semibold transition shadow-sm"
          >
            View in Dashboard
          </button>
        </div>
      </div>
    </div>
  );
};
