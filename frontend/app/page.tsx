import React from 'react';
import { LayoutDashboard, TrendingUp, ShieldCheck, PieChart } from 'lucide-react';

async function getTopRankings() {
  const baseUrl = process.env.API_URL || process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
  try {
    const res = await fetch(`${baseUrl}/api/v1/rankings/top20`, { cache: 'no-store' });
    if (!res.ok) return [];
    return res.json();
  } catch (e) {
    return [];
  }
}

export default async function HomePage() {
  const rankings = await getTopRankings();

  return (
    <div className="dashboard-container fade-in">
      <header className="page-header">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end' }}>
          <div>
            <h1>Dashboard Analítico</h1>
            <p>Visão geral da saúde quantitativa da carteira e mercado.</p>
          </div>
          {rankings.length > 0 && (
            <div className="last-update" style={{ fontSize: '0.75rem', color: 'var(--muted)', textAlign: 'right' }}>
              Última atualização: <strong>{new Date(rankings[0].as_of_date).toLocaleDateString('pt-BR')}</strong>
              <br/>Modelo: <strong>{rankings[0].model_version}</strong>
            </div>
          )}
        </div>
      </header>

      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon"><LayoutDashboard size={24} /></div>
          <div className="stat-info">
            <h3>Total Coberto</h3>
            <span className="stat-value">{rankings.length}+ Ativos</span>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon"><TrendingUp size={24} /></div>
          <div className="stat-info">
            <h3>Melhor Score</h3>
            <span className="stat-value">{rankings[0]?.final_score || '0.0'}</span>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon"><ShieldCheck size={24} /></div>
          <div className="stat-info">
            <h3>Rating "Compra"</h3>
            <span className="stat-value">{rankings.filter((r: any) => r.rating_class === 'Compra').length} Ativos</span>
          </div>
        </div>
      </div>

      <section className="top-rankings-section">
        <div className="section-header">
          <h2>Top 5 Ranking Geral</h2>
          <a href="/ranking" className="see-all">Ver todos →</a>
        </div>
        <div className="card">
          <table className="transparent-table">
            <thead>
              <tr>
                <th>Pos</th>
                <th>Ticker</th>
                <th>Empresa</th>
                <th>Score</th>
                <th>Rating</th>
                <th>Bucket</th>
              </tr>
            </thead>
            <tbody>
              {rankings.slice(0, 5).map((stock: any) => (
                <tr key={stock.ticker}>
                  <td><strong>#{stock.position}</strong></td>
                  <td><a href={`/companies/${stock.ticker}`} className="ticker-link">{stock.ticker}</a></td>
                  <td>{stock.company_name}</td>
                  <td><span className="score-val">{stock.final_score}</span></td>
                  <td>
                    <span className={`badge badge-${stock.rating_class.toLowerCase()}`}>
                      {stock.rating_class}
                    </span>
                  </td>
                  <td><span className="bucket-tag">{stock.bucket}</span></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

    </div>
  );
}
