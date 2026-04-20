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
          <header className="topbar">
            <div className="brand">AI Video Factory</div>
            <nav className="nav">
              <Link className="nav-link" href="/">
                Генерация
              </Link>
              <Link className="nav-link" href="/gallery">
                Галерея
              </Link>
            </nav>
          </header>
          {children}
        </main>
      </body>
    </html>
  );
}
