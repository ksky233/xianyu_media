import { useAuthStore } from '@/features/auth/stores/auth-store'
import { isJwtExpired } from '@/features/auth/utils/token'

export interface ApiResponse<T> {
  code: number
  msg?: string | null
  message?: string | null
  data: T | null
}

type RequestBody = BodyInit | object | null

interface ApiClientOptions extends Omit<RequestInit, 'body'> {
  body?: RequestBody
}

type ApiResponseBody<T> = Partial<ApiResponse<T>> & {
  detail?: unknown
}

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:7000'
const AUTH_ERROR_CODE = 401001

function clearAuthSession() {
  useAuthStore.getState().logout()

  if (window.location.pathname !== '/auth') {
    window.location.replace('/auth')
  }
}

function readStoredToken() {
  const storeToken = useAuthStore.getState().token

  if (storeToken) {
    return storeToken
  }

  const rawStorage = localStorage.getItem('auth-storage')

  if (!rawStorage) {
    return null
  }

  try {
    const parsed = JSON.parse(rawStorage) as { state?: { token?: string | null } }
    return parsed.state?.token ?? null
  } catch {
    return null
  }
}

function buildHeaders(token: string | null, options?: ApiClientOptions) {
  const headers = new Headers(options?.headers)

  if (!headers.has('Content-Type') && options?.body && !(options.body instanceof FormData)) {
    headers.set('Content-Type', 'application/json')
  }

  if (token && !headers.has('Authorization')) {
    headers.set('Authorization', `Bearer ${token}`)
  }

  return headers
}

async function readResponseBody<T>(response: Response) {
  try {
    return (await response.json()) as ApiResponseBody<T>
  } catch {
    return {} as ApiResponseBody<T>
  }
}

function getDataDetail(data: unknown) {
  if (data && typeof data === 'object' && 'detail' in data) {
    const detail = (data as { detail?: unknown }).detail
    return typeof detail === 'string' ? detail : ''
  }

  return ''
}

function getDataErrorCode(data: unknown) {
  if (data && typeof data === 'object' && 'error_code' in data) {
    const errorCode = (data as { error_code?: unknown }).error_code
    return typeof errorCode === 'number' ? errorCode : null
  }

  return null
}

function isAuthFailure<T>(response: ApiResponseBody<T>, statusCode: number) {
  if (statusCode === 401) {
    return true
  }

  if (getDataErrorCode(response.data) === AUTH_ERROR_CODE) {
    return true
  }

  const message = getApiMessage(response).toLowerCase()

  return (
    message.includes('token') ||
    message.includes('令牌') ||
    message.includes('未认证') ||
    message.includes('认证失败')
  )
}

function getResponseMessage<T>(response: ApiResponseBody<T>) {
  return getApiMessage(response) || '请求失败'
}

function resolveBody(body: RequestBody | undefined) {
  if (body === undefined || body === null) {
    return undefined
  }

  if (typeof body === 'string' || body instanceof FormData || body instanceof Blob) {
    return body
  }

  return JSON.stringify(body)
}

export async function apiClient<T>(path: string, options?: ApiClientOptions) {
  const token = readStoredToken()

  if (token && isJwtExpired(token)) {
    clearAuthSession()
    throw new Error('登录已过期，请重新登录')
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers: buildHeaders(token, options),
    body: resolveBody(options?.body),
  })
  const responseBody = await readResponseBody<T>(response)

  if (!response.ok) {
    if (isAuthFailure(responseBody, response.status)) {
      clearAuthSession()
    }

    throw new Error(getResponseMessage(responseBody))
  }

  if (responseBody.code !== 1) {
    if (isAuthFailure(responseBody, response.status)) {
      clearAuthSession()
    }

    throw new Error(getResponseMessage(responseBody))
  }

  return responseBody as ApiResponse<T>
}

export function getApiMessage(
  response: Partial<Pick<ApiResponse<unknown>, 'msg' | 'message' | 'data'>> & { detail?: unknown },
) {
  const detail = typeof response.detail === 'string' ? response.detail : ''

  return getDataDetail(response.data) || response.msg || response.message || detail
}
