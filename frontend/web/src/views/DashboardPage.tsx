import React, { useEffect, useMemo, useState } from "react";
import { useAuth } from "../state/auth";
import { fetchDashboardStats, fetchTransactions, submitTransaction, type DashboardStats, type TransactionRow } from "../lib/api";
import { Card, PrimaryButton } from "../ui/Primitives";

function formatRisk(v: number | null | undefined) {
  if (v == null) return "—";
  return v.toFixed(3);
}

export function DashboardPage() {
  const { accessToken } = useAuth();
  const token = accessToken!;
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [txns, setTxns] = useState<TransactionRow[] | null>(null);
  const [err, setErr] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  const [merchantName, setMerchantName] = useState("Test Shop");
  const [amount, setAmount] = useState("150.00");
  const [merchantCategory, setMerchantCategory] = useState("");
  const [cardLastFour, setCardLastFour] = useState("");

  const parsedAmount = useMemo(() => Number(amount), [amount]);

  async function refresh() {
    setErr(null);
    try {
      const [s, t] = await Promise.all([fetchDashboardStats(token), fetchTransactions(token, 25)]);
      setStats(s);
      setTxns(t);
    } catch (e) {
      setErr(e instanceof Error ? e.message : "Failed to load dashboard");
    }
  }

  useEffect(() => {
    void refresh();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  async function onSubmitTxn(e: React.FormEvent) {
    e.preventDefault();
    setSubmitting(true);
    setErr(null);
    try {
      if (!Number.isFinite(parsedAmount) || parsedAmount <= 0) throw new Error("Amount must be > 0.");
      if (!merchantName.trim()) throw new Error("Merchant name is required.");
      if (cardLastFour && !/^\d{4}$/.test(cardLastFour)) throw new Error("Card last four must be 4 digits.");

      await submitTransaction(token, {
        amount: parsedAmount,
        merchant_name: merchantName.trim(),
        merchant_category: merchantCategory.trim() || undefined,
        card_last_four: cardLastFour.trim() || undefined,
      });

      await refresh();
    } catch (e) {
      setErr(e instanceof Error ? e.message : "Transaction failed");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="grid">
      <div className="col">
        <Card>
          <div className="rowBetween">
            <div>
              <div className="h2">System overview</div>
              <div className="muted">Your transaction metrics (signed-in account only).</div>
            </div>
            <button className="ghostBtn" onClick={() => void refresh()}>
              Refresh
            </button>
          </div>

          {err ? <div className="error" style={{ marginTop: 12 }}>{err}</div> : null}

          <div className="statsGrid">
            <div className="stat">
              <div className="statLabel">Total</div>
              <div className="statValue">{stats?.total_transactions ?? "—"}</div>
            </div>
            <div className="stat">
              <div className="statLabel">Approved</div>
              <div className="statValue ok">{stats?.approved ?? "—"}</div>
            </div>
            <div className="stat">
              <div className="statLabel">Flagged</div>
              <div className="statValue warn">{stats?.flagged ?? "—"}</div>
            </div>
            <div className="stat">
              <div className="statLabel">Declined</div>
              <div className="statValue bad">{stats?.declined ?? "—"}</div>
            </div>
            <div className="stat span2">
              <div className="statLabel">Average risk score</div>
              <div className="statValue">{stats ? stats.avg_risk_score.toFixed(3) : "—"}</div>
            </div>
          </div>
        </Card>

        <Card>
          <div className="h2">Submit a transaction</div>
          <div className="muted">Uses JWT auth + Idempotency-Key, matching your backend flow.</div>

          <form onSubmit={onSubmitTxn} className="formGrid">
            <label className="field">
              <div className="fieldLabel">Merchant name</div>
              <input className="input" value={merchantName} onChange={(e) => setMerchantName(e.target.value)} required />
            </label>

            <label className="field">
              <div className="fieldLabel">Amount (USD)</div>
              <input className="input" inputMode="decimal" value={amount} onChange={(e) => setAmount(e.target.value)} required />
            </label>

            <label className="field">
              <div className="fieldLabel">Merchant category (optional)</div>
              <input className="input" value={merchantCategory} onChange={(e) => setMerchantCategory(e.target.value)} />
            </label>

            <label className="field">
              <div className="fieldLabel">Card last four (optional)</div>
              <input className="input" inputMode="numeric" value={cardLastFour} onChange={(e) => setCardLastFour(e.target.value)} placeholder="1234" />
            </label>

            <div className="row">
              <PrimaryButton type="submit" disabled={submitting}>
                {submitting ? "Submitting…" : "Submit"}
              </PrimaryButton>
              <button
                type="button"
                className="ghostBtn"
                onClick={() => {
                  setMerchantName("Test Shop");
                  setAmount("150.00");
                  setMerchantCategory("");
                  setCardLastFour("");
                }}
              >
                Reset
              </button>
            </div>
          </form>
        </Card>
      </div>

      <div className="col">
        <Card>
          <div className="h2">Recent transactions</div>
          <div className="muted">Last 25 transactions for the signed-in user.</div>

          <div className="tableWrap">
            <table className="table">
              <thead>
                <tr>
                  <th>Status</th>
                  <th>Merchant</th>
                  <th>Amount</th>
                  <th>Risk</th>
                </tr>
              </thead>
              <tbody>
                {(txns ?? []).map((t) => (
                  <tr key={t.id}>
                    <td>
                      <span className={`pill ${t.status.toLowerCase()}`}>{t.status}</span>
                    </td>
                    <td className="mono">{t.merchant_name}</td>
                    <td className="mono">
                      {t.amount} {t.currency}
                    </td>
                    <td className="mono">{formatRisk(t.risk_score as any)}</td>
                  </tr>
                ))}
                {!txns ? (
                  <tr>
                    <td colSpan={4} className="muted">
                      Loading…
                    </td>
                  </tr>
                ) : txns.length === 0 ? (
                  <tr>
                    <td colSpan={4} className="muted">
                      No transactions yet.
                    </td>
                  </tr>
                ) : null}
              </tbody>
            </table>
          </div>
        </Card>
      </div>
    </div>
  );
}

