/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./app/**/*.{js,jsx}",
    "./components/**/*.{js,jsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Emerald brand — locked. The "hired / go" green.
        brand: {
          DEFAULT: "#059669",
          light: "#10B981",
          teal: "#14B8A6",
        },
        ink: "#0F172A",
        muted: "#64748B",
        line: "#E6EEEC",
        tint: "#ECFDF5",
        tint2: "#D1FAE5",
        dash: "#6EE7B7",
      },
      backgroundImage: {
        "brand-grad": "linear-gradient(135deg,#059669,#10B981,#14B8A6)",
      },
    },
  },
  plugins: [],
};
