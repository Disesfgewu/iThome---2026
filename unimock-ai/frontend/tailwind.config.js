/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        primary: "#4f46e5",
        "primary-dark": "#3525cd",
        "primary-container": "#4f46e5",
        "on-primary": "#ffffff",
        secondary: "#006c49",
        "secondary-container": "#6cf8bb",
        tertiary: "#684000",
        surface: "#fcf8ff",
        "surface-dark": "#0c0c14",
        "surface-container": "#efecf8",
        "surface-container-low": "#f5f2fe",
        "surface-container-lowest": "#ffffff",
        "surface-variant": "#e4e1ed",
        "on-surface": "#1b1b23",
        "on-surface-variant": "#464555",
        outline: "#777587",
        "outline-variant": "#c7c4d8",
        error: "#ba1a1a",
      },
      fontFamily: {
        body: ["Sora", "sans-serif"],
        mono: ["JetBrains Mono", "monospace"],
      },
    },
  },
  plugins: [],
}
