import { BrowserRouter, Route, Routes } from "react-router";
import { Layout } from "./components/Layout";
import { UserMenu } from "./components/UserMenu";
import { I18nProvider } from "./i18n/I18nProvider";
import { AuthProvider, RequireAuth } from "./lib/auth";
import { ThemeProvider } from "./lib/theme";
import { LoginPage, SignupPage } from "./pages/AuthPages";
import { ComplaintPage } from "./pages/Complaint";
import { Home } from "./pages/Home";
import { PolicyInsights } from "./pages/PolicyInsights";
import { RejectionCheck } from "./pages/RejectionCheck";

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
                <Route path="policy" element={<RequireAuth><PolicyInsights /></RequireAuth>} />
                <Route
                  path="rejection"
                  element={<RequireAuth><RejectionCheck /></RequireAuth>}
                />
                <Route
                  path="complaint"
                  element={<RequireAuth><ComplaintPage /></RequireAuth>}
                />
                <Route path="*" element={<RequireAuth><Home /></RequireAuth>} />
              </Route>
            </Routes>
          </BrowserRouter>
        </AuthProvider>
      </I18nProvider>
    </ThemeProvider>
  );
}
