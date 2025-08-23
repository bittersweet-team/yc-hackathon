'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/contexts/auth-context'
import { Demo, listDemos, deleteDemo, getStatusColor, getStatusLabel } from '@/services/demo'
import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'
import { Video, Plus, Clock, Download, Trash2, ExternalLink, RefreshCw, User, LogOut, Home, AlertCircle } from 'lucide-react'
import Link from 'next/link'

export default function Dashboard() {
  const { user, signOut, loading: authLoading } = useAuth()
  const [demos, setDemos] = useState<Demo[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [deletingId, setDeletingId] = useState<string | null>(null)
  const [showUserMenu, setShowUserMenu] = useState(false)
  const router = useRouter()

  useEffect(() => {
    if (!authLoading && !user) {
      router.push('/')
    }
  }, [user, authLoading, router])

  useEffect(() => {
    if (user) {
      fetchDemos()
      // Poll for updates every 5 seconds
      const interval = setInterval(fetchDemos, 5000)
      return () => clearInterval(interval)
    }
  }, [user])

  const fetchDemos = async () => {
    try {
      const data = await listDemos()
      setDemos(data.sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime()))
      setError('')
    } catch (err: any) {
      setError(err.message || 'Failed to load demos')
    } finally {
      setLoading(false)
    }
  }

  const handleDelete = async (demoId: string) => {
    if (!confirm('Are you sure you want to delete this demo?')) return
    
    setDeletingId(demoId)
    try {
      await deleteDemo(demoId)
      setDemos(demos.filter(d => d.id !== demoId))
    } catch (err: any) {
      alert('Failed to delete demo: ' + err.message)
    } finally {
      setDeletingId(null)
    }
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  if (authLoading || loading) {
    return (
      <div className="min-h-screen bg-gradient-to-b from-white via-zinc-50 to-white flex items-center justify-center">
        <div className="text-center">
          <div className="h-8 w-8 border-2 border-emerald-600 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
          <p className="text-zinc-600">Loading your demos...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-white via-zinc-50 to-white">
      {/* Navigation */}
      <nav className="sticky top-0 z-40 glass-effect border-b border-zinc-200">
        <div className="container mx-auto px-4 h-16 flex items-center justify-between">
          <Link href="/" className="flex items-center space-x-2">
            <Video className="h-6 w-6" />
            <span className="font-bold text-xl">Demo Hunters</span>
          </Link>
          
          <div className="flex items-center gap-4">
            <Link href="/">
              <Button variant="ghost" size="sm">
                <Home className="h-4 w-4 mr-2" />
                Home
              </Button>
            </Link>
            
            {user && (
              <div className="relative">
                <button
                  onClick={() => setShowUserMenu(!showUserMenu)}
                  className="flex items-center gap-2 px-3 py-1.5 rounded-full hover:bg-zinc-100 transition-colors"
                >
                  <div className="h-7 w-7 rounded-full bg-emerald-600 flex items-center justify-center">
                    <User className="h-4 w-4 text-white" />
                  </div>
                  <span className="text-sm font-medium">{user.email?.split('@')[0]}</span>
                </button>
                
                {showUserMenu && (
                  <div className="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg border border-zinc-200 py-1 z-50">
                    <div className="px-4 py-2 border-b border-zinc-200">
                      <p className="text-sm font-medium">{user.user_metadata?.full_name || 'User'}</p>
                      <p className="text-xs text-zinc-500">{user.email}</p>
                    </div>
                    <button
                      onClick={() => signOut()}
                      className="w-full text-left px-4 py-2 text-sm hover:bg-zinc-50 flex items-center gap-2"
                    >
                      <LogOut className="h-4 w-4" />
                      Sign Out
                    </button>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </nav>

      <div className="container mx-auto px-4 py-8 max-w-6xl">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-zinc-900">Your Demos</h1>
            <p className="text-zinc-600 mt-1">Track and manage your demo videos</p>
          </div>
          <Link href="/">
            <Button className="bg-emerald-600 hover:bg-emerald-700">
              <Plus className="h-4 w-4 mr-2" />
              Create New Demo
            </Button>
          </Link>
        </div>

        {/* Error message */}
        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg flex items-start gap-3">
            <AlertCircle className="h-5 w-5 text-red-600 mt-0.5" />
            <p className="text-sm text-red-700">{error}</p>
          </div>
        )}

        {/* Demos Grid */}
        {demos.length === 0 ? (
          <Card className="p-12 text-center">
            <Video className="h-12 w-12 text-zinc-400 mx-auto mb-4" />
            <h3 className="text-lg font-semibold mb-2">No demos yet</h3>
            <p className="text-zinc-600 mb-6">Create your first product demo video with one click</p>
            <Link href="/">
              <Button>
                <Plus className="h-4 w-4 mr-2" />
                Create Your First Demo
              </Button>
            </Link>
          </Card>
        ) : (
          <div className="grid gap-4">
            {demos.map((demo) => (
              <Card key={demo.id} className="p-6 hover:shadow-lg transition-shadow">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    {/* URL and Description */}
                    <div className="mb-3">
                      <a 
                        href={demo.product_url} 
                        target="_blank" 
                        rel="noopener noreferrer"
                        className="text-lg font-semibold hover:text-emerald-600 transition-colors flex items-center gap-2"
                      >
                        {new URL(demo.product_url).hostname}
                        <ExternalLink className="h-4 w-4" />
                      </a>
                      {demo.description && (
                        <p className="text-sm text-zinc-600 mt-1">{demo.description}</p>
                      )}
                    </div>

                    {/* Status and Time */}
                    <div className="flex items-center gap-4 mb-4">
                      <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium ${getStatusColor(demo.status)}`}>
                        {demo.status === 'completed' ? (
                          <span className="h-2 w-2 rounded-full bg-emerald-600" />
                        ) : demo.status === 'failed' ? (
                          <span className="h-2 w-2 rounded-full bg-red-600" />
                        ) : (
                          <RefreshCw className="h-3 w-3 animate-spin" />
                        )}
                        {getStatusLabel(demo.status)}
                      </span>
                      <span className="text-xs text-zinc-500 flex items-center gap-1">
                        <Clock className="h-3 w-3" />
                        {formatDate(demo.created_at)}
                      </span>
                    </div>

                    {/* Error Message */}
                    {demo.error_message && (
                      <div className="mb-3 p-3 bg-red-50 border border-red-200 rounded-lg">
                        <p className="text-sm text-red-700">{demo.error_message}</p>
                      </div>
                    )}

                    {/* Video Links */}
                    {demo.status === 'completed' && (
                      <div className="flex flex-wrap gap-2">
                        {demo.long_video_url && (
                          <a
                            href={demo.long_video_url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="inline-flex items-center gap-2 px-3 py-1.5 bg-zinc-100 hover:bg-zinc-200 rounded-lg text-sm font-medium transition-colors"
                          >
                            <Download className="h-4 w-4" />
                            Full Demo
                          </a>
                        )}
                        {demo.short_video_urls.map((url, index) => (
                          <a
                            key={index}
                            href={url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="inline-flex items-center gap-2 px-3 py-1.5 bg-zinc-100 hover:bg-zinc-200 rounded-lg text-sm font-medium transition-colors"
                          >
                            <Download className="h-4 w-4" />
                            Short {index + 1}
                          </a>
                        ))}
                      </div>
                    )}
                  </div>

                  {/* Delete Button */}
                  <button
                    onClick={() => handleDelete(demo.id)}
                    disabled={deletingId === demo.id}
                    className="ml-4 p-2 text-zinc-400 hover:text-red-600 transition-colors disabled:opacity-50"
                  >
                    {deletingId === demo.id ? (
                      <RefreshCw className="h-4 w-4 animate-spin" />
                    ) : (
                      <Trash2 className="h-4 w-4" />
                    )}
                  </button>
                </div>
              </Card>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}