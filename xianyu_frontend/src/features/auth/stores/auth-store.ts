import { create } from 'zustand'
import { createJSONStorage, persist } from 'zustand/middleware'
import type { UserInfo } from '@/features/auth/api/auth-api'
import { isJwtExpired } from '@/features/auth/utils/token'

interface AuthState {
  _hasHydrated: boolean
  token: string | null
  user: UserInfo | null
  isAuthenticated: boolean
  login: (token: string, user: UserInfo) => void
  logout: () => void
  updateUser: (user: UserInfo) => void
  _setHasHydrated: (state: boolean) => void
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      _hasHydrated: false,
      token: null,
      user: null,
      isAuthenticated: false,
      login: (token, user) =>
        set({
          token,
          user,
          isAuthenticated: true,
        }),
      logout: () =>
        set({
          token: null,
          user: null,
          isAuthenticated: false,
        }),
      updateUser: (user) =>
        set({
          user,
        }),
      _setHasHydrated: (state) =>
        set({
          _hasHydrated: state,
        }),
    }),
    {
      name: 'auth-storage',
      storage: createJSONStorage(() => localStorage),
      onRehydrateStorage: () => (state) => {
        if (!state?.token || isJwtExpired(state.token)) {
          state?.logout()
        }

        state?._setHasHydrated(true)
      },
      partialize: (state) => ({
        token: state.token,
        user: state.user,
        isAuthenticated: state.isAuthenticated,
      }),
    },
  ),
)
