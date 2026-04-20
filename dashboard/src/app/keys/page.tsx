"use client";

import { useState } from "react";
import { api } from "@/lib/api";

export default function KeysPage() {
  const [adminSecret, setAdminSecret] = useState("");
  const [plan, setPlan] = useState("developer");
  const [newKey, setNewKey] = useState<string | null>(null);
  const [revokeId, setRevokeId] = useState("");
  const [message, setMessage] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function handleCreate() {
    if (!adminSecret) return;
    setLoading(true);
    try {
      const result = await api.createKey(plan, adminSecret);
      setNewKey(result.key);
      setMessage(null);
    } catch (e: any) {
      setMessage(`Erro: ${e.message}`);
    } finally {
      setLoading(false);
    }
  }

  async function handleRevoke() {
    if (!adminSecret || !revokeId) return;
    setLoading(true);
    try {
      await api.revokeKey(revokeId, adminSecret);
      setMessage("Key revogada com sucesso.");
      setRevokeId("");
    } catch (e: any) {
      setMessage(`Erro: ${e.message}`);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="max-w-xl">
      <h1 className="text-2xl font-bold mb-6">API Keys</h1>

      {message && (
        <div className="mb-4 p-3 bg-blue-50 border border-blue-200 rounded text-sm text-blue-700">{message}</div>
      )}

      {/* Criar key */}
      <div className="bg-white rounded-xl shadow p-6 mb-6">
        <h2 className="font-semibold mb-4">Criar nova API Key</h2>
        <label className="block text-xs text-gray-500 mb-1">Admin Secret</label>
        <input
          type="password"
          className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm mb-3"
          value={adminSecret}
          onChange={(e) => setAdminSecret(e.target.value)}
          placeholder="••••••••"
        />
        <label className="block text-xs text-gray-500 mb-1">Plano</label>
        <select
          className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm mb-4"
          value={plan}
          onChange={(e) => setPlan(e.target.value)}
        >
          <option value="free">Free</option>
          <option value="developer">Developer</option>
          <option value="business">Business</option>
          <option value="enterprise">Enterprise</option>
        </select>
        <button
          className="bg-teder-500 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-blue-700 transition w-full disabled:opacity-50"
          onClick={handleCreate}
          disabled={loading || !adminSecret}
        >
          {loading ? "Criando..." : "Criar Key"}
        </button>

        {newKey && (
          <div className="mt-4 p-3 bg-green-50 border border-green-200 rounded">
            <p className="text-xs text-green-700 font-medium mb-1">Key criada — copie agora, não será exibida novamente:</p>
            <code className="text-xs break-all text-green-900">{newKey}</code>
            <button
              className="mt-2 text-xs text-green-700 underline"
              onClick={() => navigator.clipboard.writeText(newKey)}
            >
              Copiar
            </button>
          </div>
        )}
      </div>

      {/* Revogar key */}
      <div className="bg-white rounded-xl shadow p-6">
        <h2 className="font-semibold mb-4">Revogar API Key</h2>
        <label className="block text-xs text-gray-500 mb-1">ID da Key (UUID)</label>
        <input
          type="text"
          className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm mb-4"
          value={revokeId}
          onChange={(e) => setRevokeId(e.target.value)}
          placeholder="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
        />
        <button
          className="bg-red-500 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-red-700 transition w-full disabled:opacity-50"
          onClick={handleRevoke}
          disabled={loading || !adminSecret || !revokeId}
        >
          {loading ? "Revogando..." : "Revogar Key"}
        </button>
      </div>
    </div>
  );
}
