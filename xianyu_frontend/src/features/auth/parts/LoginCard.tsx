import { zodResolver } from '@hookform/resolvers/zod'
import { Database } from 'lucide-react'
import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { useLocation, useNavigate } from 'react-router-dom'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Label } from '@/components/ui/Label'
import { login } from '@/features/auth/api/auth-api'
import { loginSchema, type LoginFormValues } from '@/features/auth/schemas/auth-schema'
import { useAuthStore } from '@/features/auth/stores/auth-store'
import { getApiMessage } from '@/lib/api-client'

interface LocationState {
  from?: {
    pathname?: string
  }
}

export function LoginCard() {
  const navigate = useNavigate()
  const location = useLocation()
  const { login: saveLogin } = useAuthStore()
  const [error, setError] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)
  const from = (location.state as LocationState | null)?.from?.pathname ?? '/video'

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginFormValues>({
    resolver: zodResolver(loginSchema),
    defaultValues: {
      username: '',
      password: '',
    },
  })

  async function handleLogin(values: LoginFormValues) {
    setIsSubmitting(true)
    setError('')

    try {
      const response = await login(values)

      if (response.code === 1 && response.data) {
        saveLogin(response.data.access_token, response.data.user_info)
        navigate(from, { replace: true })
        return
      }

      setError(getApiMessage(response) || '登录失败，请检查用户名和密码')
    } catch (loginError) {
      setError(loginError instanceof Error ? loginError.message : '登录失败，请检查网络连接')
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div className="w-full max-w-md">
      <div className="mb-8 text-center">
        <div className="mb-4 flex justify-center">
          <div className="flex h-16 w-16 items-center justify-center rounded-full bg-[var(--app-btn-color-primary)]">
            <Database className="h-8 w-8 text-white" />
          </div>
        </div>
        <h1 className="text-3xl font-bold text-[var(--app-text-color)]">欢迎回来</h1>
        <p className="mt-2 text-sm text-slate-500">登录闲鱼资源管理后台</p>
      </div>

      <form onSubmit={handleSubmit(handleLogin)} className="space-y-5">
        <div className="space-y-2">
          <Label htmlFor="login-username">用户名</Label>
          <Input
            id="login-username"
            autoComplete="username"
            placeholder="请输入用户名"
            disabled={isSubmitting}
            {...register('username')}
          />
          {errors.username ? <p className="text-sm text-red-500">{errors.username.message}</p> : null}
        </div>

        <div className="space-y-2">
          <Label htmlFor="login-password">密码</Label>
          <Input
            id="login-password"
            type="password"
            autoComplete="current-password"
            placeholder="请输入密码"
            disabled={isSubmitting}
            {...register('password')}
          />
          {errors.password ? <p className="text-sm text-red-500">{errors.password.message}</p> : null}
        </div>

        {error ? (
          <div className="rounded-lg border border-red-200 bg-red-50 px-3 py-2">
            <p className="text-sm text-red-600">{error}</p>
          </div>
        ) : null}

        <Button className="h-11 w-full" type="submit" disabled={isSubmitting}>
          {isSubmitting ? '登录中...' : '登录'}
        </Button>
      </form>
    </div>
  )
}
