'use client'

import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { ArrowRight, CheckCircle, Mail, Play, Sparkles, Video, Zap, MousePointer, Globe, Palette, LogIn, User, LogOut } from "lucide-react"
import Link from "next/link"
import { useState, useEffect, useRef } from "react"
import { AuthModal } from "@/components/auth-modal"
import { DemoForm } from "@/components/demo-form"
import { useAuth } from "@/contexts/auth-context"

export default function Home() {
  const [showAuthModal, setShowAuthModal] = useState(false)
  const [authMode, setAuthMode] = useState<'login' | 'signup'>('login')
  const [showUserMenu, setShowUserMenu] = useState(false)
  const userMenuRef = useRef<HTMLDivElement>(null)

  const { user, signOut, loading } = useAuth()

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (userMenuRef.current && !userMenuRef.current.contains(event.target as Node)) {
        setShowUserMenu(false)
      }
    }

    document.addEventListener('mousedown', handleClickOutside)
    return () => {
      document.removeEventListener('mousedown', handleClickOutside)
    }
  }, [])

  const handleGetStarted = () => {
    if (user) {
      // User is logged in, redirect to dashboard or demo creation
      console.log('User is logged in, redirect to dashboard')
    } else {
      setAuthMode('signup')
      setShowAuthModal(true)
    }
  }

  const handleSignIn = () => {
    setAuthMode('login')
    setShowAuthModal(true)
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-white via-zinc-50 to-white">
      {/* Auth Modal */}
      <AuthModal
        isOpen={showAuthModal}
        onClose={() => setShowAuthModal(false)}
        initialMode={authMode}
      />

      {/* Navigation */}
      <nav className="sticky top-0 z-40 glass-effect">
        <div className="container mx-auto px-4 h-16 flex items-center justify-between">
          <Link href="/" className="flex items-center space-x-2">
            <Video className="h-6 w-6" />
            <span className="font-bold text-xl">Demo Hunters</span>
          </Link>
          <div className="flex items-center gap-6">
            <Link href="#features" className="text-sm font-medium hover:text-zinc-600 transition-colors">
              Features
            </Link>
            <Link href="#how-it-works" className="text-sm font-medium hover:text-zinc-600 transition-colors">
              How it Works
            </Link>
            {loading ? (
              <div className="h-8 w-20 rounded-md bg-zinc-200 animate-pulse" />
            ) : user ? (
              <Link href="/dashboard">
                <Button size="sm" className="bg-zinc-900 hover:bg-zinc-800 text-white">
                  Dashboard
                </Button>
              </Link>
            ) : (
              <Button size="sm" className="bg-emerald-600 hover:bg-emerald-700 text-white" onClick={handleSignIn}>
                Get Started
              </Button>
            )}
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative py-16 md:py-24">
        <div className="container mx-auto px-4">
          <div className="text-center max-w-4xl mx-auto">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-50 border border-emerald-200 text-xs font-medium mb-6">
              <span className="relative flex h-2 w-2">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
              </span>
              <span className="text-emerald-700">AI-Powered • No Recording • Instant Delivery</span>
            </div>

            <h1 className="text-4xl md:text-6xl lg:text-7xl font-black mb-6 tracking-tight">
              <span className="text-zinc-900">Create </span>
              <span className="bg-gradient-to-r from-emerald-600 to-emerald-500 bg-clip-text text-transparent">
                Product Demos
              </span>
              <br />
              <span className="text-zinc-900 text-3xl md:text-5xl lg:text-6xl">With </span>
              <span className="bg-gradient-to-r from-emerald-500 to-teal-500 bg-clip-text text-transparent text-3xl md:text-5xl lg:text-6xl">
                One Click
              </span>
            </h1>

            <p className="text-lg md:text-xl text-zinc-600 mb-8 max-w-2xl mx-auto">
              Just paste your URL. We'll create professional demo videos automatically.
            </p>

            <DemoForm user={user} onAuthRequired={handleGetStarted} />

            <div className="flex flex-wrap items-center justify-center gap-4 md:gap-6 mt-8 text-sm text-zinc-600">
              <span className="flex items-center gap-1.5">
                <CheckCircle className="h-4 w-4 text-emerald-500 flex-shrink-0" />
                No credit card
              </span>
              <span className="flex items-center gap-1.5">
                <CheckCircle className="h-4 w-4 text-emerald-500 flex-shrink-0" />
                Max 60s videos
              </span>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-20 bg-zinc-50/50">
        <div className="container mx-auto px-4">
          <div className="text-center mb-12">
            <h2 className="text-3xl md:text-4xl font-bold mb-4">
              Everything You Need for Perfect Demos
            </h2>
            <p className="text-lg text-zinc-600">
              Professional demo videos without the hassle
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-6">
            <Card className="hover:shadow-lg transition-shadow">
              <CardHeader>
                <div className="h-12 w-12 bg-emerald-100 rounded-lg flex items-center justify-center mb-4">
                  <MousePointer className="h-6 w-6 text-emerald-600" />
                </div>
                <CardTitle>One-Click Generation</CardTitle>
                <CardDescription>
                  Just paste your product URL and let our AI do the magic
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ul className="space-y-2">
                  <li className="flex items-start gap-2">
                    <CheckCircle className="h-4 w-4 text-emerald-600 mt-0.5" />
                    <span className="text-sm text-zinc-600">Automatic navigation</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <CheckCircle className="h-4 w-4 text-emerald-600 mt-0.5" />
                    <span className="text-sm text-zinc-600">Smart interactions</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <CheckCircle className="h-4 w-4 text-emerald-600 mt-0.5" />
                    <span className="text-sm text-zinc-600">Feature highlighting</span>
                  </li>
                </ul>
              </CardContent>
            </Card>

            <Card className="hover:shadow-lg transition-shadow">
              <CardHeader>
                <div className="h-12 w-12 bg-amber-100 rounded-lg flex items-center justify-center mb-4">
                  <Palette className="h-6 w-6 text-amber-600" />
                </div>
                <CardTitle>Professional Quality</CardTitle>
                <CardDescription>
                  Studio-quality demos without the studio
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ul className="space-y-2">
                  <li className="flex items-start gap-2">
                    <CheckCircle className="h-4 w-4 text-emerald-600 mt-0.5" />
                    <span className="text-sm text-zinc-600">HD video output</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <CheckCircle className="h-4 w-4 text-emerald-600 mt-0.5" />
                    <span className="text-sm text-zinc-600">Smooth animations</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <CheckCircle className="h-4 w-4 text-emerald-600 mt-0.5" />
                    <span className="text-sm text-zinc-600">Voice narration</span>
                  </li>
                </ul>
              </CardContent>
            </Card>

            <Card className="hover:shadow-lg transition-shadow relative overflow-hidden">
              <div className="absolute top-4 right-4">
                <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-amber-100 text-amber-800">
                  Coming Soon
                </span>
              </div>
              <CardHeader>
                <div className="h-12 w-12 bg-zinc-100 rounded-lg flex items-center justify-center mb-4">
                  <Globe className="h-6 w-6 text-zinc-600" />
                </div>
                <CardTitle>Multi-Platform Export</CardTitle>
                <CardDescription>
                  Share your demos anywhere
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ul className="space-y-2 opacity-60">
                  <li className="flex items-start gap-2">
                    <div className="h-4 w-4 rounded-full border-2 border-zinc-400 mt-0.5" />
                    <span className="text-sm text-zinc-600">MP4 & WebM formats</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <div className="h-4 w-4 rounded-full border-2 border-zinc-400 mt-0.5" />
                    <span className="text-sm text-zinc-600">Social media ready</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <div className="h-4 w-4 rounded-full border-2 border-zinc-400 mt-0.5" />
                    <span className="text-sm text-zinc-600">Embed anywhere</span>
                  </li>
                </ul>
              </CardContent>
            </Card>
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section id="how-it-works" className="py-20">
        <div className="container mx-auto px-4">
          <div className="text-center mb-12">
            <h2 className="text-3xl md:text-4xl font-bold mb-4">
              Three Simple Steps
            </h2>
            <p className="text-lg text-zinc-600">
              From URL to professional demo in minutes
            </p>
          </div>

          <div className="max-w-4xl mx-auto">
            <div className="space-y-8">
              <div className="flex gap-4 items-start">
                <div className="flex-shrink-0 w-12 h-12 bg-emerald-600 text-white rounded-full flex items-center justify-center font-bold">
                  1
                </div>
                <div className="flex-1">
                  <h3 className="text-xl font-semibold mb-2">Submit Your Product URL</h3>
                  <p className="text-zinc-600">
                    Paste your product's URL and add a brief description of what you want to showcase
                  </p>
                </div>
              </div>

              <div className="flex gap-4 items-start">
                <div className="flex-shrink-0 w-12 h-12 bg-emerald-600 text-white rounded-full flex items-center justify-center font-bold">
                  2
                </div>
                <div className="flex-1">
                  <h3 className="text-xl font-semibold mb-2">AI Creates Your Demo</h3>
                  <p className="text-zinc-600">
                    Our AI navigates your product, captures key features, and creates a professional demo video
                  </p>
                </div>
              </div>

              <div className="flex gap-4 items-start">
                <div className="flex-shrink-0 w-12 h-12 bg-emerald-600 text-white rounded-full flex items-center justify-center font-bold">
                  3
                </div>
                <div className="flex-1">
                  <h3 className="text-xl font-semibold mb-2">Download & Share</h3>
                  <p className="text-zinc-600">
                    Receive your demo video via email, ready to share with customers, investors, or your team
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-gradient-to-r from-emerald-50 to-amber-50">
        <div className="container mx-auto px-4 text-center">
          <h2 className="text-3xl md:text-4xl font-bold mb-4">
            Ready to Create Amazing Demos?
          </h2>
          <p className="text-lg text-zinc-600 mb-8">
            Join thousands of teams using Demo Hunters to showcase their products
          </p>
          <Button
            size="lg"
            className="bg-zinc-900 hover:bg-zinc-800"
            onClick={handleGetStarted}
          >
            <Play className="mr-2 h-4 w-4" />
            Create Your First Demo
          </Button>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-12 border-t">
        <div className="container mx-auto px-4">
          <div className="flex flex-col md:flex-row justify-between items-center">
            <div className="flex items-center space-x-2 mb-4 md:mb-0">
              <Video className="h-5 w-5" />
              <span className="font-semibold">Demo Hunters</span>
            </div>
            <div className="flex items-center gap-6 text-sm text-zinc-600">
              <Link href="/privacy" className="hover:text-zinc-900">Privacy</Link>
              <Link href="/terms" className="hover:text-zinc-900">Terms</Link>
              <Link href="mailto:developers@bittersweet.ai" className="hover:text-zinc-900">Contact</Link>
            </div>
          </div>
          <div className="mt-8 pt-8 border-t text-center text-sm text-zinc-500">
            © 2025 Demo Hunters. All rights reserved.
          </div>
        </div>
      </footer>
    </div>
  );
}
