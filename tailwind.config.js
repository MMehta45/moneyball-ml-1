/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        orange: '#C75B12',
        green: '#154734',
        gold: '#E87722',
        cream: '#FDF8F3',
        dark: '#0D1F17',
      },
      fontFamily: {
        'space-mono': ['Space Mono', 'monospace'],
        'dm-sans': ['DM Sans', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
