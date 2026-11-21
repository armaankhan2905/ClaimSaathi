import { Link } from "react-router";
import { Icon } from "../components/Icon";
import { useI18n } from "../i18n/I18nProvider";

export function Home() {
  const { t } = useI18n();
  return (
    <section aria-labelledby="h-home">
      <div className="relative overflow-hidden rounded-[28px] border border-line bg-[linear-gradient(165deg,var(--hero-from)_0%,var(--hero-mid)_60%,var(--hero-to)_100%)] px-5 py-7 md:px-10 md:py-11">
        <span className="eyebrow">{t("hero_eyebrow")}</span>
        <h1 id="h-home" className="mt-2.5">
          {t("hero_title_1")}
          <br />
          <span className="text-accent">{t("hero_title_2")}</span>
        </h1>
        <p className="muted mt-3.5 max-w-[54ch] text-[16.5px]">{t("hero_sub")}</p>
        <div className="mt-[22px] flex flex-wrap gap-2.5">
          <Link to="/policy" className="btn primary">
            <Icon name="upload" />
            {t("cta_upload")}
          </Link>
          <Link to="/rejection" className="btn">
            <Icon name="search" />
            {t("cta_check")}
          </Link>
        </div>
      </div>
    </section>
  );
}
