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

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:7000'

function readStoredToken() {
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

function buildHeaders(options?: ApiClientOptions) {
  const headers = new Headers(options?.headers)
  const token = readStoredToken()

  if (!headers.has('Content-Type') && options?.body && !(options.body instanceof FormData)) {
    headers.set('Content-Type', 'application/json')
  }

  if (token && !headers.has('Authorization')) {
    headers.set('Authorization', `Bearer ${token}`)
  }

  return headers
}

async function readErrorMessage(response: Response) {
  try {
    const errorBody = (await response.json()) as Partial<ApiResponse<unknown>> & {
      detail?: string
    }
    return errorBody.msg ?? errorBody.message ?? errorBody.detail ?? '请求失败'
  } catch {
    return '请求失败'
  }
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
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers: buildHeaders(options),
    body: resolveBody(options?.body),
  })

  if (!response.ok) {
    throw new Error(await readErrorMessage(response))
  }

  return response.json() as Promise<ApiResponse<T>>
}

export function getApiMessage(response: Pick<ApiResponse<unknown>, 'msg' | 'message'>) {
  return response.msg ?? response.message ?? ''
}
