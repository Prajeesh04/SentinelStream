import React from "react";
import { createBrowserRouter, Navigate } from "react-router-dom";
import { AppLayout } from "./ui/AppLayout";
import { SignInPage } from "./views/SignInPage";
import { SignUpPage } from "./views/SignUpPage";
import { DashboardPage } from "./views/DashboardPage";
import { RequireAuth } from "./views/RequireAuth";

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
  { path: "*", element: <Navigate to="/" replace /> },
]);

