import React from "react";
import { AlertTriangle, CheckCircle, TrendingUp, Clock, UserCheck, ShieldX } from "lucide-react";

interface MetricsCardsProps {
  metrics: {
    revenue_at_risk: number;
    revenue_recovered: number;
    recovery_rate: number;
    active_cases: number;
    human_review_cases: number;
    blocked_actions: number;
    total_cases: number;
  };
}

export const MetricsCards: React.FC<MetricsCardsProps> = ({ metrics }) => {
  const cards = [
    {
      label: "Revenue at Risk",
      value: `₹${(metrics.revenue_at_risk || 0).toLocaleString("en-IN", { minimumFractionDigits: 0 })}`,
      description: "Identified in failed transactions",
      icon: AlertTriangle,
      color: "text-red-600",
      bg: "bg-red-50",
      border: "border-slate-200",
    },
    {
      label: "Revenue Recovered",
      value: `₹${(metrics.revenue_recovered || 0).toLocaleString("en-IN", { minimumFractionDigits: 0 })}`,
      description: "Verified captured test revenue",
      icon: CheckCircle,
      color: "text-emerald-600",
      bg: "bg-emerald-50",
      border: "border-slate-200",
    },
    {
      label: "Recovery Rate",
      value: `${(metrics.recovery_rate || 0).toFixed(1)}%`,
      description: "Proportion of cases saved",
      icon: TrendingUp,
      color: "text-brand-600",
      bg: "bg-red-50",
      border: "border-slate-200",
    },
    {
      label: "Active Recovery Cases",
      value: `${metrics.active_cases || 0}`,
      description: "In-flight recovery workflows",
      icon: Clock,
      color: "text-slate-700",
      bg: "bg-slate-100",
      border: "border-slate-200",
    },
    {
      label: "Human Review",
      value: `${metrics.human_review_cases || 0}`,
      description: "Threshold > ₹25k or critical risk",
      icon: UserCheck,
      color: "text-amber-600",
      bg: "bg-amber-50",
      border: "border-slate-200",
    },
    {
      label: "Safety Blocks",
      value: `${metrics.blocked_actions || 0}`,
      description: "Unsafe actions stopped by policy",
      icon: ShieldX,
      color: "text-slate-700",
      bg: "bg-slate-100",
      border: "border-slate-200",
    },
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-6 gap-4 mb-6">
      {cards.map((card, idx) => {
        const Icon = card.icon;
        return (
          <div
            key={idx}
            className="p-4 rounded-xl bg-white border border-slate-200 hover:border-slate-300 transition shadow-sm"
          >
            <div className="flex items-center justify-between mb-2">
              <span className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider">{card.label}</span>
              <div className={`p-1.5 rounded-lg ${card.bg}`}>
                <Icon className={`w-3.5 h-3.5 ${card.color}`} />
              </div>
            </div>
            <div className="text-xl font-bold tracking-tight text-slate-900 mb-0.5">{card.value}</div>
            <p className="text-[10px] text-slate-500 truncate">{card.description}</p>
          </div>
        );
      })}
    </div>
  );
};
