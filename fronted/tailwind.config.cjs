/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./index.html","./src/**/*.{vue,ts}"],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        primary: "#165DFF",
        secondary: "#0FC6C2",
        success: "#00B42A",
        warning: "#FF7D00",
        danger: "#F53F3F",
        info: "#86909C",
        dark: { 100: "#1D2129", 200: "#141414", 300: "#0A0A0A" },
        light:{ 100: "#F2F3F5", 200: "#F7F8FA", 300: "#FFFFFF" }
      },
      fontFamily: { inter: ["Inter","system-ui","sans-serif"] },
      boxShadow: {
        card: "0 2px 14px 0 rgba(0,0,0,.06)",
        dropdown: "0 4px 16px 0 rgba(0,0,0,.12)"
      }
    }
  },
  plugins: []
}
