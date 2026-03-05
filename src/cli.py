"""
命令行接口 - AI智能口误去除工具
"""

import sys
import os
import yaml
import click
import logging
from pathlib import Path
from typing import Optional
from tqdm import tqdm

# 添加当前目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from speech_recognizer import SpeechRecognizer
from repeat_detector import RepeatDetector
from smoothness_analyzer import SmoothnessAnalyzer
from timeline_editor import TimelineEditor
from video_editor import VideoEditor

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_config(config_path: str = "config.yaml") -> dict:
    """加载配置文件"""
    if os.path.exists(config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    else:
        logger.warning(f"配置文件不存在: {config_path}，使用默认配置")
        return {}


@click.group()
@click.version_option(version="1.0.0")
def main():
    """AI智能口误去除工具 - 自动检测并去除视频中的重复/口误内容"""
    pass


@main.command()
@click.argument('input_video', type=click.Path(exists=True))
@click.option('--output', '-o', help='输出视频路径')
@click.option('--similarity', default=0.7, type=float, help='相似度阈值 (0-1)，默认0.7')
@click.option('--max-gap', default=10.0, type=float, help='最大时间间隔（秒），默认10秒')
@click.option('--strategy', default='last',
              type=click.Choice(['last', 'longest', 'smoothest']),
              help='保留策略: last=最后版本, longest=最长版本, smoothest=最流畅版本')
@click.option('--keep-pauses/--no-keep-pauses', default=True, help='是否保留停顿/静音')
@click.option('--model', default='base', type=click.Choice(['tiny', 'base', 'small', 'medium', 'large']),
              help='Whisper模型大小，默认base')
@click.option('--config', default='config.yaml', type=click.Path(exists=True),
              help='配置文件路径')
@click.option('--preview', is_flag=True, help='预览模式，不实际剪辑视频')
@click.option('--report', help='生成剪辑报告到指定文件')
def process(input_video, output, similarity, max_gap, strategy, keep_pauses,
           model, config, preview, report):
    """
    处理视频，自动去除口误

    示例:
        ai-cutter process input.mp4 -o output.mp4
        ai-cutter process input.mp4 --similarity 0.8 --strategy smoothest
        ai-cutter process input.mp4 --preview --report report.txt
    """
    try:
        # 加载配置
        cfg = load_config(config)

        # 设置输出路径
        if output is None:
            input_path = Path(input_video)
            output = str(input_path.parent / f"{input_path.stem}_edited{input_path.suffix}")

        click.echo(f"{'='*60}")
        click.echo(f"AI智能口误去除工具")
        click.echo(f"{'='*60}")
        click.echo(f"输入: {input_video}")
        click.echo(f"输出: {output}")
        click.echo(f"相似度阈值: {similarity}")
        click.echo(f"保留策略: {strategy}")
        click.echo(f"保留停顿: {keep_pauses}")
        click.echo(f"{'='*60}\n")

        # 步骤1: 语音识别
        click.echo("[*] 步骤 1/5: 语音识别...")
        recognizer = SpeechRecognizer(
            model_size=model,
            language=cfg.get('speech', {}).get('language', 'zh'),
            device=cfg.get('speech', {}).get('device', 'cpu')
        )
        segments = recognizer.transcribe_video(input_video)
        click.echo(f"   [OK] 识别完成，共 {len(segments)} 个片段\n")

        # 步骤2: 重复检测
        click.echo("[*] 步骤 2/5: 检测重复内容...")
        detector = RepeatDetector(
            similarity_threshold=similarity,
            max_time_gap=max_gap,
            min_sentence_length=cfg.get('detection', {}).get('min_sentence_length', 5)
        )
        repeats = detector.detect_repeats(segments)

        if not repeats:
            click.echo("   [OK] 未检测到重复内容，无需剪辑\n")
            return

        click.echo(f"   [OK] 检测到 {len(repeats)} 处重复\n")

        # 步骤3: 生成剪辑时间线
        click.echo("[*] 步骤 3/5: 生成剪辑时间线...")
        editor = TimelineEditor(
            keep_pauses=keep_pauses,
            pause_threshold=cfg.get('analysis', {}).get('pause_threshold', 0.5)
        )
        timeline = editor.generate_edit_timeline(segments, repeats, strategy)
        timeline = editor.optimize_timeline(timeline)

        stats = editor.calculate_timeline_stats(timeline)
        click.echo(f"   [OK] 保留时长: {stats['keep_duration']:.1f}秒 ({stats['keep_ratio']:.1f}%)")
        click.echo(f"   [OK] 剪掉时长: {stats['cut_duration']:.1f}秒 ({stats['cut_count']}处)\n")

        # 步骤4: 生成报告
        if report:
            click.echo("[*] 步骤 4/5: 生成报告...")
            with open(report, 'w', encoding='utf-8') as f:
                f.write(detector.generate_report(repeats))
                f.write("\n\n")
                f.write(editor.format_timeline(timeline))
            click.echo(f"   [OK] 报告已保存: {report}\n")

        # 步骤5: 执行剪辑
        if preview:
            click.echo("[*] 预览模式：跳过实际剪辑\n")
            click.echo(editor.format_timeline(timeline))
        else:
            click.echo("[*] 步骤 5/5: 执行视频剪辑...")
            video_editor = VideoEditor(
                codec=cfg.get('editing', {}).get('codec', 'libx264'),
                audio_codec=cfg.get('editing', {}).get('audio_codec', 'aac'),
                quality=cfg.get('editing', {}).get('quality', 'high')
            )

            success = video_editor.apply_timeline_edit(input_video, timeline, output)

            if success:
                click.echo(f"\n   [OK] 剪辑完成！")
                click.echo(f"   [OK] 输出文件: {output}")
            else:
                click.echo(f"\n   [ERROR] 剪辑失败", err=True)
                sys.exit(1)

    except Exception as e:
        click.echo(f"\n✗ 错误: {e}", err=True)
        logger.exception("处理失败")
        sys.exit(1)


@main.command()
@click.argument('input_video', type=click.Path(exists=True))
@click.option('--output', '-o', help='输出字幕路径')
@click.option('--format', default='srt', type=click.Choice(['srt', 'vtt']),
              help='字幕格式')
@click.option('--model', default='base', type=click.Choice(['tiny', 'base', 'small', 'medium', 'large']),
              help='Whisper模型大小')
def subtitle(input_video, output, format, model):
    """
    仅生成字幕文件

    示例:
        ai-cutter subtitle input.mp4 -o subs.srt
        ai-cutter subtitle input.mp4 --format vtt
    """
    try:
        if output is None:
            input_path = Path(input_video)
            output = str(input_path.parent / f"{input_path.stem}.{format}")

        click.echo(f"正在识别音频...")
        recognizer = SpeechRecognizer(model_size=model)
        segments = recognizer.transcribe_video(input_video)

        recognizer.save_subtitle(segments, output, format)
        click.echo(f"✓ 字幕已保存: {output}")

    except Exception as e:
        click.echo(f"✗ 错误: {e}", err=True)
        sys.exit(1)


@main.command()
@click.argument('input_video', type=click.Path(exists=True))
def info(input_video):
    """
    显示视频信息

    示例:
        ai-cutter info input.mp4
    """
    try:
        video_editor = VideoEditor()
        video_info = video_editor.get_video_info(input_video)

        click.echo(f"视频信息:")
        click.echo(f"  文件: {input_video}")
        click.echo(f"  时长: {video_info.get('duration', 0):.1f}秒")
        click.echo(f"  尺寸: {video_info.get('width', 0)}x{video_info.get('height', 0)}")
        click.echo(f"  帧率: {video_info.get('fps', 0):.1f}fps")
        click.echo(f"  音频: {'有' if video_info.get('has_audio') else '无'}")

    except Exception as e:
        click.echo(f"✗ 错误: {e}", err=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
