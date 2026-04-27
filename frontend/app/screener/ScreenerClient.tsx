'use client';

import React, { useMemo, useState } from 'react';
import { Search } from 'lucide-react';

type Company = {
  id: string;
  ticker: string;
  company_name: string;
  sector?: string | null;
  listing_segment?: string | null;
};

export default function ScreenerClient({ companies }: { companies: Company[] }) {
  const [filter, setFilter] = useState('');

  const filtered = useMemo(() => {
    const query = filter.trim().toLowerCase();
    if (!query) return companies;

    return companies.filter((company) =>
      company.ticker.toLowerCase().includes(query) ||
      company.company_name.toLowerCase().includes(query)
    );
  }, [companies, filter]);

  return (
    <>
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
            {filtered.map((company) => (
              <tr key={company.id}>
                <td><strong>{company.ticker}</strong></td>
                <td>{company.company_name}</td>
                <td>{company.sector ?? '-'}</td>
                <td>{company.listing_segment ?? '-'}</td>
                <td>
                  <a href={`/companies/${company.ticker}`} className="btn-view">
                    Ver Análise
                  </a>
                </td>
              </tr>
            ))}
            {filtered.length === 0 && (
              <tr>
                <td colSpan={5} style={{ textAlign: 'center', padding: '3rem', color: 'var(--muted)' }}>
                  Nenhum ativo encontrado.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </>
  );
}
