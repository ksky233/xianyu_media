import type { ReactNode } from 'react'
import { Navigate, useLocation } from 'react-router-dom'
import { useAuthStore } from '@/features/auth/stores/auth-store'

interface AuthGuardProps {
  children: ReactNode
}

export function AuthGuard({ children }: AuthGuardProps) {
  const location = useLocation()
  const { isAuthenticated, _hasHydrated } = useAuthStore()

  if (!_hasHydrated) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-[var(--app-bg-color)]">
        <div className="text-center">
          <div className="mx-auto h-10 w-10 animate-spin rounded-full border-2 border-slate-200 border-t-[var(--app-btn-color-primary)]" />
          <p className="mt-4 text-sm text-slate-500">正在加载登录状态...</p>
        </div>
      </div>
    )
  }

  if (!isAuthenticated) {
    return <Navigate to="/auth" replace state={{ from: location }} />
  }

  return <>{children}</>
}
