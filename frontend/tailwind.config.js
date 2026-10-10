/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          orange: '#ff6900',
          'orange-hover': '#e65c00',
          'orange-light': '#fff7ed',
          'orange-border': '#ffedd5',
        },
        surface: {
          canvas: '#f3f4f6',
          sidebar: '#fbfbfb',
          card: '#ffffff',
          subtle: '#f8f9fa',
          hover: '#f1f3f5',
          border: '#e8eaed',
        }
      },
      fontFamily: {
        sans: ['"Plus Jakarta Sans"', 'system-ui', '-apple-system', 'sans-serif'],
        mono: ['"JetBrains Mono"', '"SF Mono"', 'Menlo', 'monospace'],
      },
      boxShadow: {
        'subtle': '0 1px 3px 0 rgba(0, 0, 0, 0.04), 0 1px 2px 0 rgba(0, 0, 0, 0.02)',
        'float': '0 10px 30px -10px rgba(0, 0, 0, 0.06), 0 4px 6px -2px rgba(0, 0, 0, 0.02)',
        'orange-sm': '0 2px 10px rgba(255, 105, 0, 0.25)',
      }
    },
  },
  plugins: [],
}
