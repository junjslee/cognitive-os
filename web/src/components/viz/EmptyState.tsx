import { cn } from "@/lib/utils";
import type { ReactNode } from "react";

interface EmptyStateProps {
  title: string;
  hint?: string;
  cta?: ReactNode;
  tone?: "neutral" | "error";
  className?: string;
}

export function EmptyState({
  title,
  hint,
  cta,
  tone = "neutral",
  className,
}: EmptyStateProps) {
  return (
    <div
      className={cn(
        "flex h-full flex-col items-start justify-center gap-3 border border-hairline bg-surface/20 p-8",
        tone === "error" && "border-disconfirm/30",
        className,
      )}
    >
      <span
        className={cn(
          "font-mono text-[0.6875rem] uppercase tracking-[0.2em]",
          tone === "error" ? "text-disconfirm" : "text-muted",
        )}
      >
        {tone === "error" ? "kernel · unreachable" : "kernel · uninitialized"}
      </span>
      <h3 className="font-display text-[1.25rem] leading-tight text-bone">
        {title}
      </h3>
      {hint && (
        <p className="max-w-lg font-mono text-[0.75rem] leading-relaxed text-ash">
          {hint}
        </p>
      )}
      {cta && <div className="mt-2">{cta}</div>}
    </div>
  );
}
