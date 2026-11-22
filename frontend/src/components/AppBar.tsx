import type { ReactNode } from "react";
import { Link, NavLink } from "react-router";
import { useI18n } from "../i18n/I18nProvider";
import { LANG_OPTIONS, type StringKey } from "../i18n/strings";
import { useTheme } from "../lib/theme";

const NAV: { to: string; key: StringKey }[] = [
  { to: "/", key: "nav_home" },
  { to: "/policy", key: "nav_policy" },
  { to: "/rejection", key: "nav_rej" },
  { to: "/complaint", key: "nav_comp" },
];

/** The brand mark: a round rubber-stamp seal with a tick. */
export function StampMark({ className = "h-[34px] w-[34px]" }: { className?: string }) {
  return (
    <svg viewBox="0 0 34 34" className={className} aria-hidden="true">
      <circle cx="17" cy="17" r="15" fill="none" stroke="var(--stamp)" strokeWidth="2.5" />
      <circle cx="17" cy="17" r="11" fill="none" stroke="var(--stamp)" strokeWidth="1" />
      <path d="M11 17.5l4 4 8-9" fill="none" stroke="var(--stamp)" strokeWidth="2.6" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}

function ThemeIcon({ dark }: { dark: boolean }) {
  return dark ? (
    <svg viewBox="0 0 24 24" className="h-4 w-4" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" aria-hidden="true">
      <circle cx="12" cy="12" r="4.2" />
      <path d="M12 2.5v2M12 19.5v2M4.6 4.6l1.4 1.4M18 18l1.4 1.4M2.5 12h2M19.5 12h2M4.6 19.4 6 18M18 6l1.4-1.4" />
    </svg>
  ) : (
    <svg viewBox="0 0 24 24" className="h-4 w-4" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <path d="M20 14.5A8 8 0 1 1 9.5 4a6.5 6.5 0 0 0 10.5 10.5Z" />
    </svg>
  );
}

export function AppBar({ rightSlot }: { rightSlot?: ReactNode }) {
  const { t, lang, setLang } = useI18n();
  const { theme, toggle } = useTheme();
  const dark = theme === "dark";

  return (
    <header className="sticky top-0 z-20 border-b-2 border-rule bg-surface-2">
      <div className="wrap flex flex-wrap items-center gap-x-6 gap-y-2 py-3 lg:flex-nowrap">
        <Link to="/" className="flex items-center gap-2.5 text-fg no-underline" aria-label={`${t("brand")} – ${t("nav_home")}`}>
          <StampMark />
          <b className="font-display text-[23px] font-black tracking-[.02em] uppercase [font-stretch:80%]">{t("brand")}</b>
        </Link>

        <nav
          aria-label={t("nav_main")}
          className="order-3 -mx-1 flex min-w-0 basis-full gap-1 overflow-x-auto [scrollbar-width:none] lg:order-none lg:mx-0 lg:flex-1 lg:basis-auto"
        >
          {NAV.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.to === "/"}
              className={({ isActive }) =>
                `whitespace-nowrap border-[1.5px] px-3 py-1.5 font-mono text-[15px] no-underline transition-colors ${
                  isActive ? "border-rule bg-surface font-bold text-fg" : "border-transparent text-fg/80 hover:border-line hover:bg-surface/60 hover:text-fg"
                }`
              }
            >
              {t(item.key)}
            </NavLink>
          ))}
        </nav>

        <div className="ml-auto flex items-center gap-2.5 lg:ml-0">
          <div className="seg" role="group" aria-label={t("lang_label")}>
            {LANG_OPTIONS.map((o) => (
              <button key={o.code} type="button" aria-pressed={lang === o.code} onClick={() => setLang(o.code)}>
                {o.label}
              </button>
            ))}
          </div>
          <button
            type="button"
            className="grid h-[33px] w-[33px] place-items-center border-[1.5px] border-rule bg-surface text-fg transition-colors hover:bg-surface-2"
            onClick={toggle}
            aria-pressed={dark}
            aria-label={dark ? t("theme_to_light") : t("theme_to_dark")}
            title={dark ? t("theme_to_light") : t("theme_to_dark")}
          >
            <ThemeIcon dark={dark} />
          </button>
          {rightSlot}
        </div>
      </div>
    </header>
  );
}
