import React, { createContext, useContext, useMemo, useState } from "react";

type AuthState = {
  accessToken: string | null;
};

type AuthContextValue = AuthState & {
  setAccessToken: (token: string | null, opts?: { persist?: boolean }) => void;
  signOut: () => void;
};

const STORAGE_KEY = "sentinelstream.accessToken";

const AuthContext = createContext<AuthContextValue | null>(null);

function loadInitialToken(): string | null {
  try {
    return sessionStorage.getItem(STORAGE_KEY);
  } catch {
    return null;
  }
}

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [accessToken, _setAccessToken] = useState<string | null>(() => loadInitialToken());

  const value = useMemo<AuthContextValue>(() => {
    return {
      accessToken,
      setAccessToken: (token, opts) => {
        _setAccessToken(token);
        const persist = opts?.persist ?? true;
        if (!persist) return;
        try {
          if (token) sessionStorage.setItem(STORAGE_KEY, token);
          else sessionStorage.removeItem(STORAGE_KEY);
        } catch {
          // ignore
        }
      },
      signOut: () => {
        _setAccessToken(null);
        try {
          sessionStorage.removeItem(STORAGE_KEY);
        } catch {
          // ignore
        }
      },
    };
  }, [accessToken]);

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}

