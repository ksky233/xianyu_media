import { cn } from '@/lib/utils'

interface VideoStatusBadgeProps {
  status: number
}

const statusMap: Record<number, { label: string; className: string }> = {
  0: {
    label: '全部失效',
    className: 'border-red-200 bg-red-50 text-red-600',
  },
  1: {
    label: '主流有效',
    className: 'border-amber-200 bg-amber-50 text-amber-700',
  },
  2: {
    label: '其他有效',
    className: 'border-sky-200 bg-sky-50 text-sky-700',
  },
  3: {
    label: '全部有效',
    className: 'border-emerald-200 bg-emerald-50 text-emerald-700',
  },
}

export function VideoStatusBadge({ status }: VideoStatusBadgeProps) {
  const statusConfig = statusMap[status] ?? {
    label: '未知状态',
    className: 'border-slate-200 bg-slate-50 text-slate-600',
  }

  return (
    <span
      className={cn(
        'inline-flex h-7 items-center rounded-full border px-2.5 text-xs font-medium',
        statusConfig.className,
      )}
    >
      {statusConfig.label}
    </span>
  )
}
