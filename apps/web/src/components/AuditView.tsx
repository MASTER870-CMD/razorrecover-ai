"use client";

import React, { useEffect, useState } from "react";
import { History, Search } from "lucide-react";
import { api } from "../lib/api";

export const AuditView: React.FC = () => {
  const [logs, setLogs] = useState<any[]>([]);
  const [search, setSearch] = useState<string>("");

  useEffect(() => {
    api.getAuditLogs().then(setLogs).catch(console.error);
  }, []);

  const filteredLogs = logs.filter((l) => {
    if (!search) return true;
    const q = search.toLowerCase();
    return (
      l.actor?.toLowerCase().includes(q) ||
      l.event_type?.toLowerCase().includes(q) ||
      l.action?.toLowerCase().includes(q) ||
      l.decision?.toLowerCase().includes(q) ||
      l.case_id?.toLowerCase().includes(q)
    );
  });

  return (
    <div className="p-5 rounded-xl bg-white border border-slate-200 shadow-sm space-y-4">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-3 pb-3 border-b border-slate-200">
        <div>
          <h2 className="text-base font-bold text-slate-900 flex items-center gap-2">
            <History className="w-4 h-4 text-brand-600" />
            <span>Immutable Financial & Safety Audit Log</span>
          </h2>
          <p className="text-xs text-slate-500">
            Cryptographically trace every automated diagnosis, policy check, human approval, and recovery verification.
          </p>
        </div>
        <div className="flex items-center space-x-3">
          <div className="relative">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
            <input
              type="text"
              placeholder="Search audit trail..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="pl-9 pr-3 py-1.5 rounded-lg bg-slate-50 border border-slate-200 text-xs text-slate-900 placeholder-slate-400 focus:outline-none focus:border-brand-600 w-56"
            />
          </div>
          <span className="text-xs text-slate-500 font-mono font-semibold">{filteredLogs.length} Events</span>
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs text-slate-700">
          <thead className="bg-slate-50 text-slate-500 uppercase text-[10px] font-semibold tracking-wider border-b border-slate-200">
            <tr>
              <th className="py-2.5 px-3">Timestamp</th>
              <th className="py-2.5 px-3">Actor</th>
              <th className="py-2.5 px-3">Event Type</th>
              <th className="py-2.5 px-3">Action / Decision</th>
              <th className="py-2.5 px-3">State Transition</th>
              <th className="py-2.5 px-3">Correlation ID</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100 font-mono text-[11px]">
            {filteredLogs.map((l) => (
              <tr key={l.id} className="hover:bg-slate-50 transition">
                <td className="py-2.5 px-3 text-slate-500 font-sans">
                  {new Date(l.created_at).toLocaleString()}
                </td>
                <td className="py-2.5 px-3">
                  <span
                    className={`px-2 py-0.5 rounded font-bold text-[10px] ${
                      l.actor === "POLICY_ENGINE"
                        ? "bg-slate-100 text-slate-800 border border-slate-300"
                        : l.actor === "HUMAN_OPERATOR"
                        ? "bg-amber-50 text-amber-800 border border-amber-200"
                        : l.actor === "AGENT"
                        ? "bg-red-50 text-red-700 border border-red-200"
                        : "bg-slate-100 text-slate-700 border border-slate-200"
                    }`}
                  >
                    {l.actor}
                  </span>
                </td>
                <td className="py-2.5 px-3 font-sans font-semibold text-slate-900">{l.event_type}</td>
                <td className="py-2.5 px-3 text-slate-800 font-medium">{l.action || l.decision || "—"}</td>
                <td className="py-2.5 px-3 text-slate-500 font-sans">
                  {l.previous_state ? `${l.previous_state} → ${l.new_state}` : l.new_state}
                </td>
                <td className="py-2.5 px-3 text-slate-400 truncate max-w-[120px]">
                  {l.correlation_id?.slice(0, 10)}...
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};
