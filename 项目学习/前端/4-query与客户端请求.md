# Query 与客户端请求

## 以 VideoListPage 为例：一条 Query 链路如何发生

在当前 Vite 版本里，视频列表页的入口是 `src/features/video/pages/VideoListPage.tsx`。这个页面本身主要负责页面状态和页面组合，例如当前页码 `params`、搜索表单值 `searchValues`、是否使用条件搜索 `isConditionSearch`、当前选中的视频 `selectedVideo`，以及详情弹窗是否打开 `isDetailOpen`。这些状态都属于页面交互状态，也就是只影响当前页面如何展示和如何触发请求。

真正发起列表查询的代码是这一句：

```ts
const videoListQuery = useVideoList(params, isConditionSearch)
```

`useVideoList` 位于 `src/features/video/hooks/use-video-list.ts`，它内部调用 TanStack Query 的 `useQuery`：

```ts
return useQuery({
  queryKey: ['videos', isConditionSearch, params],
  queryFn: () => (isConditionSearch ? conditionSearchVideos(params) : getVideos(params)),
})
```

这里的 `queryKey` 是这次查询在缓存系统里的身份标识。`['videos', isConditionSearch, params]` 表示同样是视频列表，但普通列表和条件搜索要区分，不同页码、不同筛选参数也要区分。只要 `params` 或 `isConditionSearch` 变化，`queryKey` 就会变化，TanStack Query 会认为这是另一次查询，并执行对应的 `queryFn`。如果之后再次访问同一个 `queryKey`，TanStack Query 可以根据缓存策略复用之前的数据，而不是把每一次组件渲染都变成一次真实 HTTP 请求。

`queryFn` 是真正获取数据的函数。当前代码里它根据 `isConditionSearch` 选择两个业务 API：普通列表走 `getVideos(params)`，条件搜索走 `conditionSearchVideos(params)`。这两个函数位于 `src/features/video/api/video-api.ts`，它们负责把前端的业务参数转换成后端接口需要的请求形式。普通列表会把 `page`、`size`、`type` 变成 URL 查询参数，然后请求 `/api/v1/videos`；条件搜索会把空值过滤掉，然后用 POST 请求 `/api/v1/videos/condition-search`。

业务 API 并不直接写完整的 `fetch` 细节，而是统一调用 `src/lib/api-client.ts` 里的 `apiClient`。`apiClient` 会拼接后端地址、读取并携带登录 token、处理 JSON 请求体、解析后端统一响应、把业务失败转换为前端错误，并在 token 失效时清理登录态和跳转登录页。也就是说，`video-api.ts` 只描述“视频业务要请求哪个接口”，`api-client.ts` 负责“所有接口请求都要遵守的通用规则”。

完整链路可以这样看：

```txt
VideoListPage
  -> useVideoList(params, isConditionSearch)
    -> useQuery({ queryKey, queryFn })
      -> getVideos(params) 或 conditionSearchVideos(params)
        -> apiClient(...)
          -> FastAPI 后端接口
```

当请求完成后，TanStack Query 会把结果放回 `videoListQuery`。页面通过 `videoListQuery.data?.data` 取出后端返回的分页数据，通过 `videoListQuery.isLoading` 判断是否展示加载状态，通过 `videoListQuery.error` 判断是否展示错误信息。页面拿到 `items`、`total`、`page`、`size` 之后，再把它们传给 `VideoTableSection` 和 `VideoPaginationSection`，完成最终渲染。

## TanStack Query 负责什么

TanStack Query 处理的是服务端状态，也就是来自后端接口、会缓存、会过期、会重新请求的数据。视频列表、视频详情、用户信息这类数据都属于服务端状态，因为它们的真实来源在后端和数据库，而不是某个 React 组件内部。

当前项目在 `src/lib/query-client.ts` 创建了全局 `queryClient`，并配置了默认行为：查询结果 30 秒内认为是新鲜的，请求失败时重试 1 次，窗口重新聚焦时不自动重新请求。随后 `src/app/providers.tsx` 使用 `QueryClientProvider` 把这个 `queryClient` 注入整个 React 应用，所以页面和业务 Hook 才能使用 `useQuery`、`useMutation`、`useQueryClient` 这些能力。

TanStack Query 的核心作用不是替你写 HTTP 请求，而是管理请求生命周期。它会记录一次查询是否正在加载、是否出错、是否成功，会根据 `queryKey` 缓存请求结果，会在参数变化时自动重新执行查询，也会在新增、编辑、删除成功后通过 `invalidateQueries` 让相关列表重新变成需要刷新。例如删除视频后，`use-video-mutations.ts` 里会调用 `queryClient.invalidateQueries({ queryKey: ['videos'] })`，这表示视频列表相关缓存已经过期，后续需要重新获取最新数据。

因此，TanStack Query 更像是前端的数据调度层。它关心的是“这份远程数据现在处于什么状态、是否可以复用、什么时候重新取”，而不是“Authorization 请求头怎么加、后端地址是什么、响应体 code 怎么判断”。

## api-client 与 features/**/api 负责什么

`src/lib/api-client.ts` 是通用 HTTP 请求底座。它不表达具体业务含义，只规定所有请求共有的规则：后端基础地址来自 `VITE_API_BASE_URL`，没有配置时默认请求 `http://localhost:7000`；请求前从认证状态里读取 token，并自动添加 `Authorization: Bearer ...`；请求体是普通对象时自动转成 JSON；响应回来后统一判断 HTTP 状态码和后端业务 `code`；认证失效时统一退出登录并跳转 `/auth`。

`features/**/api` 是业务接口层。以 `src/features/video/api/video-api.ts` 为例，它知道视频模块有哪些接口，例如获取视频列表、条件搜索、新增视频、编辑视频、删除视频；它也知道这些接口的参数应该怎么整理，例如普通列表使用 URL 查询参数，条件搜索使用 POST body。它不应该关心 token 怎么存、401 怎么处理、JSON 怎么序列化，因为这些规则已经下沉到 `api-client`。

两者的边界可以用一句话概括：`features/**/api` 描述业务接口，`api-client` 执行通用请求规则。前者回答“我要请求什么”，后者回答“请求应该怎么发”。

再加上 TanStack Query 后，三层职责是这样的：

```txt
TanStack Query
  管缓存、加载状态、错误状态、重试、刷新和失效

features/**/api
  管业务接口路径、请求方法、业务参数整理和返回类型

api-client
  管 HTTP 细节、基础地址、请求头、token、JSON、统一响应和认证失效
```

对比旧 Next 项目，原来的 `lib/api/auth.ts` 和 `lib/api/video.ts` 同时承担了业务接口和通用请求封装的职责，每个文件里都重复写了 `API_BASE_URL`、`getAuthHeaders`、`fetch`、错误处理等代码。现在迁移到 Vite 后，这些通用逻辑集中到了 `api-client.ts`，视频、认证等模块只保留自己的业务 API；原来 `components/providers/Providers.tsx` 里创建 `QueryClient` 的逻辑，则拆成了现在的 `query-client.ts` 和 `app/providers.tsx`。

所以在当前项目里，看一个接口请求时可以按照固定顺序阅读：先看页面需要什么数据，再看对应的 `features/**/hooks` 如何用 `useQuery` 或 `useMutation` 管理这份数据，然后看 `features/**/api` 调用了哪个后端接口，最后看 `api-client` 如何统一完成真正的 HTTP 请求。这条阅读路径稳定之后，后续新增模块时也可以照着同样的方式组织代码。
