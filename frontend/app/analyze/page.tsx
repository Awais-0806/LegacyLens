"use client";

import { FormEvent, useEffect, useMemo, useState } from "react";
import dynamic from "next/dynamic";
import { Shell } from "@/components/Shell";
import { CountUp } from "@/components/CountUp";
import { FindingCard } from "@/components/FindingCard";
import { PhaseCard } from "@/components/PhaseCard";
import { RiskRow } from "@/components/RiskRow";
import { StatTile } from "@/components/StatTile";
import { apiRequest, AnalyzeResponse, exportCanonicalReport } from "@/lib/api";

const ArchitectureMap = dynamic(() => import("@/components/ArchitectureMap").then((module) => module.ArchitectureMap), {
  ssr: false,
  loading: () => <div className="shimmer h-[420px] rounded-[16px]" />,
});

const stages = [
  "Validating URL",
  "Safely ingesting repository",
  "Detecting project structure",
  "Running specialist analysis",
  "Calculating health score",
  "Building roadmap",
  "Preparing report",
];

const statusMessages = ["Validating URL", "Ingesting repository", "Running 7 analyzers", "Scoring", "Building roadmap"];

const statusRotationMs = 1600;

const cap = (value: string) => value.replaceAll("_", " ").replace(/\b\w/g, (match) => match.toUpperCase());

function Badge({ children, kind = "neutral" }: { children: React.ReactNode; kind?: string }) {
  return <span className={`badge badge-${kind}`}>{children}</span>;
}

function Score({ value }: { value: number }) {
  return (
    <div className="score-ring" style={{ "--score": `${value}%` } as React.CSSProperties}>
      <div>
        <strong>
          <CountUp value={value} />
        </strong>
        <small>/ 100</small>
      </div>
    </div>
  );
}

function Section({ title, children, aside }: { title: string; children: React.ReactNode; aside?: React.ReactNode }) {
  return (
    <section className="panel">
      <div className="section-head">
        <h2>{title}</h2>
        {aside}
      </div>
      {children}
    </section>
  );
}

export default function AnalyzePage() {
  const [url, setUrl] = useState("");
  const [data, setData] = useState<AnalyzeResponse | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [query, setQuery] = useState("");
  const [severity, setSeverity] = useState("all");
  const [statusIndex, setStatusIndex] = useState(0);

  useEffect(() => {
    if (!loading) {
      setStatusIndex(0);
      return;
    }
    const timer = window.setInterval(() => {
      setStatusIndex((current) => (current + 1) % statusMessages.length);
    }, statusRotationMs);
    return () => window.clearInterval(timer);
  }, [loading]);

  async function submit(event: FormEvent) {
    event.preventDefault();
    setError("");
    setData(null);
    if (!/^https:\/\/github\.com\/[^/]+\/[^/]+\/?$/.test(url.trim())) {
      setError("Enter a public GitHub repository URL, for example https://github.com/owner/repository");
      return;
    }
    setLoading(true);
    try {
      const response = await apiRequest<AnalyzeResponse>("/analyses", {
        method: "POST",
        body: JSON.stringify({ repository_url: url.trim() }),
      });
      setData(response);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Analysis could not be completed safely.");
    } finally {
      setLoading(false);
    }
  }

  const findings = useMemo(() => {
    const reportFindings = data?.report?.findings ?? [];
    return reportFindings
      .filter(
        (finding) =>
          (severity === "all" || finding.severity === severity) &&
          `${finding.title} ${finding.description} ${finding.category} ${finding.specialist}`
            .toLowerCase()
            .includes(query.toLowerCase()),
      )
      .sort((a, b) => a.finding_id.localeCompare(b.finding_id));
  }, [data, query, severity]);

  async function download(format: "json" | "markdown" | "html") {
    if (!data) return;
    try {
      const blob = await exportCanonicalReport(format, data.report);
      const anchor = document.createElement("a");
      const href = URL.createObjectURL(blob);
      anchor.href = href;
      const safeName =
        (data.repository.name || "assessment").replace(/[^a-zA-Z0-9._-]+/g, "-").slice(0, 80) || "assessment";
      anchor.download = `legacylens-${safeName}.${format === "markdown" ? "md" : format}`;
      anchor.click();
      setTimeout(() => URL.revokeObjectURL(href), 1000);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Report export failed safely.");
    }
  }

  return (
    <Shell>
      <div className="mx-auto max-w-7xl px-5 py-10">
        <div className="mb-8">
          <p className="eyebrow">Developer intelligence / static assessment</p>
          <h1 className="hero-title">
            Understand legacy code.
            <br />
            <span>Modernize with confidence.</span>
          </h1>
          <p className="muted max-w-2xl">
            Evidence-backed repository intelligence that separates observed signals from assumptions and turns findings
            into a practical renovation sequence.
          </p>
        </div>

        <form onSubmit={submit} className="input-panel">
          <label htmlFor="repo">Public GitHub repository URL</label>
          <div className="flex flex-col gap-3 sm:flex-row">
            <input
              id="repo"
              value={url}
              onChange={(event) => setUrl(event.target.value)}
              placeholder="https://github.com/owner/repository"
              disabled={loading}
            />
            <button disabled={loading}>{loading ? "Processing…" : "Analyze repository"}</button>
          </div>
          <p className="hint">Public HTTPS GitHub repositories only. The server remains authoritative for validation.</p>
        </form>

        {loading && (
          <div className="panel mt-5" data-loading-panel>
            <div className="loading-title">
              Building your assessment <span className="pulse">●</span>
            </div>
            <p className="hint mt-2" role="status" aria-live="polite">
              {statusMessages[statusIndex]}…
            </p>

            <div className="mt-5 grid gap-4 sm:grid-cols-[145px_1fr]" aria-hidden="true">
              <div className="shimmer h-[145px] w-[145px] rounded-full" />
              <div className="grid gap-3">
                <div className="grid gap-3 sm:grid-cols-3">
                  <div className="shimmer h-[58px] rounded-[10px]" />
                  <div className="shimmer h-[58px] rounded-[10px]" />
                  <div className="shimmer h-[58px] rounded-[10px]" />
                </div>
                <div className="shimmer h-3 w-full rounded-full" />
                <div className="shimmer h-3 w-11/12 rounded-full" />
                <div className="shimmer h-3 w-4/5 rounded-full" />
              </div>
            </div>

            <ol className="mt-5 grid gap-2 sm:grid-cols-2" aria-label="Processing stages">
              {stages.map((stage, index) => (
                <li key={stage} className="shimmer flex items-center gap-3 rounded-[10px] px-3 py-2">
                  <span className="text-xs tabular-nums text-zinc-500">{index + 1}</span>
                  <span className="text-xs text-zinc-300">{stage}</span>
                </li>
              ))}
            </ol>

            <p className="hint mt-3">General processing stages; live backend progress telemetry is not claimed.</p>
          </div>
        )}

        {error && (
          <div role="alert" className="error mt-5">
            {error}
          </div>
        )}

        {data && (
          <div className="mt-8 space-y-6">
            <div className="grid gap-5 lg:grid-cols-[1.2fr_.8fr]">
              <Section title="Assessment overview">
                <div className="repo-line">
                  <div>
                    <p className="eyebrow">Repository</p>
                    <h3>{data.repository.owner}/{data.repository.name}</h3>
                    <p className="muted break-all">{data.repository.url}</p>
                  </div>
                  <Badge kind="success">{data.status}</Badge>
                </div>
                <div className="stat-grid">
                  <StatTile value={data.analysis.file_count ?? "—"} label="Files assessed" />
                  <StatTile
                    value={(data.analysis.languages ?? []).map((entry) => entry.language).join(", ") || "—"}
                    label="Detected languages"
                  />
                  <StatTile
                    value={
                      (data.analysis.technologies ?? []).map((entry) => entry.technology).slice(0, 3).join(", ") || "—"
                    }
                    label="Technology signals"
                  />
                </div>
                <p className="disclaimer">
                  Static assessment · evidence-backed · runtime verification is outside this analysis.
                </p>
              </Section>

              <Section title="Health score">
                <div className="score-layout">
                  <Score value={data.assessment.assessment.overall_score} />
                  <div>
                    <Badge kind="accent">{data.assessment.assessment.health_label}</Badge>
                    <p className="risk">
                      Risk level: <strong>{cap(data.assessment.assessment.risk_level)}</strong>
                    </p>
                    <p className="muted">Confidence: {cap(data.assessment.assessment.confidence)}</p>
                  </div>
                </div>
                <p className="summary">{data.report.executive.executive_summary}</p>
              </Section>
            </div>

            <Section title="Why this score?">
              <p className="summary">{data.assessment.assessment.score_explanation}</p>
              <div className="signal-grid">
                <div>
                  <h3>Positive signals</h3>
                  {(data.assessment.assessment.positive_signals ?? []).map((signal: string) => (
                    <p className="signal positive" key={signal}>
                      + {signal}
                    </p>
                  ))}
                </div>
                <div>
                  <h3>Limitations & unknowns</h3>
                  {[...(data.assessment.assessment.limitations ?? []), ...(data.report.limitations ?? [])]
                    .slice(0, 8)
                    .map((limitation: string) => (
                      <p className="signal" key={limitation}>
                        • {limitation}
                      </p>
                    ))}
                </div>
              </div>
              <div className="category-grid">
                {data.assessment.assessment.category_scores.map((category) => (
                  <div className="category-card" key={category.category}>
                    <div className="flex justify-between">
                      <b>{cap(category.category)}</b>
                      <strong>{Math.round(category.raw_score)}</strong>
                    </div>
                    <div className="bar">
                      <i style={{ width: `${category.raw_score}%` }} />
                    </div>
                    <p className="hint">
                      Weight {category.weight}% · {category.finding_count} findings
                    </p>
                    <p className="small">{category.explanation}</p>
                  </div>
                ))}
              </div>
            </Section>

            <Section
              title="Specialist findings"
              aside={
                <div className="filters">
                  <input
                    aria-label="Search findings"
                    placeholder="Search findings"
                    value={query}
                    onChange={(event) => setQuery(event.target.value)}
                  />
                  <select
                    value={severity}
                    onChange={(event) => setSeverity(event.target.value)}
                    aria-label="Filter severity"
                  >
                    <option value="all">All severity</option>
                    {["critical", "high", "medium", "low", "info"].map((option) => (
                      <option key={option}>{option}</option>
                    ))}
                  </select>
                </div>
              }
            >
              {findings.length === 0 ? (
                <p className="muted">No findings match the current filters.</p>
              ) : (
                <div className="stack">
                  {findings.map((finding, index) => (
                    <FindingCard key={finding.finding_id} finding={finding} index={index} />
                  ))}
                </div>
              )}
            </Section>

            <ArchitectureMap data={data} />

            <Section title="Prioritized risks">
              {(data.assessment.assessment.risk_priorities ?? []).length === 0 ? (
                <p className="muted">No prioritized risks were produced.</p>
              ) : (
                <div className="stack">
                  {data.assessment.assessment.risk_priorities.map((risk) => (
                    <RiskRow key={risk.risk_id} risk={risk} />
                  ))}
                </div>
              )}
            </Section>

            <Section title="Renovation roadmap">
              <p className="summary">{data.roadmap.roadmap.summary}</p>
              <div className="roadmap-meta">
                <div>
                  <span>Current state</span>
                  <b>{data.roadmap.roadmap.current_state}</b>
                </div>
                <div>
                  <span>Target state</span>
                  <b>{data.roadmap.roadmap.target_state}</b>
                </div>
                <div>
                  <span>Complexity</span>
                  <b>{data.roadmap.roadmap.estimated_complexity}</b>
                </div>
              </div>
              {data.roadmap.roadmap.roadmap_phases.map((phase) => (
                <PhaseCard
                  key={phase.phase_id}
                  phase={phase}
                  actions={data.roadmap.roadmap.actions.filter((action) => phase.action_ids.includes(action.action_id))}
                />
              ))}
              {data.roadmap.roadmap.blockers.length > 0 && (
                <div className="warning-box">
                  <b>Blockers requiring attention</b>
                  {data.roadmap.roadmap.blockers.map((blocker) => (
                    <p key={blocker.blocker_id}>
                      • {blocker.title}: {blocker.mitigation}
                    </p>
                  ))}
                </div>
              )}
            </Section>

            <Section title="Exports">
              <p className="muted">
                Download the canonical report representation generated by the assessment pipeline.
              </p>
              <div className="export-row">
                <button onClick={() => download("json")}>Export JSON</button>
                <button onClick={() => download("markdown")}>Export Markdown</button>
                <button onClick={() => download("html")}>Export HTML</button>
              </div>
              <p className="hint">HTML is downloaded as a file and is never injected into this application.</p>
            </Section>

            <button
              className="secondary"
              onClick={() => {
                setData(null);
                setUrl("");
                window.scrollTo({ top: 0, behavior: "smooth" });
              }}
            >
              Start another analysis
            </button>
          </div>
        )}
      </div>
    </Shell>
  );
}
