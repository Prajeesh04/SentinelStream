import React, { useEffect, useState } from "react";
import { fetchAdminStats, fetchAdminTransactions, TransactionRow } from "../lib/api";
import { useAuth } from "../state/auth";
import { useNavigate } from "react-router-dom";

export function AdminDashboard() {
  const { accessToken: token, signOut } = useAuth();
  const navigate = useNavigate();
  
  const [stats, setStats] = useState<any>(null);
  const [txns, setTxns] = useState<TransactionRow[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!token) return;
    Promise.all([
      fetchAdminStats(token),
      fetchAdminTransactions(token)
    ]).then(([s, t]) => {
      setStats(s);
      setTxns(t);
      setLoading(false);
    }).catch((err) => {
      console.error(err);
      if (err.message.includes("403") || err.message.includes("401")) {
        signOut();
        navigate("/admin/login");
      }
    });
  }, [token, navigate, signOut]);

  const handleLogout = () => {
    signOut();
    navigate("/admin/login");
  };

  if (loading) return <div style={{ color: "#fff", padding: "40px", background: "#0A0B10", minHeight: "100vh" }}>Loading Telemetry...</div>;

  return (
    <div style={{ background: "#0A0B10", color: "#F0EDE5", minHeight: "100vh", padding: "24px" }}>
      <header style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "32px", borderBottom: "1px solid rgba(255,255,255,0.1)", paddingBottom: "16px" }}>
        <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
          <div className="logoMark" style={{ background: "linear-gradient(135deg, #3B82F6, #111)", width: "32px", height: "32px" }}></div>
          <h1 className="h1" style={{ margin: 0, color: "#fff", fontSize: "24px" }}>Sentinel Command</h1>
          <div style={{ display: "flex", alignItems: "center", gap: "6px", marginLeft: "16px", padding: "4px 12px", background: "rgba(16, 185, 129, 0.1)", borderRadius: "99px", color: "#10B981", fontSize: "12px" }}>
            <div style={{ width: "8px", height: "8px", background: "#10B981", borderRadius: "50%", boxShadow: "0 0 8px #10B981" }}></div>
            System Online
          </div>
        </div>
        <button className="ghostBtn" onClick={handleLogout} style={{ color: "#fff", borderColor: "rgba(255,255,255,0.2)", background: "transparent" }}>Disconnect</button>
      </header>

      <div className="statsGrid" style={{ marginBottom: "32px" }}>
        <div className="stat" style={{ background: "rgba(20,22,30,0.8)", borderColor: "rgba(255,255,255,0.1)", backdropFilter: "blur(12px)" }}>
          <div className="statLabel" style={{ color: "rgba(255,255,255,0.5)" }}>Total Users</div>
          <div className="statValue" style={{ color: "#fff" }}>{stats?.total_users || 0}</div>
        </div>
        <div className="stat" style={{ background: "rgba(20,22,30,0.8)", borderColor: "rgba(255,255,255,0.1)", backdropFilter: "blur(12px)" }}>
          <div className="statLabel" style={{ color: "rgba(255,255,255,0.5)" }}>Total Transactions</div>
          <div className="statValue" style={{ color: "#3B82F6" }}>{stats?.total_transactions || 0}</div>
        </div>
        <div className="stat" style={{ background: "rgba(20,22,30,0.8)", borderColor: "rgba(255,255,255,0.1)", backdropFilter: "blur(12px)" }}>
          <div className="statLabel" style={{ color: "rgba(255,255,255,0.5)" }}>Rejection Rate</div>
          <div className={`statValue ${stats?.rejection_rate_percent > 15 ? 'bad' : 'warn'}`}>
            {stats?.rejection_rate_percent || 0}%
          </div>
        </div>
        <div className="stat" style={{ background: "rgba(20,22,30,0.8)", borderColor: "rgba(255,255,255,0.1)", backdropFilter: "blur(12px)" }}>
          <div className="statLabel" style={{ color: "rgba(255,255,255,0.5)" }}>Engine Latency</div>
          <div className="statValue ok">~112ms</div>
        </div>
      </div>

      <h2 className="h2" style={{ color: "#fff", marginBottom: "16px" }}>Global Transaction Feed</h2>
      <div className="tableWrap" style={{ background: "rgba(20,22,30,0.8)", borderColor: "rgba(255,255,255,0.1)", backdropFilter: "blur(12px)" }}>
        <table className="table" style={{ color: "#fff" }}>
          <thead>
            <tr>
              <th style={{ color: "rgba(255,255,255,0.5)", borderColor: "rgba(255,255,255,0.1)" }}>User ID</th>
              <th style={{ color: "rgba(255,255,255,0.5)", borderColor: "rgba(255,255,255,0.1)" }}>Amount</th>
              <th style={{ color: "rgba(255,255,255,0.5)", borderColor: "rgba(255,255,255,0.1)" }}>Merchant</th>
              <th style={{ color: "rgba(255,255,255,0.5)", borderColor: "rgba(255,255,255,0.1)" }}>Status</th>
              <th style={{ color: "rgba(255,255,255,0.5)", borderColor: "rgba(255,255,255,0.1)" }}>Reason / Rule</th>
            </tr>
          </thead>
          <tbody>
            {txns.map(t => (
              <tr key={t.id}>
                <td className="mono" style={{ fontSize: "12px", color: "rgba(255,255,255,0.7)", borderColor: "rgba(255,255,255,0.05)" }}>{t.user_id.split('-')[0]}...</td>
                <td style={{ borderColor: "rgba(255,255,255,0.05)" }}>{t.amount} {t.currency}</td>
                <td style={{ borderColor: "rgba(255,255,255,0.05)" }}>{t.merchant_name}</td>
                <td style={{ borderColor: "rgba(255,255,255,0.05)" }}>
                  <span className={`pill ${t.status.toLowerCase()}`}>{t.status}</span>
                </td>
                <td style={{ borderColor: "rgba(255,255,255,0.05)", fontSize: "12px", color: t.status === "DECLINED" ? "#EF4444" : "rgba(255,255,255,0.6)" }}>
                  {t.decline_reason || t.rule_triggered || "Clean"}
                </td>
              </tr>
            ))}
            {txns.length === 0 && (
              <tr><td colSpan={5} style={{ textAlign: "center", padding: "24px", color: "rgba(255,255,255,0.5)", borderColor: "rgba(255,255,255,0.05)" }}>No transactions in matrix</td></tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
