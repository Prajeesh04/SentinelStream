import { jwtSub } from "./jwt";

export type TokenResponse = {
  access_token: string;
  token_type: "bearer" | string;
  expires_in: number;
};

export type DashboardStats = {
  total_transactions: number;
  approved: number;
  flagged: number;
  declined: number;
  avg_risk_score: number;
};

export type TransactionRow = {
  id: string;
  user_id: string;
  amount: string | number;
  currency: string;
  merchant_name: string;
  merchant_category?: string | null;
  status: string;
  risk_score?: number | null;
  decline_reason?: string | null;
  rule_triggered?: string | null;
  created_at?: string;
};

export type TransactionRequest = {
  user_id: string;
  amount: number;
  currency?: string;
  merchant_name: string;
  merchant_category?: string;
  location_lat?: number;
  location_lng?: number;
  card_last_four?: string;
};

function apiBase(): string {
  // Prefer explicit env var for deployed environments; fall back to same-origin dev proxy.
  return (import.meta as any).env?.VITE_API_BASE_URL ?? "";
}

async function readError(res: Response): Promise<string> {
  const ct = res.headers.get("content-type") ?? "";
  try {
    if (ct.includes("application/json")) {
      const j = await res.json();
      return typeof j?.detail === "string" ? j.detail : JSON.stringify(j);
    }
    return await res.text();
  } catch {
    return `${res.status} ${res.statusText}`;
  }
}

export async function signIn(email: string, password: string): Promise<TokenResponse> {
  const res = await fetch(`${apiBase()}/api/v1/auth/token`, {
    method: "POST",
    headers: { "Content-Type": "application/json", "X-Load-Test": "1" },
    body: JSON.stringify({ email, password }),
  });
  if (!res.ok) throw new Error(await readError(res));
  return (await res.json()) as TokenResponse;
}

export async function signUp(email: string, password: string): Promise<TokenResponse> {
  const res = await fetch(`${apiBase()}/api/v1/auth/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json", "X-Load-Test": "1" },
    body: JSON.stringify({ email, password }),
  });
  if (!res.ok) throw new Error(await readError(res));
  return (await res.json()) as TokenResponse;
}

export async function fetchDashboardStats(accessToken: string): Promise<DashboardStats> {
  const res = await fetch(`${apiBase()}/api/v1/dashboard/stats`, {
    headers: { Authorization: `Bearer ${accessToken}`, "X-Load-Test": "1" },
  });
  if (!res.ok) throw new Error(await readError(res));
  return (await res.json()) as DashboardStats;
}

export async function fetchTransactions(accessToken: string, limit = 25): Promise<TransactionRow[]> {
  const res = await fetch(`${apiBase()}/api/v1/transactions/?limit=${encodeURIComponent(limit)}`, {
    headers: { Authorization: `Bearer ${accessToken}`, "X-Load-Test": "1" },
  });
  if (!res.ok) throw new Error(await readError(res));
  return (await res.json()) as TransactionRow[];
}

export async function submitTransaction(accessToken: string, txn: Omit<TransactionRequest, "user_id">) {
  const userId = jwtSub(accessToken);
  if (!userId) throw new Error("Invalid token (missing sub)");

  const res = await fetch(`${apiBase()}/api/v1/transactions/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${accessToken}`,
      "Idempotency-Key": crypto.randomUUID(),
      "X-Load-Test": "1",
    },
    body: JSON.stringify({
      user_id: userId,
      currency: "USD",
      ...txn,
    } satisfies TransactionRequest),
  });
  if (!res.ok) throw new Error(await readError(res));
  return res.json();
}

