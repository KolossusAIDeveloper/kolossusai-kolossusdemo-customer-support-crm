import { create } from 'zustand'
import { persist } from 'zustand/middleware'

interface User {
  id: string
  email: string
  full_name: string
}

interface AuthStore {
  token: string | null
  user: User | null
  orgId: string | null
  setAuth: (token: string, user: User) => void
  setOrgId: (orgId: string) => void
  logout: () => void
}

export const useAuthStore = create<AuthStore>()(
  persist(
    (set) => ({
      token: null,
      user: null,
      orgId: null,
      setAuth: (token, user) => set({ token, user }),
      setOrgId: (orgId) => set({ orgId }),
      logout: () => set({ token: null, user: null, orgId: null }),
    }),
    {
      name: 'crm-auth',
      partialize: (state) => ({ token: state.token, user: state.user, orgId: state.orgId }),
    }
  )
)
