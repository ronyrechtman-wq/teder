import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        teder: {
          50: "#f0f4ff",
          500: "#4f6ef7",
          900: "#1a237e",
        },
      },
    },
  },
  plugins: [],
};
export default config;
