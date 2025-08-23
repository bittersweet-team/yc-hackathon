'use client'

import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { ArrowRight, CheckCircle, Mail, Play, Sparkles, Video, Zap, MousePointer, Globe, Palette, LogIn } from "lucide-react"
import Link from "next/link"
import { useState } from "react"
import { AuthModal } from "@/components/auth-modal"

export default function Home() {
  const [email, setEmail] = useState("")
  const [showAuthModal, setShowAuthModal] = useState(false)
  const [authMode, setAuthMode] = useState<'login' | 'signup'>('login')

  const handleGetStarted = () => {
    setAuthMode('signup')
    setShowAuthModal(true)
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
            <Button 
              size="sm" 
              variant="ghost"
              onClick={handleSignIn}
              className="text-sm"
            >
              <LogIn className="h-4 w-4 mr-2" />
              Sign In
            </Button>
            <Button size="sm" onClick={handleGetStarted}>
              Get Started
            </Button>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative overflow-hidden py-20 md:py-32">
        <div className="absolute inset-0 bg-gradient-to-r from-emerald-50 via-transparent to-amber-50 opacity-50" />
        <div className="container mx-auto px-4 relative">
          <div className="text-center max-w-3xl mx-auto">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-100 text-emerald-700 text-sm font-medium mb-6">
              <Sparkles className="h-4 w-4" />
              AI-Powered Demo Creation
            </div>
            <h1 className="text-5xl md:text-7xl font-bold mb-6 gradient-text">
              Create Product Demos
              <br />
              <span className="text-zinc-900">With One Click</span>
            </h1>
            <p className="text-xl text-zinc-600 mb-8 text-balance">
              Transform your product URL into engaging demo videos. No recording, no editing, just instant professional demos delivered to your inbox.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <div className="flex-1 max-w-sm">
                <input
                  type="email"
                  placeholder="Enter your email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full px-4 py-3 rounded-lg border border-zinc-200 focus:outline-none focus:ring-2 focus:ring-emerald-500 transition-all"
                />
              </div>
              <Button 
                size="lg" 
                className="bg-emerald-600 hover:bg-emerald-700"
                onClick={handleGetStarted}
              >
                Start Free Trial
                <ArrowRight className="ml-2 h-4 w-4" />
              </Button>
            </div>
            <p className="text-sm text-zinc-500 mt-4">
              No credit card required
            </p>
          </div>
        </div>

        {/* Floating elements */}
        <div className="absolute top-20 left-10 animate-float">
          <div className="w-20 h-20 bg-gradient-to-br from-emerald-400 to-emerald-600 rounded-full opacity-20 blur-xl" />
        </div>
        <div className="absolute bottom-20 right-10 animate-float animation-delay-2000">
          <div className="w-32 h-32 bg-gradient-to-br from-amber-400 to-amber-600 rounded-full opacity-20 blur-xl" />
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

            <Card className="hover:shadow-lg transition-shadow">
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
                <ul className="space-y-2">
                  <li className="flex items-start gap-2">
                    <CheckCircle className="h-4 w-4 text-emerald-600 mt-0.5" />
                    <span className="text-sm text-zinc-600">MP4 & WebM formats</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <CheckCircle className="h-4 w-4 text-emerald-600 mt-0.5" />
                    <span className="text-sm text-zinc-600">Social media ready</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <CheckCircle className="h-4 w-4 text-emerald-600 mt-0.5" />
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
