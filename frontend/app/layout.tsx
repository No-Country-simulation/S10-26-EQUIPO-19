import type { Metadata } from "next";
import { Poppins } from "next/font/google";
import Link from "next/link";
import Header from "@/components/Header";
import "./globals.css";

const poppins = Poppins({
  subsets: ["latin"],
  weight: ["400", "500", "600", "700", "800"],
  variable: "--font-poppins",
  display: "swap",
});

export const metadata: Metadata = {
  title: "OpenBridge · Catálogo open source",
  description: "El camino corto a tu stack open source.",
  icons: { icon: "/logo.png" },
};

// Aplica el tema guardado (o el del sistema) antes de pintar, para evitar parpadeos.
const themeScript = `(function(){try{var t=localStorage.getItem('theme');if(t==='dark'||(!t&&window.matchMedia('(prefers-color-scheme: dark)').matches)){document.documentElement.classList.add('dark')}}catch(e){}})();`;

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="es" className={poppins.variable} suppressHydrationWarning>
      <head>
        <script dangerouslySetInnerHTML={{ __html: themeScript }} />
      </head>
      {/* suppressHydrationWarning: algunas extensiones del navegador agregan atributos al body antes de que cargue React. */}
      <body className="min-h-screen bg-surface font-sans text-text antialiased" suppressHydrationWarning>
        <Header />
        <main className="mx-auto max-w-6xl px-4 py-8">{children}</main>
        <footer className="border-t border-border px-4 py-6 text-center text-sm text-text-muted">
          OpenBridge · <span className="italic text-accent">El camino corto a tu stack open source</span> ·{" "}
          <Link href="/guia-de-estilo" className="text-primary hover:underline">Guía de estilo</Link>
        </footer>
      </body>
    </html>
  );
}
