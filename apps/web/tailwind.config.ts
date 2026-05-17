import type { Config } from 'tailwindcss';

const config: Config = {
  content: ['./src/**/*.{ts,tsx}'],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        bg: {
          DEFAULT: '#0b0e14',
          surface: '#11151c',
          elevated: '#161b24',
        },
        border: {
          DEFAULT: '#1f2530',
          subtle: '#171c25',
        },
        text: {
          DEFAULT: '#e6e8ec',
          muted: '#8b94a3',
          subtle: '#5a6271',
        },
        accent: {
          DEFAULT: '#4f8cff',
          green: '#22c55e',
          red: '#ef4444',
          amber: '#f59e0b',
        },
      },
      fontFamily: {
        sans: ['ui-sans-serif', 'system-ui', '-apple-system', 'Segoe UI', 'Roboto', 'sans-serif'],
        mono: ['ui-monospace', 'SFMono-Regular', 'Menlo', 'Consolas', 'monospace'],
      },
    },
  },
  plugins: [],
};

export default config;
