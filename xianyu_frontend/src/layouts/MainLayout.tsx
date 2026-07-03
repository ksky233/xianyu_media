import type { LucideIcon } from 'lucide-react'
import { Clapperboard, Image, LogOut } from 'lucide-react'
import { NavLink, Outlet, useNavigate } from 'react-router-dom'
import { Button } from '@/components/ui/Button'
import { useAuthStore } from '@/features/auth/stores/auth-store'
import { cn } from '@/lib/utils'

interface NavItem {
  to: string
  label: string
  icon: LucideIcon
}

const navItems: NavItem[] = [
  {
    to: '/video',
    label: '视频资源',
    icon: Clapperboard,
  },
  {
    to: '/album',
    label: '音乐专辑',
    icon: Image,
  },
]

export function MainLayout() {
  const navigate = useNavigate()
  const { user, logout } = useAuthStore()

  function handleLogout() {
    logout()
    navigate('/auth', { replace: true })
  }

  return (
    <div className="flex min-h-screen bg-[var(--app-bg-color)] text-[var(--app-text-color)]">
      <aside className="flex w-64 shrink-0 flex-col justify-between bg-[var(--app-btn-color-primary)] p-4 text-white shadow-lg">
        <div>
          <div className="mb-8 px-2">
            <p className="text-xs font-medium uppercase tracking-wide text-white/65">Xianyu Media</p>
            <h1 className="mt-2 text-xl font-semibold">资源管理</h1>
          </div>

          <nav className="space-y-1">
            {navItems.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                className={({ isActive }) =>
                  cn(
                    'flex h-10 items-center gap-3 rounded-lg px-3 text-sm font-medium transition-colors',
                    isActive ? 'bg-white text-[var(--app-text-color)]' : 'text-white/85 hover:bg-white/15',
                  )
                }
              >
                <item.icon className="h-4 w-4" />
                {item.label}
              </NavLink>
            ))}
          </nav>
        </div>

        <div className="space-y-3">
          {user ? (
            <div className="rounded-lg bg-white/14 p-3">
              <p className="text-xs text-white/70">当前用户</p>
              <p className="mt-1 truncate text-sm font-semibold">{user.username}</p>
              <p className="mt-1 text-xs text-white/65">角色：{user.role}</p>
            </div>
          ) : null}
          <Button variant="secondary" className="w-full justify-start" onClick={handleLogout}>
            <LogOut className="h-4 w-4" />
            退出登录
          </Button>
        </div>
      </aside>

      <main className="min-w-0 flex-1">
        <Outlet />
      </main>
    </div>
  )
}
