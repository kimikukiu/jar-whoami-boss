/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        obsidian: {
          black: '#0a0a0f',
          dark: '#12121a',
          purple: '#1a1a2e',
        },
        neon: {
          blue: '#4a9eff',
          cyan: '#00d4ff',
          purple: '#9b59ff',
        },
        rpg: {
          gold: '#ffd700',
          silver: '#c0c0c0',
        }
      },
      fontFamily: {
        orbitron: ['Orbitron', 'sans-serif'],
        rajdhani: ['Rajdhani', 'sans-serif'],
      },
      animation: {
        'antigravity-float': 'antigravity-float 4s ease-in-out infinite',
        'pulse-glow': 'pulse-glow 2s ease-in-out infinite',
        'holographic-shift': 'holographic-shift 5s ease infinite',
      },
      boxShadow: {
        'neon': '0 0 20px rgba(74, 158, 255, 0.3)',
        'neon-strong': '0 0 40px rgba(74, 158, 255, 0.5)',
        'neon-cyan': '0 0 20px rgba(0, 212, 255, 0.3)',
      }
    },
  },
  plugins: [],
}