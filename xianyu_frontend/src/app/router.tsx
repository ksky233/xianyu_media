import { createBrowserRouter, Navigate } from 'react-router-dom'
import { AuthGuard } from '@/components/common/AuthGuard'
import { MainLayout } from '@/layouts/MainLayout'
import { AlbumPage } from '@/features/album/pages/AlbumPage'
import { LoginPage } from '@/features/auth/pages/LoginPage'
import { VideoEditPage } from '@/features/video/pages/VideoEditPage'
import { VideoListPage } from '@/features/video/pages/VideoListPage'
import { VideoNewPage } from '@/features/video/pages/VideoNewPage'

export const router = createBrowserRouter([
  {
    path: '/auth',
    element: <LoginPage />,
  },
  {
    path: '/',
    element: (
      <AuthGuard>
        <MainLayout />
      </AuthGuard>
    ),
    children: [
      {
        index: true,
        element: <Navigate to="/video" replace />,
      },
      {
        path: 'video',
        element: <VideoListPage />,
      },
      {
        path: 'video/new',
        element: <VideoNewPage />,
      },
      {
        path: 'video/:id/edit',
        element: <VideoEditPage />,
      },
      {
        path: 'album',
        element: <AlbumPage />,
      },
    ],
  },
  {
    path: '*',
    element: <Navigate to="/video" replace />,
  },
])
