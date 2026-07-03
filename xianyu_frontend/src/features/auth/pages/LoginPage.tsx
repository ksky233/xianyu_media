import { LoginCard } from '@/features/auth/parts/LoginCard'

export function LoginPage() {
  return (
    <main className="flex min-h-screen items-center justify-center bg-[var(--app-bg-color)] px-4">
      <section className="w-full max-w-lg rounded-lg bg-[var(--app-card-color-light)] p-8 shadow-sm ring-1 ring-slate-200/70">
        <LoginCard />
      </section>
    </main>
  )
}
