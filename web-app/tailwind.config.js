/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: ['class', '[data-theme="dark"]'],
  theme: {
    extend: {
      colors: {
        base: 'var(--bg-base)',
        surface: 'var(--bg-surface)',
        panel: 'var(--bg-panel)',
        brand: 'var(--green-brand)',
        accent: 'var(--green-accent)',
        soft: 'var(--green-soft)',
        alert: 'var(--gold-alert)',
        primary: 'var(--text-primary)',
        secondary: 'var(--text-secondary)',
        muted: 'var(--text-muted)',
      },
      fontFamily: {
        display: ['Syne', 'sans-serif'],
        body: ['DM Sans', 'sans-serif'],
        malayalam: ['"Noto Sans Malayalam"', 'sans-serif'],
        mono: ['"JetBrains Mono"', 'monospace'],
      },
      boxShadow: {
        card: 'var(--shadow-card)',
      },
      borderColor: {
        default: 'var(--border-default)',
        subtle: 'var(--border-subtle)',
      },
      keyframes: {
        shimmer: {
          '100%': { transform: 'translateX(100%)' }
        }
      },
      animation: {
        shimmer: 'shimmer 1.5s infinite'
      }
    },
  },
  plugins: [],
}
