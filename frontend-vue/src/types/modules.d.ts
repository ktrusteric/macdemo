interface UserState {
  token: string
  userInfo: null | Record<string, any>
}

interface UserGetters {
  isLoggedIn: boolean
  currentUser: null | Record<string, any>
}

interface UserActions {
  setToken(token: string): void
  setUserInfo(info: any): void
  initializeFromStorage(): void
  logout(): void
}

declare module '@/store/user' {
  export const useUserStore: () => UserState & UserGetters & UserActions
}

declare module '@/store/*' {
  const value: any
  export default value
} 