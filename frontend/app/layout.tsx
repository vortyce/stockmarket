import './globals.css';
import type { Metadata } from 'next';
import { Inter } from 'next/font/google';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: 'B3 Screener | Análise Quantitativa',
  description: 'Sistema avançado de triagem e scoring para ações da B3.',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="pt-BR">
      <body className={inter.className}>
        <div className="layout-wrapper">
          <nav className="sidebar">
            <div className="logo">
              <h1>B3<span>Screener</span></h1>
            </div>
            <ul className="nav-links">
              <li><a href="/">Dashboard</a></li>
              <li><a href="/ranking">Top 20</a></li>
              <li><a href="/screener">Screener</a></li>
            </ul>
            <div className="nav-separator">
              <span>Módulos Alpha</span>
            </div>
            <ul className="nav-links">
              <li><a href="/upside" className="nav-alpha">⬆ Upside 12M</a></li>
              <li><a href="/options" className="nav-alpha">📉 Opções</a></li>
            </ul>
          </nav>
          <main className="main-content">
            {children}
          </main>
        </div>
      </body>
    </html>
  );
}
