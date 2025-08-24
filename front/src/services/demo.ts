import { createClient } from '@/lib/supabase/client'

const API_URL = process.env.DEMO_HUNTERS_API_URL || 'http://localhost:8000'

export interface Demo {
  id: string
  user_id: string
  product_url: string
  description?: string
  status: 'pending' | 'recording' | 'processing' | 'generating' | 'sending' | 'completed' | 'failed'
  long_video_url?: string
  short_video_urls: string[]
  error_message?: string
  created_at: string
  updated_at: string
}

export interface CreateDemoRequest {
  product_url: string
  description?: string
  email?: string
}

async function getAuthToken(): Promise<string> {
  const supabase = createClient()
  const { data: { session } } = await supabase.auth.getSession()

  if (!session?.access_token) {
    throw new Error('Not authenticated')
  }

  return session.access_token
}

export async function createDemo(request: CreateDemoRequest): Promise<Demo> {
  const token = await getAuthToken()

  const response = await fetch(`${API_URL}/api/demo`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify(request)
  })

  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to create demo')
  }

  return response.json()
}

export async function listDemos(): Promise<Demo[]> {
  const token = await getAuthToken()

  const response = await fetch(`${API_URL}/api/demos`, {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  })

  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to fetch demos')
  }

  return response.json()
}

export async function getDemo(demoId: string): Promise<Demo> {
  const token = await getAuthToken()

  const response = await fetch(`${API_URL}/api/demo/${demoId}`, {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  })

  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to fetch demo')
  }

  return response.json()
}

export async function deleteDemo(demoId: string): Promise<void> {
  const token = await getAuthToken()

  const response = await fetch(`${API_URL}/api/demo/${demoId}`, {
    method: 'DELETE',
    headers: {
      'Authorization': `Bearer ${token}`
    }
  })

  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to delete demo')
  }
}

export function getStatusColor(status: Demo['status']): string {
  switch (status) {
    case 'completed':
      return 'text-emerald-600 bg-emerald-50'
    case 'failed':
      return 'text-red-600 bg-red-50'
    case 'pending':
      return 'text-amber-600 bg-amber-50'
    case 'recording':
    case 'processing':
    case 'generating':
    case 'sending':
      return 'text-blue-600 bg-blue-50'
    default:
      return 'text-zinc-600 bg-zinc-50'
  }
}

export function getStatusLabel(status: Demo['status']): string {
  switch (status) {
    case 'pending':
      return 'Waiting in queue'
    case 'recording':
      return 'Recording demo'
    case 'processing':
      return 'Processing video'
    case 'generating':
      return 'Generating shorts'
    case 'sending':
      return 'Sending to email'
    case 'completed':
      return 'Ready'
    case 'failed':
      return 'Failed'
    default:
      return status
  }
}
