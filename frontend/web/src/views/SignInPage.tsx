import React, { useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { signIn } from "../lib/api";
import { useAuth } from "../state/auth";
import { Card, Field, PrimaryButton } from "../ui/Primitives";

export function SignInPage() {
  const { setAccessToken } = useAuth();
  const navigate = useNavigate();
  const location = useLocation() as any;
  const [email, setEmail] = useState("test@bank.com");
  const [password, setPassword] = useState("password123");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      const tok = await signIn(email.trim(), password);
      setAccessToken(tok.access_token, { persist: true });
      const next = location?.state?.from ?? "/";
      navigate(next, { replace: true });
    } catch (err) {
      setError(err instanceof Error ? err.message : "Sign-in failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="authShell">
      <Card>
        <h1 className="h1">SentinelStream</h1>
        <p className="muted">Sign in to monitor and protect transactions.</p>

        <form onSubmit={onSubmit} className="stack">
          <Field label="Email" type="email" value={email} onChange={setEmail} autoComplete="email" />
          <Field
            label="Password"
            type="password"
            value={password}
            onChange={setPassword}
            autoComplete="current-password"
          />
          {error ? <div className="error">{error}</div> : null}
          <PrimaryButton type="submit" disabled={loading}>
            {loading ? "Signing in…" : "Sign in"}
          </PrimaryButton>
        </form>

        <div className="footerRow">
          <span className="muted">No account?</span> <Link to="/signup">Create one</Link>
        </div>
      </Card>
    </div>
  );
}

