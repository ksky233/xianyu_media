export interface Video {
  id: number
  title: string
  type?: string | null
  cover_url?: string | null
  rating?: number | null
  quality_tag?: string | null
  description?: string | null
  episode_count?: number | null
  actors?: string | null
  year?: number | null
  baidu_url?: string | null
  quark_url?: string | null
  other_cloud_url?: string | null
  url_status: number
  marketing_text?: string | null
  extra_params?: Record<string, unknown> | null
  region?: string | null
  finished?: number | null
  sale_status?: number | null
  hot_tags?: string | null
  hot_score?: number | null
  hot_reason?: string | null
  created_at: string
  updated_at?: string | null
  deleted_at?: string | null
}

export interface VideoListResponse {
  items: Video[]
  total: number
  page: number
  size: number
}

export interface VideoQueryParams {
  page?: number
  size?: number
  type?: string
  title?: string
  url_status?: number
  actors?: string
  marketing_text?: string
  year?: number
  rating?: number
  quality_tag?: string
}

export interface VideoCreate {
  title: string
  type?: string
  cover_url?: string
  rating?: number
  quality_tag?: string
  description?: string
  episode_count?: number
  actors?: string
  year?: number
  baidu_url?: string
  quark_url?: string
  other_cloud_url?: string
  url_status?: number
  marketing_text?: string
  extra_params?: Record<string, unknown>
}

export type VideoUpdate = Partial<VideoCreate>

export interface VideoSearchValues {
  title: string
  type: string
  url_status: string
  actors: string
  year: string
  quality_tag: string
}

export interface VideoFormValues {
  title: string
  type: string
  cover_url: string
  rating: string
  quality_tag: string
  description: string
  episode_count: string
  actors: string
  year: string
  baidu_url: string
  quark_url: string
  other_cloud_url: string
  url_status: number
  marketing_text: string
}

export const videoTypeOptions = ['电影', '电视剧', '动漫', '短剧'] as const

export const urlStatusOptions = [
  { value: 0, label: '全部失效' },
  { value: 1, label: '主流有效' },
  { value: 2, label: '其他有效' },
  { value: 3, label: '全部有效' },
] as const

export const emptyVideoSearchValues: VideoSearchValues = {
  title: '',
  type: '',
  url_status: '',
  actors: '',
  year: '',
  quality_tag: '',
}

export function createVideoFormValues(video?: Video | null): VideoFormValues {
  return {
    title: video?.title ?? '',
    type: video?.type ?? '',
    cover_url: video?.cover_url ?? '',
    rating: video?.rating === null || video?.rating === undefined ? '' : String(video.rating),
    quality_tag: video?.quality_tag ?? '',
    description: video?.description ?? '',
    episode_count:
      video?.episode_count === null || video?.episode_count === undefined ? '' : String(video.episode_count),
    actors: video?.actors ?? '',
    year: video?.year === null || video?.year === undefined ? '' : String(video.year),
    baidu_url: video?.baidu_url ?? '',
    quark_url: video?.quark_url ?? '',
    other_cloud_url: video?.other_cloud_url ?? '',
    url_status: video?.url_status ?? 1,
    marketing_text: video?.marketing_text ?? '',
  }
}

function cleanText(value: string) {
  const trimmedValue = value.trim()
  return trimmedValue.length > 0 ? trimmedValue : undefined
}

function cleanNumber(value: string) {
  const trimmedValue = value.trim()

  if (!trimmedValue) {
    return undefined
  }

  const numberValue = Number(trimmedValue)
  return Number.isFinite(numberValue) ? numberValue : undefined
}

function cleanInteger(value: string) {
  const numberValue = cleanNumber(value)
  return numberValue === undefined ? undefined : Math.trunc(numberValue)
}

export function videoFormValuesToPayload(values: VideoFormValues): VideoCreate {
  const payload: VideoCreate = {
    title: values.title.trim(),
    url_status: values.url_status,
  }
  const type = cleanText(values.type)
  const coverUrl = cleanText(values.cover_url)
  const rating = cleanNumber(values.rating)
  const qualityTag = cleanText(values.quality_tag)
  const description = cleanText(values.description)
  const episodeCount = cleanInteger(values.episode_count)
  const actors = cleanText(values.actors)
  const year = cleanInteger(values.year)
  const baiduUrl = cleanText(values.baidu_url)
  const quarkUrl = cleanText(values.quark_url)
  const otherCloudUrl = cleanText(values.other_cloud_url)
  const marketingText = cleanText(values.marketing_text)

  if (type) payload.type = type
  if (coverUrl) payload.cover_url = coverUrl
  if (rating !== undefined) payload.rating = rating
  if (qualityTag) payload.quality_tag = qualityTag
  if (description) payload.description = description
  if (episodeCount !== undefined) payload.episode_count = episodeCount
  if (actors) payload.actors = actors
  if (year !== undefined) payload.year = year
  if (baiduUrl) payload.baidu_url = baiduUrl
  if (quarkUrl) payload.quark_url = quarkUrl
  if (otherCloudUrl) payload.other_cloud_url = otherCloudUrl
  if (marketingText) payload.marketing_text = marketingText

  return payload
}

export function videoSearchValuesToParams(values: VideoSearchValues, pageSize: number): VideoQueryParams {
  const year = cleanInteger(values.year)

  return {
    page: 1,
    size: pageSize,
    title: cleanText(values.title),
    type: cleanText(values.type),
    url_status: values.url_status ? Number(values.url_status) : undefined,
    actors: cleanText(values.actors),
    year,
    quality_tag: cleanText(values.quality_tag),
  }
}
