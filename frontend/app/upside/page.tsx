import React from 'react';
import { TrendingUp, AlertTriangle, Target, BarChart3, ChevronRight, ArrowUpRight } from 'lucide-react';

const API_URL = process.env.API_URL || process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

async function getUpside12MRanking() {
  try {
    const res = await fetch(`${API_URL}/api/v1/upside12m/top20`, { cache: 'no-store' });
    if (!res.ok) return [];
    return res.json();
  } catch {
    return [];
  }
}

function getBucketStyle(bucket: string): { color: string; bg: string; icon: React.ReactNode } {
  switch (bucket) {
    case 'Recuperação Operacional':
      return { color: '#10b981', bg: 'rgba(16,185,129,0.12)', icon: <TrendingUp size={14} /> };
    case 'Re-rating Forte':
      return { color: '#3b82f6', bg: 'rgba(59,130,246,0.12)', icon: <BarChart3 size={14} /> };
    case 'Assimetria Atrativa':
      return { color: '#a855f7', bg: 'rgba(168,85,247,0.12)', icon: <Target size={14} /> };
    case 'Upside de Research':
      return { color: '#f59e0b', bg: 'rgba(245,158,11,0.12)', icon: <ArrowUpRight size={14} /> };
    case 'Armadilha de Upside':
      return { color: '#ef4444', bg: 'rgba(239,68,68,0.12)', icon: <AlertTriangle size={14} /> };
    default:
      return { color: '#94a3b8', bg: 'rgba(148,163,184,0.08)', icon: null };
  }
}

function getRatingStyle(rating: string) {
  if (rating.includes('Compra Forte')) return { color: '#a855f7', bg: 'rgba(168,85,247,0.15)' };
  if (rating === 'Compra') return { color: '#10b981', bg: 'rgba(16,185,129,0.15)' };
  if (rating === 'Monitorar') return { color: '#f59e0b', bg: 'rgba(245,158,11,0.15)' };
  if (rating === 'Alerta') return { color: '#ef4444', bg: 'rgba(239,68,68,0.15)' };
  return { color: '#94a3b8', bg: 'rgba(148,163,184,0.1)' };
}

function ScoreBar({ label, value, color, weight }: { label: string; value: number; color: string; weight: string }) {
  return (
    <div className="u12m-bar-row">
      <div className="u12m-bar-label">
        <span>{label}</span>
        <span style={{ color: '#94a3b8', fontSize: '0.7rem' }}>{weight}</span>
        <strong style={{ color }}>{value.toFixed(0)}</strong>
      </div>
      <div className="u12m-bar-bg">
        <div className="u12m-bar-fill" style={{ width: `${value}%`, background: color }} />
      </div>
    </div>
  );
}

export default async function UpsidePage() {
  const ranking = await getUpside12MRanking();

  return (
    <div className="fade-in" style={{ maxWidth: 1100, margin: '0 auto' }}>
      {/* Module Header */}
      <div style={{ marginBottom: '2.5rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '0.75rem' }}>
          <div style={{
            background: 'linear-gradient(135deg, rgba(168,85,247,0.2), rgba(59,130,246,0.2))',
            border: '1px solid rgba(168,85,247,0.4)',
            padding: '0.5rem 1rem',
            borderRadius: '9999px',
            fontSize: '0.75rem',
            fontWeight: 700,
            color: '#a855f7',
            textTransform: 'uppercase',
            letterSpacing: '0.05em'
          }}>
            Módulo Alpha
          </div>
          <div style={{ color: '#64748b', fontSize: '0.875rem' }}>
            Motor independente · Não altera o Screener Base
          </div>
        </div>
        <h1 style={{ fontSize: '2rem', fontWeight: 800, marginBottom: '0.5rem' }}>
          Ranking Upside 12M
        </h1>
        <p style={{ color: '#94a3b8', maxWidth: '640px', lineHeight: 1.6 }}>
          Motor quantitativo focado em potencial de valorização — re-rating de múltiplos, 
          recuperação operacional e assimetria de risco/retorno. Separado e independente 
          do Ranking Base de Qualidade.
        </p>

        {/* Distinction Badge */}
        <div style={{
          display: 'inline-flex', gap: '2rem', marginTop: '1.5rem',
          background: 'rgba(255,255,255,0.03)', border: '1px solid #2d3748',
          borderRadius: '0.75rem', padding: '1rem 1.5rem'
        }}>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.25rem' }}>
            <span style={{ fontSize: '0.7rem', color: '#64748b', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Ranking Base</span>
            <span style={{ fontSize: '0.875rem', color: '#94a3b8' }}>Qualidade · Dividendos · Governança</span>
          </div>
          <div style={{ width: 1, background: '#2d3748' }} />
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.25rem' }}>
            <span style={{ fontSize: '0.7rem', color: '#a855f7', textTransform: 'uppercase', letterSpacing: '0.05em' }}>⬆ Upside 12M (atual)</span>
            <span style={{ fontSize: '0.875rem', color: '#e2e8f0', fontWeight: 600 }}>Re-rating · Recuperação · Assimetria</span>
          </div>
        </div>
      </div>

      {/* Ranking Table */}
      {ranking.length === 0 ? (
        <div className="card" style={{ textAlign: 'center', padding: '4rem', color: '#94a3b8' }}>
          <p>Nenhum dado de ranking 12M disponível. Execute o job de recalibração.</p>
        </div>
      ) : (
        <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr style={{ background: 'rgba(255,255,255,0.02)' }}>
                <th style={{ padding: '1rem 1.25rem', textAlign: 'left', color: '#64748b', fontSize: '0.75rem', textTransform: 'uppercase', letterSpacing: '0.05em', fontWeight: 600, width: 48 }}>#</th>
                <th style={{ padding: '1rem 1.25rem', textAlign: 'left', color: '#64748b', fontSize: '0.75rem', textTransform: 'uppercase', letterSpacing: '0.05em', fontWeight: 600 }}>Empresa</th>
                <th style={{ padding: '1rem 1.25rem', textAlign: 'center', color: '#64748b', fontSize: '0.75rem', textTransform: 'uppercase', letterSpacing: '0.05em', fontWeight: 600 }}>Score</th>
                <th style={{ padding: '1rem 1.25rem', textAlign: 'left', color: '#64748b', fontSize: '0.75rem', textTransform: 'uppercase', letterSpacing: '0.05em', fontWeight: 600 }}>Bucket</th>
                <th style={{ padding: '1rem 1.25rem', textAlign: 'center', color: '#64748b', fontSize: '0.75rem', textTransform: 'uppercase', letterSpacing: '0.05em', fontWeight: 600 }}>Rating</th>
                <th style={{ padding: '1rem 1.25rem', textAlign: 'center', color: '#64748b', fontSize: '0.75rem', textTransform: 'uppercase', letterSpacing: '0.05em', fontWeight: 600 }}></th>
              </tr>
            </thead>
            <tbody>
              {ranking.map((item: any, idx: number) => {
                const bucketStyle = getBucketStyle(item.bucket);
                const ratingStyle = getRatingStyle(item.rating_class);
                const isAlert = item.bucket === 'Armadilha de Upside';
                return (
                  <tr
                    key={item.ticker}
                    style={{
                      borderTop: '1px solid #1e293b',
                      background: isAlert ? 'rgba(239,68,68,0.03)' : 'transparent',
                      transition: 'background 0.15s'
                    }}
                    className="u12m-row"
                  >
                    <td style={{ padding: '1rem 1.25rem', color: '#475569', fontWeight: 700, fontSize: '0.875rem' }}>
                      {item.position}
                    </td>
                    <td style={{ padding: '1rem 1.25rem' }}>
                      <a href={`/upside/${item.ticker}`} style={{ textDecoration: 'none' }}>
                        <div style={{ fontWeight: 800, color: '#a855f7', fontSize: '1rem' }}>{item.ticker}</div>
                        {item.company_name && (
                          <div style={{ fontSize: '0.75rem', color: '#64748b', marginTop: '0.2rem' }}>
                            {item.company_name.length > 30 ? item.company_name.slice(0, 30) + '…' : item.company_name}
                          </div>
                        )}
                      </a>
                    </td>
                    <td style={{ padding: '1rem 1.25rem', textAlign: 'center' }}>
                      <div style={{
                        display: 'inline-flex', alignItems: 'center', justifyContent: 'center',
                        width: 52, height: 52, borderRadius: '50%',
                        border: `3px solid ${bucketStyle.color}30`,
                        background: bucketStyle.bg,
                        fontWeight: 800, fontSize: '1rem', color: bucketStyle.color
                      }}>
                        {item.final_score.toFixed(0)}
                      </div>
                    </td>
                    <td style={{ padding: '1rem 1.25rem' }}>
                      <div style={{
                        display: 'inline-flex', alignItems: 'center', gap: '0.4rem',
                        background: bucketStyle.bg, color: bucketStyle.color,
                        border: `1px solid ${bucketStyle.color}30`,
                        padding: '0.3rem 0.75rem', borderRadius: '9999px',
                        fontSize: '0.75rem', fontWeight: 600
                      }}>
                        {bucketStyle.icon}
                        {item.bucket}
                      </div>
                    </td>
                    <td style={{ padding: '1rem 1.25rem', textAlign: 'center' }}>
                      <span style={{
                        background: ratingStyle.bg, color: ratingStyle.color,
                        padding: '0.2rem 0.6rem', borderRadius: '9999px',
                        fontSize: '0.7rem', fontWeight: 700, textTransform: 'uppercase'
                      }}>
                        {item.rating_class}
                      </span>
                    </td>
                    <td style={{ padding: '1rem 1.25rem', textAlign: 'center' }}>
                      <a href={`/upside/${item.ticker}`} style={{
                        display: 'inline-flex', alignItems: 'center', gap: '0.25rem',
                        color: '#a855f7', fontSize: '0.75rem', fontWeight: 700
                      }}>
                        Detalhar <ChevronRight size={14} />
                      </a>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}

      {/* Legend */}
      <div style={{
        marginTop: '2rem', display: 'flex', gap: '1.5rem', flexWrap: 'wrap',
        padding: '1rem 1.5rem', background: 'rgba(255,255,255,0.02)',
        border: '1px solid #1e293b', borderRadius: '0.75rem'
      }}>
        <span style={{ color: '#64748b', fontSize: '0.75rem', fontWeight: 600, textTransform: 'uppercase', alignSelf: 'center' }}>Buckets:</span>
        {[
          { label: 'Recuperação Operacional', color: '#10b981' },
          { label: 'Re-rating Forte', color: '#3b82f6' },
          { label: 'Assimetria Atrativa', color: '#a855f7' },
          { label: 'Upside de Research', color: '#f59e0b' },
          { label: 'Armadilha de Upside ⚠', color: '#ef4444' },
          { label: 'Neutro', color: '#64748b' },
        ].map(b => (
          <div key={b.label} style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
            <div style={{ width: 8, height: 8, borderRadius: '50%', background: b.color }} />
            <span style={{ fontSize: '0.75rem', color: '#94a3b8' }}>{b.label}</span>
          </div>
        ))}
      </div>

      <style>{`
        .u12m-row:hover { background: rgba(168,85,247,0.04) !important; }
        .u12m-bar-row { margin-bottom: 1rem; }
        .u12m-bar-label { display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.4rem; font-size: 0.8rem; color: #cbd5e1; }
        .u12m-bar-bg { background: rgba(255,255,255,0.05); height: 7px; border-radius: 4px; overflow: hidden; }
        .u12m-bar-fill { height: 100%; border-radius: 4px; transition: width 0.6s ease; }
      `}</style>
    </div>
  );
}
