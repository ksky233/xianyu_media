import { ArrowLeft, Save } from 'lucide-react'
import { useEffect, useState } from 'react'
import type { FormEvent } from 'react'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Label } from '@/components/ui/Label'
import { Textarea } from '@/components/ui/Textarea'
import {
  createVideoFormValues,
  type VideoFormValues,
  urlStatusOptions,
  videoTypeOptions,
} from '@/features/video/schemas/video-schema'

interface VideoFormProps {
  initialValues?: VideoFormValues
  submitLabel: string
  isSubmitting: boolean
  error?: string
  onSubmit: (values: VideoFormValues) => void
  onCancel: () => void
}

export function VideoForm({
  initialValues = createVideoFormValues(),
  submitLabel,
  isSubmitting,
  error,
  onSubmit,
  onCancel,
}: VideoFormProps) {
  const [values, setValues] = useState<VideoFormValues>(initialValues)

  useEffect(() => {
    setValues(initialValues)
  }, [initialValues])

  function updateValue<Key extends keyof VideoFormValues>(field: Key, value: VideoFormValues[Key]) {
    setValues((currentValues) => ({
      ...currentValues,
      [field]: value,
    }))
  }

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    onSubmit(values)
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-6 rounded-lg bg-white p-6 shadow-sm ring-1 ring-slate-200/70">
      <div className="grid gap-5 md:grid-cols-2">
        <div className="space-y-2">
          <Label htmlFor="video-title">标题 *</Label>
          <Input
            id="video-title"
            value={values.title}
            onChange={(event) => updateValue('title', event.target.value)}
            required
          />
        </div>

        <div className="space-y-2">
          <Label htmlFor="video-type">类型</Label>
          <select
            id="video-type"
            value={values.type}
            onChange={(event) => updateValue('type', event.target.value)}
            className="h-10 w-full rounded-lg border border-slate-200 bg-white px-3 text-sm outline-none focus:border-[var(--app-btn-color-primary)] focus:ring-2 focus:ring-[var(--app-btn-color-primary)]/20"
          >
            <option value="">未选择</option>
            {videoTypeOptions.map((type) => (
              <option key={type} value={type}>
                {type}
              </option>
            ))}
          </select>
        </div>

        <div className="space-y-2">
          <Label htmlFor="video-cover">封面 URL</Label>
          <Input
            id="video-cover"
            value={values.cover_url}
            onChange={(event) => updateValue('cover_url', event.target.value)}
            placeholder="https://..."
          />
        </div>

        <div className="space-y-2">
          <Label htmlFor="video-rating">评分</Label>
          <Input
            id="video-rating"
            type="number"
            min="0"
            max="10"
            step="0.1"
            value={values.rating}
            onChange={(event) => updateValue('rating', event.target.value)}
            placeholder="0-10"
          />
        </div>

        <div className="space-y-2">
          <Label htmlFor="video-quality">清晰度标签</Label>
          <Input
            id="video-quality"
            value={values.quality_tag}
            onChange={(event) => updateValue('quality_tag', event.target.value)}
            placeholder="1080P / 720P / WEB-DL"
          />
        </div>

        <div className="space-y-2">
          <Label htmlFor="video-episode">集数</Label>
          <Input
            id="video-episode"
            type="number"
            min="0"
            value={values.episode_count}
            onChange={(event) => updateValue('episode_count', event.target.value)}
          />
        </div>

        <div className="space-y-2">
          <Label htmlFor="video-year">年份</Label>
          <Input
            id="video-year"
            type="number"
            min="1900"
            max="2100"
            value={values.year}
            onChange={(event) => updateValue('year', event.target.value)}
          />
        </div>

        <div className="space-y-2">
          <Label htmlFor="video-status">网盘状态</Label>
          <select
            id="video-status"
            value={values.url_status}
            onChange={(event) => updateValue('url_status', Number(event.target.value))}
            className="h-10 w-full rounded-lg border border-slate-200 bg-white px-3 text-sm outline-none focus:border-[var(--app-btn-color-primary)] focus:ring-2 focus:ring-[var(--app-btn-color-primary)]/20"
          >
            {urlStatusOptions.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </div>
      </div>

      <div className="space-y-2">
        <Label htmlFor="video-actors">演员</Label>
        <Input
          id="video-actors"
          value={values.actors}
          onChange={(event) => updateValue('actors', event.target.value)}
          placeholder="多个演员用逗号分隔"
        />
      </div>

      <div className="space-y-2">
        <Label htmlFor="video-description">描述</Label>
        <Textarea
          id="video-description"
          value={values.description}
          onChange={(event) => updateValue('description', event.target.value)}
          rows={4}
        />
      </div>

      <div className="grid gap-5 md:grid-cols-3">
        <div className="space-y-2">
          <Label htmlFor="video-baidu">百度网盘</Label>
          <Input
            id="video-baidu"
            value={values.baidu_url}
            onChange={(event) => updateValue('baidu_url', event.target.value)}
          />
        </div>

        <div className="space-y-2">
          <Label htmlFor="video-quark">夸克网盘</Label>
          <Input
            id="video-quark"
            value={values.quark_url}
            onChange={(event) => updateValue('quark_url', event.target.value)}
          />
        </div>

        <div className="space-y-2">
          <Label htmlFor="video-other-cloud">其他网盘</Label>
          <Input
            id="video-other-cloud"
            value={values.other_cloud_url}
            onChange={(event) => updateValue('other_cloud_url', event.target.value)}
          />
        </div>
      </div>

      <div className="space-y-2">
        <Label htmlFor="video-marketing">营销文本</Label>
        <Textarea
          id="video-marketing"
          value={values.marketing_text}
          onChange={(event) => updateValue('marketing_text', event.target.value)}
          rows={5}
        />
      </div>

      {error ? (
        <div className="rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-600">{error}</div>
      ) : null}

      <div className="flex flex-wrap gap-3 pt-2">
        <Button type="submit" disabled={isSubmitting}>
          <Save className="h-4 w-4" />
          {isSubmitting ? '保存中...' : submitLabel}
        </Button>
        <Button variant="outline" onClick={onCancel}>
          <ArrowLeft className="h-4 w-4" />
          返回列表
        </Button>
      </div>
    </form>
  )
}
