import React, { useEffect, useState } from "react";
import { CreditCard, Search } from "lucide-react";
import { api } from "../lib/api";

export const PaymentsView: React.FC = () => {
  const [payments, setPayments] = useState<any[]>([]);
  const [search, setSearch] = useState<string>("");

  useEffect(() => {
    api.getPayments().then(setPayments).catch(console.error);
  }, []);

  const filteredPayments = payments.filter((p) => {
    if (!search) return true;
    const q = search.toLowerCase();
    return (
      p.customer_name?.toLowerCase().includes(q) ||
      p.external_id?.toLowerCase().includes(q) ||
      p.failure_reason?.toLowerCase().includes(q) ||
      p.payment_method?.toLowerCase().includes(q)
    );
  });

  return (
    <div className="p-5 rounded-xl bg-white border border-slate-200 shadow-sm space-y-4">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-3 pb-3 border-b border-slate-200">
        <div>
          <h2 className="text-base font-bold text-slate-900">Payment Transactions Ledger</h2>
          <p className="text-xs text-slate-500">Captured and failed payments ingested via Razorpay Test Mode or local simulator.</p>
        </div>
        <div className="flex items-center space-x-3">
          <div className="relative">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
            <input
              type="text"
              placeholder="Search payments..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="pl-9 pr-3 py-1.5 rounded-lg bg-slate-50 border border-slate-200 text-xs text-slate-900 placeholder-slate-400 focus:outline-none focus:border-brand-600 w-56"
            />
          </div>
          <span className="text-xs text-slate-500 font-semibold">{filteredPayments.length} transactions</span>
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs text-slate-700">
          <thead className="bg-slate-50 text-slate-500 uppercase text-[10px] font-semibold tracking-wider border-b border-slate-200">
            <tr>
              <th className="py-2.5 px-3">Payment Ref</th>
              <th className="py-2.5 px-3">Customer</th>
              <th className="py-2.5 px-3">Amount</th>
              <th className="py-2.5 px-3">Method</th>
              <th className="py-2.5 px-3">Failure Reason</th>
              <th className="py-2.5 px-3 text-center">Attempts</th>
              <th className="py-2.5 px-3">Status</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {filteredPayments.map((p) => (
              <tr key={p.id} className="hover:bg-slate-50 transition">
                <td className="py-2.5 px-3 font-mono text-slate-500">{p.external_id}</td>
                <td className="py-2.5 px-3 font-semibold text-slate-900">{p.customer_name}</td>
                <td className="py-2.5 px-3 font-bold text-slate-900">₹{p.amount?.toLocaleString("en-IN")}</td>
                <td className="py-2.5 px-3 font-mono text-[11px] text-slate-500">{p.payment_method}</td>
                <td className="py-2.5 px-3 text-slate-700 capitalize font-medium">{p.failure_reason?.replace(/_/g, " ") || "None"}</td>
                <td className="py-2.5 px-3 text-center font-bold text-slate-800">{p.attempt_count}</td>
                <td className="py-2.5 px-3">
                  <span
                    className={`px-2.5 py-0.5 text-[10px] font-bold rounded-full ${
                      p.status === "CAPTURED"
                        ? "bg-emerald-50 text-emerald-700 border border-emerald-200"
                        : "bg-red-50 text-red-700 border border-red-200"
                    }`}
                  >
                    {p.status}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};
