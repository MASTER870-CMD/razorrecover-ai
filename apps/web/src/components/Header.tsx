"use client";

import React from "react";
import { Sparkles, ShieldCheck, Database, Zap, RefreshCw, CheckCircle2 } from "lucide-react";

interface HeaderProps {
  onRunDemo: () => void;
  onRunEvaluation: () => void;
  onGenerateCases: () => void;
  isDemoRunning?: boolean;
  isEvaluating?: boolean;
  paymentMode?: string;
  dataSource?: string;
  lastSyncAt?: string | null;
  activeTab: string;
}

export const Header: React.FC<HeaderProps> = ({
  onRunDemo,
  onRunEvaluation,
  onGenerateCases,
  isDemoRunning = false,
  isEvaluating = false,
  paymentMode = "SIMULATOR MODE",
  dataSource = "LOCAL_SIMULATION",
  lastSyncAt,
}) => {
  const isRazorpayTestMode = dataSource === "RAZORPAY_TEST_MODE" || paymentMode.includes("RAZORPAY");

  return (
    <header className="border-b border-border bg-white sticky top-0 z-30 px-6 py-3 shadow-sm">
      <div className="flex items-center justify-between">
        {/* Brand & Subtitle */}
        <div className="flex items-center space-x-4">
          <div className="w-10 h-10 rounded-lg bg-brand-600 flex items-center justify-center shadow-sm text-white">
            <ShieldCheck className="w-6 h-6 text-white" />
          </div>
          <div>
            <div className="flex items-center space-x-2.5 flex-wrap">
              <span className="text-lg font-bold tracking-tight text-slate-900">
                RazorRecover <span className="text-brand-600">AI</span>
              </span>
              
              <span className="text-[11px] font-semibold uppercase tracking-wider px-2 py-0.5 rounded bg-slate-100 text-slate-700 border border-slate-200">
                AI REVENUE RECOVERY
              </span>

              {/* Data Source Indicator */}
              {isRazorpayTestMode ? (
                <span className="text-xs px-2.5 py-0.5 rounded-full font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200 flex items-center gap-1.5 shadow-sm">
                  <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
                  RAZORPAY TEST MODE
                </span>
              ) : (
                <span className="text-xs px-2.5 py-0.5 rounded-full font-semibold bg-amber-50 text-amber-700 border border-amber-200 flex items-center gap-1.5 shadow-sm">
                  <span className="w-2 h-2 rounded-full bg-amber-500" />
                  LOCAL SIMULATION
                </span>
              )}

              {lastSyncAt && (
                <span className="text-[11px] text-slate-400 flex items-center gap-1">
                  <RefreshCw className="w-2.5 h-2.5" />
                  Synced: {new Date(lastSyncAt).toLocaleTimeString()}
                </span>
              )}
            </div>
            <p className="text-xs text-slate-500 mt-0.5">
              Autonomous Revenue Recovery Infrastructure • <span className="text-slate-700 font-medium italic">"Find revenue at risk. Recover it safely."</span>
            </p>
          </div>
        </div>

        {/* Global Action Bar */}
        <div className="flex items-center space-x-3">
          {/* Quick Seed Generator */}
          <button
            onClick={onGenerateCases}
            className="flex items-center space-x-1.5 text-xs font-medium px-3 py-2 rounded-lg bg-white border border-slate-200 hover:bg-slate-50 text-slate-700 hover:text-slate-900 transition shadow-sm"
            title="Generate synthetic payment failure cases for testing"
          >
            <Database className="w-3.5 h-3.5 text-slate-500" />
            <span>Generate 50 Cases</span>
          </button>

          {/* 500-Case Evaluation Benchmark */}
          <button
            onClick={onRunEvaluation}
            disabled={isEvaluating}
            className="flex items-center space-x-1.5 text-xs font-semibold px-3.5 py-2 rounded-lg bg-white border border-slate-300 hover:border-slate-400 text-slate-800 hover:bg-slate-50 transition disabled:opacity-50 shadow-sm"
          >
            <Sparkles className={`w-3.5 h-3.5 text-brand-600 ${isEvaluating ? "animate-spin" : ""}`} />
            <span>{isEvaluating ? "Evaluating 500 Cases..." : "Run Synthetic Evaluation"}</span>
          </button>

          {/* 1-Click Interactive Demo Button */}
          <button
            onClick={onRunDemo}
            disabled={isDemoRunning}
            className="flex items-center space-x-2 text-xs font-semibold px-4 py-2 rounded-lg bg-brand-600 hover:bg-brand-700 text-white shadow-sm border border-brand-700 transition disabled:opacity-50"
          >
            <Zap className={`w-4 h-4 ${isDemoRunning ? "animate-spin" : "fill-white"}`} />
            <span>{isDemoRunning ? "Running Demo..." : "CONTROLLED DEMO"}</span>
          </button>
        </div>
      </div>
    </header>
  );
};
