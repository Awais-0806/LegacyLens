import { ImageResponse } from "next/og";

export const alt = "LegacyLens — evidence-backed repository intelligence";
export const size = { width: 1200, height: 630 };
export const contentType = "image/png";

/** Renders the social share card at build time without external assets or fonts. */
export default function OpengraphImage() {
  return new ImageResponse(
    (
      <div
        style={{
          width: "100%",
          height: "100%",
          display: "flex",
          flexDirection: "column",
          justifyContent: "space-between",
          backgroundColor: "#09090b",
          padding: 72,
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: 18 }}>
          <div
            style={{
              width: 44,
              height: 44,
              borderRadius: 12,
              border: "3px solid #a3e635",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
            }}
          >
            <div style={{ width: 14, height: 14, borderRadius: 999, backgroundColor: "#a3e635" }} />
          </div>
          <span style={{ color: "#ffffff", fontSize: 34, fontWeight: 700 }}>LegacyLens</span>
        </div>
        <div style={{ display: "flex", flexDirection: "column", gap: 18 }}>
          <span style={{ color: "#ffffff", fontSize: 64, fontWeight: 700, lineHeight: 1.1 }}>
            Legacy code. Clear direction.
          </span>
          <span style={{ color: "#a1a1aa", fontSize: 28, lineHeight: 1.4 }}>
            Evidence-backed health scores, specialist findings, and renovation roadmaps for public GitHub repositories.
          </span>
        </div>
        <div style={{ display: "flex", gap: 28, color: "#bef264", fontSize: 22 }}>
          <span>7 specialists</span>
          <span>0–100 health score</span>
          <span>3 export formats</span>
        </div>
      </div>
    ),
    { ...size },
  );
}
