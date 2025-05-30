import { defineStore } from 'pinia'

export const useUserStore = defineStore('user', {
  state: () => ({
    token: '',
    userInfo: null as null | Record<string, any>
  }),
  getters: {
    isLoggedIn: (state) => !!state.token,
    currentUser: (state) => state.userInfo
  },
  actions: {
    setToken(token: string) {
      this.token = token
      localStorage.setItem('token', token)
    },
    setUserInfo(info: any) {
      this.userInfo = info
      localStorage.setItem('userInfo', JSON.stringify(info))
    },
    initializeFromStorage() {
      const token = localStorage.getItem('token')
      const userInfo = localStorage.getItem('userInfo')
      
      if (token) {
        this.token = token
      }
      if (userInfo) {
        try {
          this.userInfo = JSON.parse(userInfo)
        } catch (e) {
          console.error('Failed to parse userInfo from localStorage:', e)
        }
      }
    },
    logout() {
      this.token = ''
      this.userInfo = null
      localStorage.removeItem('token')
      localStorage.removeItem('userInfo')
    }
  }
}) 