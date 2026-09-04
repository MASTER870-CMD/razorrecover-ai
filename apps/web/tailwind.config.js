/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "#F8FAFC",
        surface: {
          DEFAULT: "#FFFFFF",
          subtle: "#F1F5F9",
          elevated: "#FFFFFF",
          hover: "#F8FAFC",
        },
        border: {
          subtle: "#F1F5F9",
          DEFAULT: "#E2E8F0",
          strong: "#CBD5E1",
        },
        brand: {
          50: "#FEF2F2",
          100: "#FEE2E2",
          200: "#FECACA",
          500: "#EF4444",
          600: "#DC2626", // Razorpay-inspired red
          700: "#B91C1C",
          800: "#991B1B",
          900: "#7F1D1D",
        },
        fintech: {
          emerald: "#059669",
          emeraldLight: "#ECFDF5",
          emeraldBorder: "#A7F3D0",
          rose: "#DC2626",
          roseLight: "#FEF2F2",
          roseBorder: "#FECACA",
          amber: "#D97706",
          amberLight: "#FFFBEB",
          amberBorder: "#FDE68A",
          slate: "#475569",
          slateLight: "#F8FAFC",
        },
      },
      fontFamily: {
        sans: ["Inter", "-apple-system", "BlinkMacSystemFont", "Segoe UI", "Roboto", "sans-serif"],
        mono: ["JetBrains Mono", "Menlo", "Courier New", "monospace"],
      },
    },
  },
  plugins: [],
}
