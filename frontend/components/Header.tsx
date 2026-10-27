import Image from "next/image";
import Link from "next/link";
import NavLinks from "@/components/NavLinks";
import ThemeToggle from "@/components/ThemeToggle";

export default function Header() {
  return (
    <header className="border-b border-border bg-card">
      <div className="mx-auto flex max-w-6xl flex-wrap items-center justify-between gap-4 px-4 py-3">
        <Link href="/" className="flex items-center gap-3" aria-label="OpenBridge, ir al inicio">
          <Image src="/logo.png" alt="OpenBridge" width={84} height={50} priority />
        </Link>
        <nav aria-label="Principal" className="flex flex-wrap items-center gap-2 text-sm">
          <NavLinks />
          <ThemeToggle />
        </nav>
      </div>
    </header>
  );
}
