import { Link } from "react-router";
import { useI18n } from "../i18n/I18nProvider";
import { useAuth } from "../lib/auth";
import { Icon } from "./Icon";

export function UserMenu() {
  const { t } = useI18n();
  const { user, logout } = useAuth();

  if (!user) {
    return (
      <Link to="/login" className="btn px-3 py-1.5 text-[13px]">
        {t("sign_in")}
      </Link>
    );
  }

  const initials = user.full_name
    .split(/\s+/)
    .filter(Boolean)
    .slice(0, 2)
    .map((w) => w[0]!.toUpperCase())
    .join("");

  return (
    <div className="flex items-center gap-2">
      <span
        className="grid h-8 w-8 place-items-center rounded-full bg-surface-2 text-[12px] font-semibold text-accent"
        title={user.full_name}
        aria-label={user.full_name}
      >
        {initials || <Icon name="user" className="h-4 w-4" />}
      </span>
      <button type="button" className="btn px-2.5 py-1.5 text-[12.5px]" onClick={logout} title={t("sign_out")}>
        <Icon name="logout" />
        <span className="hidden xl:inline">{t("sign_out")}</span>
      </button>
    </div>
  );
}
