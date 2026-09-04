"use client";

import React, { useEffect, useState } from "react";
import { Users, Search } from "lucide-react";
import { api } from "../lib/api";

export const CustomersView: React.FC = () => {
  const [customers, setCustomers] = useState<any[]>([]);
  const [search, setSearch] = useState<string>("");
  const [selectedCustomer, setSelectedCustomer] = useState<any>(null);

  const loadCustomers = async () => {
    try {
      const data = await api.getCustomers(search);
      setCustomers(data);
    } catch (e) {
      console.error(e);
    }
  };

  useEffect(() => {
    loadCustomers();
  }, [search]);

  const viewCustomerProfile = async (id: string) => {
    try {
      const detail = await api.getCustomerDetail(id);
      setSelectedCustomer(detail);
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-3">
        <div>
          <h2 className="text-base font-bold text-slate-900">Merchant Customers & Reliability Profiles</h2>
          <p className="text-xs text-slate-500">
            Historical reliability, lifetime value, and recovery track records.
          </p>
        </div>
        <div className="relative">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
          <input
            type="text"
            placeholder="Search customers..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="pl-9 pr-3 py-1.5 rounded-lg bg-white border border-slate-200 text-xs text-slate-900 placeholder-slate-400 focus:outline-none focus:border-brand-600 w-64 shadow-sm"
          />
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Customer List */}
        <div className="md:col-span-2 p-5 rounded-xl bg-white border border-slate-200 shadow-sm">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs text-slate-700">
              <thead className="bg-slate-50 text-slate-500 uppercase text-[10px] font-semibold tracking-wider border-b border-slate-200">
                <tr>
                  <th className="py-2.5 px-3">Name</th>
                  <th className="py-2.5 px-3">Email</th>
                  <th className="py-2.5 px-3">Lifetime Value</th>
                  <th className="py-2.5 px-3">Payment Track Record</th>
                  <th className="py-2.5 px-3 text-right">Profile</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {customers.map((c) => (
                  <tr
                    key={c.id}
                    onClick={() => viewCustomerProfile(c.id)}
                    className="hover:bg-slate-50 cursor-pointer transition"
                  >
                    <td className="py-2.5 px-3 font-semibold text-slate-900">{c.name}</td>
                    <td className="py-2.5 px-3 text-slate-500 truncate max-w-[150px]">{c.email}</td>
                    <td className="py-2.5 px-3 font-bold text-slate-900">
                      ₹{c.customer_value?.toLocaleString("en-IN")}
                    </td>
                    <td className="py-2.5 px-3">
                      <span className="px-2 py-0.5 text-[10px] font-bold rounded bg-emerald-50 text-emerald-700 border border-emerald-200">
                        {((c.payment_success_rate || 0.9) * 100).toFixed(0)}% SUCCESS
                      </span>
                    </td>
                    <td className="py-2.5 px-3 text-right text-brand-600 font-bold hover:underline">Inspect</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Customer Detail Drawer */}
        <div className="p-5 rounded-xl bg-white border border-slate-200 shadow-sm">
          <h3 className="text-xs font-bold text-slate-900 uppercase tracking-wider mb-4">
            Customer Profile Summary
          </h3>
          {selectedCustomer ? (
            <div className="space-y-4 text-xs">
              <div>
                <span className="text-slate-400 text-[11px] font-medium">Customer Name</span>
                <div className="text-sm font-bold text-slate-900 mt-0.5">{selectedCustomer.customer.name}</div>
                <div className="text-slate-500 text-[11px]">{selectedCustomer.customer.email}</div>
              </div>

              <div className="grid grid-cols-2 gap-2 pt-2 border-t border-slate-100">
                <div>
                  <span className="text-slate-400 text-[11px] font-medium">Lifetime Value</span>
                  <div className="font-bold text-slate-900 mt-0.5">
                    ₹{selectedCustomer.customer.customer_value?.toLocaleString("en-IN")}
                  </div>
                </div>
                <div>
                  <span className="text-slate-400 text-[11px] font-medium">Payment Success</span>
                  <div className="font-bold text-emerald-700 mt-0.5">
                    {((selectedCustomer.customer.payment_success_rate || 0.9) * 100).toFixed(0)}%
                  </div>
                </div>
              </div>

              <div className="pt-3 border-t border-slate-100">
                <span className="text-[11px] font-bold text-slate-700 uppercase tracking-wider">Recent Payment Events</span>
                <div className="space-y-2 mt-2">
                  {selectedCustomer.recent_payments?.slice(0, 4).map((p: any) => (
                    <div key={p.id} className="p-2.5 rounded-lg bg-slate-50 border border-slate-200 flex justify-between items-center">
                      <div>
                        <span className="font-bold text-slate-900">₹{p.amount?.toLocaleString("en-IN")}</span>
                        <span className="text-[10px] text-slate-400 ml-1.5">{p.method}</span>
                      </div>
                      <span className={`text-[10px] font-bold px-2 py-0.5 rounded ${p.status === "CAPTURED" ? "bg-emerald-50 text-emerald-700 border border-emerald-200" : "bg-red-50 text-red-700 border border-red-200"}`}>
                        {p.status}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          ) : (
            <p className="text-xs text-slate-400 italic">Select a customer to view their profile and recovery history.</p>
          )}
        </div>
      </div>
    </div>
  );
};
