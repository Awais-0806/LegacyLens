"use client";

import type { ReactNode } from "react";
import { AnimatedCard } from "@/components/AnimatedCard";
import type { FindingReport } from "@/lib/api";

type FindingCardProps = {
  finding: FindingReport;
  index: number;
};

const titleCase = (value: string) => value.replaceAll("_", " ").replace(/\b\w/g, (match) => match.toUpperCase());

function Badge({ children, kind = "neutral" }: { children: ReactNode; kind?: string }) {
  return <span className={`badge badge-${kind}`}>{children}</span>;
}

export function FindingCard({ finding, index }: FindingCardProps) {
  const evidence = finding.evidence_references?.join(", ") || "No direct reference";

  return (
    <AnimatedCard index={index}>
      <details className="finding">
        <summary>
          <span>
            <Badge kind={finding.severity}>{finding.severity}</Badge> <b>{finding.title}</b>
          </span>
          <span className="muted">
            {titleCase(finding.category)} · {titleCase(finding.confidence)}
          </span>
        </summary>
        <div className="detail">
          <p>{finding.description}</p>
          <p>
            <b>Impact:</b> {finding.impact}
          </p>
          <p>
            <b>Recommendation:</b> {finding.recommendation}
          </p>
          <p>
            <b>Evidence:</b> {evidence}
          </p>
          <p>
            <b>Source:</b> {finding.source_classification}{" "}
            {finding.requires_manual_review && <Badge kind="warning">Manual review required</Badge>}
          </p>
          {finding.remediation_action_ids.length > 0 && (
            <p>
              <b>Roadmap links:</b> {finding.remediation_action_ids.join(", ")}
            </p>
          )}
        </div>
      </details>
    </AnimatedCard>
  );
}
