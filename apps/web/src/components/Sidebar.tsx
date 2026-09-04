import React from "react";
import {
  LayoutDashboard,
  ShieldAlert,
  Layers,
  CheckCircle2,
  Cpu,
  CreditCard,
  Users,
  BarChart3,
  History,
  Sliders,
  Plug,
  Settings as SettingsIcon,
} from "lucide-react";

interface SidebarProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
  pendingApprovalsCount: number;
}

export const Sidebar: React.FC<SidebarProps> = ({
  activeTab,
  setActiveTab,
  pendingApprovalsCount,
}) => {
  const navItems = [
    { id: "overview", label: "Overview", icon: LayoutDashboard },
    { id: "risk", label: "Revenue Risk", icon: ShieldAlert },
    { id: "queue", label: "Recovery Queue", icon: Layers },
    {
      id: "approvals",
      label: "Human Approvals",
      icon: CheckCircle2,
      badge: pendingApprovalsCount > 0 ? pendingApprovalsCount : undefined,
    },
    { id: "agent", label: "AI Agent", icon: Cpu },
    { id: "payments", label: "Payments", icon: CreditCard },
    { id: "customers", label: "Customers", icon: Users },
    { id: "evaluations", label: "Evaluations", icon: BarChart3 },
    { id: "audit", label: "Audit Log", icon: History },
    { id: "policy", label: "Policy Guardrails", icon: Sliders },
    { id: "connection", label: "Razorpay Connection", icon: Plug },
    { id: "settings", label: "Settings", icon: SettingsIcon },
  ];

  return (
    <aside className="w-64 border-r border-slate-200 bg-white flex flex-col justify-between p-4 min-h-[calc(100vh-65px)] select-none">
      <nav className="space-y-1">
        <p className="text-[11px] font-bold text-slate-400 uppercase tracking-wider px-3 mb-2">
          Fintech Operations
        </p>
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = activeTab === item.id;
          return (
            <button
              key={item.id}
              onClick={() => setActiveTab(item.id)}
              className={`w-full flex items-center justify-between px-3 py-2.5 rounded-lg text-xs font-medium transition ${
                isActive
                  ? "bg-brand-50 text-brand-700 font-semibold border-l-4 border-brand-600 rounded-l-none"
                  : "text-slate-600 hover:bg-slate-50 hover:text-slate-900 border-l-4 border-transparent"
              }`}
            >
              <div className="flex items-center space-x-2.5">
                <Icon className={`w-4 h-4 ${isActive ? "text-brand-600" : "text-slate-400"}`} />
                <span>{item.label}</span>
              </div>
              {item.badge !== undefined && (
                <span className="px-2 py-0.5 text-[10px] font-bold rounded-full bg-amber-100 text-amber-800 border border-amber-200">
                  {item.badge}
                </span>
              )}
            </button>
          );
        })}
      </nav>

      {/* Safety Engine Footnote */}
      <div className="p-3 rounded-lg bg-slate-50 border border-slate-200 mt-6 shadow-sm">
        <div className="flex items-center space-x-2 text-xs font-semibold text-slate-800">
          <span className="w-2 h-2 rounded-full bg-emerald-500" />
          <span>Safety Guard Active</span>
        </div>
        <p className="text-[11px] text-slate-500 mt-1 leading-relaxed">
          Deterministic checks enforce recovery windows, limits, and human reviews prior to link creation.
        </p>
      </div>
    </aside>
  );
};
