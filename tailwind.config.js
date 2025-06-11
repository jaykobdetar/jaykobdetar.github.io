/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./index.html",
    "./search.html", 
    "./authors.html",
    "./article.html",
    "./404.html",
    "./integrated/**/*.html"
  ],
  theme: {
    extend: {
      fontFamily: {
        'inter': ['Inter', 'sans-serif'],
        'playfair': ['Playfair Display', 'serif'],
      },
      colors: {
        'indigo': {
          50: '#eef2ff',
          100: '#e0e7ff',
          200: '#c7d2fe',
          300: '#a5b4fc',
          400: '#818cf8',
          500: '#6366f1',
          600: '#4f46e5',
          700: '#4338ca',
          800: '#3730a3',
          900: '#312e81',
        }
      },
      animation: {
        'fade-in-down': 'fadeInDown 0.5s ease-out',
        'fade-in-up': 'fadeInUp 0.5s ease-out',
        'pulse': 'pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'loading': 'loading 1.5s infinite',
        'smoothTicker': 'smoothTicker 25s linear infinite',
      },
      keyframes: {
        fadeInDown: {
          'from': { opacity: '0', transform: 'translateY(-100%)' },
          'to': { opacity: '1', transform: 'translateY(0)' }
        },
        fadeInUp: {
          'from': { opacity: '0', transform: 'translateY(30px)' },
          'to': { opacity: '1', transform: 'translateY(0)' }
        },
        loading: {
          '0%': { 'background-position': '200% 0' },
          '100%': { 'background-position': '-200% 0' }
        },
        smoothTicker: {
          '0%': { transform: 'translateX(100%)' },
          '100%': { transform: 'translateX(-100%)' }
        }
      },
      backdropBlur: {
        xs: '2px',
      },
      zIndex: {
        '60': '60',
        '70': '70',
        '80': '80',
        '90': '90',
        '100': '100',
      }
    },
  },
  plugins: [
    // Add typography plugin if needed
    // require('@tailwindcss/typography'),
  ],
}