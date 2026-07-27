# AlphaStock Frontend

React-based web interface for the [AlphaStock](https://github.com/Neon549/Alpha_stock) multi-agent A-share analysis system.

🌐 **Live Demo**: [alphastock.cloud](https://alphastock.cloud) · 📦 **Backend**: [Neon549/Alpha_stock](https://github.com/Neon549/Alpha_stock)

---

## Features

| Page | Description |
|---|---|
| **Home** | Landing page with product overview and entry points |
| **Chat** | Conversational interface to the multi-agent analysis pipeline — input a ticker and get fundamental / technical / sentiment verdict |
| **Stock** | Buy signal screener — daily scan across A-share stocks with KDJ + alpha factor scoring |
| **Backtest** | Run KDJ+MACD / RSI / Bollinger Band strategies with grid-search optimization; view Sharpe ratio, max drawdown, win rate |

---

## Tech Stack

| Layer | Technology |
|---|---|
| Framework | React 18 + Vite |
| Routing | React Router DOM v6 |
| State | Zustand |
| Charts | Chart.js + react-chartjs-2 |
| Auth | Google OAuth (`@react-oauth/google`) + Email/Password |
| Deployment | Tencent Cloud · Nginx · GitHub Actions CI/CD |

---

## Quick Start

```bash
cd react-app
npm install
npm run dev
```

Open [http://localhost:5173](http://localhost:5173).

The app proxies API calls to the backend. Make sure the backend is running at `http://localhost:8000` or update `VITE_API_BASE` in your `.env.local`:

```env
VITE_API_BASE=http://localhost:8000
```

---

## Project Structure

```
react-app/
├── src/
│   ├── pages/
│   │   ├── Home.jsx
│   │   ├── Chat.jsx          # Main agent chat interface
│   │   ├── Stock.jsx         # Buy signal screener
│   │   ├── Backtest.jsx      # Quantitative backtest UI
│   │   └── ResetPassword.jsx
│   ├── components/
│   │   ├── Navbar.jsx
│   │   └── AuthModal.jsx     # Login / register / Google OAuth
│   ├── store/                # Zustand stores
│   ├── api.js                # Axios instance + endpoint wrappers
│   └── constants.js
└── package.json
```

---

## Deployment

Pushes to `main` automatically deploy via GitHub Actions:

1. SSH into the Tencent Cloud server
2. `git pull origin main`
3. `npm install && npm run build`
4. `systemctl reload nginx`

Required GitHub Secrets: `SERVER_HOST`, `SERVER_USER`, `NEON_ALPHA` (SSH key).
