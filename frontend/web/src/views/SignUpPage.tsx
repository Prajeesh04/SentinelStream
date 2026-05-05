import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { signUp } from "../lib/api";
import { useAuth } from "../state/auth";
import { Card, Field, PrimaryButton } from "../ui/Primitives";

export function SignUpPage() {
  const { setAccessToken } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    const p = password;
    if (p.length < 8) {
      setError("Password must be at least 8 characters.");
      return;
    }
    if (p !== confirm) {
      setError("Passwords do not match.");
      return;
    }
    setLoading(true);
    try {
      const tok = await signUp(email.trim(), password, confirm);
      setAccessToken(tok.access_token, { persist: true });
      navigate("/", { replace: true });
    } catch (err) {
      setError(err instanceof Error ? err.message : "Sign-up failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="authShell">
      <Card>
        <h1 className="h1">Create account</h1>
        <p className="muted">A secure account to access transaction guard tools.</p>

        <form onSubmit={onSubmit} className="stack">
          <Field label="Email" type="email" value={email} onChange={setEmail} autoComplete="email" />
          <Field
            label="Password"
            type="password"
            value={password}
            onChange={setPassword}
            autoComplete="new-password"
            hint="Minimum 8 characters"
          />
          <Field
            label="Confirm password"
            type="password"
            value={confirm}
            onChange={setConfirm}
            autoComplete="new-password"
          />
          {error ? <div className="error">{error}</div> : null}
          <PrimaryButton type="submit" disabled={loading}>
            {loading ? "Creating…" : "Create account"}
          </PrimaryButton>
        </form>

        <div className="footerRow">
          <span className="muted">Already have an account?</span> <Link to="/signin">Sign in</Link>
        </div>
      </Card>
    </div>
  );
}

