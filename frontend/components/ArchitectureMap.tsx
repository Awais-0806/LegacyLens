"use client";

import { useCallback, useEffect, useMemo, useRef, useState, type ComponentType, type Ref } from "react";
import { useReducedMotion } from "framer-motion";
import ForceGraph2D, { type ForceGraphMethods, type ForceGraphProps, type NodeObject } from "react-force-graph-2d";
import type { AnalyzeResponse, CategoryScore, FindingReport } from "@/lib/api";

type ArchitectureMapProps = {
  data: AnalyzeResponse;
};

type ColorMode = "health" | "size";
type NodeKind = "repository" | "language" | "technology" | "entry";

type MapNode = {
  id: string;
  label: string;
  kind: NodeKind;
  val: number;
  summary: string;
  paths: string[];
  extensions: string[];
  findings: FindingReport[];
  categories: CategoryScore[];
  health: string;
  sizeRatio: number;
};

type MapLink = {
  source: string;
  target: string;
  weight: number;
  reason: string;
};

// react-force-graph-2d types graphData as GraphData<NodeObject<NodeType>, ...>, which double-wraps the generic and
// makes every accessor disagree with our node type; the cast restores MapNode/MapLink as the real generics.
type MapGraphProps = ForceGraphProps<MapNode, MapLink> & { ref?: Ref<ForceGraphMethods<MapNode, MapLink>> };
const ForceGraph = ForceGraph2D as unknown as ComponentType<MapGraphProps>;

const MAX_LANGUAGES = 8;
const MAX_ENTRY_POINTS = 12;
const MAX_TECHNOLOGIES = 12;

// Mirrors the detector map in backend/app/analysis/languages.py so edges line up with what the backend counted.
const EXTENSION_LANGUAGE: Record<string, string> = {
  py: "Python",
  js: "JavaScript",
  jsx: "JavaScript",
  ts: "TypeScript",
  tsx: "TypeScript",
  java: "Java",
  go: "Go",
  rs: "Rust",
  c: "C",
  h: "C",
  cpp: "C++",
  cs: "C#",
  php: "PHP",
  rb: "Ruby",
  kt: "Kotlin",
  swift: "Swift",
  html: "HTML",
  css: "CSS",
  sql: "SQL",
  sh: "Shell",
};

const SEVERITY_RANK: Record<string, number> = { info: 0, low: 1, medium: 2, high: 3, critical: 4 };
const SEVERITY_COLOR: Record<string, string> = {
  info: "#a3e635",
  low: "#bef264",
  medium: "#fcd34d",
  high: "#fca5a5",
  critical: "#fca5a5",
};
const CONFIDENCE_COLOR: Record<string, string> = { high: "#a3e635", medium: "#fcd34d", low: "#71717a" };
const RISK_COLOR: Record<string, string> = {
  low: "#a3e635",
  moderate: "#bef264",
  medium: "#bef264",
  elevated: "#fcd34d",
  high: "#fca5a5",
  critical: "#fca5a5",
};
const NEUTRAL = "#71717a";
const SIZE_RAMP = ["#3f3f46", "#71717a", "#e4e4e7"];
const LINK_COLOR = "rgba(163, 230, 53, 0.15)";
const LINK_COLOR_ACTIVE = "rgba(163, 230, 53, 0.5)";

const normalize = (path: string) => path.replaceAll("\\", "/");
const baseName = (path: string) => path.slice(path.lastIndexOf("/") + 1);
const extensionOf = (path: string) => {
  const name = baseName(path);
  const dot = name.lastIndexOf(".");
  return dot > 0 ? name.slice(dot + 1).toLowerCase() : "";
};

// Evidence references arrive as "<path>:<evidence_type>"; sentinels such as "repository" are not paths.
const evidencePath = (reference: string) => {
  const cut = reference.lastIndexOf(":");
  const path = normalize(cut > 0 ? reference.slice(0, cut) : reference);
  return path.includes("/") || extensionOf(path) ? path : "";
};

const formatCount = (value: number) => value.toLocaleString("en-US");
const formatBytes = (bytes: number) =>
  bytes >= 1048576 ? `${(bytes / 1048576).toFixed(1)} MB` : bytes >= 1024 ? `${Math.round(bytes / 1024)} KB` : `${bytes} B`;

function rampColor(ratio: number) {
  const clamped = Math.min(1, Math.max(0, ratio));
  const position = clamped * (SIZE_RAMP.length - 1);
  const low = Math.floor(position);
  const high = Math.min(SIZE_RAMP.length - 1, low + 1);
  const mix = position - low;
  const channel = (hex: string) => [1, 3, 5].map((offset) => parseInt(hex.slice(offset, offset + 2), 16));
  const from = channel(SIZE_RAMP[low]);
  const to = channel(SIZE_RAMP[high]);
  const [r, g, b] = from.map((value, index) => Math.round(value + (to[index] - value) * mix));
  return `rgb(${r}, ${g}, ${b})`;
}

const radiusOf = (node: MapNode) => (node.kind === "repository" ? 15 : 3 + Math.sqrt(node.val) * 1.7);

const worstFinding = (findings: FindingReport[]) =>
  findings.reduce<FindingReport | null>(
    (worst, finding) => (!worst || (SEVERITY_RANK[finding.severity] ?? 0) > (SEVERITY_RANK[worst.severity] ?? 0) ? finding : worst),
    null,
  );

const titleCase = (value: string) => value.replaceAll("_", " ").replace(/\b\w/g, (match) => match.toUpperCase());

const linkEndId = (end: unknown) => {
  if (typeof end === "object" && end) return String((end as { id?: string | number }).id ?? "");
  return String(end ?? "");
};

export function ArchitectureMap({ data }: ArchitectureMapProps) {
  const [colorMode, setColorMode] = useState<ColorMode>("health");
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [hoverId, setHoverId] = useState<string | null>(null);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [viewport, setViewport] = useState({ width: 0, height: 420 });
  const hostRef = useRef<HTMLDivElement | null>(null);
  const graphRef = useRef<ForceGraphMethods<MapNode, MapLink> | null>(null);
  const reduceMotion = useReducedMotion();

  const { nodes, links, hiddenEntryPoints } = useMemo(() => {
    const analysis = data.analysis;
    const findings = data.report.findings ?? [];
    const categories = data.assessment.assessment.category_scores ?? [];
    const languages = [...(analysis.languages ?? [])].sort((left, right) => right.loc - left.loc).slice(0, MAX_LANGUAGES);
    const technologies = (analysis.technologies ?? []).slice(0, MAX_TECHNOLOGIES);
    const entryPoints = (analysis.entry_points ?? []).map(normalize);

    const largestBytes = new Map<string, number>();
    (analysis.metrics.largest_files ?? []).forEach((entry) => {
      const path = normalize(String(entry.path ?? ""));
      const bytes = Number(entry.size_bytes ?? 0);
      if (path && Number.isFinite(bytes)) largestBytes.set(path, bytes);
    });

    const findingEvidence = findings.map((finding) => ({
      finding,
      paths: (finding.evidence_references ?? []).map(evidencePath).filter(Boolean),
    }));
    const categoryEvidence = categories.map((category) => ({
      category,
      paths: (category.evidence_references ?? []).map(normalize).filter(Boolean),
    }));

    const findingsFor = (matches: (path: string) => boolean) =>
      findingEvidence.filter((entry) => entry.paths.some(matches)).map((entry) => entry.finding);
    const categoriesFor = (matches: (path: string) => boolean) =>
      categoryEvidence.filter((entry) => entry.paths.some(matches)).map((entry) => entry.category);
    const mergeCategories = (lists: CategoryScore[][]) => {
      const seen = new Set<string>();
      return lists.flat().filter((category) => (seen.has(category.category) ? false : (seen.add(category.category), true)));
    };

    const maxLoc = Math.max(1, ...languages.map((language) => language.loc));
    const entryBytes = entryPoints.map((path) => largestBytes.get(path) ?? 0);
    const maxEntryBytes = Math.max(0, ...entryBytes);

    const repository: MapNode = {
      id: "repository",
      label: `${data.repository.owner}/${data.repository.name}`,
      kind: "repository",
      val: 60,
      summary: `${formatCount(analysis.file_count)} files · ${formatCount(analysis.directory_count)} directories · ${formatBytes(analysis.total_size_bytes)}`,
      paths: [],
      extensions: [],
      findings,
      categories,
      health: RISK_COLOR[String(data.assessment.assessment.risk_level ?? "").toLowerCase()] ?? NEUTRAL,
      sizeRatio: 1,
    };

    const languageNodes: MapNode[] = languages.map((language) => {
      const paths = (language.evidence_files ?? []).map(normalize);
      const extensions = [
        ...new Set([
          ...Object.keys(EXTENSION_LANGUAGE).filter((extension) => EXTENSION_LANGUAGE[extension] === language.language),
          ...paths.map(extensionOf).filter(Boolean),
        ]),
      ];
      const matches = (path: string) => paths.includes(path) || extensions.includes(extensionOf(path));
      const related = findingsFor(matches);
      const worst = worstFinding(related);
      return {
        id: `language:${language.language}`,
        label: language.language,
        kind: "language",
        val: Math.min(40, 6 + Math.sqrt(language.loc) / 5),
        summary: `${formatCount(language.loc)} LOC · ${formatCount(language.file_count)} files · ${(language.share * 100).toFixed(1)}% of code${worst ? ` · highest severity ${worst.severity}` : " · no findings reference these files"}`,
        paths,
        extensions,
        findings: related,
        categories: mergeCategories([categoriesFor(matches), related.map((finding) => categories.find((c) => c.category === finding.category)).filter((c): c is CategoryScore => Boolean(c))]),
        health: worst ? SEVERITY_COLOR[worst.severity] ?? NEUTRAL : NEUTRAL,
        sizeRatio: Math.sqrt(language.loc / maxLoc),
      };
    });

    const technologyNodes: MapNode[] = technologies.map((technology) => {
      const paths = (technology.evidence ?? []).map(normalize);
      const extensions = [...new Set(paths.map(extensionOf).filter(Boolean))];
      const related = findingsFor((path) => paths.includes(path));
      return {
        id: `technology:${technology.technology}`,
        label: technology.technology,
        kind: "technology",
        val: 5,
        summary: `${technology.confidence} confidence · ${paths.length} evidence file${paths.length === 1 ? "" : "s"}`,
        paths,
        extensions,
        findings: related,
        categories: mergeCategories([categoriesFor((path) => paths.includes(path)), related.map((finding) => categories.find((c) => c.category === finding.category)).filter((c): c is CategoryScore => Boolean(c))]),
        health: CONFIDENCE_COLOR[technology.confidence] ?? NEUTRAL,
        sizeRatio: 0.35,
      };
    });

    const entryNodes: MapNode[] = entryPoints.slice(0, MAX_ENTRY_POINTS).map((path, index) => {
      const bytes = entryBytes[index];
      const extensions = extensionOf(path) ? [extensionOf(path)] : [];
      const related = findingsFor((candidate) => candidate === path);
      const worst = worstFinding(related);
      return {
        id: `entry:${path}`,
        label: baseName(path),
        kind: "entry",
        val: 5,
        summary: `${path}${bytes ? ` · ${formatBytes(bytes)}` : ""}${worst ? ` · highest severity ${worst.severity}` : ""}`,
        paths: [path],
        extensions,
        findings: related,
        categories: related.map((finding) => categories.find((c) => c.category === finding.category)).filter((c): c is CategoryScore => Boolean(c)),
        health: worst ? SEVERITY_COLOR[worst.severity] ?? NEUTRAL : NEUTRAL,
        sizeRatio: maxEntryBytes > 0 && bytes > 0 ? Math.max(0.15, bytes / maxEntryBytes) : 0.25,
      };
    });

    const edges: MapLink[] = [];
    languageNodes.forEach((language, index) => {
      edges.push({
        source: repository.id,
        target: language.id,
        weight: languages[index].share,
        reason: `${(languages[index].share * 100).toFixed(1)}% of detected code`,
      });
      entryNodes.forEach((entry) => {
        if (entry.extensions.some((extension) => language.extensions.includes(extension))) {
          edges.push({ source: language.id, target: entry.id, weight: 0.35, reason: "Entry point file extension matches this language" });
        }
      });
    });
    technologyNodes.forEach((technology) => {
      edges.push({ source: repository.id, target: technology.id, weight: 0.35, reason: "Technology evidence detected in repository" });
      languageNodes.forEach((language) => {
        const byExtension = technology.extensions.some((extension) => language.extensions.includes(extension));
        const byEvidence = technology.paths.some((path) => language.paths.includes(path));
        if (byExtension || byEvidence) {
          edges.push({
            source: technology.id,
            target: language.id,
            weight: 0.5,
            reason: byExtension ? "Evidence file extensions match this language" : "Evidence file is also cited for this language",
          });
        }
      });
    });

    return {
      nodes: [repository, ...languageNodes, ...technologyNodes, ...entryNodes],
      links: edges,
      hiddenEntryPoints: Math.max(0, entryPoints.length - MAX_ENTRY_POINTS),
    };
  }, [data]);

  const graphData = useMemo(() => ({ nodes, links }), [nodes, links]);
  const selected = nodes.find((node) => node.id === selectedId) ?? null;

  useEffect(() => {
    const host = hostRef.current;
    if (!host) return;
    const observer = new ResizeObserver((entries) => {
      const box = entries[0].contentRect;
      setViewport({ width: Math.max(240, Math.round(box.width)), height: Math.max(240, Math.round(box.height)) });
    });
    observer.observe(host);
    return () => observer.disconnect();
  }, []);

  useEffect(() => {
    const frame = requestAnimationFrame(() => graphRef.current?.zoomToFit(reduceMotion ? 0 : 400, 48));
    return () => cancelAnimationFrame(frame);
  }, [isFullscreen, viewport.width, reduceMotion]);

  useEffect(() => {
    if (!isFullscreen) return;
    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") setIsFullscreen(false);
    };
    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, [isFullscreen]);

  const colorOf = useCallback(
    (node: MapNode) => (colorMode === "health" ? node.health : rampColor(node.sizeRatio)),
    [colorMode],
  );

  const drawNode = useCallback(
    (node: NodeObject<MapNode>, context: CanvasRenderingContext2D, globalScale: number) => {
      const x = node.x ?? 0;
      const y = node.y ?? 0;
      const radius = radiusOf(node);
      const isActive = node.id === selectedId || node.id === hoverId;
      context.beginPath();
      context.arc(x, y, radius, 0, 2 * Math.PI);
      context.fillStyle = colorOf(node);
      context.fill();
      context.lineWidth = isActive ? 2 : 1;
      context.strokeStyle = isActive ? "#ffffff" : "rgba(9, 9, 11, 0.85)";
      context.stroke();

      const showLabel = node.kind === "repository" || node.kind === "language" || globalScale >= 0.9 || isActive;
      if (!showLabel) return;
      const fontSize = 11 / globalScale;
      context.font = `${fontSize}px Arial, Helvetica, sans-serif`;
      context.textAlign = "center";
      context.textBaseline = "top";
      context.fillStyle = isActive ? "#ffffff" : "#a1a1aa";
      context.fillText(node.label, x, y + radius + fontSize * 0.3);
    },
    [colorOf, hoverId, selectedId],
  );

  const paintPointerArea = useCallback((node: NodeObject<MapNode>, color: string, context: CanvasRenderingContext2D) => {
    context.beginPath();
    context.arc(node.x ?? 0, node.y ?? 0, radiusOf(node) + 4, 0, 2 * Math.PI);
    context.fillStyle = color;
    context.fill();
  }, []);

  const modeButton = (mode: ColorMode, label: string) => (
    <button
      type="button"
      onClick={() => setColorMode(mode)}
      aria-pressed={colorMode === mode}
      className={`rounded-[9px] border px-3 py-2 text-xs font-semibold ${
        colorMode === mode ? "border-[#a3e635] bg-[#a3e635] text-[#111]" : "border-[#3f3f46] text-[#d4d4d8] hover:border-[#71717a]"
      }`}
    >
      {label}
    </button>
  );

  return (
    <section className={isFullscreen ? "panel fixed inset-0 z-50 flex flex-col overflow-hidden rounded-none" : "panel flex flex-col"}>
      <div className="section-head">
        <h2>Architecture Map</h2>
        <div className="flex flex-wrap items-center gap-2">
          <div className="flex gap-2" role="group" aria-label="Node colour mode">
            {modeButton("health", "By health")}
            {modeButton("size", "By size")}
          </div>
          <button
            type="button"
            onClick={() => setIsFullscreen((current) => !current)}
            aria-expanded={isFullscreen}
            className="rounded-[9px] border border-[#3f3f46] px-3 py-2 text-xs font-semibold text-[#d4d4d8] hover:border-[#a3e635] hover:text-[#bef264]"
          >
            {isFullscreen ? "Exit fullscreen" : "Fullscreen"}
          </button>
        </div>
      </div>

      {nodes.length <= 1 ? (
        <p className="muted">No languages, technologies, or entry points were detected, so there is nothing to map.</p>
      ) : (
        <>
          <div
            ref={hostRef}
            className={isFullscreen ? "relative min-h-0 flex-1 overflow-hidden" : "relative h-[420px] overflow-hidden sm:h-[460px]"}
            role="img"
            aria-label={`Force-directed map of ${nodes.length - 1} structural signals for ${data.repository.owner}/${data.repository.name}`}
          >
            <ForceGraph
              ref={graphRef}
              width={viewport.width}
              height={viewport.height}
              graphData={graphData}
              backgroundColor="rgba(0, 0, 0, 0)"
              nodeVal={(node) => node.val}
              nodeCanvasObject={drawNode}
              nodePointerAreaPaint={paintPointerArea}
              linkColor={(link) =>
                selectedId && (linkEndId(link.source) === selectedId || linkEndId(link.target) === selectedId)
                  ? LINK_COLOR_ACTIVE
                  : LINK_COLOR
              }
              linkWidth={(link) => 0.8 + link.weight * 3.5}
              onNodeClick={(node) => setSelectedId(node.id === selectedId ? null : String(node.id))}
              onNodeHover={(node) => setHoverId(node ? String(node.id) : null)}
              onBackgroundClick={() => setSelectedId(null)}
              onEngineStop={() => graphRef.current?.zoomToFit(reduceMotion ? 0 : 400, 48)}
              warmupTicks={reduceMotion ? 160 : 0}
              cooldownTicks={reduceMotion ? 0 : Infinity}
              autoPauseRedraw
              enableNodeDrag={!reduceMotion}
              d3AlphaDecay={0.035}
            />

            {selected && (
              <aside
                className="absolute z-10 overflow-y-auto rounded-t-[16px] border border-[#3f3f46] p-4 shadow-[0_-10px_40px_rgba(0,0,0,0.55)] max-sm:inset-x-0 max-sm:bottom-0 max-sm:max-h-[62%] sm:inset-y-3 sm:right-3 sm:w-[330px]"
                style={{ background: "linear-gradient(145deg, #151518, #101012)" }}
                aria-label={`${selected.label} details`}
              >
                <div className="flex items-start justify-between gap-3">
                  <div className="min-w-0">
                    <p className="eyebrow">{selected.kind}</p>
                    <h3 className="break-all text-[17px] font-extrabold">{selected.label}</h3>
                  </div>
                  <button
                    type="button"
                    onClick={() => setSelectedId(null)}
                    aria-label="Close node details"
                    className="shrink-0 rounded-[9px] border border-[#3f3f46] px-2 py-1 text-xs text-[#d4d4d8] hover:border-[#a3e635] hover:text-[#bef264]"
                  >
                    ✕
                  </button>
                </div>

                <p className="small mt-2">{selected.summary}</p>
                {selected.extensions.length > 0 && (
                  <p className="hint mt-1">Extensions: {selected.extensions.join(", ")}</p>
                )}

                <h4 className="mt-4 text-[11px] font-extrabold uppercase tracking-[0.16em] text-[#a1a1aa]">
                  Related findings · {selected.findings.length}
                </h4>
                <div className="mt-2 grid gap-2">
                  {selected.findings.length === 0 ? (
                    <p className="hint">No specialist finding cites this node.</p>
                  ) : (
                    selected.findings.slice(0, 8).map((finding) => (
                      <div key={finding.finding_id} className="rounded-[10px] border border-[#27272a] bg-[#0d0d0f] p-3">
                        <div className="flex flex-wrap items-center gap-2">
                          <span className={`badge badge-${finding.severity}`}>{finding.severity}</span>
                          <b className="text-[13px]">{finding.title}</b>
                        </div>
                        <p className="hint mt-1">
                          {finding.finding_id} · {finding.source_classification}
                        </p>
                      </div>
                    ))
                  )}
                  {selected.findings.length > 8 && <p className="hint">+{selected.findings.length - 8} more findings</p>}
                </div>

                <h4 className="mt-4 text-[11px] font-extrabold uppercase tracking-[0.16em] text-[#a1a1aa]">
                  Related category scores
                </h4>
                <div className="mt-2 grid gap-2">
                  {selected.categories.length === 0 ? (
                    <p className="hint">No category score cites this node.</p>
                  ) : (
                    selected.categories.slice(0, 7).map((category) => (
                      <div
                        key={category.category}
                        className="flex items-center justify-between gap-3 rounded-[10px] border border-[#27272a] bg-[#0d0d0f] px-3 py-2"
                      >
                        <span className="text-[13px]">{titleCase(category.category)}</span>
                        <span className="text-[13px] tabular-nums">
                          <b className="text-[#bef264]">{Math.round(category.raw_score)}</b>
                          <span className="hint"> /100 · weight {category.weight}%</span>
                        </span>
                      </div>
                    ))
                  )}
                </div>

                {selected.paths.length > 0 && (
                  <>
                    <h4 className="mt-4 text-[11px] font-extrabold uppercase tracking-[0.16em] text-[#a1a1aa]">
                      Evidence paths
                    </h4>
                    <ul className="mt-2 grid gap-1">
                      {selected.paths.slice(0, 6).map((path) => (
                        <li key={path} className="break-all font-mono text-[11px] text-[#a1a1aa]">
                          {path}
                        </li>
                      ))}
                    </ul>
                    {selected.paths.length > 6 && <p className="hint mt-1">+{selected.paths.length - 6} more paths</p>}
                  </>
                )}
              </aside>
            )}
          </div>

          <div className="mt-3 flex flex-wrap items-center gap-x-4 gap-y-2">
            {colorMode === "health" ? (
              [
                ["#a3e635", "Healthy / info"],
                ["#bef264", "Low"],
                ["#fcd34d", "Medium"],
                ["#fca5a5", "High or critical"],
                [NEUTRAL, "No findings"],
              ].map(([color, label]) => (
                <span key={label} className="flex items-center gap-2 text-[11px] text-[#a1a1aa]">
                  <i className="inline-block h-2.5 w-2.5 rounded-full" style={{ background: color }} />
                  {label}
                </span>
              ))
            ) : (
              <span className="flex items-center gap-2 text-[11px] text-[#a1a1aa]">
                <i
                  className="inline-block h-2.5 w-16 rounded-full"
                  style={{ background: "linear-gradient(90deg, #3f3f46, #71717a, #e4e4e7)" }}
                />
                Smaller → larger footprint
              </span>
            )}
            <span className="hint">
              Node size follows lines of code for languages. Technology nodes are coloured by detection confidence in
              health mode. Click a node for its evidence; drag to pan, scroll to zoom.
              {hiddenEntryPoints > 0 ? ` ${hiddenEntryPoints} further entry points are not drawn.` : ""}
            </span>
          </div>
        </>
      )}
    </section>
  );
}
