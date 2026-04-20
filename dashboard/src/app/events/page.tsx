"use client";

import { useEffect, useState } from "react";
import { api, Event } from "@/lib/api";

const ACTION_COLORS: Record<string, string> = {
  allow: "bg-green-100 text-green-700",
  warn: "bg-yellow-100 text-yellow-700",
  block: "bg-red-100 text-red-700",
};

function exportCSV(events: Event[]) {
  const headers = ["timestamp", "agent_id", "action", "risk_score", "threats", "latency_ms", "request_id"];
  const rows = events.map((e) => [
    e.created_at,
    e.agent_id,
    e.action,
    e.risk_score,
    e.threats.join("|"),
    e.latency_ms,
    e.request_id,
  ]);
  const csv = [headers, ...rows].map((r) => r.join(",")).join("\n");
  const blob = new Blob([csv], { type: "text/csv" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `teder-auditoria-lgpd-${new Date().toISOString().slice(0, 10)}.csv`;
  a.click();
}

export default function EventsPage() {
  const [events, setEvents] = useState<Event[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [actionFilter, setActionFilter] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    api.events(page, 50, actionFilter || undefined)
      .then((r) => { setEvents(r.items); setTotal(r.total); })
      .finally(() => setLoading(false));
  }, [page, actionFilter]);

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold">Eventos</h1>
        <div className="flex gap-3">
          <select
            className="border border-gray-300 rounded-lg px-3 py-2 text-sm"
            value={actionFilter}
            onChange={(e) => { setActionFilter(e.target.value); setPage(1); }}
          >
            <option value="">Todos</option>
            <option value="allow">Allow</option>
            <option value="warn">Warn</option>
            <option value="block">Block</option>
          </select>
          <button
            className="bg-teder-500 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-blue-700 transition"
            onClick={() => exportCSV(events)}
          >
            Exportar relatório LGPD
          </button>
        </div>
      </div>

      <div className="bg-white rounded-xl shadow overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-gray-50 border-b border-gray-200">
            <tr>
              {["Timestamp", "Agent ID", "Action", "Threats", "Risk Score", "Latência"].map((h) => (
                <th key={h} className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase">{h}</th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {loading ? (
              <tr><td colSpan={6} className="text-center py-8 text-gray-400">Carregando...</td></tr>
            ) : events.length === 0 ? (
              <tr><td colSpan={6} className="text-center py-8 text-gray-400">Nenhum evento encontrado</td></tr>
            ) : events.map((e) => (
              <tr key={e.id} className="hover:bg-gray-50">
                <td className="px-4 py-3 text-gray-500 whitespace-nowrap">
                  {new Date(e.created_at).toLocaleString("pt-BR")}
                </td>
                <td className="px-4 py-3 font-mono text-xs">{e.agent_id}</td>
                <td className="px-4 py-3">
                  <span className={`px-2 py-0.5 rounded-full text-xs font-semibold ${ACTION_COLORS[e.action]}`}>
                    {e.action.toUpperCase()}
                  </span>
                </td>
                <td className="px-4 py-3">
                  <div className="flex flex-wrap gap-1">
                    {e.threats.map((t) => (
                      <span key={t} className="bg-gray-100 text-gray-600 px-2 py-0.5 rounded text-xs">{t}</span>
                    ))}
                  </div>
                </td>
                <td className="px-4 py-3">{e.risk_score.toFixed(2)}</td>
                <td className="px-4 py-3">{e.latency_ms.toFixed(0)}ms</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Paginação */}
      <div className="flex items-center justify-between mt-4 text-sm text-gray-500">
        <span>{total} evento{total !== 1 ? "s" : ""} no total</span>
        <div className="flex gap-2">
          <button disabled={page === 1} onClick={() => setPage(p => p - 1)}
            className="px-3 py-1 border rounded disabled:opacity-40">Anterior</button>
          <span className="px-3 py-1">Página {page}</span>
          <button disabled={page * 50 >= total} onClick={() => setPage(p => p + 1)}
            className="px-3 py-1 border rounded disabled:opacity-40">Próxima</button>
        </div>
      </div>
    </div>
  );
}
