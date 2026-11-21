import { Link } from "react-router";
import { Icon } from "../components/Icon";
import { PageHead } from "../components/PageHead";
import { useI18n } from "../i18n/I18nProvider";
import type { StringKey } from "../i18n/strings";

// Stand-in for the Policy Insights, Rejection Check and Complaint pages until their stages are built.
export function SectionPlaceholder({ eyebrow, title, lede }: { eyebrow: StringKey; title: StringKey; lede: StringKey }) {
  const { t } = useI18n();
  return (
    <>
      <PageHead eyebrow={t(eyebrow)} title={t(title)} lede={t(lede)} />
      <div className="panel flex flex-wrap items-start gap-4">
        <span className="grid h-11 w-11 flex-none place-items-center rounded-xl bg-surface-2 text-accent">
          <Icon name="tools" className="h-[22px] w-[22px]" />
        </span>
        <div className="min-w-[220px] flex-1">
          <h2 className="text-xl">{t("building_title")}</h2>
          <p className="muted mt-1.5">{t("building_text")}</p>
        </div>
        <Link to="/" className="btn">
          {t("back_home")}
        </Link>
      </div>
    </>
  );
}
