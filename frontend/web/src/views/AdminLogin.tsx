import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { signIn } from "../lib/api";
import { useAuth } from "../state/auth";

export function AdminLogin() {
  const navigate = useNavigate();
  const { setAccessToken } = useAuth();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    try {
      const res = await signIn(email, password);
      setAccessToken(res.access_token);
      navigate("/admin");
    } catch (err: any) {
      setError(err.message || "Failed to login as admin");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="authShell" style={{ background: "#0A0B10", color: "#F0EDE5" }}>
      <main className="main" style={{ width: "100%", maxWidth: "420px" }}>
        <div style={{ textAlign: "center", marginBottom: "32px" }}>
          <div className="logoMark" style={{ margin: "0 auto 16px", background: "linear-gradient(135deg, #3B82F6, #111)" }}></div>
          <h1 className="h1" style={{ color: "#fff" }}>Sentinel Command</h1>
          <p className="muted" style={{ color: "rgba(255,255,255,0.6)" }}>Secure Administrator Access</p>
        </div>

        <form className="card" onSubmit={handleSubmit} style={{ background: "rgba(20, 22, 30, 0.8)", border: "1px solid rgba(255,255,255,0.1)", backdropFilter: "blur(12px)" }}>
          {error && <div className="error" style={{ marginBottom: "16px" }}>{error}</div>}
          
          <div className="stack">
            <label className="field">
              <span className="fieldLabel" style={{ color: "#ccc" }}>Admin Email</span>
              <input
                type="email"
                className="input"
                style={{ background: "rgba(0,0,0,0.4)", color: "#fff", borderColor: "rgba(255,255,255,0.2)" }}
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              />
            </label>

            <label className="field">
              <span className="fieldLabel" style={{ color: "#ccc" }}>Security Key</span>
              <input
                type="password"
                className="input"
                style={{ background: "rgba(0,0,0,0.4)", color: "#fff", borderColor: "rgba(255,255,255,0.2)" }}
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
            </label>

            <button type="submit" className="primaryBtn" disabled={loading} style={{ background: "linear-gradient(135deg, #3B82F6, #2563EB)", marginTop: "8px" }}>
              {loading ? "Authenticating..." : "Establish Connection"}
            </button>
          </div>
        </form>
      </main>
    </div>
  );
}
