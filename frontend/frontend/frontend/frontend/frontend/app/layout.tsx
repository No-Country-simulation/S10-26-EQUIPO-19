import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "OpenBridge - Catálogo Open Source",
  description: "Catálogo curado open-source. Encontrá la herramienta ideal.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="es">
      <body>{children}</body>
    </html>
  );
}
