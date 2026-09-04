import React, { useState, useEffect } from "react";
import { Plug, RefreshCw, CheckCircle2, AlertCircle, ShieldCheck, KeyRound, ExternalLink, ArrowRight } from "lucide-react";
import { api } from "../lib/api";

export const RazorpayConnectionView: React.FC = () => {
  const [connectionStatus, setConnectionStatus] = useState<any>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [isTesting, setIsTesting] = useState<boolean>(false);
  const [isSyncingPayments, setIsSyncingPayments] = useState<boolean>(false);
  const [isSyncingLinks, setIsSyncingLinks] = useState<boolean>(false);
  const [actionMessage, setActionMessage] = useState<{ type: "success" | "error"; text: string } | null>(null);

  const loadStatus = async () => {
    setIsLoading(true);
    try {
      const status = await api.getRazorpayConnection();
      setConnectionStatus(status);
    } catch (err: any) {
      console.error("Failed to load connection status:", err);
      setActionMessage({ type: "error", text: err.message || "Failed to load connection status" });
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadStatus();
  }, []);

  const handleTestConnection = async () => {
    setIsTesting(true);
    setActionMessage(null);
    try {
      const res = await api.testRazorpayConnection();
      if (res.connected) {
        setActionMessage({ type: "success", text: `Connection successful! Mode: ${res.mode}` });
      } else {
        setActionMessage({ type: "error", text: res.error || "Connection test failed. Check your API credentials." });
      }
      await loadStatus();
    } catch (err: any) {
      setActionMessage({ type: "error", text: err.message || "Test connection failed" });
    } finally {
      setIsTesting(false);
    }
  };

  const handleSyncPayments = async () => {
    setIsSyncingPayments(true);
    setActionMessage(null);
    try {
      const res = await api.syncRazorpayPayments();
      setActionMessage({
        type: "success",
        text: `Synchronized ${res.synced_count} payment records from ${res.mode}.`,
      });
      await loadStatus();
    } catch (err: any) {
      setActionMessage({ type: "error", text: err.message || "Payment sync failed" });
    } finally {
      setIsSyncingPayments(false);
    }
  };

  const handleSyncPaymentLinks = async () => {
    setIsSyncingLinks(true);
    setActionMessage(null);
    try {
      const res = await api.syncRazorpayPaymentLinks();
      setActionMessage({
        type: "success",
        text: `Synchronized ${res.synced_count} payment links.`,
      });
      await loadStatus();
    } catch (err: any) {
      setActionMessage({ type: "error", text: err.message || "Payment links sync failed" });
    } finally {
      setIsSyncingLinks(false);
    }
  };

  const isConnected = connectionStatus?.is_connected;

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      {/* Header Banner */}
      <div className="p-5 rounded-xl bg-white border border-slate-200 shadow-sm flex items-start justify-between">
        <div className="flex items-start space-x-3.5">
          <div className="w-10 h-10 rounded-lg bg-red-50 border border-red-200 flex items-center justify-center text-brand-600 mt-0.5">
            <Plug className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h2 className="text-base font-bold text-slate-900">Razorpay Connection & Integration</h2>
              <span
                className={`text-xs px-2.5 py-0.5 rounded-full font-bold flex items-center gap-1.5 ${
                  isConnected
                    ? "bg-emerald-50 text-emerald-700 border border-emerald-200"
                    : "bg-amber-50 text-amber-800 border border-amber-200"
                }`}
              >
                <span className={`w-2 h-2 rounded-full ${isConnected ? "bg-emerald-500 animate-pulse" : "bg-amber-500"}`} />
                {isConnected ? "CONNECTED" : "NOT CONNECTED (SIMULATOR FALLBACK)"}
              </span>
            </div>
            <p className="text-xs text-slate-500 mt-1 leading-relaxed">
              Connect Razorpay Test Mode credentials to ingest real test transactions, emit webhooks, and issue live Test Payment Links.
            </p>
          </div>
        </div>
      </div>

      {actionMessage && (
        <div
          className={`p-4 rounded-xl border text-xs flex items-center space-x-2.5 shadow-sm ${
            actionMessage.type === "success"
              ? "bg-emerald-50 border-emerald-200 text-emerald-800"
              : "bg-red-50 border-red-200 text-red-800"
          }`}
        >
          {actionMessage.type === "success" ? (
            <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
          ) : (
            <AlertCircle className="w-4 h-4 text-red-600 shrink-0" />
          )}
          <span>{actionMessage.text}</span>
        </div>
      )}

      {/* Connection Card */}
      <div className="p-6 rounded-xl bg-white border border-slate-200 shadow-sm space-y-5">
        <h3 className="text-xs font-bold text-slate-900 uppercase tracking-wider flex items-center gap-2">
          <KeyRound className="w-4 h-4 text-brand-600" />
          <span>API Credentials & Status</span>
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
          <div className="p-4 rounded-lg bg-slate-50 border border-slate-200 space-y-1">
            <span className="text-slate-500 block font-medium">Key ID</span>
            <div className="font-mono text-sm font-bold text-slate-900">
              {connectionStatus?.key_id_masked || "rzp_test_••••••••"}
            </div>
            <p className="text-[10px] text-slate-400">Configured via backend environment variable `RAZORPAY_KEY_ID`.</p>
          </div>

          <div className="p-4 rounded-lg bg-slate-50 border border-slate-200 space-y-1">
            <span className="text-slate-500 block font-medium">Key Secret</span>
            <div className="font-mono text-sm font-bold text-slate-900">
              •••••••••••••••••••••••• (Secured)
            </div>
            <p className="text-[10px] text-slate-400">Never exposed to browser. Kept in backend runtime only.</p>
          </div>

          <div className="p-4 rounded-lg bg-slate-50 border border-slate-200 space-y-1">
            <span className="text-slate-500 block font-medium">Last Successful Sync</span>
            <div className="text-xs font-bold text-slate-900">
              {connectionStatus?.last_sync_at ? new Date(connectionStatus.last_sync_at).toLocaleString() : "Never synced"}
            </div>
            <p className="text-[10px] text-slate-400">Timestamp of latest API pull.</p>
          </div>

          <div className="p-4 rounded-lg bg-slate-50 border border-slate-200 space-y-1">
            <span className="text-slate-500 block font-medium">Last Error</span>
            <div className={`text-xs font-semibold ${connectionStatus?.last_error ? "text-red-600" : "text-slate-500"}`}>
              {connectionStatus?.last_error || "None"}
            </div>
            <p className="text-[10px] text-slate-400">Gateway communication status.</p>
          </div>
        </div>

        {/* Action Controls */}
        <div className="flex items-center space-x-3 pt-4 border-t border-slate-200 flex-wrap gap-y-2">
          <button
            onClick={handleTestConnection}
            disabled={isTesting}
            className="flex items-center space-x-2 px-4 py-2 rounded-lg bg-brand-600 hover:bg-brand-700 text-white text-xs font-semibold shadow-sm transition disabled:opacity-50"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isTesting ? "animate-spin" : ""}`} />
            <span>{isTesting ? "Testing..." : "TEST CONNECTION"}</span>
          </button>

          <button
            onClick={handleSyncPayments}
            disabled={isSyncingPayments}
            className="flex items-center space-x-2 px-4 py-2 rounded-lg bg-white border border-slate-300 hover:bg-slate-50 text-slate-800 text-xs font-semibold shadow-sm transition disabled:opacity-50"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isSyncingPayments ? "animate-spin" : ""}`} />
            <span>{isSyncingPayments ? "Syncing..." : "SYNC PAYMENTS"}</span>
          </button>

          <button
            onClick={handleSyncPaymentLinks}
            disabled={isSyncingLinks}
            className="flex items-center space-x-2 px-4 py-2 rounded-lg bg-white border border-slate-300 hover:bg-slate-50 text-slate-800 text-xs font-semibold shadow-sm transition disabled:opacity-50"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isSyncingLinks ? "animate-spin" : ""}`} />
            <span>{isSyncingLinks ? "Syncing..." : "SYNC PAYMENT LINKS"}</span>
          </button>
        </div>
      </div>

      {/* Webhook Configuration Guide */}
      <div className="p-6 rounded-xl bg-white border border-slate-200 shadow-sm space-y-4">
        <h3 className="text-xs font-bold text-slate-900 uppercase tracking-wider flex items-center gap-2">
          <ShieldCheck className="w-4 h-4 text-emerald-700" />
          <span>Webhook Ingestion & Idempotency</span>
        </h3>
        <p className="text-xs text-slate-600 leading-relaxed">
          RazorRecover AI verifies webhook signatures using HMAC-SHA256 with the raw request body and guarantees idempotency by recording unique Razorpay event IDs. Duplicate event deliveries will not trigger double recovery actions.
        </p>
        <div className="p-3.5 rounded-lg bg-slate-50 border border-slate-200 font-mono text-xs text-slate-800 flex items-center justify-between">
          <span>POST /api/webhooks/razorpay</span>
          <span className="text-[10px] font-semibold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200">
            SIGNATURE & IDEMPOTENCY ENFORCED
          </span>
        </div>
      </div>
    </div>
  );
};
