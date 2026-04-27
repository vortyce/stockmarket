import React from 'react';
import ScreenerClient from './ScreenerClient';

async function getCompanies() {
  const baseUrl = process.env.API_URL || process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
  try {
    const res = await fetch(`${baseUrl}/api/v1/companies`, { cache: 'no-store' });
    if (!res.ok) return [];
    return res.json();
  } catch {
    return [];
  }
}

export default async function ScreenerPage() {
  const companies = await getCompanies();

  return (
    <div className="screener-container fade-in">
      <header className="page-header">
        <h1>Screener de Ativos</h1>
        <p>Explore toda a base de empresas com filtros fundamentais.</p>
      </header>

      <ScreenerClient companies={companies} />

    </div>
  );
}
