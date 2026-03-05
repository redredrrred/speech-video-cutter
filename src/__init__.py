"""
AI智能口误去除工具
"""

__version__ = "1.0.0"
__author__ = "AI Video Cutter"

from .speech_recognizer import SpeechRecognizer
from .repeat_detector import RepeatDetector
from .smoothness_analyzer import SmoothnessAnalyzer
from .timeline_editor import TimelineEditor
from .video_editor import VideoEditor

__all__ = [
    'SpeechRecognizer',
    'RepeatDetector',
    'SmoothnessAnalyzer',
    'TimelineEditor',
    'VideoEditor'
]
