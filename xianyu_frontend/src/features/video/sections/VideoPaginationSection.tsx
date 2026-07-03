import { ChevronLeft, ChevronRight } from 'lucide-react'
import { Button } from '@/components/ui/Button'

interface VideoPaginationSectionProps {
  total: number
  page: number
  size: number
  onPageChange: (page: number) => void
}

export function VideoPaginationSection({ total, page, size, onPageChange }: VideoPaginationSectionProps) {
  const totalPages = Math.max(1, Math.ceil(total / size))
  const isFirstPage = page <= 1
  const isLastPage = page >= totalPages

  return (
    <section className="flex flex-wrap items-center justify-between gap-3 rounded-lg bg-[var(--app-card-color-light)] px-5 py-4 shadow-sm ring-1 ring-slate-200/70">
      <p className="text-sm text-slate-600">
        共 <span className="font-semibold text-slate-900">{total}</span> 条数据，第{' '}
        <span className="font-semibold text-slate-900">{page}</span> /{' '}
        <span className="font-semibold text-slate-900">{totalPages}</span> 页
      </p>

      <div className="flex gap-2">
        <Button size="sm" variant="outline" disabled={isFirstPage} onClick={() => onPageChange(page - 1)}>
          <ChevronLeft className="h-4 w-4" />
          上一页
        </Button>
        <Button size="sm" variant="outline" disabled={isLastPage} onClick={() => onPageChange(page + 1)}>
          下一页
          <ChevronRight className="h-4 w-4" />
        </Button>
      </div>
    </section>
  )
}
