import React from 'react';

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

export default async function RankingPage() {
  const rankings = await getTopRankings();

  return (
    <div className="ranking-container fade-in">
      <header className="page-header">
        <h1>B3 Top 20 Ranking</h1>
        <p>As 20 melhores oportunidades detectadas pelo motor de scoring.</p>
      </header>

      <div className="card">
        <table>
          <thead>
            <tr>
              <th>#</th>
              <th>Ticker</th>
              <th>Empresa</th>
              <th>Setor</th>
              <th>Score</th>
              <th>Rating</th>
              <th>Bucket</th>
            </tr>
          </thead>
          <tbody>
            {rankings.map((stock: any) => (
              <tr key={stock.ticker}>
                <td><strong>{stock.position}</strong></td>
                <td className="ticker-cell">
                  <a href={`/companies/${stock.ticker}`}>{stock.ticker}</a>
                </td>
                <td>{stock.company_name}</td>
                <td><span className="sector-tag">{stock.sector}</span></td>
                <td><span className="score-badge">{stock.final_score}</span></td>
                <td>
                  <span className={`badge badge-${stock.rating_class.toLowerCase()}`}>
                    {stock.rating_class}
                  </span>
                </td>
                <td>{stock.bucket}</td>
              </tr>
            ))}
            {rankings.length === 0 && (
              <tr>
                <td colSpan={7} style={{textAlign: 'center', padding: '3rem', color: 'var(--muted)'}}>
                  Nenhum ranking gerado ainda. Execute o job de recalculo.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
