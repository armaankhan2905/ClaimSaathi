import { Component, type ErrorInfo, type ReactNode } from "react";
import { useI18n } from "../i18n/I18nProvider";
import { Icon } from "./Icon";

function Fallback() {
  const { t } = useI18n();
  return (
    <div className="panel flex flex-wrap items-start gap-4" role="alert">
      <span className="grid h-11 w-11 flex-none place-items-center rounded-xl bg-surface-2 text-bad">
        <Icon name="alert" className="h-[22px] w-[22px]" />
      </span>
      <div className="min-w-[220px] flex-1">
        <h2 className="text-xl">{t("err_page_title")}</h2>
        <p className="muted mt-1.5">{t("err_page_text")}</p>
      </div>
      <button type="button" className="btn primary" onClick={() => window.location.reload()}>
        {t("err_page_reload")}
      </button>
    </div>
  );
}

/** Keeps one broken page (or a page that failed to download after an update) from blanking the whole app. */
export class ErrorBoundary extends Component<{ children: ReactNode }, { failed: boolean }> {
  state = { failed: false };

  static getDerivedStateFromError() {
    return { failed: true };
  }

  componentDidCatch(error: Error, info: ErrorInfo) {
    console.error("Page error", error, info.componentStack);
  }

  render() {
    return this.state.failed ? <Fallback /> : this.props.children;
  }
}
