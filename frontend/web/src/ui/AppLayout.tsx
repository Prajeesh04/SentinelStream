import React from "react";
import { Outlet, useNavigate } from "react-router-dom";
import { useAuth } from "../state/auth";

export function AppLayout() {
  const { signOut } = useAuth();
  const navigate = useNavigate();

  return (
    <div className="appShell">
      <header className="topbar">
        <div className="brand">
          <div className="logoMark" aria-hidden />
          <div>
            <div className="brandName">SentinelStream</div>
            <div className="brandSub">High-Throughput Transaction Guard</div>
          </div>
        </div>
        <div className="spacer" />
        <button
          className="ghostBtn"
          onClick={() => {
            signOut();
            navigate("/signin", { replace: true });
          }}
        >
          Sign out
        </button>
      </header>
      <main className="main">
        <Outlet />
      </main>
    </div>
  );
}

