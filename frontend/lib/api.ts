const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function getTop20() {
  const res = await fetch(`${API_URL}/rankings/top20`, { cache: "no-store" });
  if (!res.ok) throw new Error("Falha ao carregar top20");
  return res.json();
}

export async function getScore(ticker: string) {
  const res = await fetch(`${API_URL}/scores/${ticker}`, { cache: "no-store" });
  if (!res.ok) throw new Error("Falha ao carregar score");
  return res.json();
}
