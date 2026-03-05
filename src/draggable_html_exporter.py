"""
Enhanced HTML Exporter with Draggable Timeline
"""

import os
import json
from typing import List, Dict


def create_draggable_html(video_path: str, timeline: List[Dict],
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

    html_template = f'''<!DOCTYPE html>
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
        <h1>AI视频剪辑器 - 可拖拽时间线</h1>

        <div class="video-section">
            <h2 style="color: #4ec9b0; margin-top: 0;">视频预览</h2>
            <div class="video-wrapper">
                <video id="videoPlayer" controls>
                    <source src="file:///{os.path.abspath(video_path).replace(os.sep, '/')}\" type="video/mp4">
                    您的浏览器不支持视频播放。
                </video>
            </div>
            <div class="video-controls">
                <button onclick="skipBackward()">-5秒</button>
                <button onclick="togglePlay()">播放/暂停</button>
                <button onclick="skipForward()">+5秒</button>
                <button onclick="skipToNextSegment()">下一片段</button>
                <button onclick="skipToPrevSegment()">上一片段</button>
                <button onclick="setPlaybackSpeed(0.5)">0.5x</button>
                <button onclick="setPlaybackSpeed(1)">1x</button>
                <button onclick="setPlaybackSpeed(1.5)">1.5x</button>
                <button onclick="setPlaybackSpeed(2)">2x</button>
            </div>
        </div>

        <div class="timeline-editor">
            <div class="timeline-header">
                <h2>可视化时间线 (可拖拽调整)</h2>
                <div class="edit-controls">
                    <button class="secondary" onclick="toggleAllSegments()">切换全部</button>
                    <button class="secondary" onclick="optimizeTimeline()">智能优化</button>
                    <button class="secondary" onclick="resetTimeline()">重置</button>
                </div>
            </div>

            <div class="timeline-visual" id="timelineVisual">
                <div class="timeline-track" id="timelineTrack"></div>
                <div class="timeline-ruler" id="timelineRuler"></div>
                <div class="playhead" id="playhead"></div>
            </div>

            <p style="color: #888; font-size: 13px; margin-bottom: 15px;">
                点击时间线上的片段切换保留/删除状态，拖拽红色播放头跳转位置
            </p>
        </div>

        <div class="timeline-editor" id="segmentList">
            <div class="timeline-header">
                <h2>片段列表</h2>
                <div class="edit-controls">
                    <input type="text" id="searchInput" placeholder="搜索片段..."
                           style="background: #1e1e1e; border: 1px solid #4ec9b0; color: #fff; padding: 8px 12px; border-radius: 4px; width: 200px;"
                           oninput="filterSegments()">
                </div>
            </div>
            <div class="segment-list" id="segmentListContainer"></div>
        </div>

        <div class="stats">
            <h2 style="color: #4ec9b0; margin-top: 0;">统计信息</h2>
            <div class="stats-grid">
                <div class="stat-item">
                    <div class="stat-value" id="totalSegments">0</div>
                    <div class="stat-label">总片段</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value" id="keepCount">0</div>
                    <div class="stat-label">保留</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value" id="cutCount">0</div>
                    <div class="stat-label">剪掉</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value" id="keepDuration">0</div>
                    <div class="stat-label">保留时长(秒)</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value" id="cutDuration">0</div>
                    <div class="stat-label">剪掉时长(秒)</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value" id="keepRatio">0%</div>
                    <div class="stat-label">保留比例</div>
                </div>
            </div>
        </div>

        <div class="controls">
            <h2>导出选项</h2>
            <div class="controls-row">
                <button onclick="exportJSON()">导出JSON (浏览器)</button>
                <button onclick="copyToClipboard()">复制到剪贴板</button>
                <button class="secondary" onclick="showExportHelp()">帮助</button>
            </div>
            <p style="color: #888; font-size: 13px; margin-top: 10px;">
                导出其他格式请在命令行使用: python main.py export video.mp4 --format [edl|xml|html]
            </p>
        </div>

        <div class="edit-panel hidden" id="editPanel">
            <h3>编辑选中片段</h3>
            <div class="edit-controls">
                <label>开始时间(秒):</label>
                <input type="number" id="editStart" step="0.1">
                <label>结束时间(秒):</label>
                <input type="number" id="editEnd" step="0.1">
                <button onclick="applyEdit()">应用</button>
                <button class="secondary" onclick="cancelEdit()">取消</button>
            </div>
        </div>
    </div>

    <div class="modal hidden" id="loadingModal">
        <div class="modal-content">
            <h2>正在处理...</h2>
            <div class="spinner"></div>
            <p id="loadingText">请稍候</p>
        </div>
    </div>

    <script>
        // 时间线数据
        const timelineData = {json.dumps(timeline)};
        const videoPath = "{os.path.abspath(video_path).replace(os.sep, '/')}";
        const video = document.getElementById('videoPlayer');
        let selectedSegment = null;
        let isPlaying = false;
        let originalTimeline = JSON.parse(JSON.stringify(timelineData));

        // 初始化
        function init() {{
            renderTimeline();
            renderSegmentList();
            updateStats();
            setupVideoListeners();
            setupPlayhead();
            generateRuler();
        }}

        // 渲染可视化时间线
        function renderTimeline() {{
            const track = document.getElementById('timelineTrack');
            track.innerHTML = '';

            if (!timelineData || timelineData.length === 0) return;

            const totalDuration = timelineData[timelineData.length - 1].end;

            timelineData.forEach((item, index) => {{
                const segment = document.createElement('div');
                segment.className = `timeline-segment ${{{item.action}}}`;
                if (selectedSegment === index) {{
                    segment.classList.add('selected');
                }}

                const width = ((item.end - item.start) / totalDuration) * 100;
                const left = (item.start / totalDuration) * 100;

                segment.style.position = 'absolute';
                segment.style.left = left + '%';
                segment.style.width = width + '%';

                const label = document.createElement('div');
                label.className = 'segment-label';
                const shortText = (item.text || '(无文本)').substring(0, 20);
                label.textContent = shortText + (shortText.length >= 20 ? '...' : '');
                segment.appendChild(label);

                segment.onclick = (e) => {{
                    e.stopPropagation();
                    selectSegment(index);
                }};

                track.appendChild(segment);
            }});
        }}

        // 生成时间刻度
        function generateRuler() {{
            const ruler = document.getElementById('timelineRuler');
            ruler.innerHTML = '';

            if (!timelineData || timelineData.length === 0) return;

            const totalDuration = timelineData[timelineData.length - 1].end;
            const interval = totalDuration > 300 ? 60 : (totalDuration > 60 ? 30 : 10);

            for (let t = 0; t <= totalDuration; t += interval) {{
                const mark = document.createElement('div');
                mark.className = 'ruler-mark';
                mark.style.left = (t / totalDuration * 100) + '%';
                mark.textContent = formatTime(t);
                ruler.appendChild(mark);
            }}
        }}

        // 设置播放头
        function setupPlayhead() {{
            const playhead = document.getElementById('playhead');
            const timelineVisual = document.getElementById('timelineVisual');

            if (!timelineData || timelineData.length === 0) return;

            const totalDuration = timelineData[timelineData.length - 1].end;

            // 拖拽功能
            let isDragging = false;

            playhead.addEventListener('mousedown', (e) => {{
                isDragging = true;
                e.preventDefault();
            }});

            document.addEventListener('mousemove', (e) => {{
                if (!isDragging) return;

                const rect = timelineVisual.getBoundingClientRect();
                const x = e.clientX - rect.left;
                const percentage = Math.max(0, Math.min(1, x / rect.width));
                const newTime = percentage * totalDuration;

                video.currentTime = newTime;
                updatePlayhead();
            }});

            document.addEventListener('mouseup', () => {{
                isDragging = false;
            }});

            // 点击跳转
            timelineVisual.addEventListener('click', (e) => {{
                if (e.target === playhead) return;

                const rect = timelineVisual.getBoundingClientRect();
                const x = e.clientX - rect.left;
                const percentage = Math.max(0, Math.min(1, x / rect.width));
                const newTime = percentage * totalDuration;

                video.currentTime = newTime;
                updatePlayhead();
            }});
        }}

        // 更新播放头位置
        function updatePlayhead() {{
            if (!timelineData || timelineData.length === 0) return;

            const totalDuration = timelineData[timelineData.length - 1].end;
            const playhead = document.getElementById('playhead');
            const percentage = (video.currentTime / totalDuration) * 100;
            playhead.style.left = percentage + '%';
        }}

        // 设置视频监听器
        function setupVideoListeners() {{
            video.addEventListener('timeupdate', updatePlayhead);
            video.addEventListener('play', () => {{ isPlaying = true; }});
            video.addEventListener('pause', () => {{ isPlaying = false; }});
        }}

        // 渲染片段列表
        function renderSegmentList(filter = '') {{
            const container = document.getElementById('segmentListContainer');
            container.innerHTML = '';

            if (!timelineData) return;

            const filteredData = timelineData.map((item, index) => ({{...item, index}}))
                .filter(item => !filter ||
                    (item.text && item.text.toLowerCase().includes(filter.toLowerCase())) ||
                    formatTime(item.start).includes(filter) ||
                    formatTime(item.end).includes(filter));

            filteredData.forEach(item => {{
                const div = document.createElement('div');
                div.className = `segment-item ${{{item.action}}}`;
                if (selectedSegment === item.index) {{
                    div.classList.add('selected');
                }}

                const start = formatTime(item.start);
                const end = formatTime(item.end);
                const duration = (item.end - item.start).toFixed(1);
                const action = item.action === 'keep' ? '保留' : '剪掉';
                const actionClass = item.action === 'keep' ? 'action-keep' : 'action-cut';
                const text = item.text || '(无文本)';

                div.innerHTML = `
                    <div class="segment-time">${{{start}}}} - ${{{end}}}</div>
                    <div class="segment-content">${{{{text}}}}</div>
                    <div class="segment-duration">${{{{duration}}}}s</div>
                    <div class="segment-action ${{{actionClass}}}">${{{{action}}}}</div>
                `;

                div.onclick = () => selectSegment(item.index);
                div.ondblclick = () => {{
                    jumpToSegment(item.index);
                    togglePlay();
                }};

                container.appendChild(div);
            }});
        }}

        // 选择片段
        function selectSegment(index) {{
            selectedSegment = index;
            renderTimeline();
            renderSegmentList(document.getElementById('searchInput').value);

            // 显示编辑面板
            const panel = document.getElementById('editPanel');
            panel.classList.remove('hidden');
            document.getElementById('editStart').value = timelineData[index].start.toFixed(2);
            document.getElementById('editEnd').value = timelineData[index].end.toFixed(2);
        }}

        // 跳转到指定片段
        function jumpToSegment(index) {{
            const segment = timelineData[index];
            video.currentTime = segment.start;
            updatePlayhead();
        }}

        // 切换片段状态
        function toggleSegment(index) {{
            timelineData[index].action = timelineData[index].action === 'keep' ? 'cut' : 'keep';
            renderTimeline();
            renderSegmentList(document.getElementById('searchInput').value);
            updateStats();
        }}

        // 切换全部片段
        function toggleAllSegments() {{
            const allKeep = timelineData.every(item => item.action === 'keep');
            timelineData.forEach(item => {{
                item.action = allKeep ? 'cut' : 'keep';
            }});
            renderTimeline();
            renderSegmentList(document.getElementById('searchInput').value);
            updateStats();
        }}

        // 智能优化
        function optimizeTimeline() {{
            showLoading('正在智能优化时间线...');

            setTimeout(() => {{
                // 简单的优化策略：保留更长的片段
                let i = 0;
                while (i < timelineData.length) {{
                    if (timelineData[i].action === 'cut') {{
                        const currentDuration = timelineData[i].end - timelineData[i].start;
                        // 如果剪掉的片段比保留的更长，则交换
                        if (i + 1 < timelineData.length && timelineData[i + 1].action === 'keep') {{
                            const nextDuration = timelineData[i + 1].end - timelineData[i + 1].start;
                            if (currentDuration > nextDuration) {{
                                timelineData[i].action = 'keep';
                                timelineData[i + 1].action = 'cut';
                            }}
                        }}
                    }}
                    i++;
                }}

                renderTimeline();
                renderSegmentList(document.getElementById('searchInput').value);
                updateStats();
                hideLoading();
            }}, 500);
        }}

        // 重置时间线
        function resetTimeline() {{
            if (confirm('确定要重置所有修改吗？')) {{
                Object.assign(timelineData, originalTimeline);
                selectedSegment = null;
                renderTimeline();
                renderSegmentList(document.getElementById('searchInput').value);
                updateStats();
                document.getElementById('editPanel').classList.add('hidden');
            }}
        }}

        // 过滤片段
        function filterSegments() {{
            const filter = document.getElementById('searchInput').value;
            renderSegmentList(filter);
        }}

        // 应用编辑
        function applyEdit() {{
            if (selectedSegment === null) return;

            const newStart = parseFloat(document.getElementById('editStart').value);
            const newEnd = parseFloat(document.getElementById('editEnd').value);

            if (newStart >= newEnd) {{
                alert('开始时间必须小于结束时间');
                return;
            }}

            timelineData[selectedSegment].start = newStart;
            timelineData[selectedSegment].end = newEnd;

            renderTimeline();
            renderSegmentList(document.getElementById('searchInput').value);
            updateStats();
            document.getElementById('editPanel').classList.add('hidden');
        }}

        // 取消编辑
        function cancelEdit() {{
            document.getElementById('editPanel').classList.add('hidden');
        }}

        // 更新统计信息
        function updateStats() {{
            if (!timelineData) return;

            const totalSegments = timelineData.length;
            const keepSegments = timelineData.filter(item => item.action === 'keep');
            const cutSegments = timelineData.filter(item => item.action === 'cut');

            const keepDuration = keepSegments.reduce((sum, item) => sum + (item.end - item.start), 0);
            const cutDuration = cutSegments.reduce((sum, item) => sum + (item.end - item.start), 0);
            const totalDuration = keepDuration + cutDuration;
            const keepRatio = totalDuration > 0 ? (keepDuration / totalDuration * 100) : 0;

            document.getElementById('totalSegments').textContent = totalSegments;
            document.getElementById('keepCount').textContent = keepSegments.length;
            document.getElementById('cutCount').textContent = cutSegments.length;
            document.getElementById('keepDuration').textContent = keepDuration.toFixed(1);
            document.getElementById('cutDuration').textContent = cutDuration.toFixed(1);
            document.getElementById('keepRatio').textContent = keepRatio.toFixed(1) + '%';
        }}

        // 格式化时间
        function formatTime(seconds) {{
            const mins = Math.floor(seconds / 60);
            const secs = Math.floor(seconds % 60);
            return `${{{{mins.toString().padStart(2, '0')}}}}:${{{{secs.toString().padStart(2, '0')}}}}`;
        }}

        // 播放控制
        function togglePlay() {{
            if (video.paused) {{
                video.play();
            }} else {{
                video.pause();
            }}
        }}

        function skipBackward() {{
            video.currentTime = Math.max(0, video.currentTime - 5);
        }}

        function skipForward() {{
            video.currentTime = Math.min(video.duration, video.currentTime + 5);
        }}

        function skipToNextSegment() {{
            if (selectedSegment === null || selectedSegment >= timelineData.length - 1) {{
                selectedSegment = 0;
            }} else {{
                selectedSegment++;
            }}
            jumpToSegment(selectedSegment);
            renderTimeline();
            renderSegmentList(document.getElementById('searchInput').value);
        }}

        function skipToPrevSegment() {{
            if (selectedSegment === null || selectedSegment <= 0) {{
                selectedSegment = timelineData.length - 1;
            }} else {{
                selectedSegment--;
            }}
            jumpToSegment(selectedSegment);
            renderTimeline();
            renderSegmentList(document.getElementById('searchInput').value);
        }}

        function setPlaybackSpeed(rate) {{
            video.playbackRate = rate;
        }}

        // 导出功能
        function exportJSON() {{
            showLoading('正在生成JSON文件...');

            setTimeout(() => {{
                const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(timelineData, null, 2));
                const downloadAnchorNode = document.createElement('a');
                downloadAnchorNode.setAttribute("href", dataStr);
                downloadAnchorNode.setAttribute("download", "timeline_edited.json");
                document.body.appendChild(downloadAnchorNode);
                downloadAnchorNode.click();
                downloadAnchorNode.remove();
                hideLoading();
            }}, 300);
        }}

        function copyToClipboard() {{
            showLoading('正在复制到剪贴板...');

            setTimeout(() => {{
                navigator.clipboard.writeText(JSON.stringify(timelineData, null, 2)).then(() => {{
                    hideLoading();
                    alert('时间线数据已复制到剪贴板！');
                }}).catch(err => {{
                    hideLoading();
                    alert('复制失败: ' + err);
                }});
            }}, 300);
        }}

        function showExportHelp() {{
            alert(`导出其他格式的命令行用法:\\n\\n` +
                  `EDL格式 (DaVinci Resolve):\\n` +
                  `python main.py export video.mp4 --format edl -o project.edl\\n\\n` +
                  `XML格式 (Final Cut Pro/Premiere):\\n` +
                  `python main.py export video.mp4 --format xml -o project.xml\\n\\n` +
                  `HTML格式 (可拖拽界面):\\n` +
                  `python main.py export video.mp4 --format html -o editor.html`);
        }}

        // 加载提示
        function showLoading(text) {{
            document.getElementById('loadingText').textContent = text;
            document.getElementById('loadingModal').classList.remove('hidden');
        }}

        function hideLoading() {{
            document.getElementById('loadingModal').classList.add('hidden');
        }}

        // 键盘快捷键
        document.addEventListener('keydown', (e) => {{
            if (e.target.tagName === 'INPUT') return;

            switch(e.key) {{
                case ' ':
                    e.preventDefault();
                    togglePlay();
                    break;
                case 'ArrowLeft':
                    skipBackward();
                    break;
                case 'ArrowRight':
                    skipForward();
                    break;
                case 'Escape':
                    cancelEdit();
                    selectedSegment = null;
                    renderTimeline();
                    renderSegmentList(document.getElementById('searchInput').value);
                    break;
            }}
        }});

        // 启动
        init();
    </script>
</body>
</html>
'''

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_template)

    return output_path
