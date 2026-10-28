import Image from "next/image";
import Link from "next/link";
import NavLinks from "@/components/NavLinks";
import ThemeToggle from "@/components/ThemeToggle";

export default function Header() {
  return (
    <header className="border-b border-border bg-card">
      <div className="mx-auto flex max-w-6xl flex-wrap items-center justify-between gap-4 px-4 py-4">
        <Link href="/" className="flex items-center" aria-label="OpenBridge, ir al inicio">
          {/* Logo completo de la identidad visual, con el slogan. Se muestra grande para que el slogan se lea. */}
          <Image
            src="/logo-horizontal.png"
            alt="OpenBridge: el camino corto a tu stack open source"
            width={440}
            height={79}
            className="h-auto w-[260px] sm:w-[340px] lg:w-[440px]"
            priority
          />
        </Link>
        <nav aria-label="Principal" className="flex flex-wrap items-center gap-2 text-sm">
          <NavLinks />
          <ThemeToggle />
        </nav>
      </div>
    </header>
  );
}
