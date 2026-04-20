"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import clsx from "clsx";

const nav = [
  { href: "/", label: "Overview" },
  { href: "/events", label: "Eventos" },
  { href: "/agents", label: "Agentes" },
  { href: "/keys", label: "API Keys" },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="w-56 bg-white border-r border-gray-200 flex flex-col py-8 px-4">
      <div className="mb-8 px-2">
        <span className="text-xl font-bold text-teder-900">TEDER</span>
        <span className="block text-xs text-gray-400 mt-0.5">Agent Security</span>
      </div>
      <nav className="flex flex-col gap-1">
        {nav.map((item) => (
          <Link
            key={item.href}
            href={item.href}
            className={clsx(
              "px-3 py-2 rounded-lg text-sm font-medium transition",
              pathname === item.href
                ? "bg-teder-50 text-teder-900"
                : "text-gray-600 hover:bg-gray-100"
            )}
          >
            {item.label}
          </Link>
        ))}
      </nav>
      <div className="mt-auto">
        <button
          className="text-xs text-gray-400 hover:text-red-500 transition"
          onClick={() => {
            sessionStorage.removeItem("teder_key");
            window.location.reload();
          }}
        >
          Sair
        </button>
      </div>
    </aside>
  );
}
