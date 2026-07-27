import { Routes, Route } from 'react-router-dom'
import Navbar from './components/Navbar'
import AuthModal from './components/AuthModal'
import Home from './pages/Home'
import Chat from './pages/Chat'
import Backtest from './pages/Backtest'
import Stock from './pages/Stock'

export default function App() {
  return (
    <>
      <Navbar />
      <AuthModal />
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/chat" element={<Chat />} />
        <Route path="/backtest" element={<Backtest />} />
        <Route path="/stock" element={<Stock />} />
      </Routes>
    </>
  )
}
