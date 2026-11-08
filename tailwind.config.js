/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./frontend/**/*.html",
    "./frontend/**/*.js"
  ],
  corePlugins: {
    preflight: false
  },
  theme: {
    colors: {
      transparent: 'transparent',
      current: 'currentColor',
      inherit: 'inherit',
      white: 'var(--color-ink)',
      black: 'var(--color-paper)',
      slate: {
        50: 'var(--color-paper-2)',
        100: 'var(--color-paper-2)',
        200: 'var(--color-paper-3)',
        300: 'var(--color-ink-2)',
        400: 'var(--color-muted)',
        500: 'var(--color-muted)',
        600: 'var(--color-rule-2)',
        700: 'var(--color-rule)',
        800: 'var(--color-paper-2)',
        900: 'var(--color-paper)',
        950: 'var(--color-paper)'
      },
      emerald: {
        300: 'var(--color-accent)',
        400: 'var(--color-accent)',
        500: 'var(--color-accent)',
        600: 'var(--color-accent)'
      },
      yellow: {
        400: 'var(--color-accent)'
      },
      primary: 'var(--color-accent)',
      primaryHover: 'var(--color-accent)',
      dark: 'var(--color-paper)',
      slateDark: 'var(--color-paper-2)',
    },
    spacing: {
      '0': '0px',
      '0.5': 'var(--space-3xs)',
      '1': 'var(--space-3xs)',
      '1.5': 'var(--space-2xs)',
      '2': 'var(--space-xs)',
      '2.5': 'var(--space-sm)',
      '3': 'var(--space-sm)',
      '3.5': '14px',
      '4': 'var(--space-md)',
      '5': '20px',
      '6': 'var(--space-lg)',
      '7': '28px',
      '8': '32px',
      '9': '36px',
      '10': 'var(--space-xl)',
      '11': '44px',
      '12': '48px',
      '14': '56px',
      '16': 'var(--space-2xl)',
      '20': '80px',
      '24': 'var(--space-3xl)',
      '28': '112px',
      '32': '128px',
      '36': 'var(--space-4xl)',
      '40': '160px',
      '44': '176px',
      '48': '192px',
      '52': '208px',
      '56': '224px',
      '60': '240px',
      '64': '256px',
      '72': '288px',
      '80': '320px',
      '96': '384px',
      'px': '1px'
    },
    transitionProperty: {
      none: 'none',
      all: 'color, background-color, border-color, text-decoration-color, fill, stroke, opacity, box-shadow, transform, filter, backdrop-filter',
      DEFAULT: 'color, background-color, border-color, text-decoration-color, fill, stroke, opacity, box-shadow, transform, filter, backdrop-filter',
      colors: 'color, background-color, border-color, text-decoration-color, fill, stroke',
      opacity: 'opacity',
      shadow: 'box-shadow',
      transform: 'transform',
    },
    extend: {
      fontFamily: {
        sans: ['var(--font-body)', 'sans-serif'],
      }
    }
  },
  plugins: []
}
