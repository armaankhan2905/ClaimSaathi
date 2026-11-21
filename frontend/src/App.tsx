import { BrowserRouter, Route, Routes } from "react-router";
import { Layout } from "./components/Layout";
import { I18nProvider } from "./i18n/I18nProvider";
import { ThemeProvider } from "./lib/theme";
import { Home } from "./pages/Home";
import { SectionPlaceholder } from "./pages/SectionPlaceholder";

export default function App() {
  return (
    <ThemeProvider>
      <I18nProvider>
        <BrowserRouter>
          <Routes>
            <Route element={<Layout />}>
              <Route index element={<Home />} />
              <Route path="policy" element={<SectionPlaceholder eyebrow="policy_eyebrow" title="nav_policy" lede="policy_sub" />} />
              <Route path="rejection" element={<SectionPlaceholder eyebrow="rej_eyebrow" title="nav_rej" lede="rej_sub" />} />
              <Route path="complaint" element={<SectionPlaceholder eyebrow="comp_eyebrow" title="nav_comp" lede="comp_sub" />} />
              <Route path="*" element={<Home />} />
            </Route>
          </Routes>
        </BrowserRouter>
      </I18nProvider>
    </ThemeProvider>
  );
}
