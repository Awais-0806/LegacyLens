import type { RiskPriority } from "@/lib/api";

type RiskRowProps = {
  risk: RiskPriority;
};

const titleCase = (value: string) => value.replaceAll("_", " ").replace(/\b\w/g, (match) => match.toUpperCase());

export function RiskRow({ risk }: RiskRowProps) {
  return (
    <div className="risk-row">
      <span className={`badge badge-${risk.priority}`}>{risk.priority}</span>
      <div>
        <b>{risk.title}</b>
        <p className="small">{risk.rationale}</p>
        <p className="hint">
          {titleCase(risk.category)} · {risk.severity} · {risk.confidence}
          {risk.requires_manual_review ? " · manual verification recommended" : ""}
        </p>
      </div>
    </div>
  );
}
