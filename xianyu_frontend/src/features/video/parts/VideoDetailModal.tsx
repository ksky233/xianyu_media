import { X } from 'lucide-react'
import { Button } from '@/components/ui/Button'
import { VideoCloudLinks } from '@/features/video/parts/VideoCloudLinks'
import { VideoStatusBadge } from '@/features/video/parts/VideoStatusBadge'
import type { Video } from '@/features/video/schemas/video-schema'

interface VideoDetailModalProps {
  video: Video | null
  isOpen: boolean
  onClose: () => void
}

function DetailItem({ label, value }: { label: string; value?: string | number | null }) {
  if (value === null || value === undefined || value === '') {
    return null
  }

  return (
    <div className="rounded-lg border border-slate-200 bg-white px-3 py-2">
      <p className="text-xs text-slate-500">{label}</p>
      <p className="mt-1 text-sm font-medium text-slate-800">{value}</p>
    </div>
  )
}

export function VideoDetailModal({ video, isOpen, onClose }: VideoDetailModalProps) {
  if (!isOpen || !video) {
    return null
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/35 p-4">
      <div className="flex max-h-[90vh] w-full max-w-5xl flex-col overflow-hidden rounded-lg bg-[var(--app-card-color-light)] shadow-2xl">
        <div className="flex h-16 shrink-0 items-center justify-between border-b border-slate-200 px-6">
          <h2 className="text-lg font-semibold text-slate-900">视频详情</h2>
          <Button size="icon" variant="ghost" onClick={onClose} title="关闭">
            <X className="h-5 w-5" />
          </Button>
        </div>

        <div className="grid flex-1 gap-6 overflow-y-auto p-6 lg:grid-cols-[280px_1fr]">
          <div>
            {video.cover_url ? (
              <img
                src={video.cover_url}
                alt={video.title}
                className="aspect-[2/3] w-full rounded-lg object-cover ring-1 ring-slate-200"
              />
            ) : (
              <div className="flex aspect-[2/3] w-full items-center justify-center rounded-lg bg-slate-100 text-sm text-slate-400 ring-1 ring-slate-200">
                暂无封面
              </div>
            )}
          </div>

          <div className="space-y-6">
            <div>
              <div className="flex flex-wrap items-center gap-2">
                {video.type ? (
                  <span className="inline-flex h-7 items-center rounded-full bg-[var(--app-btn-color-scendary)] px-2.5 text-xs font-medium text-slate-800">
                    {video.type}
                  </span>
                ) : null}
                {video.quality_tag ? (
                  <span className="inline-flex h-7 items-center rounded-full border border-indigo-200 bg-indigo-50 px-2.5 text-xs font-medium text-indigo-700">
                    {video.quality_tag}
                  </span>
                ) : null}
                <VideoStatusBadge status={video.url_status} />
              </div>
              <h3 className="mt-3 text-2xl font-semibold text-slate-950">{video.title}</h3>
              {video.description ? (
                <p className="mt-3 whitespace-pre-wrap text-sm leading-6 text-slate-600">{video.description}</p>
              ) : null}
            </div>

            <section>
              <h4 className="mb-3 text-sm font-semibold text-slate-800">基础信息</h4>
              <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
                <DetailItem label="评分" value={video.rating} />
                <DetailItem label="集数" value={video.episode_count} />
                <DetailItem label="年份" value={video.year} />
                <DetailItem label="演员" value={video.actors} />
                <DetailItem label="地区" value={video.region} />
                <DetailItem label="热度分" value={video.hot_score} />
              </div>
            </section>

            <section>
              <h4 className="mb-3 text-sm font-semibold text-slate-800">网盘链接</h4>
              <VideoCloudLinks video={video} />
            </section>

            {video.marketing_text ? (
              <section>
                <h4 className="mb-3 text-sm font-semibold text-slate-800">营销文本</h4>
                <p className="whitespace-pre-wrap rounded-lg border border-slate-200 bg-white p-3 text-sm leading-6 text-slate-700">
                  {video.marketing_text}
                </p>
              </section>
            ) : null}

            {video.extra_params ? (
              <section>
                <h4 className="mb-3 text-sm font-semibold text-slate-800">扩展参数</h4>
                <pre className="overflow-x-auto rounded-lg border border-slate-200 bg-slate-50 p-3 text-xs text-slate-600">
                  {JSON.stringify(video.extra_params, null, 2)}
                </pre>
              </section>
            ) : null}
          </div>
        </div>
      </div>
    </div>
  )
}
