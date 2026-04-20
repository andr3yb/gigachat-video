import "./globals.css";
import Link from "next/link";
import type { ReactNode } from "react";

export const metadata = {
  title: "AI Video Factory",
  description: "Generate videos from images"
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="ru">
      <body>
        <main className="page">
          <nav className="row">
            <Link href="/">Генерация</Link>
            <Link href="/gallery">Галерея</Link>
          </nav>
          {children}
        </main>
      </body>
    </html>
  );
}
