import { create } from 'zustand'

export const useAuth = create((set, get) => ({
  // Keep authentication only for the current browser session. Closing the
  // browser/tab starts a fresh session and requires a new login.
  token: sessionStorage.getItem('token') || null,
  username: sessionStorage.getItem('username') || null,

  login(token, username) {
    localStorage.removeItem('token')
    localStorage.removeItem('username')
    sessionStorage.setItem('token', token)
    sessionStorage.setItem('username', username)
    set({ token, username })
  },

  logout() {
    sessionStorage.removeItem('token')
    sessionStorage.removeItem('username')
    set({ token: null, username: null })
  },

  isLoggedIn: () => !!get().token,
}))

export const useModal = create((set) => ({
  isOpen: false,
  tab: 'login',
  open: (tab = 'login') => set({ isOpen: true, tab }),
  close: () => set({ isOpen: false }),
}))
