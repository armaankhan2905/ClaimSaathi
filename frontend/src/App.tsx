import { lazy, Suspense, type ReactNode } from "react";
import { BrowserRouter, Route, Routes } from "react-router";
import { Layout } from "./components/Layout";
import { UserMenu } from "./components/UserMenu";
import { I18nProvider } from "./i18n/I18nProvider";
import { AuthProvider, RequireAuth } from "./lib/auth";
import { ThemeProvider } from "./lib/theme";
import { LoginPage, SignupPage } from "./pages/AuthPages";
import { Home } from "./pages/Home";

// The bigger pages download only when opened, so the first visit loads faster.
const PolicyInsights = lazy(() => import("./pages/PolicyInsights").then((m) => ({ default: m.PolicyInsights })));
const RejectionCheck = lazy(() => import("./pages/RejectionCheck").then((m) => ({ default: m.RejectionCheck })));
const ComplaintPage = lazy(() => import("./pages/Complaint").then((m) => ({ default: m.ComplaintPage })));

function Page({ children }: { children: ReactNode }) {
  return (
    <RequireAuth>
      <Suspense fallback={<div className="h-40 animate-pulse rounded-2xl bg-surface-2" aria-busy="true" />}>{children}</Suspense>
    </RequireAuth>
  );
}

export default function App() {
  return (
    <ThemeProvider>
      <I18nProvider>
        <AuthProvider>
          <BrowserRouter>
            <Routes>
              <Route element={<Layout barRight={<UserMenu />} />}>
                <Route path="login" element={<LoginPage />} />
                <Route path="signup" element={<SignupPage />} />
                <Route index element={<RequireAuth><Home /></RequireAuth>} />
                <Route path="policy" element={<Page><PolicyInsights /></Page>} />
                <Route path="rejection" element={<Page><RejectionCheck /></Page>} />
                <Route path="complaint" element={<Page><ComplaintPage /></Page>} />
                <Route path="*" element={<RequireAuth><Home /></RequireAuth>} />
              </Route>
            </Routes>
          </BrowserRouter>
        </AuthProvider>
      </I18nProvider>
    </ThemeProvider>
  );
}
