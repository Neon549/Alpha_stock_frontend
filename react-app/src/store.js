import { create } from 'zustand'

export const useAuth = create((set, get) => ({
  token: localStorage.getItem('token') || null,
  username: localStorage.getItem('username') || null,

  login(token, username) {
    localStorage.setItem('token', token)
    localStorage.setItem('username', username)
    set({ token, username })
  },

  logout() {
    localStorage.removeItem('token')
    localStorage.removeItem('username')
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
