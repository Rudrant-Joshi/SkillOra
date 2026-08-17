/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        bg: '#000000',
        surface: '#0A0A0A',
        surface2: '#111111',
        border: '#FFFFFF',
        borderDim: '#242424',
        green: '#39FF14',
        greenDim: '#1c8a0a',
        textDim: '#8A8A8A',
        textMute: '#4A4A4A',
      },
      fontFamily: {
        display: ['"Archivo Black"', 'sans-serif'],
        mono: ['"Space Mono"', 'monospace'],
      },
    },
  },
  plugins: [],
};
