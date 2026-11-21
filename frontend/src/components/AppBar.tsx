import type { ReactNode } from "react";
import { Link, NavLink } from "react-router";
import { useI18n } from "../i18n/I18nProvider";
import { LANG_OPTIONS, type StringKey } from "../i18n/strings";
import { useTheme } from "../lib/theme";
import { Icon } from "./Icon";

const NAV: { to: string; key: StringKey }[] = [
  { to: "/", key: "nav_home" },
  { to: "/policy", key: "nav_policy" },
  { to: "/rejection", key: "nav_rej" },
  { to: "/complaint", key: "nav_comp" },
];

export function AppBar({ rightSlot }: { rightSlot?: ReactNode }) {
  const { t, lang, setLang } = useI18n();
  const { theme, toggle } = useTheme();
  const dark = theme === "dark";

  return (
    <header className="sticky top-0 z-20 border-b border-line bg-bg">
      <div className="wrap flex flex-wrap items-center gap-x-[18px] gap-y-2.5 py-3 md:flex-nowrap">
        <Link to="/" className="flex items-center gap-2.5 text-fg no-underline" aria-label={`${t("brand")} – ${t("nav_home")}`}>
          <span className="grid h-[30px] w-[30px] place-items-center rounded-[9px] bg-accent text-accent-ink">
            <Icon name="shield" className="h-[18px] w-[18px]" />
          </span>
          <b className="font-display text-[19px] font-semibold tracking-[.02em]">{t("brand")}</b>
        </Link>

        <nav
          aria-label={t("nav_main")}
          className="order-3 flex min-w-0 basis-full gap-1 overflow-x-auto [scrollbar-width:none] md:order-none md:flex-1 md:basis-auto"
        >
          {NAV.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.to === "/"}
              className={({ isActive }) =>
                `whitespace-nowrap rounded-[9px] px-3 py-2 text-sm font-medium no-underline transition-colors ${
                  isActive ? "bg-accent text-accent-ink" : "text-muted hover:bg-surface-2 hover:text-fg"
                }`
              }
            >
              {t(item.key)}
            </NavLink>
          ))}
        </nav>

        <div className="ml-auto flex items-center gap-2.5 md:ml-0">
          <button
            type="button"
            className="btn px-2.5 py-1.5 text-[12.5px]"
            onClick={toggle}
            aria-pressed={dark}
            aria-label={dark ? t("theme_to_light") : t("theme_to_dark")}
            title={dark ? t("theme_to_light") : t("theme_to_dark")}
          >
            <span aria-hidden="true" className="text-base leading-none">
              {dark ? "☀" : "☾"}
            </span>
            <span className="hidden sm:inline md:hidden xl:inline">{dark ? t("theme_light") : t("theme_dark")}</span>
          </button>
          <div className="seg" role="group" aria-label={t("lang_label")}>
            {LANG_OPTIONS.map((o) => (
              <button key={o.code} type="button" aria-pressed={lang === o.code} onClick={() => setLang(o.code)}>
                {o.label}
              </button>
            ))}
          </div>
          {rightSlot}
        </div>
      </div>
    </header>
  );
}
