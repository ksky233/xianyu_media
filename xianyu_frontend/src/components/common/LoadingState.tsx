interface LoadingStateProps {
  text?: string
}

export function LoadingState({ text = '正在加载...' }: LoadingStateProps) {
  return (
    <div className="flex min-h-64 items-center justify-center">
      <div className="text-center">
        <div className="mx-auto h-9 w-9 animate-spin rounded-full border-2 border-slate-200 border-t-[var(--app-btn-color-primary)]" />
        <p className="mt-3 text-sm text-slate-500">{text}</p>
      </div>
    </div>
  )
}
