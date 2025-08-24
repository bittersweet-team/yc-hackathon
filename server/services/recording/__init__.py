"""
Recording service module for browser-based demo recording
"""

from .recording import BrowserRecorder

__all__ = [
    'BrowserRecorder',
    'generate_viral_dubbing',
    'ViralDubbingScript',
    'VideoDubbingProcessor',
]