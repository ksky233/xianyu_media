interface JwtPayload {
  exp?: unknown
}

function decodeBase64Url(value: string) {
  const base64 = value.replace(/-/g, '+').replace(/_/g, '/')
  const padded = base64.padEnd(Math.ceil(base64.length / 4) * 4, '=')

  return atob(padded)
}

export function getJwtExpiresAt(token: string) {
  try {
    const [, payload] = token.split('.')

    if (!payload) {
      return null
    }

    const decoded = JSON.parse(decodeBase64Url(payload)) as JwtPayload

    return typeof decoded.exp === 'number' ? decoded.exp * 1000 : null
  } catch {
    return null
  }
}

export function isJwtExpired(token: string, now = Date.now()) {
  const expiresAt = getJwtExpiresAt(token)

  return expiresAt === null || expiresAt <= now
}
