/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'dark-bg': '#0D1117',
        'card-bg': '#161B22',
        'border': '#30363D',
        'text-primary': '#E6EDF3',
        'text-secondary': '#8B949E',
        'accent': '#2F81F7',
        'critical': '#F85149',
        'warning': '#D29922',
        'info': '#58A6FF',
        'success': '#3FB950',
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      },
    },
  },
  plugins: [],
}
