"""
Blender VSE (视频序列编辑器) 集成模块
生成完整的Blender项目和脚本，用于专业视频编辑
"""

import os
import json
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class BlenderVSEExporter:
    """Blender视频序列编辑器导出器"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def create_blender_project(self, video_path: str, timeline: List[Dict],
                               output_path: str, project_name: str = "AI_Video_Cutter") -> str:
        """
        创建完整的Blender VSE项目

        Args:
            video_path: 原视频路径
            timeline: 剪辑时间线
            output_path: 输出目录
            project_name: 项目名称

        Returns:
            生成的脚本文件路径
        """
        try:
            # 确保输出目录存在
            os.makedirs(output_path, exist_ok=True)

            # 生成多个文件：Blender脚本、项目信息、使用说明
            script_path = os.path.join(output_path, f"{project_name}_blender_script.py")
            info_path = os.path.join(output_path, f"{project_name}_project_info.json")
            readme_path = os.path.join(output_path, f"{project_name}_README.txt")

            # 1. 生成Blender Python脚本
            self._generate_blender_script(video_path, timeline, script_path, project_name)

            # 2. 生成项目信息文件
            self._generate_project_info(video_path, timeline, info_path, project_name)

            # 3. 生成使用说明
            self._generate_readme(output_path, readme_path, project_name)

            self.logger.info(f"Blender VSE项目已创建: {output_path}")
            return script_path

        except Exception as e:
            self.logger.error(f"创建Blender项目失败: {e}")
            raise

    def _generate_blender_script(self, video_path: str, timeline: List[Dict],
                                  script_path: str, project_name: str):
        """生成可在Blender中运行的Python脚本"""

        video_path_abs = os.path.abspath(video_path).replace('\\', '/')
        timeline_json = json.dumps(timeline, ensure_ascii=False)

        script_content = f'''"""
Blender VSE (视频序列编辑器) 脚本
由AI视频剪辑器自动生成

项目: {project_name}
视频: {os.path.basename(video_path)}

使用方法:
1. 打开Blender
2. 切换到Video Editing工作区
3. Window → Toggle System Console
4. 在System Console中运行: Scripting → Open → 选择此脚本
   或者直接在Scripting工作区中运行此脚本
"""

import bpy
import os
import json

# 清空当前场景
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# 切换到视频编辑工作区
if 'Video Editing' not in [ws.name for ws in bpy.data.workspaces]:
    # 创建新的视频编辑工作区
    workspace = bpy.data.workspaces.new('Video Editing')
    workspace.screens[0].areas[0].type = 'VIDEO_EDITOR'
else:
    # 使用现有的视频编辑工作区
    for window in bpy.context.window_manager.windows:
        for area in window.screen.areas:
            if area.type == 'VIEW_3D':
                area.type = 'VIDEO_EDITOR'
                break

# 确保当前场景有序列编辑器
if not bpy.context.scene.sequence_editor:
    bpy.context.scene.sequence_editor_create()

# 获取序列编辑器
seq_editor = bpy.context.scene.sequence_editor

# 视频文件路径
VIDEO_PATH = r"{video_path_abs}"

# 时间线数据
TIMELINE_DATA = {timeline_json}

print(f"="*60)
print(f"AI视频剪辑器 - Blender VSE脚本")
print(f"="*60)
print(f"项目: {project_name}")
print(f"视频: {{VIDEO_PATH}}")
print(f"时间线索引: {{len(TIMELINE_DATA)}} 个片段")
print(f"="*60)

# 添加视频到VSE
try:
    # 导入视频
    bpy.ops.sequencer.movie_strip_add(filepath=VIDEO_PATH)
    main_strip = seq_editor.sequences_all[-1]
    main_strip.name = "原始视频"

    print(f"✓ 视频已添加: {{main_strip.name}}")
    print(f"  时长: {{main_strip.frame_duration}} 帧")
    print(f"  帧率: {{bpy.context.scene.render.fps}} fps")

    # 获取场景信息
    fps = bpy.context.scene.render.fps
    total_frames = main_strip.frame_final_end

    print(f"\\n开始处理剪辑时间线...")

    # 创建标记点用于剪辑
    marker_frame = 0
    keep_count = 0
    cut_count = 0

    for item in TIMELINE_DATA:
        start_frame = int(item['start'] * fps)
        end_frame = int(item['end'] * fps)

        if item['action'] == 'keep':
            # 保留的片段 - 添加绿色标记
            marker = seq_editor.markers.new(frame=start_frame, name=f"保留: {{item.get('text', '')[:20]}}")
            keep_count += 1
        else:
            # 剪掉的片段 - 添加红色标记
            marker = seq_editor.markers.new(frame=start_frame, name=f"剪掉: {{item.get('text', '')[:20]}}")
            cut_count += 1

    print(f"\\n剪辑标记已创建:")
    print(f"  保留片段: {{keep_count}}")
    print(f"  剪掉片段: {{cut_count}}")

    # 设置预览范围
    if TIMELINE_DATA:
        first_keep = next((item for item in TIMELINE_DATA if item['action'] == 'keep'), None)
        if first_keep:
            start_frame = int(first_keep['start'] * fps)
            bpy.context.scene.frame_start = start_frame
            bpy.context.scene.frame_end = total_frames

    # 切换到预览模式
    for window in bpy.context.window_manager.windows:
        for area in window.screen.areas:
            if area.type == 'VIDEO_EDITOR':
                for region in area.regions:
                    if region.type == 'PREVIEW':
                        override = {{'area': area, 'region': region}}
                        try:
                            bpy.ops.sequencer.view_all(override)
                        except:
                            pass
                        break

    print(f"\\n✓ Blender VSE项目设置完成!")
    print(f"\\n下一步操作:")
    print(f"1. 在时间线中查看彩色标记")
    print(f"2. 绿色标记 = 保留的内容")
    print(f"3. 红色标记 = 需要剪掉的内容")
    print(f"4. 可以手动调整剪辑点")
    print(f"5. 导出最终视频: File → Export → Movie")

except Exception as e:
    print(f"✗ 错误: {{e}}")
    import traceback
    traceback.print_exc()

print(f"="*60)
'''

        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(script_content)

        self.logger.info(f"Blender脚本已生成: {script_path}")

    def _generate_project_info(self, video_path: str, timeline: List[Dict],
                               info_path: str, project_name: str):
        """生成项目信息JSON文件"""

        # 计算统计信息
        keep_segments = [item for item in timeline if item['action'] == 'keep']
        cut_segments = [item for item in timeline if item['action'] == 'cut']

        keep_duration = sum(item['end'] - item['start'] for item in keep_segments)
        cut_duration = sum(item['end'] - item['start'] for item in cut_segments)
        total_duration = keep_duration + cut_duration

        project_info = {
            "project_name": project_name,
            "video_path": os.path.abspath(video_path),
            "video_filename": os.path.basename(video_path),
            "timeline": timeline,
            "statistics": {
                "total_segments": len(timeline),
                "keep_segments": len(keep_segments),
                "cut_segments": len(cut_segments),
                "keep_duration": round(keep_duration, 2),
                "cut_duration": round(cut_duration, 2),
                "total_duration": round(total_duration, 2),
                "keep_ratio": round(keep_duration / total_duration * 100, 1) if total_duration > 0 else 0
            },
            " blender_settings": {
                "fps": 30,
                "resolution": "1920x1080",
                "audio_codec": "AAC",
                "video_codec": "H.264"
            }
        }

        with open(info_path, 'w', encoding='utf-8') as f:
            json.dump(project_info, f, indent=2, ensure_ascii=False)

        self.logger.info(f"项目信息已生成: {info_path}")

    def _generate_readme(self, output_path: str, readme_path: str, project_name: str):
        """生成使用说明文件"""

        readme_content = f'''# {project_name} - Blender VSE项目

## 🎬 项目概述

这是一个由AI视频剪辑器自动生成的Blender VSE项目。AI已经分析了你的视频并标记了需要剪辑的部分。

## 📊 项目统计

请查看 `{project_name}_project_info.json` 文件获取详细的统计信息。

## 🚀 使用方法

### 方法1: 运行Python脚本（推荐）

1. **安装Blender**
   - 下载地址: https://www.blender.org/download/
   - 选择与你系统匹配的版本
   - 安装并启动Blender

2. **打开脚本编辑器**
   - 在Blender顶部标签栏选择 `Scripting` 工作区
   - 或按 `Shift + F3` 切换到Scripting工作区

3. **运行脚本**
   - 点击 `Open` 按钮，选择 `{project_name}_blender_script.py`
   - 点击 `Run Script` 按钮（或按 `Alt + P`）
   - 查看底部的System Console输出

4. **切换到视频编辑模式**
   - 顶部标签栏选择 `Video Editing`
   - 你会看到已经导入的视频和彩色标记

### 方法2: 手动导入

1. **新建视频编辑项目**
   - File → New → Video Editing

2. **导入视频**
   - Add → Movie (快捷键: Shift + A)
   - 选择你的原始视频文件

3. **查看剪辑标记**
   - 脚本会自动在时间线上添加标记
   - 绿色标记 = 保留
   - 红色标记 = 剪掉

## 🎯 在Blender中编辑视频

### 查看时间线
- 时间线在底部，显示视频的所有帧
- 彩色标记指示了AI建议的剪辑点

### 手动调整剪辑
1. **播放视频** (快捷键: Space)
2. **移动播放头** (鼠标拖动或按左右箭头)
3. **添加剪辑点** (快捷键: K)
4. **删除不需要的片段** (选中后按 Delete)
5. **移动片段** (按 G 键拖动)

### 高级编辑
- **淡入淡出**: 选中片段 → Sidebar → Add Effect → Cross
- **音频处理**: 音频在视频下方，可以单独编辑
- **颜色校正**: 切换到Compositing工作区

## 📤 导出最终视频

### 方法1: 快速导出
1. File → Export → Movie
2. 选择输出位置
3. 点击Export

### 方法2: 高质量导出
1. Render Properties (右侧面板)
2. 设置:
   - Resolution: 1920x1080 (或你的视频分辨率)
   - Frame Rate: 30fps (或你的视频帧率)
   - Format: MPEG-4
   - Video Codec: H.264
   - Audio Codec: AAC
3. File → Export → Movie

## ⌨️ 常用快捷键

- **Space**: 播放/暂停
- **Shift + A**: 添加素材
- **Delete**: 删除选中片段
- **K**: 在播放头位置切割
- **G**: 移动片段
- **S**: 调整片段大小
- **Home**: 查看整个时间线
- **NumPad 0**: 切换到预览窗口
- **NumPad 1**: 切换到时间线

## 🎨 界面说明

- **顶部**: 时间轴，可以拖动播放头
- **中部**: 视频预览窗口
- **底部**: 片段轨道（视频+音频）
- **右侧**: 属性面板，可以调整参数

## 💡 提示

1. **保存项目**: File → Save (快捷键: Ctrl + S)，保存为.blend文件
2. **自动保存**: Blender会自动保存备份到临时文件夹
3. **撤销**: Ctrl + Z 可以撤销操作
4. **重做**: Ctrl + Shift + Z 可以重做操作

## 🔧 故障排除

### 视频无法播放
- 确认视频格式是Blender支持的（MP4, AVI, MOV等）
- 检查视频文件路径是否正确

### 脚本运行错误
- 查看System Console的详细错误信息
- 确认Blender版本（建议使用3.0+）

### 导出失败
- 检查输出路径是否有写入权限
- 尝试降低视频质量设置

## 📚 更多资源

- Blender官方文档: https://docs.blender.org/manual/en/latest/editors/video_sequencer/index.html
- 视频教程: https://www.youtube.com/results?search_query=blender+video+sequencer+tutorial
- Blender社区: https://blender.stackexchange.com/

## 🎉 开始编辑！

现在你可以开始使用Blender的强大功能来编辑你的视频了。AI已经为你标记了需要剪辑的部分，你只需要：

1. 查看标记
2. 确认剪辑点
3. 导出最终视频

祝编辑愉快！ 🎬
'''

        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(readme_content)

        self.logger.info(f"使用说明已生成: {readme_path}")


# 便捷函数
def create_blender_vse_project(video_path: str, timeline: List[Dict],
                               output_dir: str, project_name: str = "AI_Video_Cutter") -> str:
    """
    创建Blender VSE项目

    Args:
        video_path: 视频文件路径
        timeline: 剪辑时间线
        output_dir: 输出目录
        project_name: 项目名称

    Returns:
        生成的脚本文件路径
    """
    exporter = BlenderVSEExporter()
    return exporter.create_blender_project(video_path, timeline, output_dir, project_name)
