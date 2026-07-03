import { useQuery } from '@tanstack/react-query'
import { getVideo } from '@/features/video/api/video-api'

export function useVideoDetail(videoId: number | null) {
  return useQuery({
    queryKey: ['video', videoId],
    enabled: videoId !== null,
    queryFn: () => {
      if (videoId === null) {
        throw new Error('缺少视频 ID')
      }

      return getVideo(videoId)
    },
  })
}
