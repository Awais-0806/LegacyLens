const ICON_PATHS = {
  arrow: "M5 12h14m-6-6 6 6-6 6",
  architecture: "M9 3h6v6H9zM3 15h6v6H3zM15 15h6v6h-6zM12 9v3M6 15v-3h12v3",
  security: "m12 3 8 3v5c0 5-8 10-8 10S4 16 4 11V6l8-3Zm-4 9 3 3 5-6",
  dependencies: "m12 3 9 5-9 5-9-5 9-5ZM3 8v9l9 5 9-5V8M12 13v9M7.5 5.5l9 5",
  testing: "m9 3 6 0M10 3v6l-6 10a1.3 1.3 0 0 0 1 2h14a1.3 1.3 0 0 0 1-2L14 9V3M8 14h8",
  documentation: "M12 5C9 3 5 3 3 4v16c3-1 6-1 9 1 3-2 6-2 9-1V4c-2-1-6-1-9 1Zm0 0v16",
  maintainability: "m8 5-6 7 6 7m8-14 6 7-6 7M14 3l-4 18",
  modernization: "M4 19V9m8 10V5m8 14V2M2 22h20",
  repository: "M8 5a2 2 0 1 0-4 0 2 2 0 0 0 4 0Zm12 0a2 2 0 1 0-4 0 2 2 0 0 0 4 0ZM8 19a2 2 0 1 0-4 0 2 2 0 0 0 4 0ZM6 7v10m12-10v2a4 4 0 0 1-4 4H6",
  roadmap: "M4 5h16M4 12h10M4 19h6m6-3 4 3-4 3",
  check: "m5 12 4 4L19 6",
} as const;

type LandingIconProps = {
  name: keyof typeof ICON_PATHS;
  className?: string;
};

/** Renders a decorative icon with a consistent stroke and no client runtime. */
export function LandingIcon({ name, className }: LandingIconProps) {
  return (
    <svg
      className={className}
      width="20"
      height="20"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.5"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
      focusable="false"
    >
      <path d={ICON_PATHS[name]} />
    </svg>
  );
}
