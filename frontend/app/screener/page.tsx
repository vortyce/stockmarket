'use client';
import React, { useState, useEffect } from 'react';
import { Search, Filter, Info } from 'lucide-react';

export default function ScreenerPage() {
  const [companies, setCompanies] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('');

  useEffect(() => {
    const fetchCompanies = async () => {
      const baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      try {
        const res = await fetch(`${baseUrl}/api/v1/companies`);
        const data = await res.json();
        setCompanies(data);
      } catch (e) {
        console.error('Failed to fetch companies', e);
      } finally {
        setLoading(false);
      }
    };
    fetchCompanies();
  }, []);

  const filtered = companies.filter(c =>
    c.ticker.toLowerCase().includes(filter.toLowerCase()) ||
    c.company_name.toLowerCase().includes(filter.toLowerCase())
  );

  return (
    <div className="screener-container fade-in">
      <header className="page-header">
        <h1>Screener de Ativos</h1>
        <p>Explore toda a base de empresas com filtros fundamentais.</p>
      </header>

      <div className="filter-bar card">
        <div className="search-input">
          <Search size={18} />
          <input
            type="text"
            placeholder="Buscar por ticker ou nome..."
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
          />
        </div>
        <div className="active-filters">
          <span className="results-count">{filtered.length} Resultados</span>
        </div>
      </div>

      <div className="card">
        {loading ? (
          <div className="loading">Carregando base de dados...</div>
        ) : (
          <table>
            <thead>
              <tr>
                <th>Ticker</th>
                <th>Nome</th>
                <th>Setor</th>
                <th>Segmento</th>
                <th>Ações</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((company: any) => (
                <tr key={company.id}>
                  <td><strong>{company.ticker}</strong></td>
                  <td>{company.company_name}</td>
                  <td>{company.sector}</td>
                  <td>{company.listing_segment}</td>
                  <td>
                    <a href={`/companies/${company.ticker}`} className="btn-view">
                      Ver Análise
                    </a>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

    </div>
  );
}
