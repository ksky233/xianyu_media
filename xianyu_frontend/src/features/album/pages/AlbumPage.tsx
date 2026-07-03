import { Music } from 'lucide-react'

export function AlbumPage() {
  return (
    <div className="p-8">
      <div className="flex min-h-96 items-center justify-center rounded-lg border border-dashed border-slate-300 bg-white/60">
        <div className="text-center">
          <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-slate-100 text-slate-400">
            <Music className="h-6 w-6" />
          </div>
          <h1 className="mt-4 text-xl font-semibold text-slate-800">音乐专辑</h1>
          <p className="mt-2 text-sm text-slate-500">这个模块暂时保留入口，后续再迁移具体业务。</p>
        </div>
      </div>
    </div>
  )
}
