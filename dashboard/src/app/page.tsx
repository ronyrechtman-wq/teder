"use client";

import { useEffect, useState } from "react";
import { api, Event } from "@/lib/api";
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
} from "recharts";
import { format, parseISO, subDays } from "date-fns";
import { ptBR } from "date-fns/locale";

interface DayStat {
  day: string;
  allow: number;
  warn: number;
  block: number;
}

function buildDayStats(events: Event[]): DayStat[] {
  const map: Record<string, DayStat> = {};
  events.forEach((e) => {
    const day = e.created_at.slice(0, 10);
    if (!map[day]) map[day] = { day, allow: 0, warn: 0, block: 0 };
    map[day][e.action]++;
  });
  return Object.values(map).sort((a, b) => a.day.localeCompare(b.day));
}

export default function Overview() {
  const [events, setEvents] = useState<Event[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api.events(1, 200)
      .then((r) => setEvents(r.items))
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  const total = events.length;
  const blocked = events.filter((e) => e.action === "block").length;
  const avgRisk = total > 0
    ? (events.reduce((s, e) => s + e.risk_score, 0) / total).toFixed(2)
    : "—";
  const dayStats = buildDayStats(events);
  const hasEventsToday = events.some(
    (e) => e.created_at.slice(0, 10) === new Date().toISOString().slice(0, 10)
  );

  if (loading) return <p className="text-gray-500">Carregando...</p>;
  if (error) return <p className="text-red-500">Erro: {error}</p>;

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Overview</h1>

      {/* Cards */}
      <div className="grid grid-cols-3 gap-4 mb-8">
        <StatCard label="Requisições no mês" value={String(total)} />
        <StatCard label="Bloqueios" value={String(blocked)} highlight={blocked > 0} />
        <StatCard label="Risk score médio" value={avgRisk} />
      </div>

      {/* Plataforma */}
      <div className="bg-blue-50 border border-blue-200 rounded-xl p-4 mb-8">
        <p className="text-sm text-blue-700 font-medium">
          {hasEventsToday
            ? `TEDER detectou ${blocked} ameaça${blocked !== 1 ? "s" : ""} nos seus agentes hoje`
            : "TEDER protegendo — nenhuma ameaça detectada hoje"}
        </p>
      </div>

      {/* Gráfico */}
      <div className="bg-white rounded-xl shadow p-6">
        <h2 className="text-base font-semibold mb-4">Volume diário de eventos</h2>
        {dayStats.length === 0 ? (
          <p className="text-gray-400 text-sm">Nenhum evento registrado ainda.</p>
        ) : (
          <ResponsiveContainer width="100%" height={280}>
            <LineChart data={dayStats}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="day" tick={{ fontSize: 11 }} />
              <YAxis tick={{ fontSize: 11 }} />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="allow" stroke="#22c55e" name="Allow" strokeWidth={2} dot={false} />
              <Line type="monotone" dataKey="warn" stroke="#f59e0b" name="Warn" strokeWidth={2} dot={false} />
              <Line type="monotone" dataKey="block" stroke="#ef4444" name="Block" strokeWidth={2} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        )}
      </div>
    </div>
  );
}

function StatCard({ label, value, highlight }: { label: string; value: string; highlight?: boolean }) {
  return (
    <div className={`rounded-xl p-5 shadow ${highlight ? "bg-red-50 border border-red-200" : "bg-white"}`}>
      <p className="text-xs text-gray-500 uppercase tracking-wide">{label}</p>
      <p className={`text-3xl font-bold mt-1 ${highlight ? "text-red-600" : "text-gray-900"}`}>{value}</p>
    </div>
  );
}
