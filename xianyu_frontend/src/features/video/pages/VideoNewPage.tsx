import { useMemo } from 'react'
import { useNavigate } from 'react-router-dom'
import { VideoForm } from '@/features/video/parts/VideoForm'
import { useCreateVideoMutation } from '@/features/video/hooks/use-video-mutations'
import {
  createVideoFormValues,
  videoFormValuesToPayload,
  type VideoFormValues,
} from '@/features/video/schemas/video-schema'

export function VideoNewPage() {
  const navigate = useNavigate()
  const initialValues = useMemo(() => createVideoFormValues(), [])
  const createVideoMutation = useCreateVideoMutation({
    onSuccess: () => navigate('/video'),
  })
  const error = createVideoMutation.error instanceof Error ? createVideoMutation.error.message : ''

  function handleSubmit(values: VideoFormValues) {
    createVideoMutation.mutate(videoFormValuesToPayload(values))
  }

  return (
    <div className="mx-auto max-w-5xl space-y-6 p-8">
      <header>
        <h1 className="text-2xl font-semibold text-slate-950">新增视频</h1>
        <p className="mt-2 text-sm text-slate-500">录入视频基础信息、网盘链接和营销文本。</p>
      </header>

      <VideoForm
        initialValues={initialValues}
        submitLabel="创建视频"
        isSubmitting={createVideoMutation.isPending}
        error={error}
        onSubmit={handleSubmit}
        onCancel={() => navigate('/video')}
      />
    </div>
  )
}
