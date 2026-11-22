import { useEffect, type ReactNode } from "react";

/** Sets the browser tab title for the current page. */
export function usePageTitle(title?: string) {
  useEffect(() => {
    document.title = title ? `${title} · ClaimSaathi` : "ClaimSaathi";
  }, [title]);
}

/** A page header set like the cover label of a case file. */
export function PageHead({ eyebrow, title, lede, actions }: { eyebrow: string; title: string; lede?: string; actions?: ReactNode }) {
  usePageTitle(title);
  return (
    <div className="mb-8 flex flex-wrap items-end justify-between gap-5 border-b-[1.5px] border-dashed border-line pb-6">
      <div>
        <span className="eyebrow">{eyebrow}</span>
        <h1 className="mt-2">{title}</h1>
        {lede && <p className="muted mt-3 max-w-[62ch] text-[16.5px] leading-relaxed">{lede}</p>}
      </div>
      {actions}
    </div>
  );
}
