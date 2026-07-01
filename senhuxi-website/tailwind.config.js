/** @type {import('tailwindcss').Config} */

export default {
  darkMode: "class",
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    container: {
      center: true,
      padding: {
        DEFAULT: "1.5rem",
        lg: "2rem",
        xl: "3rem",
      },
    },
    extend: {
      colors: {
        // 米白宣纸色系
        paper: {
          50: "#FBF8F2",
          100: "#F5F1EA",
          200: "#EFEAE0",
          300: "#E4DDCE",
        },
        // 墨绿黑文本
        ink: {
          900: "#1F2A24",
          800: "#2C3530",
          700: "#3A4640",
          600: "#56625A",
        },
        // 苔藓绿 / 竹青 强调色
        moss: {
          DEFAULT: "#5B6B4E",
          light: "#7A8C68",
          dark: "#3F4A36",
        },
        bamboo: "#8FA777",
        // 赭石 / 暖陶 点缀
        ochre: "#A86B3C",
        clay: "#C98A5C",
        // 辅助
        wood: "#7A5B3D",
        mist: "#B8B2A7",
      },
      fontFamily: {
        serif: ['"Noto Serif SC"', '"Cormorant Garamond"', "serif"],
        sans: ['"Noto Sans SC"', "Inter", "system-ui", "sans-serif"],
        display: ['"Cormorant Garamond"', '"Noto Serif SC"', "serif"],
      },
      fontSize: {
        // 杂志式字号
        "display-xl": ["clamp(3.5rem, 8vw, 7rem)", { lineHeight: "1.05", letterSpacing: "-0.02em" }],
        "display-lg": ["clamp(2.5rem, 5vw, 4rem)", { lineHeight: "1.1", letterSpacing: "-0.01em" }],
        "display-md": ["clamp(2rem, 3.5vw, 3rem)", { lineHeight: "1.15" }],
      },
      letterSpacing: {
        widest2: "0.3em",
      },
      maxWidth: {
        content: "1280px",
        prose: "720px",
      },
      transitionTimingFunction: {
        soft: "cubic-bezier(0.22, 1, 0.36, 1)",
      },
      keyframes: {
        "fade-up": {
          "0%": { opacity: "0", transform: "translateY(24px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
        "breath": {
          "0%, 100%": { transform: "translateY(0)", opacity: "0.6" },
          "50%": { transform: "translateY(8px)", opacity: "1" },
        },
      },
      animation: {
        "fade-up": "fade-up 0.9s cubic-bezier(0.22, 1, 0.36, 1) both",
        "breath": "breath 2.4s ease-in-out infinite",
      },
    },
  },
  plugins: [],
};
