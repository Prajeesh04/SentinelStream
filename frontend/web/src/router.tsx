import React from "react";
import { createBrowserRouter, Navigate } from "react-router-dom";
import { AppLayout } from "./ui/AppLayout";
import { SignInPage } from "./views/SignInPage";
import { SignUpPage } from "./views/SignUpPage";
import { DashboardPage } from "./views/DashboardPage";
import { RequireAuth } from "./views/RequireAuth";
import { AdminLogin } from "./views/AdminLogin";
import { AdminDashboard } from "./views/AdminDashboard";

export const router = createBrowserRouter([
  {
    path: "/",
    element: (
      <RequireAuth>
        <AppLayout />
      </RequireAuth>
    ),
    children: [{ index: true, element: <DashboardPage /> }],
  },
  { path: "/signin", element: <SignInPage /> },
  { path: "/signup", element: <SignUpPage /> },
  { path: "/admin/login", element: <AdminLogin /> },
  { 
    path: "/admin", 
    element: (
      <RequireAuth>
        <AdminDashboard />
      </RequireAuth>
    ) 
  },
  { path: "*", element: <Navigate to="/" replace /> },
]);

