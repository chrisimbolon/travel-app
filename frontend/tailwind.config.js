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
        brand: {
          50:  "#e6f4f1",
          100: "#b3e0d8",
          200: "#80ccbf",
          300: "#4db8a6",
          400: "#26a892",
          500: "#1d9e75",  // primary — matches our teal
          600: "#0f6e56",
          700: "#085041",
          800: "#04342c",
          900: "#021a16",
        },
      },
      fontFamily: {
        sans: ["var(--font-inter)", "system-ui", "sans-serif"],
      },
      borderRadius: {
        "2xl": "1rem",
        "3xl": "1.5rem",
      },
    },
  },
  plugins: [],
};
