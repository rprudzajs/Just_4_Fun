/** @type {import('tailwindcss').Config} */
export default {
  content: [
    './index.html',
    './src/**/*.{js,jsx,ts,tsx}'
  ],
  theme: {
    extend: {
      fontFamily: {
        display: ['"Poppins"', '"Manrope"', 'sans-serif'],
        sans: ['"Inter"', 'system-ui', 'sans-serif']
      },
      colors: {
        midnight: '#0b1026',
        aurora: '#2e8bff'
      },
      boxShadow: {
        luxe: '0 30px 80px rgba(12, 22, 53, 0.45)',
        glass: '0 12px 35px rgba(15, 34, 72, 0.4)'
      }
    }
  },
  plugins: []
};
