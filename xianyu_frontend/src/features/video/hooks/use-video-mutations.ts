import { useMutation, useQueryClient } from '@tanstack/react-query'
import {
  createVideo,
  deleteVideo,
  updateVideo,
} from '@/features/video/api/video-api'
import type { VideoCreate, VideoUpdate } from '@/features/video/schemas/video-schema'

interface MutationOptions {
  onSuccess?: () => void
}

export function useCreateVideoMutation(options?: MutationOptions) {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (data: VideoCreate) => createVideo(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['videos'] })
      options?.onSuccess?.()
    },
  })
}

export function useUpdateVideoMutation(videoId: number, options?: MutationOptions) {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (data: VideoUpdate) => updateVideo(videoId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['videos'] })
      queryClient.invalidateQueries({ queryKey: ['video', videoId] })
      options?.onSuccess?.()
    },
  })
}

export function useDeleteVideoMutation() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (id: number) => deleteVideo(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['videos'] })
    },
  })
}
