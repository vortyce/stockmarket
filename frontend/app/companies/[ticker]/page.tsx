import React from 'react';
import { 
  TrendingUp, 
  TrendingDown, 
  Activity, 
  Target, 
  ExternalLink,
  ChevronLeft
} from 'lucide-react';

async function getCompanyData(ticker: string) {
  const baseUrl = process.env.API_URL || process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
  // Note: Standard fetch behavior for RSC
  const companyRes = await fetch(`${baseUrl}/api/v1/companies/${ticker}`, { cache: 'no-store' });
  const scoreRes = await fetch(`${baseUrl}/api/v1/scores/${ticker}`, { cache: 'no-store' });
  const financialsRes = await fetch(`${baseUrl}/api/v1/companies/${ticker}/financials`, { cache: 'no-store' });
  const marketRes = await fetch(`${baseUrl}/api/v1/companies/${ticker}/market`, { cache: 'no-store' });
  
  if (!companyRes.ok) return null;
  
  const company = await companyRes.json();
  const score = scoreRes.ok ? await scoreRes.json() : null;
  const financials = financialsRes.ok ? await financialsRes.json() : [];
  const market = marketRes.ok ? await marketRes.json() : null;
  
  return { company, score, financials, market };
}

export default async function CompanyDetailPage({ params }: { params: Promise<{ ticker: string }> }) {
  const { ticker } = await params;
  const data = await getCompanyData(ticker);

  if (!data) return <div className="p-8">Empresa não encontrada.</div>;

  const { company, score, financials, market } = data;
  const latestFin = financials?.length > 0 ? financials[0] : null;

  const blocks = [
    { name: 'Qualidade', score: score?.quality_raw || 0, color: '#3b82f6' },
    { name: 'Valuation', score: score?.valuation_raw || 0, color: '#f59e0b' },
    { name: 'Dividendos', score: score?.dividends_raw || 0, color: '#10b981' },
    { name: 'Tendência', score: score?.trend_raw || 0, color: '#8b5cf6' },
    { name: 'Gov/Liq', score: score?.gov_liq_raw || 0, color: '#ec4899' },
  ];

  return (
    <div className="company-page fade-in">
      <nav className="breadcrumb">
        <a href="/screener" className="back-link">
          <ChevronLeft size={16} /> Voltar ao Screener
        </a>
      </nav>

      <header className="company-header card">
        <div className="header-main">
          <div className="title-group">
            <div className="ticker-badge">{ticker}</div>
            <h1>{company.company_name}</h1>
            <p>{company.sector} • {company.listing_segment}</p>
          </div>
          <div className="score-group">
            <div className="final-score-circle">
               <span className="score-num">{score?.final_score || 'N/A'}</span>
               <span className="score-label">Score Global</span>
            </div>
            <div className="rating-pill">
                <span className={`badge badge-${score?.rating_class?.toLowerCase()}`}>
                    {score?.rating_class || 'Sem Rating'}
                </span>
                <span className="bucket-info">{score?.bucket}</span>
            </div>
          </div>
        </div>
      </header>

      <div className="grid-layout">
        <section className="analysis-grid">
           <div className="card spider-card">
              <h2>Composição do Score</h2>
              <div className="block-list">
                {blocks.map(block => (
                   <div key={block.name} className="block-item">
                      <div className="block-label">
                         <span>{block.name}</span>
                         <strong>{block.score}</strong>
                      </div>
                      <div className="progress-bg">
                         <div className="progress-fill" style={{width: `${block.score}%`, background: block.color}}></div>
                      </div>
                   </div>
                ))}
              </div>
           </div>

           <div className="card summary-card">
              <h2>Resumo da Tese</h2>
              <p className="summary-text">{score?.summary || 'Dados analíticos não disponíveis para este ticker.'}</p>
              <div className="metadata-grid">
                  <div className="meta-item">
                     <label>CVM Code</label>
                     <span>{company.cvm_code}</span>
                  </div>
                  <div className="meta-item">
                     <label>CNPJ</label>
                     <span>{company.cnpj}</span>
                  </div>
                  <div className="meta-item">
                     <label>Free Float</label>
                     <span>{((company.free_float || 0) * 100).toFixed(2)}%</span>
                  </div>
              </div>
           </div>
        </section>

        <section className="raw-data-section card">
           <h2>Histórico e Indicadores</h2>
           <p className="text-muted">Abaixo estão os indicadores utilizados para o cálculo do score acima.</p>
           <div className="indicators-container" style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '2rem', marginTop: '1.5rem' }}>
              <div className="market-indicators">
                <h3 style={{ borderBottom: '1px solid var(--border)', paddingBottom: '0.5rem', marginBottom: '1rem', color: 'var(--muted)' }}>Indicadores de Mercado</h3>
                {market ? (
                  <table className="transparent-table">
                    <tbody>
                      <tr><td><strong>Preço Atual</strong></td><td>R$ {market.price?.toFixed(2) || '-'}</td></tr>
                      <tr><td><strong>P/L</strong></td><td>{market.pe?.toFixed(2) || '-'}x</td></tr>
                      <tr><td><strong>P/VP</strong></td><td>{market.pb?.toFixed(2) || '-'}x</td></tr>
                      <tr><td><strong>EV/EBITDA</strong></td><td>{market.ev_ebitda?.toFixed(2) || '-'}x</td></tr>
                      <tr><td><strong>Dividend Yield</strong></td><td>{(market.dividend_yield * 100).toFixed(2) || '-'}%</td></tr>
                      <tr><td><strong>Valor de Mercado</strong></td><td>R$ {(market.market_cap / 1e9).toFixed(2)} B</td></tr>
                    </tbody>
                  </table>
                ) : <p className="text-muted">Dados de mercado não disponíveis.</p>}
              </div>

              <div className="financial-indicators">
                <h3 style={{ borderBottom: '1px solid var(--border)', paddingBottom: '0.5rem', marginBottom: '1rem', color: 'var(--muted)' }}>Último Balanço DFP ({latestFin?.year || '-'})</h3>
                {latestFin ? (
                  <table className="transparent-table">
                    <tbody>
                      <tr><td><strong>Receita Líquida</strong></td><td>R$ {(latestFin.revenue / 1e9).toFixed(2)} B</td></tr>
                      <tr><td><strong>EBITDA</strong></td><td>R$ {(latestFin.ebitda / 1e9).toFixed(2)} B</td></tr>
                      <tr><td><strong>Lucro Líquido</strong></td><td>R$ {(latestFin.net_income / 1e9).toFixed(2)} B</td></tr>
                      <tr><td><strong>Margem Líquida</strong></td><td>{(latestFin.net_margin * 100).toFixed(2)}%</td></tr>
                      <tr><td><strong>ROE</strong></td><td>{(latestFin.roe * 100).toFixed(2)}%</td></tr>
                      <tr><td><strong>Dívida Líquida / EBITDA</strong></td><td>{latestFin.ebitda > 0 ? (latestFin.net_debt / latestFin.ebitda).toFixed(2) : '-'}x</td></tr>
                    </tbody>
                  </table>
                ) : <p className="text-muted">Dados financeiros anuais não disponíveis.</p>}
              </div>
           </div>
        </section>
      </div>
    </div>
  );
}
