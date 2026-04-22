'use client';

import React, { useState, useEffect } from 'react';
import './options.css';

function SuggestionCard({ s, onAccept }: { s: any, onAccept: (id: string, shares: number) => void }) {
    const [shares, setShares] = useState(s.contracts * 100 || 100);
    const premiumUnit = s.premium || 0;
    const totalPremium = (shares * premiumUnit).toFixed(2);

    return (
        <div className="suggestion-card">
            <div className="card-header">
                <span className="card-ticker">{s.ticker}</span>
                <div className="overlay-score-circle" title="Overlay Score">
                    {Math.round(s.overlay_score)}
                </div>
            </div>
            <div className="card-body">
                <p style={{fontSize: '1.2rem'}}>Opção: <strong>{s.option_display_code}</strong></p>
                <p style={{fontSize: '0.8rem', color: 'var(--muted)', marginTop: '-8px', marginBottom: '12px'}}>
                    Ref: {s.option_symbol_raw}
                </p>
                <div className="card-metrics-grid">
                    <p>Strike: <strong>R$ {s.strike?.toFixed(2) || '---'}</strong></p>
                    <p>Vencimento: <strong>{s.expiration_date ? new Date(s.expiration_date + 'T00:00:00').toLocaleDateString('pt-BR') : 'Vencimento indisponível'}</strong></p>
                    <p>DTE: <strong style={{color: s.dte != null && s.dte <= 21 ? 'var(--warning)' : 'inherit'}}>{s.dte != null ? `${s.dte} dias` : 'DTE indisponível'}</strong></p>
                    <p>Prêmio Est.: <strong>R$ {s.premium?.toFixed(2) || '---'}</strong></p>
                    <p>Delta: <strong>{s.delta?.toFixed(2) || '---'}</strong></p>
                </div>
                <div style={{marginTop: '12px', padding: '12px', background: 'var(--bg)', borderRadius: '8px', border: '1px solid var(--border)'}}>
                    <label style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px', fontSize: '0.9rem'}}>
                        Quantidade (Ações):
                        <input 
                            type="number" 
                            value={shares} 
                            onChange={(e) => setShares(Number(e.target.value))}
                            step="100"
                            min="100"
                            style={{width: '90px', padding: '4px 8px', borderRadius: '4px', border: '1px solid var(--border)', background: 'var(--bg-card)', color: 'var(--text)'}}
                        />
                    </label>
                    <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '1.05rem', color: 'var(--primary)', fontWeight: 'bold'}}>
                        <span>Total a Receber:</span>
                        <span>R$ {totalPremium}</span>
                    </div>
                </div>
            </div>
            <div className="suggestion-footer">
                <div style={{color: 'var(--primary)', fontWeight: 600, marginBottom: '4px'}}>
                    🎯 {s.reason_summary}
                </div>
                <div style={{color: 'var(--muted)', marginBottom: '12px'}}>
                    🛡 {s.risk_summary || 'Risco padrão de baixa na ação.'}
                </div>
                <button 
                    className="refresh-btn" 
                    style={{width: '100%', borderColor: 'var(--primary)', color: 'var(--primary)', fontWeight: 'bold'}} 
                    onClick={() => onAccept(s.id, shares)}
                >
                    🚀 Executar Sugestão
                </button>
            </div>
        </div>
    );
}

export default function OptionsPage() {
    const [monitored, setMonitored] = useState<any[]>([]);
    const [suggestions, setSuggestions] = useState<any[]>([]);
    const [activeTab, setActiveTab] = useState<'CC' | 'CSP'>('CC');
    const [loading, setLoading] = useState(true);
    const [lastUpdate, setLastUpdate] = useState<string>('');

    const fetchData = async () => {
        setLoading(true);
        const baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
        try {
            // Parallel fetch
            const [monRes, sugRes] = await Promise.all([
                fetch(`${baseUrl}/api/v1/options/monitor`),
                fetch(`${baseUrl}/api/v1/options/suggestions`)
            ]);

            if (monRes.ok) setMonitored(await monRes.json());
            if (sugRes.ok) setSuggestions(await sugRes.json());
            
            setLastUpdate(new Date().toLocaleTimeString('pt-BR'));
        } catch (e) {
            console.error("Error fetching options data", e);
        } finally {
            setLoading(false);
        }
    };

    const acceptSuggestion = async (id: string, shares: number) => {
        const baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
        try {
            const res = await fetch(`${baseUrl}/api/v1/options/suggestions/${id}/accept?custom_shares=${shares}`, {
                method: 'POST'
            });
            if (res.ok) {
                fetchData();
            } else {
                console.error("Failed to accept suggestion");
            }
        } catch (e) {
            console.error("Network error while accepting suggestion", e);
        }
    };

    useEffect(() => {
        fetchData();
    }, []);

    const filteredSuggestions = suggestions.filter(s => 
        s.suggestion_type === (activeTab === 'CC' ? 'COVERED_CALL' : 'CASH_PUT')
    );

    return (
        <div className="options-container fade-in">
            <header className="options-header">
                <div>
                    <h1>Módulo de Opções</h1>
                    <p className="timestamp">Última atualização: {lastUpdate || '---'}</p>
                </div>
                <button className="refresh-btn" onClick={fetchData} disabled={loading}>
                    {loading ? 'Atualizando...' : '🔄 Atualizar Monitor'}
                </button>
            </header>

            {/* SEÇÃO 1: MONITORAMENTO (ACIMA) */}
            <section className="options-section">
                <h2 className="section-title">📊 Monitoramento de Posições</h2>
                <div className="card">
                    {monitored.length > 0 ? (
                        <table>
                            <thead>
                                <tr>
                                    <th>Ticker</th>
                                    <th>Valor Ativo</th>
                                    <th>Opção</th>
                                    <th>Strike</th>
                                    <th>Prêmio Rec.</th>
                                    <th>Vencimento</th>
                                    <th>DTE</th>
                                    <th>Pnl %</th>
                                    <th>Sinal</th>
                                    <th>Rolagem</th>
                                </tr>
                            </thead>
                            <tbody>
                                {monitored.map((pos) => (
                                    <tr key={pos.position_id}>
                                        <td className="ticker-cell"><strong>{pos.ticker}</strong></td>
                                        <td>R$ {pos.spot_price ? pos.spot_price.toFixed(2) : '---'}</td>
                                        <td>{pos.option_symbol} <span style={{fontSize: '0.7rem', color: 'var(--muted)'}}>{pos.option_type}</span></td>
                                        <td>{pos.strike.toFixed(2)}</td>
                                        <td>R$ {pos.entry_price ? pos.entry_price.toFixed(2) : '---'}</td>
                                        <td>{new Date(pos.expiration_date + 'T00:00:00').toLocaleDateString('pt-BR')}</td>
                                        <td style={{color: pos.current_dte <= 21 ? 'var(--warning)' : 'inherit'}}>
                                            {pos.current_dte}d
                                        </td>
                                        <td style={{color: pos.pnl_pct >= 0 ? 'var(--success)' : 'var(--danger)', fontWeight: 600}}>
                                            {pos.pnl_pct.toFixed(1)}%
                                        </td>
                                        <td>
                                            <span className={`signal-badge signal-${pos.signal.toLowerCase()}`}>
                                                {pos.signal.replace('_', ' ')}
                                            </span>
                                            {pos.should_close && (
                                                <div style={{fontSize: '0.7rem', color: 'var(--danger)', marginTop: '4px'}}>
                                                    ⚠ {pos.close_reason}
                                                </div>
                                            )}
                                        </td>
                                        <td>
                                            {pos.thesis_valid_for_roll ? (
                                                <span className="roll-badge roll-badge-allowed">Liberado para Roll</span>
                                            ) : (
                                                <div>
                                                    <span className={`roll-badge ${pos.should_close ? 'roll-badge-critical' : 'roll-badge-blocked'}`}>
                                                        {pos.should_close ? 'Apenas Fechar' : 'Bloqueado por Tese'}
                                                    </span>
                                                    <span className="block-reason">{pos.roll_block_reason}</span>
                                                </div>
                                            )}
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    ) : (
                        <div style={{padding: '3rem', textAlign: 'center', color: 'var(--muted)'}}>
                            Nenhuma posição aberta encontrada no monitor.
                        </div>
                    )}
                </div>
            </section>

            {/* SEÇÃO 2: SUGESTÕES (ABAIXO) */}
            <section className="options-section">
                <h2 className="section-title">💡 Sugestões de Operações</h2>
                
                <div className="suggestions-tabs">
                    <button 
                        className={`tab-btn ${activeTab === 'CC' ? 'active' : ''}`}
                        onClick={() => setActiveTab('CC')}
                    >
                        Covered Calls
                    </button>
                    <button 
                        className={`tab-btn ${activeTab === 'CSP' ? 'active' : ''}`}
                        onClick={() => setActiveTab('CSP')}
                    >
                        Cash-Secured Puts
                    </button>
                </div>

                <div className="options-grid">
                    {filteredSuggestions.map((s, idx) => (
                        <SuggestionCard key={idx} s={s} onAccept={acceptSuggestion} />
                    ))}
                    {filteredSuggestions.length === 0 && (
                        <div style={{gridColumn: '1/-1', padding: '3rem', textAlign: 'center', color: 'var(--muted)', background: 'var(--bg-card)', borderRadius: '12px'}}>
                            Nenhuma sugestão encontrada para os filtros atuais.
                        </div>
                    )}
                </div>
            </section>
        </div>
    );
}
