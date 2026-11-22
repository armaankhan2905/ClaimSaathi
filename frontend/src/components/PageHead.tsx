import { useEffect, type ReactNode } from "react";

/** Sets the browser tab title for the current page. */
export function usePageTitle(title?: string) {
  useEffect(() => {
    document.title = title ? `${title} · ClaimSaathi` : "ClaimSaathi";
  }, [title]);
}

export function PageHead({ eyebrow, title, lede, actions }: { eyebrow: string; title: string; lede?: string; actions?: ReactNode }) {
  usePageTitle(title);
  return (
    <div className="mb-6 flex flex-wrap items-end justify-between gap-5">
      <div>
        <span className="eyebrow">{eyebrow}</span>
        <h1 className="mt-1.5">{title}</h1>
        {lede && <p className="muted mt-2 max-w-[62ch]">{lede}</p>}
      </div>
      {actions}
    </div>
  );
}
