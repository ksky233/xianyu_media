import { useMemo } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { LoadingState } from '@/components/common/LoadingState'
import { Button } from '@/components/ui/Button'
import { VideoForm } from '@/features/video/parts/VideoForm'
import { useVideoDetail } from '@/features/video/hooks/use-video-detail'
import { useUpdateVideoMutation } from '@/features/video/hooks/use-video-mutations'
import {
  createVideoFormValues,
  videoFormValuesToPayload,
  type VideoFormValues,
} from '@/features/video/schemas/video-schema'

export function VideoEditPage() {
  const navigate = useNavigate()
  const { id } = useParams()
  const parsedId = id ? Number(id) : null
  const isValidVideoId = parsedId !== null && Number.isInteger(parsedId)
  const videoId = isValidVideoId ? parsedId : 0
  const videoDetailQuery = useVideoDetail(isValidVideoId ? videoId : null)
  const updateVideoMutation = useUpdateVideoMutation(videoId, {
    onSuccess: () => navigate('/video'),
  })
  const video = videoDetailQuery.data?.data ?? null
  const initialValues = useMemo(() => createVideoFormValues(video), [video])
  const loadError = videoDetailQuery.error instanceof Error ? videoDetailQuery.error.message : ''
  const updateError = updateVideoMutation.error instanceof Error ? updateVideoMutation.error.message : ''

  function handleSubmit(values: VideoFormValues) {
    updateVideoMutation.mutate(videoFormValuesToPayload(values))
  }

  if (!isValidVideoId) {
    return (
      <div className="space-y-4 p-8">
        <h1 className="text-2xl font-semibold text-slate-950">视频 ID 无效</h1>
        <Button variant="outline" onClick={() => navigate('/video')}>
          返回列表
        </Button>
      </div>
    )
  }

  if (videoDetailQuery.isLoading) {
    return <LoadingState text="正在加载视频详情..." />
  }

  if (loadError || !video) {
    return (
      <div className="space-y-4 p-8">
        <h1 className="text-2xl font-semibold text-slate-950">无法加载视频</h1>
        <p className="text-sm text-red-600">{loadError || '视频不存在'}</p>
        <Button variant="outline" onClick={() => navigate('/video')}>
          返回列表
        </Button>
      </div>
    )
  }

  return (
    <div className="mx-auto max-w-5xl space-y-6 p-8">
      <header>
        <h1 className="text-2xl font-semibold text-slate-950">编辑视频</h1>
        <p className="mt-2 text-sm text-slate-500">正在编辑：{video.title}</p>
      </header>

      <VideoForm
        initialValues={initialValues}
        submitLabel="保存修改"
        isSubmitting={updateVideoMutation.isPending}
        error={updateError}
        onSubmit={handleSubmit}
        onCancel={() => navigate('/video')}
      />
    </div>
  )
}
