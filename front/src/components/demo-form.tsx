'use client'

import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { ArrowRight, Globe, Sparkles } from 'lucide-react'
import { User } from '@supabase/supabase-js'
import { createDemo } from '@/services/demo'
import { useRouter } from 'next/navigation'

interface DemoFormProps {
  user: User | null
  onAuthRequired: () => void
}

const DEMO_STORAGE_KEY = 'pending_demo_request'

export function DemoForm({ user, onAuthRequired }: DemoFormProps) {
  const [productUrl, setProductUrl] = useState('')
  const [description, setDescription] = useState('')
  const [showExpanded, setShowExpanded] = useState(false)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState('')
  const router = useRouter()

  // Load saved demo request from localStorage
  useEffect(() => {
    const saved = localStorage.getItem(DEMO_STORAGE_KEY)
    if (saved) {
      try {
        const { url, desc } = JSON.parse(saved)
        if (url) {
          setProductUrl(url)
          setShowExpanded(true)
        }
        if (desc) {
          setDescription(desc)
        }
      } catch (e) {
        console.error('Failed to load saved demo request', e)
      }
    }
  }, [])

  // Auto-submit if user just logged in and has pending request
  useEffect(() => {
    if (user) {
      const saved = localStorage.getItem(DEMO_STORAGE_KEY)
      if (saved) {
        try {
          const { url, autoSubmit } = JSON.parse(saved)
          if (url && autoSubmit) {
            // Clear the auto-submit flag
            localStorage.setItem(DEMO_STORAGE_KEY, JSON.stringify({ url, desc: description, autoSubmit: false }))
            // Submit the demo
            handleSubmit()
          }
        } catch (e) {
          console.error('Failed to auto-submit demo', e)
        }
      }
    }
  }, [user])

  const handleUrlChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const url = e.target.value
    setProductUrl(url)
    setError('')
    
    // Show expanded form when user starts typing
    if (url.length > 0 && !showExpanded) {
      setShowExpanded(true)
    }
    
    // Save to localStorage
    localStorage.setItem(DEMO_STORAGE_KEY, JSON.stringify({ 
      url, 
      desc: description,
      autoSubmit: false 
    }))
  }

  const handleDescriptionChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const desc = e.target.value
    setDescription(desc)
    
    // Save to localStorage
    localStorage.setItem(DEMO_STORAGE_KEY, JSON.stringify({ 
      url: productUrl, 
      desc,
      autoSubmit: false 
    }))
  }

  const validateUrl = (url: string) => {
    try {
      new URL(url)
      return true
    } catch {
      return false
    }
  }

  const handleSubmit = async () => {
    // Validate URL
    if (!productUrl) {
      setError('Please enter a product URL')
      return
    }
    
    if (!validateUrl(productUrl)) {
      setError('Please enter a valid URL (e.g., https://example.com)')
      return
    }

    // Check if user is logged in
    if (!user) {
      // Save the request with auto-submit flag
      localStorage.setItem(DEMO_STORAGE_KEY, JSON.stringify({ 
        url: productUrl, 
        desc: description,
        autoSubmit: true 
      }))
      // Open auth modal
      onAuthRequired()
      return
    }

    // Submit the demo request
    setIsSubmitting(true)
    setError('')
    
    try {
      const demo = await createDemo({
        product_url: productUrl,
        description: description || undefined
      })
      
      // Clear saved data
      localStorage.removeItem(DEMO_STORAGE_KEY)
      
      // Redirect to dashboard
      router.push('/dashboard')
    } catch (err: any) {
      setError(err.message || 'Failed to create demo. Please try again.')
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div className="w-full max-w-xl mx-auto">
      <div className="relative">
        {/* URL Input - Always visible */}
        <div className="relative group">
          <div className="absolute inset-0 bg-gradient-to-r from-emerald-600/20 to-teal-600/20 rounded-lg blur-xl group-hover:from-emerald-600/30 group-hover:to-teal-600/30 transition-all" />
          <div className="relative flex items-center">
            <Globe className="absolute left-4 h-5 w-5 text-zinc-400" />
            <input
              type="url"
              placeholder="Your product URL"
              value={productUrl}
              onChange={handleUrlChange}
              className="w-full pl-12 pr-4 py-3.5 text-base rounded-lg border border-zinc-200 bg-white focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent transition-all"
              autoFocus
            />
          </div>
        </div>

        {/* Expanded section - Shows when user starts typing */}
        {showExpanded && (
          <div className="mt-3 space-y-3 animate-in slide-in-from-top-1 duration-200">
            {/* Description textarea */}
            <div className="relative">
              <textarea
                placeholder="Additional instructions (optional) - e.g., Focus on dashboard, highlight key features..."
                value={description}
                onChange={handleDescriptionChange}
                className="w-full px-4 py-3 min-h-[80px] text-sm rounded-lg border border-zinc-200 bg-white focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent transition-all resize-none"
              />
            </div>

            {/* Error message */}
            {error && (
              <p className="text-sm text-red-600 px-1">{error}</p>
            )}

            {/* Submit button */}
            <Button
              size="lg"
              className="w-full bg-emerald-600 hover:bg-emerald-700 text-white font-semibold shadow-lg hover:shadow-xl transition-all"
              onClick={handleSubmit}
              disabled={isSubmitting || !productUrl}
            >
              {isSubmitting ? (
                <>
                  <span className="h-4 w-4 border-2 border-white/30 border-t-white rounded-full animate-spin mr-2" />
                  Creating your demo...
                </>
              ) : (
                <>
                  Generate Demo
                  <Sparkles className="ml-2 h-4 w-4" />
                </>
              )}
            </Button>
          </div>
        )}
      </div>
    </div>
  )
}