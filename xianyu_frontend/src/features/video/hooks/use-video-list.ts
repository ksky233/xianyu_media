import { useQuery } from '@tanstack/react-query'
import { conditionSearchVideos, getVideos } from '@/features/video/api/video-api'
import type { VideoQueryParams } from '@/features/video/schemas/video-schema'

export function useVideoList(params: VideoQueryParams, isConditionSearch: boolean) {
  return useQuery({
    queryKey: ['videos', isConditionSearch, params],
    queryFn: () => (isConditionSearch ? conditionSearchVideos(params) : getVideos(params)),
  })
}
