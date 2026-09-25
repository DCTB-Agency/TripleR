/**
 * Triple R Europe — Tailwind theme tokens v0.3 ("premium industrieel")
 * Mirrors tokens.css 1:1. Use: `theme: { extend: require('./tailwind.tokens.cjs') }`
 */
const v = (n) => `var(--${n})`;
module.exports = {
  colors: {
    blue: { 50: v('blue-50'), 300: v('blue-300'), 500: v('blue-500'), 700: v('blue-700'), 800: v('blue-800'), 900: v('blue-900') },
    indigo: { 200: v('indigo-200'), 800: v('indigo-800'), 900: v('indigo-900') },
    night: { 300: v('night-300'), 700: v('night-700'), 900: v('night-900'), 950: v('night-950') },
    grey: { 50: v('grey-50'), 100: v('grey-100'), 200: v('grey-200'), 400: v('grey-400'), 600: v('grey-600') },
    ink: v('ink'), white: v('white'),
    ok: v('ok-700'), err: v('err-700'), check: { 50: v('check-50'), 700: v('check-700') },
  },
  fontFamily: {
    sans: ['Geist', 'Helvetica Neue', 'Arial', 'sans-serif'],
    mono: ['Geist Mono', 'ui-monospace', 'Menlo', 'Consolas', 'monospace'],
  },
  fontSize: {
    display: [v('fs-display'), { lineHeight: '1.02', letterSpacing: '-0.045em', fontWeight: '600' }],
    h1: [v('fs-h1'), { lineHeight: '1.1', letterSpacing: '-0.035em', fontWeight: '600' }],
    h2: [v('fs-h2'), { lineHeight: '1.1', letterSpacing: '-0.035em', fontWeight: '600' }],
    h3: [v('fs-h3'), { lineHeight: '1.2', fontWeight: '600' }],
    h4: [v('fs-h4'), { lineHeight: '1.3', fontWeight: '600' }],
    lead: [v('fs-lead'), { lineHeight: '1.6' }],
    body: [v('fs-body'), { lineHeight: '1.6' }],
    sm: [v('fs-sm'), { lineHeight: '1.55' }],
    xs: [v('fs-xs'), { lineHeight: '1.5' }],
    num: [v('fs-num'), { lineHeight: '1', letterSpacing: '-0.05em', fontWeight: '500' }],
  },
  spacing: { 1: v('s-1'), 2: v('s-2'), 3: v('s-3'), 4: v('s-4'), 5: v('s-5'), 6: v('s-6'), 8: v('s-8'), 10: v('s-10'), 12: v('s-12'), 16: v('s-16'), 20: v('s-20'), 24: v('s-24'), section: v('section-y'), gutter: v('gutter') },
  maxWidth: { container: v('container') },
  gap: { grid: v('gap') },
  screens: { sm: '480px', md: '768px', lg: '1024px', xl: '1280px' },
  borderRadius: { DEFAULT: v('radius'), lg: v('radius-lg'), pill: v('radius-pill') },
  backgroundImage: { brand: v('brand-gradient') },
  boxShadow: { card: v('shadow-card'), float: v('shadow-float'), focus: v('focus'), 'focus-dark': v('focus-dark') },
  transitionDuration: { DEFAULT: '200ms', slow: '600ms' },
  transitionTimingFunction: { DEFAULT: 'cubic-bezier(.2,.7,.2,1)' },
};
