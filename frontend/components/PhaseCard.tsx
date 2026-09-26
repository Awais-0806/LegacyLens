import type { ReactNode } from "react";
import type { RenovationAction, RoadmapPhase } from "@/lib/api";

type PhaseCardProps = {
  phase: RoadmapPhase;
  actions: RenovationAction[];
};

function Badge({ children, kind = "neutral" }: { children: ReactNode; kind?: string }) {
  return <span className={`badge badge-${kind}`}>{children}</span>;
}

export function PhaseCard({ phase, actions }: PhaseCardProps) {
  return (
    <details className="phase">
      <summary>
        <b>
          {phase.sequence}. {phase.name}
        </b>
        <span className="muted">{phase.action_ids.length} actions</span>
      </summary>
      <p>{phase.objective}</p>
      {actions.map((action) => (
        <div className="action" key={action.action_id}>
          <div className="flex flex-wrap gap-2">
            <b>
              {action.action_id} · {action.title}
            </b>
            <Badge>{action.priority}</Badge>
            <Badge>{action.effort}</Badge>
            <Badge kind="warning">{action.automation_safety}</Badge>
          </div>
          <p>{action.description}</p>
          <p className="small">
            <b>Outcome:</b> {action.expected_outcome}
          </p>
          <p className="small">
            <b>Acceptance:</b> {action.acceptance_criteria.join("; ") || "Manual confirmation required"}
          </p>
        </div>
      ))}
    </details>
  );
}
