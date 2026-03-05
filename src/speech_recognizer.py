"""
语音识别模块 - 使用 Whisper 进行语音识别生成字幕
"""

import whisper
import tempfile
import os
from typing import List, Dict, Optional
from pathlib import Path
import logging

# 配置 ffmpeg 路径（Whisper 需要）
FFMPEG_PATH = r"C:\Users\lenovo\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.0.1-full_build\bin\ffmpeg.exe"
os.environ['PATH'] = os.path.dirname(FFMPEG_PATH) + os.pathsep + os.environ.get('PATH', '')

logger = logging.getLogger(__name__)


class SpeechRecognizer:
    """语音识别器，使用 Whisper 模型"""

    def __init__(self, model_size: str = "base", language: str = "zh", device: str = "cpu"):
        """
        初始化语音识别器

        Args:
            model_size: Whisper 模型大小 (tiny/base/small/medium/large)
            language: 语言代码 (zh=中文, en=英文)
            device: 运行设备 (cpu/cuda)
        """
        self.model_size = model_size
        self.language = language
        self.device = device
        self.model = None
        self._load_model()

    def _load_model(self):
        """加载 Whisper 模型"""
        try:
            logger.info(f"正在加载 Whisper 模型 ({self.model_size})...")
            self.model = whisper.load_model(self.model_size, device=self.device)
            logger.info("模型加载成功")
        except Exception as e:
            logger.error(f"模型加载失败: {e}")
            raise

    def transcribe_audio(self, audio_path: str) -> List[Dict]:
        """
        识别音频文件

        Args:
            audio_path: 音频文件路径

        Returns:
            识别结果列表，每个元素包含 start, end, text
            [{"start": 0.0, "end": 5.2, "text": "字幕内容"}, ...]
        """
        try:
            logger.info(f"正在识别音频: {audio_path}")

            # 使用 Whisper 进行识别
            result = self.model.transcribe(
                audio_path,
                language=self.language,
                word_timestamps=True,  # 获取词级别时间戳
                verbose=False
            )

            # 提取分段信息
            segments = []
            for segment in result['segments']:
                segments.append({
                    'start': segment['start'],
                    'end': segment['end'],
                    'text': segment['text'].strip()
                })

            logger.info(f"识别完成，共 {len(segments)} 个片段")
            return segments

        except Exception as e:
            logger.error(f"音频识别失败: {e}")
            raise

    def transcribe_video(self, video_path: str,
                        audio_extractor: Optional['AudioExtractor'] = None) -> List[Dict]:
        """
        识别视频文件中的语音

        Args:
            video_path: 视频文件路径
            audio_extractor: 音频提取器实例（可选）

        Returns:
            识别结果列表
        """
        from audio_extractor import AudioExtractor

        # 提取音频
        if audio_extractor is None:
            audio_extractor = AudioExtractor()

        logger.info(f"正在从视频中提取音频: {video_path}")
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_audio:
            audio_path = audio_extractor.extract_audio(video_path, tmp_audio.name)

        try:
            # 识别音频
            segments = self.transcribe_audio(audio_path)
            return segments
        finally:
            # 清理临时文件
            if os.path.exists(audio_path):
                os.remove(audio_path)

    def save_subtitle(self, segments: List[Dict], output_path: str, format: str = "srt"):
        """
        保存字幕文件

        Args:
            segments: 识别结果列表
            output_path: 输出文件路径
            format: 字幕格式 (srt/vtt)
        """
        try:
            if format.lower() == "srt":
                self._save_srt(segments, output_path)
            elif format.lower() == "vtt":
                self._save_vtt(segments, output_path)
            else:
                raise ValueError(f"不支持的字幕格式: {format}")

            logger.info(f"字幕文件已保存: {output_path}")
        except Exception as e:
            logger.error(f"保存字幕文件失败: {e}")
            raise

    def _save_srt(self, segments: List[Dict], output_path: str):
        """保存为 SRT 格式"""
        with open(output_path, 'w', encoding='utf-8') as f:
            for i, segment in enumerate(segments, 1):
                start_time = self._seconds_to_srt_time(segment['start'])
                end_time = self._seconds_to_srt_time(segment['end'])

                f.write(f"{i}\n")
                f.write(f"{start_time} --> {end_time}\n")
                f.write(f"{segment['text']}\n\n")

    def _save_vtt(self, segments: List[Dict], output_path: str):
        """保存为 VTT 格式"""
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("WEBVTT\n\n")
            for segment in segments:
                start_time = self._seconds_to_vtt_time(segment['start'])
                end_time = self._seconds_to_vtt_time(segment['end'])

                f.write(f"{start_time} --> {end_time}\n")
                f.write(f"{segment['text']}\n\n")

    @staticmethod
    def _seconds_to_srt_time(seconds: float) -> str:
        """将秒数转换为 SRT 时间格式 (00:00:00,000)"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"

    @staticmethod
    def _seconds_to_vtt_time(seconds: float) -> str:
        """将秒数转换为 VTT 时间格式 (00:00:00.000)"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d}.{millis:03d}"


# 便捷函数
def transcribe_video(video_path: str, model_size: str = "base",
                    language: str = "zh") -> List[Dict]:
    """
    便捷函数：识别视频中的语音

    Args:
        video_path: 视频文件路径
        model_size: Whisper 模型大小
        language: 语言代码

    Returns:
        识别结果列表
    """
    recognizer = SpeechRecognizer(model_size=model_size, language=language)
    return recognizer.transcribe_video(video_path)
