import type { ReactNode } from "react";
import { AnimatePresence, motion } from "motion/react";
import { Outlet, useLocation } from "react-router";
import { useI18n } from "../i18n/I18nProvider";
import { AppBar } from "./AppBar";

export function Layout({ barRight }: { barRight?: ReactNode }) {
  const { t } = useI18n();
  const location = useLocation();

  return (
    <div className="flex min-h-dvh flex-col">
      <AppBar rightSlot={barRight} />
      <main className="wrap w-full flex-1 pt-7 pb-16">
        <AnimatePresence mode="wait">
          <motion.div
            key={location.pathname}
            initial={{ opacity: 0, y: 6 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -4 }}
            transition={{ duration: 0.18, ease: "easeOut" }}
          >
            <Outlet />
          </motion.div>
        </AnimatePresence>
      </main>
      <footer className="border-t border-line">
        <div className="wrap flex flex-wrap justify-between gap-3 py-[22px] text-[12.5px] text-muted">
          <span>{t("footer_note")}</span>
          <span>{t("footer_privacy")}</span>
        </div>
      </footer>
    </div>
  );
}
