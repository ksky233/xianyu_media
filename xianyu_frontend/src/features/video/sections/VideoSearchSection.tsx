import { Plus, RotateCcw, Search } from 'lucide-react'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { videoTypeOptions, type VideoSearchValues, urlStatusOptions } from '@/features/video/schemas/video-schema'

interface VideoSearchSectionProps {
  values: VideoSearchValues
  onChange: (values: VideoSearchValues) => void
  onSearch: () => void
  onReset: () => void
  onCreate: () => void
}

export function VideoSearchSection({
  values,
  onChange,
  onSearch,
  onReset,
  onCreate,
}: VideoSearchSectionProps) {
  function updateValue<Key extends keyof VideoSearchValues>(field: Key, value: VideoSearchValues[Key]) {
    onChange({
      ...values,
      [field]: value,
    })
  }

  return (
    <section className="rounded-lg bg-[var(--app-card-color-light)] p-5 shadow-sm ring-1 ring-slate-200/70">
      <div className="mb-4 flex items-center justify-between gap-4">
        <div>
          <h2 className="text-base font-semibold text-slate-900">筛选视频</h2>
          <p className="mt-1 text-sm text-slate-500">按标题、类型、状态等条件查找资源。</p>
        </div>
        <Button onClick={onCreate}>
          <Plus className="h-4 w-4" />
          新增视频
        </Button>
      </div>

      <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-[1.4fr_1fr_1fr_1fr_1fr_auto]">
        <Input
          value={values.title}
          onChange={(event) => updateValue('title', event.target.value)}
          placeholder="搜索标题"
        />

        <select
          value={values.type}
          onChange={(event) => updateValue('type', event.target.value)}
          className="h-10 rounded-lg border border-slate-200 bg-white px-3 text-sm outline-none focus:border-[var(--app-btn-color-primary)] focus:ring-2 focus:ring-[var(--app-btn-color-primary)]/20"
        >
          <option value="">全部类型</option>
          {videoTypeOptions.map((type) => (
            <option key={type} value={type}>
              {type}
            </option>
          ))}
        </select>

        <select
          value={values.url_status}
          onChange={(event) => updateValue('url_status', event.target.value)}
          className="h-10 rounded-lg border border-slate-200 bg-white px-3 text-sm outline-none focus:border-[var(--app-btn-color-primary)] focus:ring-2 focus:ring-[var(--app-btn-color-primary)]/20"
        >
          <option value="">全部状态</option>
          {urlStatusOptions.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>

        <Input
          value={values.actors}
          onChange={(event) => updateValue('actors', event.target.value)}
          placeholder="演员"
        />

        <Input
          type="number"
          value={values.year}
          onChange={(event) => updateValue('year', event.target.value)}
          placeholder="年份"
        />

        <div className="flex gap-2">
          <Button className="flex-1 xl:flex-none" onClick={onSearch}>
            <Search className="h-4 w-4" />
            搜索
          </Button>
          <Button className="flex-1 xl:flex-none" variant="outline" onClick={onReset}>
            <RotateCcw className="h-4 w-4" />
            重置
          </Button>
        </div>
      </div>
    </section>
  )
}
