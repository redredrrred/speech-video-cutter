"""
音频提取模块 - 从视频中提取音频
"""

import os
import tempfile
from typing import Optional
from pathlib import Path
import logging

# 配置 ffmpeg 路径
FFMPEG_PATH = r"C:\Users\lenovo\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.0.1-full_build\bin\ffmpeg.exe"
os.environ['IMAGEIO_FFMPEG_EXE'] = FFMPEG_PATH

try:
    from moviepy import VideoFileClip
except ImportError:
    VideoFileClip = None

logger = logging.getLogger(__name__)


class AudioExtractor:
    """音频提取器"""

    def __init__(self):
        """初始化音频提取器"""
        if VideoFileClip is None:
            raise ImportError("需要安装 moviepy: pip install moviepy")

    def extract_audio(self, video_path: str, output_path: Optional[str] = None) -> str:
        """
        从视频文件中提取音频

        Args:
            video_path: 视频文件路径
            output_path: 输出音频文件路径（可选）

        Returns:
            提取的音频文件路径
        """
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"视频文件不存在: {video_path}")

        try:
            logger.info(f"正在提取音频: {video_path}")

            # 加载视频
            video_clip = VideoFileClip(video_path)

            # 如果没有指定输出路径，创建临时文件
            if output_path is None:
                output_path = tempfile.mktemp(suffix='.wav')

            # 确保输出目录存在
            output_dir = os.path.dirname(output_path)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir)

            # 提取音频
            audio_clip = video_clip.audio

            if audio_clip is None:
                raise ValueError("视频文件中没有音频轨道")

            # 保存音频文件
            audio_clip.write_audiofile(output_path)

            # 清理
            audio_clip.close()
            video_clip.close()

            logger.info(f"音频提取完成: {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"音频提取失败: {e}")
            raise

    def get_audio_info(self, video_path: str) -> dict:
        """
        获取视频音频信息

        Args:
            video_path: 视频文件路径

        Returns:
            音频信息字典
        """
        try:
            video_clip = VideoFileClip(video_path)
            audio_clip = video_clip.audio

            if audio_clip is None:
                return {"has_audio": False}

            info = {
                "has_audio": True,
                "duration": audio_clip.duration,
                "fps": audio_clip.fps if hasattr(audio_clip, 'fps') else None,
                "channels": audio_clip.nchannels if hasattr(audio_clip, 'nchannels') else None
            }

            video_clip.close()

            return info

        except Exception as e:
            logger.error(f"获取音频信息失败: {e}")
            return {"has_audio": False, "error": str(e)}
