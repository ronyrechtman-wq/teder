"use client";

import { useEffect, useState } from "react";
import { api, Event } from "@/lib/api";

interface AgentStat {
  agent_id: string;
  total: number;
  avg_risk: number;
  blocked: number;
}

function buildAgentStats(events: Event[]): AgentStat[] {
  const map: Record<string, { total: number; risk_sum: number; blocked: number }> = {};
  events.forEach((e) => {
    if (!map[e.agent_id]) map[e.agent_id] = { total: 0, risk_sum: 0, blocked: 0 };
    map[e.agent_id].total++;
    map[e.agent_id].risk_sum += e.risk_score;
    if (e.action === "block") map[e.agent_id].blocked++;
  });
  return Object.entries(map).map(([agent_id, s]) => ({
    agent_id,
    total: s.total,
    avg_risk: s.risk_sum / s.total,
    blocked: s.blocked,
  })).sort((a, b) => b.total - a.total);
}

export default function AgentsPage() {
  const [stats, setStats] = useState<AgentStat[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.events(1, 500)
      .then((r) => setStats(buildAgentStats(r.items)))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Agentes</h1>
      <div className="bg-white rounded-xl shadow overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-gray-50 border-b border-gray-200">
            <tr>
              {["Agent ID", "Requisições", "Risk Score Médio", "Bloqueios"].map((h) => (
                <th key={h} className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase">{h}</th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {loading ? (
              <tr><td colSpan={4} className="text-center py-8 text-gray-400">Carregando...</td></tr>
            ) : stats.length === 0 ? (
              <tr><td colSpan={4} className="text-center py-8 text-gray-400">Nenhum agente encontrado</td></tr>
            ) : stats.map((s) => (
              <tr key={s.agent_id} className="hover:bg-gray-50">
                <td className="px-4 py-3 font-mono text-xs">{s.agent_id}</td>
                <td className="px-4 py-3">{s.total}</td>
                <td className="px-4 py-3">
                  <span className={s.avg_risk > 0.5 ? "text-red-600 font-semibold" : "text-gray-700"}>
                    {s.avg_risk.toFixed(2)}
                  </span>
                </td>
                <td className="px-4 py-3">{s.blocked}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
