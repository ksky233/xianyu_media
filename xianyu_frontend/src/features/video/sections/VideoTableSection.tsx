import { Eye, Pencil, Trash2 } from 'lucide-react'
import { Button } from '@/components/ui/Button'
import { EmptyState } from '@/components/common/EmptyState'
import { VideoStatusBadge } from '@/features/video/parts/VideoStatusBadge'
import type { Video } from '@/features/video/schemas/video-schema'

interface VideoTableSectionProps {
  videos: Video[]
  isDeleting: boolean
  onView: (video: Video) => void
  onEdit: (video: Video) => void
  onDelete: (video: Video) => void
}

function formatRating(rating?: number | null) {
  return rating === null || rating === undefined ? '-' : rating
}

export function VideoTableSection({
  videos,
  isDeleting,
  onView,
  onEdit,
  onDelete,
}: VideoTableSectionProps) {
  return (
    <section className="overflow-hidden rounded-lg bg-[var(--app-card-color-light)] shadow-sm ring-1 ring-slate-200/70">
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-slate-200">
          <thead className="bg-slate-50">
            <tr>
              <th className="w-24 px-5 py-3 text-left text-xs font-semibold uppercase text-slate-500">ID</th>
              <th className="px-5 py-3 text-left text-xs font-semibold uppercase text-slate-500">标题</th>
              <th className="w-32 px-5 py-3 text-left text-xs font-semibold uppercase text-slate-500">类型</th>
              <th className="w-24 px-5 py-3 text-left text-xs font-semibold uppercase text-slate-500">评分</th>
              <th className="w-32 px-5 py-3 text-left text-xs font-semibold uppercase text-slate-500">状态</th>
              <th className="w-48 px-5 py-3 text-left text-xs font-semibold uppercase text-slate-500">操作</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-200 bg-white">
            {videos.length === 0 ? (
              <tr>
                <td colSpan={6}>
                  <EmptyState title="暂无视频数据" description="可以调整筛选条件，或新增一条视频资源。" />
                </td>
              </tr>
            ) : (
              videos.map((video) => (
                <tr key={video.id} className="hover:bg-slate-50/80">
                  <td className="whitespace-nowrap px-5 py-4 text-sm font-mono text-slate-500">{video.id}</td>
                  <td className="px-5 py-4">
                    <div className="max-w-xl">
                      <p className="truncate text-sm font-medium text-slate-900">{video.title}</p>
                      {video.quality_tag ? (
                        <p className="mt-1 text-xs text-slate-500">{video.quality_tag}</p>
                      ) : null}
                    </div>
                  </td>
                  <td className="whitespace-nowrap px-5 py-4 text-sm text-slate-600">{video.type || '-'}</td>
                  <td className="whitespace-nowrap px-5 py-4 text-sm text-slate-600">{formatRating(video.rating)}</td>
                  <td className="whitespace-nowrap px-5 py-4">
                    <VideoStatusBadge status={video.url_status} />
                  </td>
                  <td className="whitespace-nowrap px-5 py-4">
                    <div className="flex items-center gap-2">
                      <Button size="sm" variant="ghost" onClick={() => onView(video)}>
                        <Eye className="h-4 w-4" />
                        查看
                      </Button>
                      <Button size="sm" variant="ghost" onClick={() => onEdit(video)}>
                        <Pencil className="h-4 w-4" />
                        编辑
                      </Button>
                      <Button size="sm" variant="danger" disabled={isDeleting} onClick={() => onDelete(video)}>
                        <Trash2 className="h-4 w-4" />
                        删除
                      </Button>
                    </div>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </section>
  )
}
