"""
Blender导出模块 - 生成可在Blender中编辑的项目
"""

import os
import json
from typing import List, Dict, Optional
from pathlib import Path
import logging

# 导入增强的可拖拽HTML导出器
from draggable_html_exporter import create_draggable_html

logger = logging.getLogger(__name__)


class BlenderExporter:
    """导出时间线到Blender项目"""

    def __init__(self):
        """初始化Blender导出器"""
        pass

    def create_blender_project(self, video_path: str, timeline: List[Dict],
                              output_path: str) -> str:
        """
        创建Blender项目文件

        Args:
            video_path: 原视频路径
            timeline: 剪辑时间线
            output_path: 输出的.blend文件路径

        Returns:
            Blender项目文件路径
        """
        try:
            import bpy

            # 初始化Blender场景
            self._setup_scene()

            # 获取视频信息
            video_info = self._get_video_info(video_path)
            fps = video_info.get('fps', 30)

            # 添加视频到视频序列编辑器
            strip = self._add_video_strip(video_path, fps)

            # 根据时间线应用剪辑
            self._apply_timeline_edits(timeline, strip, fps)

            # 保存.blend文件
            bpy.ops.wm.save_as_mainfile(filepath=output_path)

            logger.info(f"Blender项目已创建: {output_path}")
            return output_path

        except ImportError:
            logger.warning("未安装bpy模块，生成Python脚本代替")
            return self._create_blender_script(video_path, timeline, output_path)

    def _setup_scene(self):
        """设置Blender场景用于视频编辑"""
        import bpy

        # 清空默认场景
        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.object.delete()

        # 切换到视频编辑界面
        bpy.context.window.workspace = bpy.data.workspaces['Video Editing']
        bpy.context.area.type = 'VIDEO_EDITOR'

        # 设置视频序列编辑器
        if not bpy.data.scenes['Scene'].sequence_editor:
            sequencer_data = bpy.data.scenes['Scene'].sequence_editor_create()
        else:
            sequencer_data = bpy.data.scenes['Scene'].sequence_editor

    def _get_video_info(self, video_path: str) -> Dict:
        """获取视频信息"""
        try:
            from moviepy import VideoFileClip
            clip = VideoFileClip(video_path)
            info = {
                'fps': clip.fps,
                'duration': clip.duration,
                'width': clip.w,
                'height': clip.h
            }
            clip.close()
            return info
        except:
            return {'fps': 30, 'duration': 0, 'width': 1920, 'height': 1080}

    def _add_video_strip(self, video_path: str, fps: float):
        """添加视频条带"""
        import bpy

        try:
            # 添加视频条带到视频序列编辑器
            bpy.ops.sequencer.movie_strip_add(filepath=video_path)
            strip = bpy.context.scene.sequence_editor.sequences.all_sequences[-1]
            strip.channel = 1
            return strip
        except Exception as e:
            logger.error(f"添加视频失败: {e}")
            return None

    def _apply_timeline_edits(self, timeline: List[Dict], strip, fps: float):
        """应用剪辑时间线"""
        if not strip:
            logger.warning("视频条带不存在，跳过剪辑")
            return

        # Blender中需要反向操作（从后往前删除）
        keep_segments = [item for item in timeline if item['action'] == 'keep']

        if not keep_segments:
            logger.warning("没有要保留的片段")
            return

        # 在Blender中应用切割
        # 注意：这需要在Blender中手动调整，或者使用更复杂的脚本
        logger.info(f"在Blender中标记了{len(keep_segments)}个保留片段")

    def _create_blender_script(self, video_path: str, timeline: List[Dict],
                                output_path: str) -> str:
        """
        创建可以在Blender中运行的Python脚本

        Args:
            video_path: 视频路径
            timeline: 剪辑时间线
            output_path: 输出路径

        Returns:
            脚本文件路径
        """
        script_path = output_path.replace('.blend', '_script.py')

        script_content = f'''import bpy
import os

# 设置视频路径
video_path = r"{os.path.abspath(video_path)}"

# 清空场景
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# 切换到视频编辑模式
bpy.context.window.workspace = bpy.data.workspaces['Video Editing']

# 添加视频
try:
    bpy.ops.sequencer.movie_strip_add(filepath=video_path)
    strip = bpy.context.scene.sequence_editor.sequences.all_sequences[-1]
    strip.channel = 1
    print(f"已添加视频: {{video_path}}")
except Exception as e:
    print(f"添加视频失败: {{e}}")

# 剪辑时间线
timeline = {json.dumps(timeline, indent=2, ensure_ascii=False)}

# 标记保留片段
keep_segments = [item for item in timeline if item['action'] == 'keep']
print(f"共 {{len(keep_segments)}} 个保留片段")

# 保存项目
bpy.ops.wm.save_as_mainfile(filepath=r"{os.path.abspath(output_path)}")
print(f"项目已保存")
'''

        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(script_content)

        logger.info(f"Blender脚本已创建: {script_path}")
        return script_path

    def export_to_edl(self, timeline: List[Dict], output_path: str) -> str:
        """
        导出为EDL格式（可被DaVinci Resolve等软件导入）

        Args:
            timeline: 剪辑时间线
            output_path: EDL文件输出路径

        Returns:
            EDL文件路径
        """
        lines = []
        lines.append(f"TITLE: AI Video Cutter Project")
        lines.append("")

        event_number = 1
        for item in timeline:
            if item['action'] == 'keep':
                # EDL格式: 001  001  V     C        00:00:00:00 00:00:10:00 00:00:00:00 00:00:10:00
                # 这里的格式可能需要调整，具体看目标软件的要求
                start_time = self._seconds_to_timecode(item['start'])
                end_time = self._seconds_to_timecode(item['end'])

                lines.append(f"{event_number:03d}  001  V     C        {start_time} {end_time} {start_time} {end_time}")
                lines.append(f" * FROM CLIP NAME: {item.get('text', 'clip')[:32]}")
                lines.append("")
                event_number += 1

        edl_content = "\n".join(lines)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(edl_content)

        logger.info(f"EDL文件已创建: {output_path}")
        return output_path

    def export_to_xml(self, video_path: str, timeline: List[Dict],
                     output_path: str) -> str:
        """
        导出为FCPXML格式（Final Cut Pro XML）

        Args:
            video_path: 视频路径
            timeline: 剪辑时间线
            output_path: XML文件输出路径

        Returns:
            XML文件路径
        """
        import xml.etree.ElementTree as ET

        # 创建XML根元素
        xmeml = ET.Element('xmeml', version="5")

        # 添加序列信息
        sequence = ET.SubElement(xmeml, 'sequence')
        ET.SubElement(sequence, 'name').text = "AI Video Cutter Project"
        ET.SubElement(sequence, 'duration').text = str(int(timeline[-1]['end'] * 30)) if timeline else "0"

        # 添加媒体信息
        media = ET.SubElement(xmeml, 'media')
        video = ET.SubElement(media, 'video')

        # 添加原始视频信息
        track = ET.SubElement(video, 'track')
        ET.SubElement(track, 'name').text = "Video Track 1"
        ET.SubElement(track, 'output').text = "video"

        # 添加剪辑片段
        for item in timeline:
            if item['action'] == 'keep':
                clipitem = ET.SubElement(track, 'clipitem')
                ET.SubElement(clipitem, 'name').text = item.get('text', 'clip')[:255]
                ET.SubElement(clipitem, 'duration').text = str(int((item['end'] - item['start']) * 30))
                ET.SubElement(clipitem, 'start').text = str(int(item['start'] * 30))
                ET.SubElement(clipitem, 'end').text = str(int(item['end'] * 30))

                # 添加文件引用
                file_elem = ET.SubElement(clipitem, 'file')
                ET.SubElement(file_elem, 'name').text = os.path.basename(video_path)
                pathurl = ET.SubElement(file_elem, 'pathurl')
                pathurl.text = f"file://{os.path.abspath(video_path).replace(os.sep, '/')}"

        # 生成XML字符串
        xml_string = ET.tostring(xmeml, encoding='unicode', method='xml')

        # 写入文件
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
            f.write('<!DOCTYPE xmeml>\n')
            f.write(xml_string)

        logger.info(f"FCPXML文件已创建: {output_path}")
        return output_path

    def create_interactive_html(self, video_path: str, timeline: List[Dict],
                               repeats: List[Dict], output_path: str) -> str:
        """
        创建增强的可拖拽时间线HTML界面

        Args:
            video_path: 视频路径
            timeline: 剪辑时间线
            repeats: 重复检测结果
            output_path: HTML输出路径

        Returns:
            HTML文件路径
        """
        logger.info(f"创建可拖拽HTML界面: {output_path}")
        return create_draggable_html(video_path, timeline, repeats, output_path)
        html_content = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI视频剪辑器 - 可拖拽时间线</title>
    <style>
        * {{
            box-sizing: border-box;
        }}
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #d4d4d4;
            min-height: 100vh;
        }}
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: #2d2d2d;
            border-radius: 12px;
            padding: 30px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }}
        h1 {{
            color: #4ec9b0;
            border-bottom: 3px solid #4ec9b0;
            padding-bottom: 15px;
            margin-top: 0;
            font-size: 28px;
        }}
        .video-section {{
            background: #1e1e1e;
            padding: 25px;
            border-radius: 8px;
            margin-bottom: 25px;
            border: 1px solid #3d3d3d;
        }}
        .video-wrapper {{
            position: relative;
            background: #000;
            border-radius: 8px;
            overflow: hidden;
        }}
        video {{
            width: 100%;
            max-width: 900px;
            display: block;
            margin: 0 auto;
            border-radius: 4px;
        }}
        .video-controls {{
            display: flex;
            justify-content: center;
            gap: 10px;
            margin-top: 15px;
            flex-wrap: wrap;
        }}
        .video-controls button {{
            background: #3d3d3d;
            color: #fff;
            border: 1px solid #4ec9b0;
            padding: 8px 16px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 13px;
            transition: all 0.3s;
        }}
        .video-controls button:hover {{
            background: #4ec9b0;
            color: #1e1e1e;
        }}
        .timeline-editor {{
            background: #1e1e1e;
            padding: 25px;
            border-radius: 8px;
            margin-bottom: 25px;
            border: 1px solid #3d3d3d;
        }}
        .timeline-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            flex-wrap: wrap;
            gap: 15px;
        }}
        .timeline-header h2 {{
            margin: 0;
            color: #4ec9b0;
            font-size: 20px;
        }}
        .timeline-visual {{
            position: relative;
            height: 120px;
            background: #000;
            border-radius: 8px;
            margin: 20px 0;
            overflow: hidden;
            border: 2px solid #3d3d3d;
        }}
        .timeline-track {{
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            display: flex;
            align-items: stretch;
        }}
        .timeline-segment {{
            position: relative;
            border-right: 2px solid #000;
            transition: all 0.3s;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 12px;
            font-weight: bold;
            text-shadow: 1px 1px 2px rgba(0,0,0,0.8);
            overflow: hidden;
            padding: 5px;
        }}
        .timeline-segment:hover {{
            filter: brightness(1.2);
            transform: scaleY(1.05);
        }}
        .timeline-segment.keep {{
            background: linear-gradient(135deg, #4ec9b0 0%, #3db8a0 100%);
            color: #000;
        }}
        .timeline-segment.cut {{
            background: linear-gradient(135deg, #f44747 0%, #e33939 100%);
            color: #fff;
            opacity: 0.7;
        }}
        .timeline-segment.selected {{
            box-shadow: 0 0 0 3px #fff, 0 0 20px rgba(78, 201, 176, 0.8);
            z-index: 10;
        }}
        .timeline-segment .segment-label {{
            text-align: center;
            word-break: break-word;
            hyphens: auto;
        }}
        .timeline-ruler {{
            position: absolute;
            bottom: 0;
            left: 0;
            right: 0;
            height: 25px;
            background: rgba(0,0,0,0.8);
            display: flex;
            align-items: flex-end;
            font-size: 11px;
            color: #888;
        }}
        .ruler-mark {{
            position: absolute;
            bottom: 0;
            height: 15px;
            border-left: 1px solid #666;
            padding-left: 3px;
        }}
        .playhead {{
            position: absolute;
            top: 0;
            bottom: 0;
            width: 2px;
            background: #ff6b6b;
            z-index: 100;
            cursor: ew-resize;
            box-shadow: 0 0 10px rgba(255, 107, 107, 0.8);
        }}
        .playhead::before {{
            content: '';
            position: absolute;
            top: -5px;
            left: -4px;
            width: 0;
            height: 0;
            border-left: 5px solid transparent;
            border-right: 5px solid transparent;
            border-top: 8px solid #ff6b6b;
        }}
        .segment-list {{
            max-height: 400px;
            overflow-y: auto;
            background: #000;
            border-radius: 8px;
            padding: 15px;
            border: 1px solid #3d3d3d;
        }}
        .segment-item {{
            display: flex;
            align-items: center;
            padding: 12px;
            margin: 8px 0;
            border-radius: 6px;
            cursor: pointer;
            transition: all 0.3s;
            border: 2px solid transparent;
        }}
        .segment-item:hover {{
            background: #3d3d3d;
            transform: translateX(5px);
        }}
        .segment-item.keep {{
            border-left: 4px solid #4ec9b0;
        }}
        .segment-item.cut {{
            border-left: 4px solid #f44747;
            opacity: 0.7;
        }}
        .segment-item.selected {{
            background: #3d3d3d;
            border-color: #4ec9b0;
        }}
        .segment-item .segment-time {{
            min-width: 150px;
            font-family: 'Consolas', monospace;
            font-size: 13px;
            color: #4ec9b0;
        }}
        .segment-item .segment-content {{
            flex: 1;
            font-size: 14px;
            padding: 0 15px;
        }}
        .segment-item .segment-action {{
            min-width: 100px;
            text-align: center;
            font-weight: bold;
            font-size: 13px;
        }}
        .segment-item .segment-duration {{
            min-width: 80px;
            text-align: right;
            font-family: 'Consolas', monospace;
            color: #888;
            font-size: 12px;
        }}
        .action-keep {{ color: #4ec9b0; }}
        .action-cut {{ color: #f44747; }}
        .controls {{
            background: #1e1e1e;
            padding: 20px;
            border-radius: 8px;
            margin-top: 20px;
            border: 1px solid #3d3d3d;
        }}
        .controls h2 {{
            margin-top: 0;
            color: #4ec9b0;
            font-size: 18px;
        }}
        .controls-row {{
            display: flex;
            gap: 12px;
            flex-wrap: wrap;
            margin-bottom: 15px;
        }}
        button {{
            background: linear-gradient(135deg, #4ec9b0 0%, #3db8a0 100%);
            color: #1e1e1e;
            border: none;
            padding: 12px 24px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 14px;
            font-weight: 600;
            transition: all 0.3s;
            box-shadow: 0 4px 15px rgba(78, 201, 176, 0.3);
        }}
        button:hover {{
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(78, 201, 176, 0.4);
        }}
        button:active {{
            transform: translateY(0);
        }}
        button.secondary {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
        }}
        button.secondary:hover {{
            box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
        }}
        .stats {{
            background: #1e1e1e;
            padding: 20px;
            border-radius: 8px;
            margin-top: 20px;
            border: 1px solid #3d3d3d;
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
        }}
        .stat-item {{
            background: #3d3d3d;
            padding: 15px;
            border-radius: 6px;
            text-align: center;
        }}
        .stat-value {{
            font-size: 28px;
            font-weight: bold;
            color: #4ec9b0;
            margin-bottom: 5px;
        }}
        .stat-label {{
            font-size: 12px;
            color: #888;
            text-transform: uppercase;
        }}
        .edit-panel {{
            background: #3d3d3d;
            padding: 20px;
            border-radius: 8px;
            margin-top: 20px;
            border: 1px solid #4ec9b0;
        }}
        .edit-panel h3 {{
            margin-top: 0;
            color: #4ec9b0;
        }}
        .edit-controls {{
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
            align-items: center;
        }}
        .edit-controls input[type="number"] {{
            background: #1e1e1e;
            border: 1px solid #4ec9b0;
            color: #fff;
            padding: 8px 12px;
            border-radius: 4px;
            width: 100px;
        }}
        .hidden {{ display: none; }}
        .modal {{
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0,0,0,0.8);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 1000;
        }}
        .modal-content {{
            background: #2d2d2d;
            padding: 30px;
            border-radius: 12px;
            max-width: 600px;
            text-align: center;
            border: 2px solid #4ec9b0;
        }}
        .modal-content h2 {{
            color: #4ec9b0;
            margin-top: 0;
        }}
        .spinner {{
            border: 4px solid #f3f3f3;
            border-top: 4px solid #4ec9b0;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 20px auto;
        }}
        @keyframes spin {{
            0% {{ transform: rotate(0deg); }}
            100% {{ transform: rotate(360deg); }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🎬 AI视频剪辑器 - 交互式编辑</h1>

        <div class="video-section">
            <h2>视频预览</h2>
            <video id="videoPlayer" controls>
                <source src="file:///{os.path.abspath(video_path).replace(os.sep, '/')}" type="video/mp4">
                您的浏览器不支持视频播放。
            </video>
        </div>

        <div class="timeline" id="timeline">
            <h2>剪辑时间线</h2>
            <div id="timelineItems"></div>
        </div>

        <div class="controls">
            <h2>操作</h2>
            <button onclick="exportEDL()">导出EDL (DaVinci)</button>
            <button onclick="exportXML()">导出XML (FCP)</button>
            <button onclick="exportJSON()">导出JSON</button>
            <button onclick="toggleAll()">切换全部</button>
        </div>

        <div class="stats">
            <h2>统计信息</h2>
            <p>总片段数: <span id="totalSegments">0</span></p>
            <p>保留: <span id="keepCount">0</span></p>
            <p>剪掉: <span id="cutCount">0</span></p>
            <p>保留时长: <span id="keepDuration">0</span>秒</p>
        </div>
    </div>

    <script>
        // 时间线数据
        const timeline = {json.dumps(timeline)};
        const video = document.getElementById('videoPlayer');
        let currentSegment = 0;

        // 渲染时间线
        function renderTimeline() {{
            const container = document.getElementById('timelineItems');
            container.innerHTML = '';

            let keepCount = 0;
            let cutCount = 0;
            let keepDuration = 0;

            timeline.forEach((item, index) => {{
                const div = document.createElement('div');
                div.className = `timeline-item ${{item.action}}`;
                div.onclick = () => jumpToSegment(index);

                const start = formatTime(item.start);
                const end = formatTime(item.end);
                const duration = (item.end - item.start).toFixed(1);
                const action = item.action === 'keep' ? '保留' : '剪掉';
                const actionClass = item.action === 'keep' ? 'action-keep' : 'action-cut';
                const text = item.text || '(无文本)';

                div.innerHTML = `
                    <div class="time">${{start}} - ${{end}}</div>
                    <div class="content">{{${text}}}</div>
                    <div class="action ${{actionClass}}">${{action}}</div>
                `;

                container.appendChild(div);

                if (item.action === 'keep') {{
                    keepCount++;
                    keepDuration += (item.end - item.start);
                }} else {{
                    cutCount++;
                }}
            }});

            // 更新统计
            document.getElementById('totalSegments').textContent = timeline.length;
            document.getElementById('keepCount').textContent = keepCount;
            document.getElementById('cutCount').textContent = cutCount;
            document.getElementById('keepDuration').textContent = keepDuration.toFixed(1);
        }}

        // 格式化时间
        function formatTime(seconds) {{
            const mins = Math.floor(seconds / 60);
            const secs = Math.floor(seconds % 60);
            return `${{mins.toString().padStart(2, '0')}}:${{secs.toString().padStart(2, '0')}}`;
        }}

        // 跳转到指定片段
        function jumpToSegment(index) {{
            const segment = timeline[index];
            video.currentTime = segment.start;
            video.play();
        }}

        // 切换片段状态
        function toggleSegment(index) {{
            timeline[index].action = timeline[index].action === 'keep' ? 'cut' : 'keep';
            renderTimeline();
        }}

        // 切换全部
        function toggleAll() {{
            const allKeep = timeline.every(item => item.action === 'keep');
            timeline.forEach(item => {{
                item.action = allKeep ? 'cut' : 'keep';
            }});
            renderTimeline();
        }}

        // 导出功能
        function exportEDL() {{
            alert('EDL导出功能：请在命令行中使用 --export-edl 参数');
        }}

        function exportXML() {{
            alert('XML导出功能：请在命令行中使用 --export-xml 参数');
        }}

        function exportJSON() {{
            const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(timeline, null, 2));
            const downloadAnchorNode = document.createElement('a');
            downloadAnchorNode.setAttribute("href", dataStr);
            downloadAnchorNode.setAttribute("download", "timeline.json");
            document.body.appendChild(downloadAnchorNode);
            downloadAnchorNode.click();
            downloadAnchorNode.remove();
        }}

        // 初始化
        renderTimeline();
    </script>
</body>
</html>
'''

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

        logger.info(f"交互式HTML已创建: {output_path}")
        return output_path

    @staticmethod
    def _seconds_to_timecode(seconds: float) -> str:
        """将秒数转换为时间码格式 (HH:MM:SS:FF)"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        frames = int((seconds % 1) * 30)  # 假设30fps
        return f"{hours:02d}:{minutes:02d}:{secs:02d}:{frames:02d}"


# 便捷函数
def create_blender_project(video_path: str, timeline: List[Dict],
                          output_path: str) -> str:
    """创建Blender项目"""
    exporter = BlenderExporter()
    return exporter.create_blender_project(video_path, timeline, output_path)


def export_to_edl(timeline: List[Dict], output_path: str) -> str:
    """导出为EDL格式"""
    exporter = BlenderExporter()
    return exporter.export_to_edl(timeline, output_path)


def export_to_xml(video_path: str, timeline: List[Dict], output_path: str) -> str:
    """导出为FCPXML格式"""
    exporter = BlenderExporter()
    return exporter.export_to_xml(video_path, timeline, output_path)


def create_interactive_html(video_path: str, timeline: List[Dict],
                           repeats: List[Dict], output_path: str) -> str:
    """创建交互式HTML报告"""
    exporter = BlenderExporter()
    return exporter.create_interactive_html(video_path, timeline, repeats, output_path)
