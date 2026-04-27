import React from 'react';
import { ChevronLeft, TrendingUp, AlertTriangle, Target, BarChart3, ArrowUpRight, Info } from 'lucide-react';

const API_URL = process.env.API_URL || process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

async function getUpsideDetail(ticker: string) {
  try {
    const [detailRes, companyRes] = await Promise.all([
      fetch(`${API_URL}/api/v1/upside12m/${ticker}`, { cache: 'no-store' }),
      fetch(`${API_URL}/api/v1/companies/${ticker}`, { cache: 'no-store' }),
    ]);
    if (!detailRes.ok) return null;
    const detail = await detailRes.json();
    const company = companyRes.ok ? await companyRes.json() : null;
    return { detail, company };
  } catch {
    return null;
  }
}

function getBucketConfig(bucket: string) {
  const configs: Record<string, { color: string; bg: string; border: string; icon: React.ReactNode; description: string }> = {
    'Recuperação Operacional': {
      color: '#10b981', bg: 'rgba(16,185,129,0.08)', border: 'rgba(16,185,129,0.25)',
      icon: <TrendingUp size={20} />,
      description: 'O ativo apresenta melhora expressiva em margens e resultado operacional.'
    },
    'Re-rating Forte': {
      color: '#3b82f6', bg: 'rgba(59,130,246,0.08)', border: 'rgba(59,130,246,0.25)',
      icon: <BarChart3 size={20} />,
      description: 'Ação negociada com desconto significativo frente ao seu histórico de múltiplos.'
    },
    'Assimetria Atrativa': {
      color: '#a855f7', bg: 'rgba(168,85,247,0.08)', border: 'rgba(168,85,247,0.25)',
      icon: <Target size={20} />,
      description: 'Combinação rara: valuation deprimido + margens em expansão + balanço saudável.'
    },
    'Upside de Research': {
      color: '#f59e0b', bg: 'rgba(245,158,11,0.08)', border: 'rgba(245,158,11,0.25)',
      icon: <ArrowUpRight size={20} />,
      description: 'Desconto apontado por analistas com consenso de compra, suportado pelos fundamentos.'
    },
    'Armadilha de Upside': {
      color: '#ef4444', bg: 'rgba(239,68,68,0.08)', border: 'rgba(239,68,68,0.35)',
      icon: <AlertTriangle size={20} />,
      description: 'Alerta: upside externo alto, mas fundamentos operacionais ou dívida contraindicam. Risco de value trap.'
    },
    'Neutro': {
      color: '#94a3b8', bg: 'rgba(148,163,184,0.05)', border: 'rgba(148,163,184,0.2)',
      icon: <Info size={20} />,
      description: 'Sem assimetria ou driver de re-rating claro no momento de cálculo.'
    }
  };
  return configs[bucket] ?? configs['Neutro'];
}

interface ScoreBlock { label: string; value: number; color: string; weight: string; description: string }

function ScoreBlockBar({ block }: { block: ScoreBlock }) {
  return (
    <div style={{
      background: 'rgba(255,255,255,0.02)', border: '1px solid #1e293b',
      borderRadius: '0.75rem', padding: '1.25rem'
    }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.75rem' }}>
        <div>
          <div style={{ fontWeight: 700, color: '#e2e8f0', fontSize: '0.875rem' }}>{block.label}</div>
          <div style={{ fontSize: '0.7rem', color: '#64748b', marginTop: '0.2rem' }}>{block.description}</div>
        </div>
        <div style={{ textAlign: 'right' }}>
          <div style={{ fontWeight: 800, fontSize: '1.25rem', color: block.color }}>{block.value.toFixed(0)}</div>
          <div style={{ fontSize: '0.65rem', color: '#475569' }}>{block.weight}</div>
        </div>
      </div>
      <div style={{ background: 'rgba(255,255,255,0.05)', height: 8, borderRadius: 4, overflow: 'hidden' }}>
        <div style={{ width: `${block.value}%`, height: '100%', background: block.color, borderRadius: 4, transition: 'width 0.6s ease' }} />
      </div>
    </div>
  );
}

export default async function UpsideDetailPage({ params }: { params: Promise<{ ticker: string }> }) {
  const { ticker } = await params;
  const data = await getUpsideDetail(ticker);

  if (!data) {
    return (
      <div style={{ maxWidth: 900, margin: '0 auto' }}>
        <a href="/upside" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: '#94a3b8', marginBottom: '2rem', fontSize: '0.875rem' }}>
          <ChevronLeft size={16} /> Voltar ao Ranking Upside 12M
        </a>
        <div className="card" style={{ textAlign: 'center', padding: '4rem', color: '#94a3b8' }}>
          <AlertTriangle size={48} style={{ marginBottom: '1rem', opacity: 0.5 }} />
          <p>Análise Upside 12M não disponível para <strong>{ticker}</strong>.</p>
          <p style={{ marginTop: '0.5rem', fontSize: '0.875rem' }}>Execute o job de recalibração para gerar dados.</p>
        </div>
      </div>
    );
  }

  const { detail, company } = data;
  const m = detail.metrics;
  const bucketConfig = getBucketConfig(detail.bucket);

  const scoreBlocks: ScoreBlock[] = [
    { label: 'Upside Externo', value: m.upside_ext_raw, color: '#a855f7', weight: '30%', description: `Baseado no target de research vs preço capturado (${detail.research_target?.source_name ?? '—'})` },
    { label: 'Re-rating Potencial', value: m.rerating_raw, color: '#3b82f6', weight: '25%', description: 'Desconto do P/L atual vs média histórica do ativo' },
    { label: 'Recuperação Operacional', value: m.recup_operacional_raw, color: '#10b981', weight: '25%', description: 'Crescimento de EBITDA, melhora de margens, reversão de resultado' },
    { label: 'Assimetria', value: m.assimetria_raw, color: '#f59e0b', weight: '10%', description: 'Valuation deprimido + margens melhorando + dívida estável/caindo' },
    { label: 'Governança / Liquidez', value: m.gov_liq_raw, color: '#06b6d4', weight: '10%', description: 'Segmento de listagem, free float e liquidez de mercado' },
  ];

  const hasTarget = detail.research_target?.target_price;
  const upsidePct = hasTarget
    ? (((detail.research_target.target_price / (detail.research_target.target_price / (1 + m.upside_ext_raw / 100))) - 1) * 100).toFixed(1)
    : null;

  return (
    <div className="fade-in" style={{ maxWidth: 960, margin: '0 auto' }}>
      {/* Back Link */}
      <a href="/upside" style={{
        display: 'inline-flex', alignItems: 'center', gap: '0.5rem',
        color: '#94a3b8', marginBottom: '2rem', fontSize: '0.875rem',
        transition: 'color 0.2s'
      }}>
        <ChevronLeft size={16} /> Voltar ao Ranking Upside 12M
      </a>

      {/* Module Tag */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1.5rem', flexWrap: 'wrap' }}>
        <div style={{
          background: 'rgba(168,85,247,0.15)', border: '1px solid rgba(168,85,247,0.35)',
          color: '#a855f7', padding: '0.3rem 0.75rem', borderRadius: '9999px',
          fontSize: '0.7rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.05em'
        }}>
          ⬆ Upside 12M
        </div>
        <div style={{ fontSize: '0.75rem', color: '#475569' }}>
          Análise independente · v{detail.model_version} · {detail.as_of_date}
        </div>
      </div>

      {/* Hero Card */}
      <div className="card" style={{
        marginBottom: '2rem', padding: '2rem',
        background: `linear-gradient(135deg, ${bucketConfig.bg}, rgba(22,26,35,0.9))`,
        border: `1px solid ${bucketConfig.border}`,
      }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '1.5rem' }}>
          {/* Left: Identity */}
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.5rem' }}>
              <div style={{
                background: 'rgba(168,85,247,0.2)', color: '#a855f7',
                padding: '0.35rem 0.65rem', borderRadius: '0.375rem',
                fontWeight: 800, fontSize: '0.875rem'
              }}>{ticker}</div>
              {company?.sector && (
                <span style={{ fontSize: '0.75rem', color: '#64748b', background: 'rgba(255,255,255,0.04)', padding: '0.2rem 0.5rem', borderRadius: '0.25rem' }}>
                  {company.sector}
                </span>
              )}
            </div>
            <h1 style={{ fontSize: '1.75rem', fontWeight: 800, marginBottom: '0.75rem' }}>
              {company?.company_name ?? ticker}
            </h1>

            {/* Bucket Display */}
            <div style={{
              display: 'inline-flex', alignItems: 'center', gap: '0.5rem',
              background: bucketConfig.bg, color: bucketConfig.color,
              border: `1px solid ${bucketConfig.border}`,
              padding: '0.5rem 1rem', borderRadius: '9999px',
              fontWeight: 700, fontSize: '0.875rem'
            }}>
              {bucketConfig.icon}
              {detail.bucket}
            </div>

            {/* Bucket Explanation */}
            <p style={{ marginTop: '1rem', color: '#94a3b8', fontSize: '0.9rem', maxWidth: 480, lineHeight: 1.6 }}>
              {bucketConfig.description}
            </p>
            {detail.summary && detail.summary !== bucketConfig.description && (
              <p style={{ marginTop: '0.5rem', color: '#cbd5e1', fontSize: '0.875rem', fontStyle: 'italic', maxWidth: 480 }}>
                "{detail.summary}"
              </p>
            )}
          </div>

          {/* Right: Score Circle + Rating */}
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '1rem' }}>
            <div style={{
              width: 110, height: 110, borderRadius: '50%',
              border: `4px solid ${bucketConfig.color}`,
              background: `${bucketConfig.color}15`,
              display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center'
            }}>
              <span style={{ fontSize: '1.875rem', fontWeight: 800, color: bucketConfig.color, lineHeight: 1 }}>
                {detail.final_score.toFixed(0)}
              </span>
              <span style={{ fontSize: '0.55rem', color: '#64748b', textTransform: 'uppercase', letterSpacing: '0.05em', marginTop: '0.25rem' }}>
                Score 12M
              </span>
            </div>
            <div style={{
              background: detail.rating_class.includes('Compra Forte') ? 'rgba(168,85,247,0.2)'
                : detail.rating_class === 'Compra' ? 'rgba(16,185,129,0.2)'
                  : detail.rating_class === 'Alerta' ? 'rgba(239,68,68,0.2)'
                    : 'rgba(245,158,11,0.2)',
              color: detail.rating_class.includes('Compra Forte') ? '#a855f7'
                : detail.rating_class === 'Compra' ? '#10b981'
                  : detail.rating_class === 'Alerta' ? '#ef4444'
                    : '#f59e0b',
              padding: '0.4rem 1rem', borderRadius: '9999px',
              fontWeight: 800, textTransform: 'uppercase', fontSize: '0.75rem', letterSpacing: '0.05em'
            }}>
              {detail.rating_class}
            </div>
          </div>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 320px', gap: '2rem', alignItems: 'start' }}>
        {/* Score Blocks */}
        <div>
          <h2 style={{ fontWeight: 700, marginBottom: '1.25rem', color: '#94a3b8', textTransform: 'uppercase', letterSpacing: '0.05em', fontSize: '0.75rem' }}>
            Decomposição do Score 12M
          </h2>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
            {scoreBlocks.map(b => <ScoreBlockBar key={b.label} block={b} />)}
          </div>

          {/* Penalties */}
          {m.penalties_raw > 0 && (
            <div style={{
              marginTop: '0.75rem', background: 'rgba(239,68,68,0.06)',
              border: '1px solid rgba(239,68,68,0.25)', borderRadius: '0.75rem', padding: '1.25rem',
              display: 'flex', justifyContent: 'space-between', alignItems: 'center'
            }}>
              <div>
                <div style={{ fontWeight: 700, color: '#ef4444', fontSize: '0.875rem' }}>⚠ Penalidades</div>
                <div style={{ fontSize: '0.7rem', color: '#64748b', marginTop: '0.2rem' }}>
                  Fatores de risco identificados pelo modelo (dívida, deterioração, binários)
                </div>
              </div>
              <div style={{ fontWeight: 800, fontSize: '1.5rem', color: '#ef4444' }}>
                −{m.penalties_raw.toFixed(0)}
              </div>
            </div>
          )}

          {/* Final Calc */}
          <div style={{
            marginTop: '1rem', padding: '1.25rem',
            background: 'rgba(255,255,255,0.03)', borderRadius: '0.75rem',
            display: 'flex', justifyContent: 'space-between', alignItems: 'center',
            borderTop: `2px solid ${bucketConfig.color}30`
          }}>
            <span style={{ color: '#94a3b8', fontSize: '0.875rem', fontWeight: 600 }}>Score Final (ponderado − penalidades)</span>
            <span style={{ fontWeight: 800, fontSize: '1.75rem', color: bucketConfig.color }}>
              {detail.final_score.toFixed(2)}
            </span>
          </div>
        </div>

        {/* Sidebar: Research Target + Context */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          {/* Research Target Card */}
          <div className="card">
            <h3 style={{ fontSize: '0.75rem', fontWeight: 700, color: '#64748b', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '1.25rem' }}>
              Research Target
            </h3>
            {hasTarget ? (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end' }}>
                  <div>
                    <div style={{ color: '#64748b', fontSize: '0.7rem', marginBottom: '0.25rem' }}>Preço Alvo</div>
                    <div style={{ fontWeight: 800, fontSize: '1.5rem', color: '#10b981' }}>
                      R$ {detail.research_target.target_price.toFixed(2)}
                    </div>
                  </div>
                  <div style={{ textAlign: 'right' }}>
                    <div style={{ color: '#64748b', fontSize: '0.7rem', marginBottom: '0.25rem' }}>Upside</div>
                    <div style={{ fontWeight: 800, fontSize: '1.25rem', color: '#a855f7' }}>
                      {(m.upside_ext_raw / 2).toFixed(1)}%
                    </div>
                  </div>
                </div>
                <div style={{ background: 'rgba(255,255,255,0.03)', borderRadius: '0.5rem', padding: '0.75rem', display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem' }}>
                    <span style={{ color: '#64748b' }}>Fonte</span>
                    <span style={{ fontWeight: 600 }}>{detail.research_target.source_name}</span>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem' }}>
                    <span style={{ color: '#64748b' }}>Recomendação</span>
                    <span style={{ fontWeight: 600, color: detail.research_target.rating_recommendation === 'Buy' ? '#10b981' : '#f59e0b' }}>
                      {detail.research_target.rating_recommendation}
                    </span>
                  </div>
                </div>
                <div style={{ fontSize: '0.7rem', color: '#475569', lineHeight: 1.5 }}>
                  * Upside calculado sobre preço capturado no momento do research, não o preço atual.
                </div>
              </div>
            ) : (
              <p style={{ color: '#64748b', fontSize: '0.875rem' }}>Sem target externo cadastrado.</p>
            )}
          </div>

          {/* Disclamer / Context Box */}
          <div style={{
            background: 'rgba(168,85,247,0.06)', border: '1px solid rgba(168,85,247,0.2)',
            borderRadius: '0.75rem', padding: '1.25rem'
          }}>
            <div style={{ fontWeight: 700, color: '#a855f7', fontSize: '0.75rem', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '0.75rem' }}>
              Sobre este Módulo
            </div>
            <p style={{ fontSize: '0.8rem', color: '#64748b', lineHeight: 1.6 }}>
              Este score é independente do Ranking Base de Qualidade. Ele foca em 
              potencial de valorização e não substitui análise individual do ativo.
            </p>
            <div style={{ marginTop: '1rem', paddingTop: '0.75rem', borderTop: '1px solid rgba(255,255,255,0.05)' }}>
              <a href="/ranking" style={{ fontSize: '0.8rem', color: '#64748b', display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                Ver Ranking Base <ArrowUpRight size={12} />
              </a>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
