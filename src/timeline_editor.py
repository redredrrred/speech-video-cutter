"""
时间线编辑模块 - 生成和优化剪辑时间线
"""

from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class TimelineEditor:
    """时间线编辑器"""

    def __init__(self, keep_pauses: bool = True, pause_threshold: float = 0.5):
        """
        初始化时间线编辑器

        Args:
            keep_pauses: 是否保留停顿
            pause_threshold: 停顿检测阈值（秒）
        """
        self.keep_pauses = keep_pauses
        self.pause_threshold = pause_threshold

    def generate_edit_timeline(self, segments: List[Dict],
                              repeats: List[Dict],
                              strategy: str = "last") -> List[Dict]:
        """
        根据重复检测结果生成剪辑时间线

        Args:
            segments: 所有语音片段
            repeats: 重复检测结果
            strategy: 保留策略 (last/longest/smoothest)

        Returns:
            剪辑时间线
            [
                {"action": "keep", "start": 4.0, "end": 8.2},
                {"action": "cut", "start": 0.0, "end": 4.0},
                ...
            ]
        """
        if not segments:
            return []

        # 初始化：所有片段都保留
        timeline = []
        for seg in segments:
            timeline.append({
                'action': 'keep',
                'start': seg['start'],
                'end': seg['end'],
                'text': seg['text']
            })

        # 处理重复片段
        for repeat in repeats:
            first = repeat['first']
            second = repeat['second']
            recommended = repeat['recommended']

            # 确定要剪掉的部分
            if recommended == 'second':
                # 保留第二遍，剪掉第一遍
                cut_start = first['start']
                cut_end = first['end']
            else:
                # 保留第一遍，剪掉第二遍
                cut_start = second['start']
                cut_end = second['end']

            # 标记要剪掉的部分
            for item in timeline:
                if item['action'] == 'keep':
                    # 检查是否需要剪掉这个片段（或其中一部分）
                    if item['start'] >= cut_start and item['end'] <= cut_end:
                        # 整个片段都在剪掉范围内
                        item['action'] = 'cut'
                    elif item['start'] < cut_end and item['end'] > cut_start:
                        # 部分重叠，需要分割
                        if item['start'] < cut_start:
                            # 保留前半部分
                            item['end'] = cut_start
                        if item['end'] > cut_end:
                            # 保留后半部分，需要创建新条目
                            new_item = item.copy()
                            new_item['start'] = cut_end
                            timeline.append(new_item)

        # 移除空片段（start >= end）
        timeline = [item for item in timeline if item['start'] < item['end']]

        # 排序并合并相邻片段
        timeline = sorted(timeline, key=lambda x: x['start'])
        timeline = self._merge_adjacent_items(timeline)

        logger.info(f"生成剪辑时间线，共 {len(timeline)} 个操作")
        return timeline

    def _merge_adjacent_items(self, timeline: List[Dict]) -> List[Dict]:
        """合并相邻的相同操作"""
        if not timeline:
            return []

        merged = [timeline[0]]

        for item in timeline[1:]:
            last = merged[-1]

            # 检查是否可以合并
            if (item['action'] == last['action'] and
                item['start'] <= last['end'] + self.pause_threshold):
                # 可以合并
                last['end'] = max(last['end'], item['end'])
            else:
                # 不能合并，添加新条目
                merged.append(item)

        return merged

    def optimize_timeline(self, timeline: List[Dict]) -> List[Dict]:
        """
        优化时间线，确保停顿被保留

        Args:
            timeline: 原始时间线

        Returns:
            优化后的时间线
        """
        if not self.keep_pauses:
            return timeline

        optimized = []

        for i, item in enumerate(timeline):
            if item['action'] == 'cut':
                # 检查下一个保留片段
                next_item = None
                if i + 1 < len(timeline):
                    next_item = timeline[i + 1]

                if next_item and next_item['action'] == 'keep':
                    gap = next_item['start'] - item['end']

                    # 如果有停顿，保留它
                    if gap > self.pause_threshold:
                        # 调整切割点
                        item['end'] = next_item['start']
                        logger.debug(f"保留停顿: {gap:.2f}秒")

            optimized.append(item)

        # 再次合并相邻片段
        optimized = self._merge_adjacent_items(optimized)

        return optimized

    def calculate_timeline_stats(self, timeline: List[Dict]) -> Dict:
        """
        计算时间线统计信息

        Args:
            timeline: 剪辑时间线

        Returns:
            统计信息
            {
                "total_duration": float,
                "keep_duration": float,
                "cut_duration": float,
                "keep_ratio": float,
                "cut_count": int
            }
        """
        total_duration = 0
        keep_duration = 0
        cut_duration = 0
        cut_count = 0

        for item in timeline:
            duration = item['end'] - item['start']
            total_duration = max(total_duration, item['end'])

            if item['action'] == 'keep':
                keep_duration += duration
            elif item['action'] == 'cut':
                cut_duration += duration
                cut_count += 1

        keep_ratio = (keep_duration / total_duration * 100) if total_duration > 0 else 0

        return {
            'total_duration': total_duration,
            'keep_duration': keep_duration,
            'cut_duration': cut_duration,
            'keep_ratio': keep_ratio,
            'cut_count': cut_count
        }

    def format_timeline(self, timeline: List[Dict]) -> str:
        """
        格式化时间线为可读文本

        Args:
            timeline: 剪辑时间线

        Returns:
            格式化的文本
        """
        lines = ["=" * 60, "剪辑时间线", "=" * 60, ""]

        for item in timeline:
            action_symbol = "[+]" if item['action'] == 'keep' else "[-]"
            duration = item['end'] - item['start']
            text_preview = item.get('text', '')[:30]
            if len(text_preview) == 30:
                text_preview += "..."

            lines.append(
                f"{action_symbol} [{item['action'].upper()}] "
                f"{item['start']:.2f}s - {item['end']:.2f}s "
                f"({duration:.2f}s)"
            )

            if text_preview:
                lines.append(f"    {text_preview}")
            lines.append("")

        # 添加统计信息
        stats = self.calculate_timeline_stats(timeline)
        lines.append("-" * 60)
        lines.append("统计信息:")
        lines.append(f"  总时长: {stats['total_duration']:.2f}秒")
        lines.append(f"  保留: {stats['keep_duration']:.2f}秒 ({stats['keep_ratio']:.1f}%)")
        lines.append(f"  剪掉: {stats['cut_duration']:.2f}秒 ({stats['cut_count']}处)")
        lines.append("=" * 60)

        return "\n".join(lines)

    def validate_timeline(self, timeline: List[Dict]) -> bool:
        """
        验证时间线是否有效

        Args:
            timeline: 剪辑时间线

        Returns:
            是否有效
        """
        if not timeline:
            logger.warning("时间线为空")
            return False

        # 检查时间顺序
        for i in range(len(timeline) - 1):
            if timeline[i]['end'] > timeline[i + 1]['start']:
                logger.error(f"时间线错误: 片段 {i} 和 {i+1} 重叠")
                return False

        # 检查操作类型
        valid_actions = {'keep', 'cut'}
        for item in timeline:
            if item['action'] not in valid_actions:
                logger.error(f"无效的操作类型: {item['action']}")
                return False

            if item['start'] >= item['end']:
                logger.error(f"无效的时间范围: {item['start']} >= {item['end']}")
                return False

        return True
