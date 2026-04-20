"use client";

import { useState, useEffect } from "react";

export function AuthGate({ children }: { children: React.ReactNode }) {
  const [key, setKey] = useState<string | null>(null);
  const [input, setInput] = useState("");
  const [ready, setReady] = useState(false);

  useEffect(() => {
    const stored = sessionStorage.getItem("teder_key");
    setKey(stored);
    setReady(true);
  }, []);

  if (!ready) return null;

  if (!key) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="bg-white rounded-2xl shadow-lg p-10 w-full max-w-md">
          <div className="mb-6 text-center">
            <h1 className="text-3xl font-bold text-teder-900">TEDER</h1>
            <p className="text-gray-500 mt-1">Insira sua API Key para acessar o dashboard</p>
          </div>
          <input
            type="password"
            className="w-full border border-gray-300 rounded-lg px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-teder-500"
            placeholder="sk-teder-..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter" && input.startsWith("sk-teder-")) {
                sessionStorage.setItem("teder_key", input);
                setKey(input);
              }
            }}
          />
          <button
            className="mt-4 w-full bg-teder-500 text-white py-3 rounded-lg font-semibold hover:bg-blue-700 transition"
            onClick={() => {
              if (input.startsWith("sk-teder-")) {
                sessionStorage.setItem("teder_key", input);
                setKey(input);
              }
            }}
          >
            Entrar
          </button>
        </div>
      </div>
    );
  }

  return <>{children}</>;
}
