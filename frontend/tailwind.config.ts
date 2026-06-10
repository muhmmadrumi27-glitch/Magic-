import type { Config } from 'tailwindcss';
export default {
  content: [
    './app/**/*.{js,ts,jsx,tsx}',
    './components/**/*.{js,ts,jsx,tsx}'
  ],
  theme: {
    extend: {
      colors: {
        surface: '#0f172a',
        muted: '#94a3b8',
        accent: '#38bdf8'
      }
    }
  },
  plugins: []
} satisfies Config;
