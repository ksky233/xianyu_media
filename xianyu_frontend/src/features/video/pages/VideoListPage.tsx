import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { LoadingState } from '@/components/common/LoadingState'
import { VideoDetailModal } from '@/features/video/parts/VideoDetailModal'
import { VideoPaginationSection } from '@/features/video/sections/VideoPaginationSection'
import { VideoSearchSection } from '@/features/video/sections/VideoSearchSection'
import { VideoTableSection } from '@/features/video/sections/VideoTableSection'
import { useVideoList } from '@/features/video/hooks/use-video-list'
import { useDeleteVideoMutation } from '@/features/video/hooks/use-video-mutations'
import {
  emptyVideoSearchValues,
  videoSearchValuesToParams,
  type Video,
  type VideoQueryParams,
  type VideoSearchValues,
} from '@/features/video/schemas/video-schema'

export function VideoListPage() {
  const navigate = useNavigate()
  const [params, setParams] = useState<VideoQueryParams>({
    page: 1,
    size: 10,
  })
  const [searchValues, setSearchValues] = useState<VideoSearchValues>({ ...emptyVideoSearchValues })
  const [isConditionSearch, setIsConditionSearch] = useState(false)
  const [selectedVideo, setSelectedVideo] = useState<Video | null>(null)
  const [isDetailOpen, setIsDetailOpen] = useState(false)
  const videoListQuery = useVideoList(params, isConditionSearch)
  const deleteVideoMutation = useDeleteVideoMutation()

  const listData = videoListQuery.data?.data
  const videos = listData?.items ?? []
  const total = listData?.total ?? 0
  const currentPage = listData?.page ?? params.page ?? 1
  const pageSize = listData?.size ?? params.size ?? 10
  const queryError = videoListQuery.error instanceof Error ? videoListQuery.error.message : ''
  const deleteError = deleteVideoMutation.error instanceof Error ? deleteVideoMutation.error.message : ''

  function handleSearch() {
    setIsConditionSearch(true)
    setParams(videoSearchValuesToParams(searchValues, pageSize))
  }

  function handleReset() {
    setIsConditionSearch(false)
    setSearchValues({ ...emptyVideoSearchValues })
    setParams({
      page: 1,
      size: pageSize,
    })
  }

  function handlePageChange(page: number) {
    setParams((currentParams) => ({
      ...currentParams,
      page,
    }))
  }

  function handleView(video: Video) {
    setSelectedVideo(video)
    setIsDetailOpen(true)
  }

  function handleDelete(video: Video) {
    if (window.confirm(`确认删除「${video.title}」吗？`)) {
      deleteVideoMutation.mutate(video.id)
    }
  }

  return (
    <div className="space-y-6 p-8">
      <header>
        <h1 className="text-2xl font-semibold text-slate-950">视频资源管理</h1>
        <p className="mt-2 text-sm text-slate-500">管理视频资源、网盘链接、营销文本和资源状态。</p>
      </header>

      <VideoSearchSection
        values={searchValues}
        onChange={setSearchValues}
        onSearch={handleSearch}
        onReset={handleReset}
        onCreate={() => navigate('/video/new')}
      />

      {queryError || deleteError ? (
        <div className="rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-600">
          {queryError || deleteError}
        </div>
      ) : null}

      {videoListQuery.isLoading ? (
        <LoadingState text="正在加载视频列表..." />
      ) : (
        <>
          <VideoTableSection
            videos={videos}
            isDeleting={deleteVideoMutation.isPending}
            onView={handleView}
            onEdit={(video) => navigate(`/video/${video.id}/edit`)}
            onDelete={handleDelete}
          />
          <VideoPaginationSection
            total={total}
            page={currentPage}
            size={pageSize}
            onPageChange={handlePageChange}
          />
        </>
      )}

      <VideoDetailModal
        video={selectedVideo}
        isOpen={isDetailOpen}
        onClose={() => {
          setSelectedVideo(null)
          setIsDetailOpen(false)
        }}
      />
    </div>
  )
}
