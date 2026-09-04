"use client";

import React, { useEffect, useState } from "react";
import { Sliders, Save, CheckCircle2, ShieldCheck } from "lucide-react";
import { api } from "../lib/api";

export const SettingsView: React.FC = () => {
  const [settings, setSettings] = useState<any>({
    automatic_recovery_enabled: true,
    max_retry_attempts: 3,
    max_automatic_amount: 25000,
    human_approval_threshold: 0.70,
    recovery_window_days: 14,
    max_contact_attempts: 2,
    retry_cooldown_minutes: 60,
  });
  const [saved, setSaved] = useState<boolean>(false);
  const [isSaving, setIsSaving] = useState<boolean>(false);

  useEffect(() => {
    api.getSettings().then(setSettings).catch(console.error);
  }, []);

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSaving(true);
    try {
      await api.updateSettings(settings);
      setSaved(true);
      setTimeout(() => setSaved(false), 3000);
    } catch (err) {
      console.error(err);
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="max-w-3xl space-y-6">
      <div className="p-5 rounded-xl bg-white border border-slate-200 shadow-sm flex items-start space-x-3.5">
        <div className="w-10 h-10 rounded-lg bg-red-50 border border-red-200 flex items-center justify-center text-brand-600 shrink-0 mt-0.5">
          <Sliders className="w-5 h-5" />
        </div>
        <div>
          <h2 className="text-base font-bold text-slate-900">Deterministic Safety Policy Guardrails</h2>
          <p className="text-xs text-slate-500 mt-1 leading-relaxed">
            Configure financial limits, human approval thresholds, maximum attempts, and decay windows. Every policy modification automatically generates an immutable audit log.
          </p>
        </div>
      </div>

      <form onSubmit={handleSave} className="p-6 rounded-2xl bg-white border border-slate-200 shadow-sm space-y-5">
        {/* Toggle Automatic Recovery */}
        <div className="flex items-center justify-between p-4 rounded-xl bg-slate-50 border border-slate-200">
          <div>
            <div className="text-xs font-bold text-slate-900">Autonomous Recovery Engine</div>
            <p className="text-[11px] text-slate-500">Allow AI agent to execute policy-cleared actions automatically</p>
          </div>
          <input
            type="checkbox"
            checked={settings.automatic_recovery_enabled}
            onChange={(e) => setSettings({ ...settings, automatic_recovery_enabled: e.target.checked })}
            className="w-4 h-4 accent-brand-600 rounded cursor-pointer"
          />
        </div>

        {/* 1. Max Automatic Amount */}
        <div>
          <label className="block text-xs font-bold text-slate-900 mb-1">
            Automatic Recovery Limit (₹ INR)
          </label>
          <p className="text-[11px] text-slate-500 mb-2">
            Failed payments exceeding this ceiling mandate merchant human approval before link generation.
          </p>
          <input
            type="number"
            value={settings.max_automatic_amount}
            onChange={(e) => setSettings({ ...settings, max_automatic_amount: parseFloat(e.target.value) })}
            className="w-full px-3 py-2 rounded-lg bg-slate-50 border border-slate-200 text-xs text-slate-900 focus:outline-none focus:border-brand-600 font-mono"
          />
        </div>

        {/* 2. Human Approval Threshold (AI Confidence) */}
        <div>
          <label className="block text-xs font-bold text-slate-900 mb-1">
            Minimum AI Confidence Score (0.0 to 1.0)
          </label>
          <p className="text-[11px] text-slate-500 mb-2">
            Recommendations below this confidence rating are automatically flagged for human review.
          </p>
          <input
            type="number"
            step="0.05"
            min="0.1"
            max="1.0"
            value={settings.human_approval_threshold}
            onChange={(e) => setSettings({ ...settings, human_approval_threshold: parseFloat(e.target.value) })}
            className="w-full px-3 py-2 rounded-lg bg-slate-50 border border-slate-200 text-xs text-slate-900 focus:outline-none focus:border-brand-600 font-mono"
          />
        </div>

        {/* 3. Max Retries */}
        <div>
          <label className="block text-xs font-bold text-slate-900 mb-1">
            Maximum Permitted Recovery Attempts
          </label>
          <p className="text-[11px] text-slate-500 mb-2">
            Hard stop after reaching maximum tries to prevent customer fatigue and card penalty fees.
          </p>
          <input
            type="number"
            value={settings.max_retry_attempts}
            onChange={(e) => setSettings({ ...settings, max_retry_attempts: parseInt(e.target.value) })}
            className="w-full px-3 py-2 rounded-lg bg-slate-50 border border-slate-200 text-xs text-slate-900 focus:outline-none focus:border-brand-600 font-mono"
          />
        </div>

        {/* 4. Recovery Window */}
        <div>
          <label className="block text-xs font-bold text-slate-900 mb-1">
            Recovery Window (Days)
          </label>
          <p className="text-[11px] text-slate-500 mb-2">
            Transactions older than this duration will automatically transition to EXPIRED.
          </p>
          <input
            type="number"
            value={settings.recovery_window_days}
            onChange={(e) => setSettings({ ...settings, recovery_window_days: parseInt(e.target.value) })}
            className="w-full px-3 py-2 rounded-lg bg-slate-50 border border-slate-200 text-xs text-slate-900 focus:outline-none focus:border-brand-600 font-mono"
          />
        </div>

        {/* 5. Customer Contact Limit */}
        <div>
          <label className="block text-xs font-bold text-slate-900 mb-1">
            Customer Contact Limit
          </label>
          <p className="text-[11px] text-slate-500 mb-2">
            Maximum automated payment link messages sent per failed invoice cycle.
          </p>
          <input
            type="number"
            value={settings.max_contact_attempts}
            onChange={(e) => setSettings({ ...settings, max_contact_attempts: parseInt(e.target.value) })}
            className="w-full px-3 py-2 rounded-lg bg-slate-50 border border-slate-200 text-xs text-slate-900 focus:outline-none focus:border-brand-600 font-mono"
          />
        </div>

        {/* 6. Cooldown Minutes */}
        <div>
          <label className="block text-xs font-bold text-slate-900 mb-1">
            Recovery Action Cooldown (Minutes)
          </label>
          <p className="text-[11px] text-slate-500 mb-2">
            Minimum waiting period before subsequent dunning communication or retry.
          </p>
          <input
            type="number"
            value={settings.retry_cooldown_minutes}
            onChange={(e) => setSettings({ ...settings, retry_cooldown_minutes: parseInt(e.target.value) })}
            className="w-full px-3 py-2 rounded-lg bg-slate-50 border border-slate-200 text-xs text-slate-900 focus:outline-none focus:border-brand-600 font-mono"
          />
        </div>

        <div className="pt-4 border-t border-slate-200 flex items-center justify-between">
          {saved ? (
            <span className="text-xs text-emerald-700 font-bold flex items-center gap-1.5">
              <CheckCircle2 className="w-4 h-4 text-emerald-600" /> Changes applied & audited!
            </span>
          ) : (
            <span />
          )}
          <button
            type="submit"
            disabled={isSaving}
            className="px-5 py-2.5 rounded-lg bg-brand-600 hover:bg-brand-700 text-white text-xs font-semibold transition flex items-center space-x-1.5 shadow-sm"
          >
            <Save className="w-3.5 h-3.5" />
            <span>{isSaving ? "Saving..." : "Save Guardrails"}</span>
          </button>
        </div>
      </form>
    </div>
  );
};
