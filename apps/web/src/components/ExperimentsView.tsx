import React from "react";
import { FlaskConical, TrendingUp, CheckCircle, BarChart3 } from "lucide-react";

export const ExperimentsView: React.FC = () => {
  const experiments = [
    {
      name: "Immediate Retry vs. Smart Delayed Retry",
      hypothesis: "Delayed retries for insufficient funds reduce bank rate limits and recover 32% more revenue.",
      strategyA: "Immediate Retry (0m)",
      strategyB: "Smart Delayed Retry (24h)",
      attemptsA: 250,
      attemptsB: 250,
      recoveredA: 184500,
      recoveredB: 348200,
      rateA: 38.4,
      rateB: 72.8,
      winner: "Strategy B (Smart Delayed Retry)",
    },
    {
      name: "Payment Link Dunning vs. Static Retry for 3DS Failures",
      hypothesis: "Sending interactive Razorpay Payment Links upon 3DS OTP abortion outperforms blind retries.",
      strategyA: "Static Re-debit",
      strategyB: "Dynamic Payment Link",
      attemptsA: 180,
      attemptsB: 180,
      recoveredA: 42000,
      recoveredB: 198500,
      rateA: 14.2,
      rateB: 68.5,
      winner: "Strategy B (Dynamic Payment Link)",
    },
  ];

  return (
    <div className="space-y-6">
      <div className="p-4 rounded-xl bg-surface border border-border">
        <h2 className="text-base font-bold text-white flex items-center gap-2">
          <FlaskConical className="w-4 h-4 text-brand-400" />
          <span>Autonomous Recovery Strategy Experiments (A/B)</span>
        </h2>
        <p className="text-xs text-slate-400 mt-0.5">
          Empirical testing of recovery tactics to maximize capital recovery while preserving customer goodwill.
        </p>
      </div>

      <div className="space-y-6">
        {experiments.map((exp, idx) => (
          <div key={idx} className="p-6 rounded-2xl bg-surface border border-border space-y-4">
            <div>
              <div className="flex items-center justify-between">
                <h3 className="text-sm font-bold text-white">{exp.name}</h3>
                <span className="px-2.5 py-0.5 text-xs font-bold rounded-full bg-emerald-500/15 text-emerald-400 border border-emerald-500/30">
                  Winner: {exp.winner}
                </span>
              </div>
              <p className="text-xs text-slate-400 mt-1 italic">{exp.hypothesis}</p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* Strategy A */}
              <div className="p-4 rounded-xl bg-surface-subtle border border-border">
                <div className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">
                  Strategy A: {exp.strategyA}
                </div>
                <div className="flex items-baseline space-x-2">
                  <span className="text-xl font-bold text-white">{exp.rateA}%</span>
                  <span className="text-xs text-slate-400">Recovery Rate</span>
                </div>
                <div className="text-xs text-slate-400 mt-2">
                  Recovered: <span className="text-white font-medium">₹{exp.recoveredA.toLocaleString("en-IN")}</span> ({exp.attemptsA} attempts)
                </div>
              </div>

              {/* Strategy B */}
              <div className="p-4 rounded-xl bg-emerald-500/5 border border-emerald-500/30">
                <div className="text-xs font-semibold text-emerald-400 uppercase tracking-wider mb-2 flex items-center justify-between">
                  <span>Strategy B: {exp.strategyB}</span>
                  <span className="text-[10px] font-bold px-1.5 py-0.2 rounded bg-emerald-500/20 text-emerald-300">+{(exp.rateB - exp.rateA).toFixed(1)}%</span>
                </div>
                <div className="flex items-baseline space-x-2">
                  <span className="text-xl font-bold text-emerald-400">{exp.rateB}%</span>
                  <span className="text-xs text-emerald-300">Recovery Rate</span>
                </div>
                <div className="text-xs text-slate-400 mt-2">
                  Recovered: <span className="text-white font-medium">₹{exp.recoveredB.toLocaleString("en-IN")}</span> ({exp.attemptsB} attempts)
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
