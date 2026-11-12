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
      white: '#FFFFFF',
      black: '#1A1917',
      paper: 'var(--color-paper)',
      paperRaised: 'var(--color-paper-2)',
      ivory: 'var(--color-paper-3)',
      ink: 'var(--color-ink)',
      inkSecondary: 'var(--color-ink-2)',
      muted: 'var(--color-muted)',
      rule: 'var(--color-rule)',
      ruleStrong: 'var(--color-rule-2)',
      forest: {
        DEFAULT: 'var(--color-forest)',
        hover: 'var(--color-forest-hover)',
        light: 'var(--color-forest-light)',
        border: 'var(--color-forest-border)'
      },
      clay: {
        DEFAULT: 'var(--color-clay)',
        hover: 'var(--color-clay-hover)',
        light: 'var(--color-clay-light)',
        border: 'var(--color-clay-border)'
      },
      slate: {
        50: 'var(--color-paper-3)',
        100: 'var(--color-paper-3)',
        200: 'var(--color-rule)',
        300: 'var(--color-ink-2)',
        400: 'var(--color-ink-2)',
        500: 'var(--color-muted)',
        600: 'var(--color-ink-2)',
        700: 'var(--color-ink-2)',
        800: 'var(--color-ink)',
        900: 'var(--color-ink)',
        950: 'var(--color-ink)'
      },
      emerald: {
        50: 'var(--color-forest-light)',
        100: 'var(--color-forest-light)',
        200: 'var(--color-forest-border)',
        300: 'var(--color-forest)',
        400: 'var(--color-forest)',
        500: 'var(--color-forest)',
        600: 'var(--color-forest-hover)',
        700: 'var(--color-forest-hover)',
      },
      yellow: {
        400: 'var(--color-warning)'
      },
      primary: 'var(--color-forest)',
      primaryHover: 'var(--color-forest-hover)',
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
        serif: ['var(--font-display)', 'serif'],
        mono: ['var(--font-mono)', 'monospace'],
      }
    }
  },
  plugins: []
}
