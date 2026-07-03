import { Check, Copy, Link } from 'lucide-react'
import { useState } from 'react'
import { Button } from '@/components/ui/Button'
import type { Video } from '@/features/video/schemas/video-schema'

interface VideoCloudLinksProps {
  video: Video
}

const linkLabels = [
  { key: 'baidu_url', label: '百度网盘' },
  { key: 'quark_url', label: '夸克网盘' },
  { key: 'other_cloud_url', label: '其他网盘' },
] as const

export function VideoCloudLinks({ video }: VideoCloudLinksProps) {
  const [copiedKey, setCopiedKey] = useState<string | null>(null)

  async function handleCopy(text: string, key: string) {
    await navigator.clipboard.writeText(text)
    setCopiedKey(key)
    window.setTimeout(() => setCopiedKey(null), 1600)
  }

  const availableLinks = linkLabels
    .map((item) => ({
      ...item,
      value: video[item.key],
    }))
    .filter((item) => item.value)

  if (availableLinks.length === 0) {
    return <p className="text-sm text-slate-400">暂无网盘链接</p>
  }

  return (
    <div className="space-y-2">
      {availableLinks.map((item) => (
        <div
          key={item.key}
          className="flex items-center gap-3 rounded-lg border border-slate-200 bg-white px-3 py-2"
        >
          <Link className="h-4 w-4 shrink-0 text-slate-400" />
          <div className="min-w-0 flex-1">
            <p className="text-xs text-slate-500">{item.label}</p>
            <p className="truncate text-sm font-medium text-slate-800">{item.value}</p>
          </div>
          <Button
            size="icon"
            variant="ghost"
            title={`复制${item.label}`}
            onClick={() => handleCopy(item.value ?? '', item.key)}
          >
            {copiedKey === item.key ? <Check className="h-4 w-4" /> : <Copy className="h-4 w-4" />}
          </Button>
        </div>
      ))}
    </div>
  )
}
