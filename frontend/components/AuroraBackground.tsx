import styles from "./LandingPage.module.css";

/** Adds a decorative CSS aurora that respects reduced-motion preferences. */
export function AuroraBackground() {
  return <div className={styles.aurora} aria-hidden="true" />;
}
