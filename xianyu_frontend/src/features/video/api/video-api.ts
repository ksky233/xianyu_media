import { apiClient } from '@/lib/api-client'
import type {
  Video,
  VideoCreate,
  VideoListResponse,
  VideoQueryParams,
  VideoUpdate,
} from '@/features/video/schemas/video-schema'

function createSearchParams(params: VideoQueryParams) {
  const queryParams = new URLSearchParams()

  if (params.page) queryParams.set('page', String(params.page))
  if (params.size) queryParams.set('size', String(params.size))
  if (params.type) queryParams.set('video_type', params.type)

  return queryParams
}

function compactParams(params: VideoQueryParams) {
  return Object.fromEntries(
    Object.entries(params).filter(([, value]) => value !== undefined && value !== ''),
  ) as Record<string, string | number>
}

export function getVideos(params: VideoQueryParams) {
  const queryParams = createSearchParams(params)
  return apiClient<VideoListResponse>(`/api/v1/videos?${queryParams.toString()}`)
}

export function conditionSearchVideos(params: VideoQueryParams) {
  return apiClient<VideoListResponse>('/api/v1/videos/condition-search', {
    method: 'POST',
    body: compactParams(params),
  })
}

export function getVideo(id: number) {
  return apiClient<Video>(`/api/v1/videos/${id}`)
}

export function createVideo(data: VideoCreate) {
  return apiClient<Video>('/api/v1/videos/create', {
    method: 'POST',
    body: data,
  })
}

export function updateVideo(id: number, data: VideoUpdate) {
  return apiClient<Video>(`/api/v1/videos/${id}`, {
    method: 'PUT',
    body: data,
  })
}

export function deleteVideo(id: number) {
  return apiClient<unknown>(`/api/v1/videos/${id}`, {
    method: 'DELETE',
  })
}

export function batchDeleteVideos(ids: number[]) {
  return apiClient<unknown>('/api/v1/videos/batch-delete', {
    method: 'POST',
    body: ids,
  })
}
