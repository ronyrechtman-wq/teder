import type { Metadata } from "next";
import "./globals.css";
import { AuthGate } from "@/components/AuthGate";
import { Sidebar } from "@/components/Sidebar";

export const metadata: Metadata = {
  title: "TEDER Dashboard",
  description: "Segurança em tempo real para agentes autônomos",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="pt-BR">
      <body className="bg-gray-50 text-gray-900 min-h-screen">
        <AuthGate>
          <div className="flex min-h-screen">
            <Sidebar />
            <main className="flex-1 p-8">{children}</main>
          </div>
        </AuthGate>
      </body>
    </html>
  );
}
