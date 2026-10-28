"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const LINKS = [
  { href: "/", label: "Catálogo" },
  { href: "/asistente", label: "Asistente" },
];

export default function NavLinks() {
  const pathname = usePathname();
  return (
    <>
      {LINKS.map((link) => {
        const active = link.href === "/" ? pathname === "/" : pathname.startsWith(link.href);
        return (
          <Link
            key={link.href}
            href={link.href}
            aria-current={active ? "page" : undefined}
            className={`inline-flex h-11 items-center rounded-[var(--radius-pill)] px-5 font-semibold ${
              active ? "bg-primary text-primary-contrast" : "text-text-muted hover:bg-surface-hover"
            }`}
          >
            {link.label}
          </Link>
        );
      })}
    </>
  );
}
