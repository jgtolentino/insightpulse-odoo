import type { AppProps } from 'next/app';
import { ConfigProvider, theme as antTheme } from 'antd';
import 'antd/dist/reset.css';
import '../styles/globals.css';

// Custom theme configuration following Ant Design Visual Specs
const theme = {
  token: {
    // Landing.AI Professional Color Palette
    colorPrimary: '#0272d4',      // Professional blue
    colorSuccess: '#62D134',      // Green accent
    colorWarning: '#ffbf00',      // Yellow-6
    colorError: '#f04134',        // Red-6
    colorInfo: '#6dc7e1',         // Light blue accent
    colorLink: '#0272d4',         // Link blue
    colorTextHeading: '#053e68',  // Deep blue headings
    colorText: '#4b4b4b',         // Body text

    // Typography - Landing.AI Professional Scale
    fontSize: 16,
    fontSizeHeading1: 46,         // Landing.AI H1 size
    fontSizeHeading2: 39,         // Landing.AI H2 size
    fontSizeHeading3: 28,
    fontSizeHeading4: 24,
    fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
    lineHeight: 1.4,              // Landing.AI body line-height
    lineHeightHeading1: 1.2,
    lineHeightHeading2: 1.3,

    // Spacing - 8px Grid System
    padding: 16,
    paddingSM: 12,
    paddingLG: 24,
    paddingXL: 32,
    margin: 16,
    marginSM: 12,
    marginLG: 24,
    marginXL: 32,

    // Border Radius
    borderRadius: 8,
    borderRadiusLG: 16,
    borderRadiusSM: 4,

    // Motion - Ant Design 2.x Authentic Easing
    motionDurationFast: '0.1s',
    motionDurationMid: '0.2s',
    motionDurationSlow: '0.3s',
    motionEaseInOut: 'cubic-bezier(0.645, 0.045, 0.355, 1)',
    motionEaseOut: 'cubic-bezier(0.215, 0.61, 0.355, 1)',
    motionEaseIn: 'cubic-bezier(0.55, 0.055, 0.675, 0.19)',

    // Layout
    screenXS: 480,
    screenSM: 576,
    screenMD: 768,
    screenLG: 992,
    screenXL: 1200,
    screenXXL: 1600,
  },
  components: {
    Button: {
      borderRadius: 8,              // Landing.AI style
      controlHeight: 40,
      fontSize: 14,                 // Landing.AI button font size
      fontWeight: 500,
      primaryColor: '#027eea',      // Landing.AI button blue
      algorithm: true,
    },
    Card: {
      borderRadiusLG: 12,
      paddingLG: 24,
      boxShadowTertiary: '0 1px 2px rgba(0, 0, 0, 0.04)',
    },
    Typography: {
      fontSizeHeading1: 46,         // Landing.AI H1
      fontSizeHeading2: 39,         // Landing.AI H2
      fontSizeHeading3: 28,
      fontWeightStrong: 700,        // Bold for headings
      colorTextHeading: '#053e68',  // Deep blue
      colorText: '#4b4b4b',         // Body text
      colorTextSecondary: 'rgba(75, 75, 75, 0.7)',
    },
    Input: {
      borderRadius: 8,
      controlHeight: 40,
    },
    Select: {
      borderRadius: 8,
      controlHeight: 40,
    },
  },
  algorithm: antTheme.defaultAlgorithm,
};

export default function App({ Component, pageProps }: AppProps) {
  return (
    <ConfigProvider theme={theme}>
      <Component {...pageProps} />
    </ConfigProvider>
  );
}
