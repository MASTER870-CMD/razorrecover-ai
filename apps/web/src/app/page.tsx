"use client";

import React, { useEffect, useState } from "react";
import { Header } from "../components/Header";
import { Sidebar } from "../components/Sidebar";
import { MetricsCards } from "../components/MetricsCards";
import { ChartsSection } from "../components/Charts";
import { RecoveryQueue } from "../components/RecoveryQueue";
import { HumanApprovalQueue } from "../components/HumanApprovalQueue";
import { CaseDetailModal } from "../components/CaseDetailModal";
import { DemoModal } from "../components/DemoModal";
import { EvaluationDashboard } from "../components/EvaluationDashboard";
import { AgentFeed } from "../components/AgentFeed";
import { CustomersView } from "../components/CustomersView";
import { PaymentsView } from "../components/PaymentsView";
import { AuditView } from "../components/AuditView";
import { SettingsView } from "../components/SettingsView";
import { RazorpayConnectionView } from "../components/RazorpayConnectionView";
import { ErrorBoundary } from "../components/ErrorBoundary";
import { api } from "../lib/api";
import { Zap, AlertTriangle, ShieldCheck } from "lucide-react";

export default function DashboardPage() {
  const [activeTab, setActiveTab] = useState<string>("overview");
  const [dashboardData, setDashboardData] = useState<any>(null);
  const [cases, setCases] = useState<any[]>([]);
  const [selectedCaseDetail, setSelectedCaseDetail] = useState<any>(null);
  const [isDemoOpen, setIsDemoOpen] = useState<boolean>(false);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [paymentMode, setPaymentMode] = useState<string>("SIMULATOR MODE");

  const loadData = async () => {
    setIsLoading(true);
    try {
      const [summary, caseList, health] = await Promise.all([
        api.getDashboard().catch(() => null),
        api.getCases().catch(() => []),
        api.getHealth().catch(() => null),
      ]);

      if (summary) setDashboardData(summary);
      if (caseList) setCases(caseList);
      if (health?.payment_mode) setPaymentMode(health.payment_mode);
    } catch (err) {
      console.error("Failed to load dashboard data:", err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadData();
    // Background polling for dynamic updates
    const timer = setInterval(loadData, 10000);
    return () => clearInterval(timer);
  }, []);

  const handleSelectCase = async (caseId: string) => {
    try {
      const detail = await api.getCaseDetail(caseId);
      setSelectedCaseDetail(detail);
    } catch (err) {
      console.error("Failed to fetch case detail:", err);
    }
  };

  const handleAnalyzeCase = async (caseId: string) => {
    try {
      await api.analyzeCase(caseId);
      await loadData();
      if (selectedCaseDetail?.case?.id === caseId) {
        handleSelectCase(caseId);
      }
    } catch (err) {
      console.error("Analysis failed:", err);
    }
  };

  const handleApproveCase = async (caseId: string) => {
    try {
      await api.approveCase(caseId);
      await loadData();
      if (selectedCaseDetail?.case?.id === caseId) {
        handleSelectCase(caseId);
      }
    } catch (err) {
      console.error("Approval failed:", err);
    }
  };

  const handleRejectCase = async (caseId: string) => {
    try {
      await api.rejectCase(caseId);
      await loadData();
      if (selectedCaseDetail?.case?.id === caseId) {
        handleSelectCase(caseId);
      }
    } catch (err) {
      console.error("Rejection failed:", err);
    }
  };

  const handleExecuteCase = async (caseId: string) => {
    try {
      await api.executeCase(caseId);
      await loadData();
      if (selectedCaseDetail?.case?.id === caseId) {
        handleSelectCase(caseId);
      }
    } catch (err) {
      console.error("Execution failed:", err);
    }
  };

  const handleVerifyCase = async (caseId: string) => {
    try {
      await api.verifyCase(caseId);
      await loadData();
      if (selectedCaseDetail?.case?.id === caseId) {
        handleSelectCase(caseId);
      }
    } catch (err) {
      console.error("Verification failed:", err);
    }
  };

  const handleGenerateCases = async () => {
    try {
      await api.generateCases(50);
      await loadData();
    } catch (err) {
      console.error("Failed to generate cases:", err);
    }
  };

  const pendingApprovalsCount = cases.filter((c) => c.current_state === "PENDING_APPROVAL").length;

  return (
    <div className="min-h-screen bg-[#F8FAFC] text-slate-900 flex flex-col">
      {/* Top Header */}
      <Header
        onRunDemo={() => setIsDemoOpen(true)}
        onRunEvaluation={() => setActiveTab("evaluations")}
        onGenerateCases={handleGenerateCases}
        paymentMode={paymentMode}
        dataSource={dashboardData?.data_source}
        lastSyncAt={dashboardData?.last_sync_at}
        activeTab={activeTab}
      />

      {/* Main Workspace Layout */}
      <div className="flex flex-1">
        {/* Navigation Sidebar */}
        <Sidebar
          activeTab={activeTab}
          setActiveTab={setActiveTab}
          pendingApprovalsCount={pendingApprovalsCount}
        />

        {/* Dynamic Tab Content Area */}
        <main className="flex-1 p-8 overflow-y-auto max-w-7xl mx-auto w-full">
          {/* 1-Click Controlled Demo Notification Banner on Overview */}
          {activeTab === "overview" && (
            <div className="mb-6 p-4 rounded-xl bg-white border border-slate-200 shadow-sm flex flex-col sm:flex-row sm:items-center justify-between gap-4">
              <div className="flex items-center space-x-3">
                <div className="p-2.5 rounded-lg bg-red-50 text-brand-600 border border-red-200">
                  <Zap className="w-5 h-5 fill-brand-600" />
                </div>
                <div>
                  <h2 className="text-sm font-bold text-slate-900 flex items-center gap-2">
                    Experience RazorRecover AI in Action
                    <span className="text-[10px] px-2 py-0.5 rounded font-bold bg-slate-100 text-slate-700 border border-slate-200">
                      CONTROLLED DEMONSTRATION
                    </span>
                  </h2>
                  <p className="text-xs text-slate-500 mt-0.5">
                    Trigger the complete end-to-end recovery of Acme Media's ₹4,999 failed subscription in under 2 minutes.
                  </p>
                </div>
              </div>
              <button
                onClick={() => setIsDemoOpen(true)}
                className="px-4 py-2 rounded-lg bg-brand-600 hover:bg-brand-700 text-white text-xs font-semibold shadow-sm transition shrink-0"
              >
                Launch Controlled Demo
              </button>
            </div>
          )}

          {/* Overview Tab Content */}
          {activeTab === "overview" && dashboardData && (
            <>
              <MetricsCards metrics={dashboardData} />
              <ChartsSection
                riskOverTime={dashboardData.revenue_at_risk_over_time || []}
                recoveredOverTime={dashboardData.revenue_recovered_over_time || []}
                failureBreakdown={dashboardData.failure_reason_breakdown || []}
                actionBreakdown={dashboardData.recovery_action_breakdown || []}
              />
              <RecoveryQueue
                cases={cases}
                onSelectCase={handleSelectCase}
                onAnalyzeCase={handleAnalyzeCase}
                onApproveCase={handleApproveCase}
                onExecuteCase={handleExecuteCase}
              />
            </>
          )}

          {/* Revenue Risk Radar Tab */}
          {activeTab === "risk" && (
            <div className="space-y-6">
              <div className="p-4 rounded-xl bg-white border border-slate-200 shadow-sm">
                <h2 className="text-base font-bold text-slate-900 flex items-center gap-2">
                  <AlertTriangle className="w-4 h-4 text-red-600" />
                  <span>Revenue Risk Radar</span>
                </h2>
                <p className="text-xs text-slate-500 mt-0.5">
                  Real-time transaction risk scoring and recovery decay curves.
                </p>
              </div>
              <RecoveryQueue
                cases={cases}
                onSelectCase={handleSelectCase}
                onAnalyzeCase={handleAnalyzeCase}
                onApproveCase={handleApproveCase}
                onExecuteCase={handleExecuteCase}
              />
            </div>
          )}

          {/* Recovery Queue Tab */}
          {activeTab === "queue" && (
            <div className="space-y-6">
              <div className="p-4 rounded-xl bg-white border border-slate-200 shadow-sm">
                <h2 className="text-base font-bold text-slate-900">Recovery Queue</h2>
                <p className="text-xs text-slate-500 mt-0.5">
                  All active, pending, executed, and blocked revenue recovery incidents.
                </p>
              </div>
              <RecoveryQueue
                cases={cases}
                onSelectCase={handleSelectCase}
                onAnalyzeCase={handleAnalyzeCase}
                onApproveCase={handleApproveCase}
                onExecuteCase={handleExecuteCase}
              />
            </div>
          )}

          {/* Human Approvals Tab */}
          {activeTab === "approvals" && (
            <HumanApprovalQueue
              cases={cases}
              onApprove={handleApproveCase}
              onReject={handleRejectCase}
              onSelectCase={handleSelectCase}
            />
          )}

          {/* AI Agent Live Feed */}
          {activeTab === "agent" && <AgentFeed />}

          {/* 500-Case Evaluation Benchmark */}
          {activeTab === "evaluations" && <EvaluationDashboard />}

          {/* Payments View */}
          {activeTab === "payments" && <PaymentsView />}

          {/* Customers View */}
          {activeTab === "customers" && <CustomersView />}

          {/* Audit Logs */}
          {activeTab === "audit" && <AuditView />}

          {/* Policy Guardrails */}
          {activeTab === "policy" && <SettingsView />}

          {/* Razorpay Connection */}
          {activeTab === "connection" && <RazorpayConnectionView />}

          {/* Settings */}
          {activeTab === "settings" && <SettingsView />}
        </main>
      </div>

      {/* Case Detail Interactive Modal */}
      {selectedCaseDetail && (
        <ErrorBoundary
          fallbackTitle="Unable to display case details"
          fallbackMessage="An unexpected issue occurred while rendering this case. You can close this and continue navigating."
        >
          <CaseDetailModal
            caseData={selectedCaseDetail}
            onClose={() => setSelectedCaseDetail(null)}
            onAnalyze={handleAnalyzeCase}
            onApprove={handleApproveCase}
            onReject={handleRejectCase}
            onExecute={handleExecuteCase}
            onVerify={handleVerifyCase}
          />
        </ErrorBoundary>
      )}

      {/* 1-Click Interactive Demo Modal */}
      <DemoModal
        isOpen={isDemoOpen}
        onClose={() => setIsDemoOpen(false)}
        onFinished={loadData}
      />
    </div>
  );
}
