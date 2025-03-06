/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // University of Toronto colors
        'uoft-blue': '#1E3765', // Pantone 655
        'uoft-light-blue': '#6FC7EA', // Pantone 2985
        'ios-blue': '#1E3765', // Replaced with U of T Blue
        'ios-blue-dark': '#15294A', // Darker shade of U of T Blue
        'ios-green': '#34C759',
        'ios-indigo': '#5856D6',
        'ios-orange': '#FF9500',
        'ios-pink': '#FF2D55',
        'ios-purple': '#AF52DE',
        'ios-red': '#FF3B30',
        'ios-teal': '#6FC7EA', // Replaced with U of T Light Blue
        'ios-yellow': '#FFCC00',
        'ios-gray': {
          50: '#F9F9F9',
          100: '#F2F2F7',
          200: '#E5E5EA',
          300: '#D1D1D6',
          400: '#C7C7CC',
          500: '#AEAEB2',
          600: '#8E8E93',
          700: '#636366',
          800: '#48484A',
          900: '#3A3A3C',
        },
      },
      borderRadius: {
        'ios': '0.85rem',
        'ios-lg': '1.25rem',
        'ios-xl': '1.5rem',
      },
      boxShadow: {
        'ios': '0 2px 10px rgba(0, 0, 0, 0.05)',
        'ios-strong': '0 4px 14px rgba(0, 0, 0, 0.1)',
        'ios-inner': 'inset 0 2px 4px rgba(0, 0, 0, 0.05)',
      },
      fontSize: {
        'ios-caption': '0.65rem',
      },
    },
    fontFamily: {
      sans: [
        '-apple-system',
        'BlinkMacSystemFont',
        'San Francisco',
        'Helvetica Neue',
        'Helvetica',
        'Arial',
        'sans-serif',
      ],
    },
  },
  plugins: [],
}