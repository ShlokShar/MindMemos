/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./templates/*"],
  theme: {
    extend: {
      colors: {
        primarytext: "#1f3a1e",
        accent: "#88ddda",
      },
      fontFamily: {
        poppins: ["poppins", "sans-serif"]
      }
    },
  },
  plugins: [],
}

