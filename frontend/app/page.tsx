import Link from "next/link";
import { AuroraBackground } from "@/components/AuroraBackground";
import { LandingIcon } from "@/components/LandingIcon";
import { Shell } from "@/components/Shell";
import styles from "@/components/LandingPage.module.css";

const ANALYZE_PATH = "/analyze";
const DASHBOARD_PREVIEW_PATH = "/overview";
const EXAMPLE_HEALTH_SCORE = 72;
const MAX_HEALTH_SCORE = 100;
const EXPORT_FORMATS = ["JSON", "Markdown", "HTML"] as const;

const SPECIALISTS = [
  {
    icon: "architecture",
    title: "Architecture",
    description: "Map the shape of an unfamiliar codebase. Surface entry points, structural signals, and the boundaries worth a closer look.",
    signal: "Structure & entry points",
  },
  {
    icon: "security",
    title: "Security",
    description: "Flag security-related signals that deserve human review, without running repository code.",
    signal: "Risk signals",
  },
  {
    icon: "dependencies",
    title: "Dependencies",
    description: "Inspect dependency manifests and lockfile signals to understand the maintenance surface.",
    signal: "Manifests & lockfiles",
  },
  {
    icon: "testing",
    title: "Testing",
    description: "Find test files and testing signals. Know what is visible, and what still needs verification.",
    signal: "Test presence",
  },
  {
    icon: "documentation",
    title: "Documentation",
    description: "Assess the documentation signals that help the next developer get oriented and contribute.",
    signal: "Project guidance",
  },
  {
    icon: "maintainability",
    title: "Maintainability",
    description: "Spot code-size and organization signals that can make everyday changes harder to manage.",
    signal: "Maintenance friction",
  },
  {
    icon: "modernization",
    title: "Modernization Readiness",
    description: "Bring the evidence together to identify a practical starting point for renovation.",
    signal: "Readiness signals",
  },
] as const;

const WORKFLOW = [
  {
    step: "01",
    icon: "repository",
    title: "Ingest",
    description: "Start with a public GitHub URL. LegacyLens inventories the repository without executing its code.",
    output: "A structured repository inventory",
  },
  {
    step: "02",
    icon: "architecture",
    title: "Analyze",
    description: "Seven specialists examine static signals, explain their findings, and inform a transparent health score.",
    output: "Evidence, not a black-box verdict",
  },
  {
    step: "03",
    icon: "roadmap",
    title: "Roadmap",
    description: "Turn findings into prioritized risks and a phased renovation plan. Export the briefing and share the next steps.",
    output: "A clearer starting point for change",
  },
] as const;

const METRICS = [
  { value: "07", label: "specialist analyzers" },
  { value: "0–100", label: "explainable health score" },
  { value: "P0–P3", label: "risk priority framework" },
  { value: "03", label: "portable export formats" },
] as const;

/** Introduces the assessment workflow without fetching or simulating live results. */
export default function HomePage() {
  return (
    <div className={styles.landing} data-landing-page>
      <a className={styles.skipLink} href="#landing-content">Skip to content</a>
      <Shell>
        <div id="landing-content" tabIndex={-1}>
          <section className={styles.hero} aria-labelledby="hero-title">
            <AuroraBackground />
            <div className={`${styles.container} ${styles.heroGrid}`}>
              <div className={styles.heroCopy}>
                <p className={styles.eyebrow}>
                  <span className={styles.statusDot} />
                  Evidence-backed repository intelligence
                </p>
                <h1 id="hero-title" className={styles.title}>
                  Legacy code.<br /><span>Clear direction.</span>
                </h1>
                <p className={styles.heroDescription}>
                  Understand what you inherited. See what needs attention.
                  Turn an unfamiliar repository into an evidence-backed plan
                  for what comes next.
                </p>
                <div className={styles.actions}>
                  <Link href={ANALYZE_PATH} className={styles.primaryButton}>
                    Analyze a repository <LandingIcon name="arrow" />
                  </Link>
                  <Link href={DASHBOARD_PREVIEW_PATH} className={styles.secondaryButton}>
                    Explore dashboard preview
                  </Link>
                </div>
                <p className={styles.trustNote}>
                  <LandingIcon name="security" />
                  Public GitHub repositories. Static analysis. No code execution.
                </p>
              </div>

              <figure className={styles.preview} aria-labelledby="preview-caption">
                <div className={styles.previewHeader}>
                  <span><LandingIcon name="repository" /> Repository briefing</span>
                  <span className={styles.exampleBadge}>Illustrative example</span>
                </div>
                <div className={styles.previewBody}>
                  <div className={styles.scoreSummary}>
                    <div className={styles.scoreRing}>
                      <svg viewBox="0 0 120 120" aria-hidden="true" focusable="false">
                        <circle className={styles.ringTrack} cx="60" cy="60" r="52" />
                        <circle
                          className={styles.ringValue}
                          cx="60"
                          cy="60"
                          r="52"
                          pathLength={MAX_HEALTH_SCORE}
                          strokeDasharray={`${EXAMPLE_HEALTH_SCORE} ${MAX_HEALTH_SCORE}`}
                        />
                      </svg>
                      <div><strong>{EXAMPLE_HEALTH_SCORE}</strong><span>/ {MAX_HEALTH_SCORE}</span></div>
                    </div>
                    <div className={styles.scoreCopy}>
                      <p className={styles.previewLabel}>REPOSITORY HEALTH</p>
                      <h2>A score with a why.</h2>
                      <p>Visible signals. Explained trade-offs.<br />A starting point, not a verdict.</p>
                    </div>
                  </div>
                  <div className={styles.evidenceCard}>
                    <div className={styles.evidenceHeading}>
                      <span><LandingIcon name="testing" /> Testing signal</span>
                      <span className={styles.reviewBadge}>Review</span>
                    </div>
                    <p>No test files detected in the inspected snapshot.</p>
                    <span className={styles.evidenceDetail}>Verify the signal before planning a change.</span>
                  </div>
                  <div className={styles.roadmapPreview}>
                    <span className={styles.previewLabel}>FROM FINDING TO NEXT STEP</span>
                    <div><LandingIcon name="roadmap" /><span>Establish a testing baseline</span><LandingIcon name="arrow" /></div>
                  </div>
                </div>
                <figcaption id="preview-caption" className={styles.previewFooter}>
                  <span>Example only · not a live assessment</span>
                  <div aria-label="Available export formats">
                    {EXPORT_FORMATS.map((format) => <span key={format}>{format}</span>)}
                  </div>
                </figcaption>
              </figure>
            </div>
          </section>

          <div className={styles.container}>
            <dl className={styles.metrics} aria-label="Assessment capabilities">
              {METRICS.map(({ value, label }) => (
                <div key={label}><dt>{label}</dt><dd>{value}</dd></div>
              ))}
            </dl>

            <section className={styles.section} aria-labelledby="workflow-title">
              <div className={styles.sectionHeading}>
                <div>
                  <p className={styles.eyebrow}>HOW IT WORKS</p>
                  <h2 id="workflow-title">From repository to a way forward.</h2>
                </div>
                <p>Less time finding your bearings.<br />More clarity on the next right change.</p>
              </div>
              <ol className={styles.workflow}>
                {WORKFLOW.map(({ step, icon, title, description, output }) => (
                  <li key={step} className={styles.step} data-workflow-step>
                    <div className={styles.stepTop}>
                      <span className={styles.iconTile}><LandingIcon name={icon} /></span>
                      <span className={styles.stepNumber} aria-hidden="true">{step}</span>
                    </div>
                    <h3>{title}</h3>
                    <p>{description}</p>
                    <div className={styles.stepOutput}><LandingIcon name="check" />{output}</div>
                  </li>
                ))}
              </ol>
            </section>

            <section className={styles.section} aria-labelledby="specialists-title">
              <div className={styles.sectionHeading}>
                <div>
                  <p className={styles.eyebrow}>SEVEN SPECIALIST PERSPECTIVES</p>
                  <h2 id="specialists-title">The bigger picture. The finer details.</h2>
                </div>
                <p>One assessment, multiple lenses.<br />Findings grounded in repository evidence.</p>
              </div>
              <div className={styles.specialists}>
                {SPECIALISTS.map(({ icon, title, description, signal }) => (
                  <article key={title} className={styles.specialist} data-specialist>
                    <span className={styles.iconTile}><LandingIcon name={icon} /></span>
                    <h3>{title}</h3>
                    <p>{description}</p>
                    <span className={styles.signal}>{signal}</span>
                  </article>
                ))}
              </div>
              <p className={styles.scopeNote}>
                Static signals guide investigation. They do not replace a security audit,
                measured test coverage, or engineering judgment.
              </p>
            </section>

            <footer className={styles.footer}>
              <p>Built for the IBM Bob 2.0 Hackathon.</p>
              <Link href={ANALYZE_PATH}>Start with your repository <LandingIcon name="arrow" /></Link>
            </footer>
          </div>
        </div>
      </Shell>
    </div>
  );
}
