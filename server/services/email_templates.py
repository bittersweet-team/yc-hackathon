"""
Email templates for Demo Hunters
Simple HTML5 templates without CSS
"""

def get_demo_started_email_html(product_name: str, product_url: str, description: str) -> str:
    """Generate the demo started email HTML"""
    return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Demo Generation Started - Demo Hunters</title>
</head>
<body>
    <header>
        <h1>🎬 Demo Hunters</h1>
    </header>
    <main>
        <section>
            <p>✅ Processing Started</p>
            
            <h2>🚀 Your Demo is Being Generated!</h2>
            <p>We've started creating professional demo videos for <strong>{product_name}</strong></p>
            
            <div>
                <p><strong>Product URL:</strong></p>
                <p><a href="{product_url}">{product_url}</a></p>
                {f'<p><strong>Description:</strong></p><p>{description}</p>' if description else ''}
            </div>
        </section>
        <section>
            <h3>⚡ What's Happening Now</h3>
            <ol>
                <li>
                    <strong>Recording your product demo</strong><br>
                    AI is navigating and capturing your product
                </li>
                <li>
                    <strong>Processing with AI</strong><br>
                    Analyzing and optimizing the footage
                </li>
                <li>
                    <strong>Generating short-form clips</strong><br>
                    Creating social media ready versions
                </li>
                <li>
                    <strong>Finalizing your videos</strong><br>
                    Preparing downloads and sending to you
                </li>
            </ol>
        </section>
        <section>
            <p><strong>⏱️ Estimated Time:</strong> 5-10 minutes</p>
            <p>We'll send you another email once your videos are ready!</p>
        </section>
        <hr>
        <p>While you wait, feel free to create more demos at <a href="https://demohunters.ai">demohunters.ai</a></p>
    </main>
    <footer>
        <p>© 2025 Demo Hunters. All rights reserved.</p>
        <nav>
            <a href="https://demohunters.ai/privacy">Privacy</a> | 
            <a href="https://demohunters.ai/terms">Terms</a> | 
            <a href="mailto:support@demohunters.ai">Support</a>
        </nav>
    </footer>
</body>
</html>"""


def get_demo_complete_email_html(product_name: str, description: str, long_video_url: str, short_video_urls: list) -> str:
    """Generate the demo complete email HTML"""
    return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Your Demo Videos Are Ready - Demo Hunters</title>
</head>
<body>
    <header>
        <h1>🎬 Demo Hunters</h1>
    </header>
    <main>
        <section>
            <p>✅ Videos Ready</p>
            <h2>🎬 Your Demo Videos Are Ready!</h2>
            <p>Great news! We've successfully generated demo videos for <strong>{product_name}</strong></p>
            {f'<div><p><strong>Product Description:</strong></p><p>{description}</p></div>' if description else ''}
        </section>
        <section>
            <h3>📹 Full Demo Video</h3>
            <p>Watch the complete walkthrough of your product</p>
            <div>
                <p>▶ Full Product Demo - Complete walkthrough video</p>
                <p><a href="{long_video_url}">View Full Demo</a></p>
            </div>
        </section>
        <hr>
        <section>
            <h3>🎯 Short-Form Videos</h3>
            <p>Perfect for social media sharing - optimized for maximum engagement</p>
            <ul>
                {''.join([f'<li><a href="{url}">Short Video #{i} - Optimized for social media</a></li>' for i, url in enumerate(short_video_urls, 1)])}
            </ul>
        </section>
        <section>
            <p><strong>💡 Pro Tip:</strong> These videos are optimized for different platforms</p>
            <p>Use them on TikTok, Instagram Reels, YouTube Shorts, and more!</p>
        </section>
        <hr>
        <section>
            <h3>Ready to create more demos?</h3>
            <p><a href="https://demohunters.ai">Create Another Demo</a></p>
        </section>
    </main>
    <footer>
        <p>These videos were automatically generated using AI technology.</p>
        <p>Feel free to download and share them!</p>
        <nav>
            <a href="https://demohunters.ai/privacy">Privacy</a> | 
            <a href="https://demohunters.ai/terms">Terms</a> | 
            <a href="mailto:support@demohunters.ai">Support</a>
        </nav>
        <p>© 2025 Demo Hunters. All rights reserved.</p>
    </footer>
</body>
</html>"""
