"""
视频剪辑模块 - 根据时间线执行视频剪辑
"""

import os
from typing import List, Dict, Optional
from pathlib import Path
import logging

# 配置 ffmpeg 路径
FFMPEG_PATH = r"C:\Users\lenovo\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.0.1-full_build\bin\ffmpeg.exe"
FFPROBE_PATH = r"C:\Users\lenovo\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.0.1-full_build\bin\ffprobe.exe"

os.environ['IMAGEIO_FFMPEG_EXE'] = FFMPEG_PATH
os.environ['IMAGEIO_FFPROBE_EXE'] = FFPROBE_PATH

try:
    from moviepy import VideoFileClip, concatenate_videoclips
    # MoviePy 2.x 不再需要单独导入 vfx
    try:
        from moviepy import vfx
    except ImportError:
        vfx = None
except ImportError:
    VideoFileClip = None
    concatenate_videoclips = None

logger = logging.getLogger(__name__)


class VideoEditor:
    """视频编辑器"""

    def __init__(self,
                 codec: str = "libx264",
                 audio_codec: str = "aac",
                 quality: str = "high"):
        """
        初始化视频编辑器

        Args:
            codec: 视频编码器
            audio_codec: 音频编码器
            quality: 视频质量
        """
        if VideoFileClip is None:
            raise ImportError("需要安装 moviepy: pip install moviepy")

        self.codec = codec
        self.audio_codec = audio_codec
        self.quality = quality

        # 根据质量设置比特率
        self._set_quality_params()

    def _set_quality_params(self):
        """根据质量设置编码参数"""
        quality_params = {
            "low": {"video_bitrate": "500k", "audio_bitrate": "64k"},
            "medium": {"video_bitrate": "1500k", "audio_bitrate": "128k"},
            "high": {"video_bitrate": "3000k", "audio_bitrate": "192k"},
            "ultra": {"video_bitrate": "5000k", "audio_bitrate": "256k"}
        }

        params = quality_params.get(self.quality, quality_params["high"])
        self.video_bitrate = params["video_bitrate"]
        self.audio_bitrate = params["audio_bitrate"]

    def apply_timeline_edit(self, video_path: str, timeline: List[Dict],
                           output_path: str) -> bool:
        """
        根据时间线执行剪辑

        Args:
            video_path: 输入视频路径
            timeline: 剪辑时间线
            output_path: 输出视频路径

        Returns:
            是否成功
        """
        try:
            logger.info(f"开始剪辑视频: {video_path}")

            # 加载视频
            video_clip = VideoFileClip(video_path)

            # 提取所有保留片段
            keep_clips = []
            for item in timeline:
                if item['action'] == 'keep':
                    start = item['start']
                    end = item['end']

                    # 裁剪片段
                    clip = video_clip.subclipped(start, end)
                    keep_clips.append(clip)

                    logger.debug(f"保留片段: {start:.2f}s - {end:.2f}s")

            if not keep_clips:
                logger.warning("没有要保留的片段")
                video_clip.close()
                return False

            # 拼接片段
            logger.info(f"拼接 {len(keep_clips)} 个片段...")
            final_clip = concatenate_videoclips(keep_clips, method="compose")

            # 确保输出目录存在
            output_dir = os.path.dirname(output_path)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir)

            # 导出视频
            logger.info(f"导出视频到: {output_path}")
            final_clip.write_videofile(
                output_path,
                codec=self.codec,
                audio_codec=self.audio_codec,
                bitrate=self.video_bitrate
            )

            # 清理
            for clip in keep_clips:
                clip.close()
            final_clip.close()
            video_clip.close()

            logger.info("视频剪辑完成")
            return True

        except Exception as e:
            logger.error(f"视频剪辑失败: {e}")
            return False

    def preview_timeline(self, video_path: str, timeline: List[Dict],
                        preview_output: Optional[str] = None) -> Optional[str]:
        """
        生成预览视频（低质量）

        Args:
            video_path: 输入视频路径
            timeline: 剪辑时间线
            preview_output: 预览输出路径（可选）

        Returns:
            预览视频路径，如果失败返回 None
        """
        if preview_output is None:
            # 生成预览文件名
            base_path = Path(video_path).stem
            preview_output = f"{base_path}_preview.mp4"

        # 临时降低质量以加快预览生成
        original_quality = self.quality
        original_bitrate = self.video_bitrate

        self.quality = "low"
        self._set_quality_params()

        try:
            success = self.apply_timeline_edit(video_path, timeline, preview_output)
            return preview_output if success else None
        finally:
            # 恢复原始质量设置
            self.quality = original_quality
            self.video_bitrate = original_bitrate

    def get_video_info(self, video_path: str) -> Dict:
        """
        获取视频信息

        Args:
            video_path: 视频文件路径

        Returns:
            视频信息
        """
        try:
            clip = VideoFileClip(video_path)

            info = {
                "duration": clip.duration,
                "size": clip.size,
                "fps": clip.fps,
                "has_audio": clip.audio is not None,
                "width": clip.w,
                "height": clip.h
            }

            clip.close()

            return info

        except Exception as e:
            logger.error(f"获取视频信息失败: {e}")
            return {}

    def extract_segment(self, video_path: str, start: float, end: float,
                       output_path: str) -> bool:
        """
        提取视频片段

        Args:
            video_path: 输入视频路径
            start: 开始时间（秒）
            end: 结束时间（秒）
            output_path: 输出路径

        Returns:
            是否成功
        """
        try:
            clip = VideoFileClip(video_path)
            segment = clip.subclipped(start, end)

            # 确保输出目录存在
            output_dir = os.path.dirname(output_path)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir)

            segment.write_videofile(
                output_path,
                codec=self.codec,
                audio_codec=self.audio_codec
            )

            segment.close()
            clip.close()

            return True

        except Exception as e:
            logger.error(f"提取片段失败: {e}")
            return False

    def add_fade_transition(self, clip, duration: float = 0.5):
        """
        添加淡入淡出效果

        Args:
            clip: 视频片段
            duration: 过渡时长

        Returns:
            添加效果后的片段
        """
        return clip.fadein(duration).fadeout(duration)

    def calculate_output_size(self, video_path: str, timeline: List[Dict]) -> Dict:
        """
        估算输出文件大小

        Args:
            video_path: 输入视频路径
            timeline: 剪辑时间线

        Returns:
            大小估算信息
        """
        # 获取输入文件大小
        input_size = os.path.getsize(video_path)

        # 计算保留时长比例
        total_keep_duration = 0
        total_duration = 0

        for item in timeline:
            duration = item['end'] - item['start']
            total_duration = max(total_duration, item['end'])
            if item['action'] == 'keep':
                total_keep_duration += duration

        if total_duration > 0:
            keep_ratio = total_keep_duration / total_duration
        else:
            keep_ratio = 0

        # 估算输出大小（考虑编码压缩）
        estimated_size = input_size * keep_ratio * 0.9  # 保守估计

        return {
            "input_size": input_size,
            "estimated_size": estimated_size,
            "keep_ratio": keep_ratio,
            "input_size_mb": input_size / (1024 * 1024),
            "estimated_size_mb": estimated_size / (1024 * 1024)
        }
