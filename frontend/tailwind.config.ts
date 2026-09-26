import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#0A0A0A",
        panel: "#111318",
        line: "#262A33",
        accent: "#7CFFB2",
      },
    },
  },
  plugins: [],
};

export default config;
