/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        gov: {
          primary: "#003087",
          navy: "#1e3a8a",
          saffron: "#FF9933",
          success: "#138808",
          warning: "#FFA500",
          danger: "#DC3545",
          bg: "#F7F9FC",
          text: "#1F2937",
          muted: "#475569",
          border: "#E5E7EB",
          borderStrong: "#CBD5E1"
        }
      },
      fontFamily: {
        sans: ["Inter", "Noto Sans Devanagari", "Roboto", "system-ui", "sans-serif"]
      },
      boxShadow: {
        soft: "0 10px 30px rgba(0, 31, 92, 0.08)",
        softLg: "0 18px 44px rgba(0, 31, 92, 0.12)",
        ring: "0 0 0 4px rgba(0, 48, 135, 0.14)"
      },
      borderRadius: {
        xl2: "12px",
        xl3: "16px"
      },
      keyframes: {
        "fade-up": {
          "0%": { opacity: 0, transform: "translateY(8px)" },
          "100%": { opacity: 1, transform: "translateY(0)" }
        },
        "sev-pulse": {
          "0%, 100%": { boxShadow: "0 0 0 0 rgba(220, 53, 69, .35)" },
          "50%":      { boxShadow: "0 0 0 10px rgba(220, 53, 69, 0)" }
        }
      },
      animation: {
        "fade-up": "fade-up .35s cubic-bezier(.2,.8,.2,1) both",
        "sev-pulse": "sev-pulse 1.6s infinite"
      }
    }
  },
  plugins: []
};
