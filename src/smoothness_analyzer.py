"""
流畅度分析模块 - 分析语音片段的流畅度
"""

import re
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class SmoothnessAnalyzer:
    """流畅度分析器"""

    def __init__(self,
                 filler_words: Optional[List[str]] = None,
                 stutter_pattern: str = "(.)\\1+",
                 min_speaking_rate: float = 2.0,
                 max_speaking_rate: float = 8.0):
        """
        初始化流畅度分析器

        Args:
            filler_words: 语气词列表
            stutter_pattern: 结巴检测正则表达式
            min_speaking_rate: 最小语速（字/秒）
            max_speaking_rate: 最大语速（字/秒）
        """
        self.filler_words = filler_words or [
            "呃", "啊", "那个", "然后", "就是", "嗯", "这个", "那个呢"
        ]
        self.stutter_pattern = stutter_pattern
        self.min_speaking_rate = min_speaking_rate
        self.max_speaking_rate = max_speaking_rate

    def analyze_smoothness(self, segment: Dict) -> Dict:
        """
        分析单个语音片段的流畅度

        Args:
            segment: 语音片段
                {"start": 0.0, "end": 3.5, "text": "..."}

        Returns:
            流畅度分析结果
            {
                "has_stutter": bool,
                "pause_count": int,
                "filler_word_count": int,
                "filler_words": List[str],
                "speaking_rate": float,
                "score": float
            }
        """
        text = segment['text']
        duration = segment['end'] - segment['start']

        # 检测结巴
        has_stutter = self._detect_stutter(text)

        # 统计语气词
        filler_info = self._count_filler_words(text)

        # 计算语速
        speaking_rate = len(text) / duration if duration > 0 else 0

        # 计算流畅度分数
        score = self._calculate_score(
            has_stutter=has_stutter,
            filler_count=filler_info['count'],
            speaking_rate=speaking_rate,
            duration=duration
        )

        result = {
            'has_stutter': has_stutter,
            'filler_word_count': filler_info['count'],
            'filler_words': filler_info['words'],
            'speaking_rate': speaking_rate,
            'duration': duration,
            'word_count': len(text),
            'score': score
        }

        return result

    def _detect_stutter(self, text: str) -> bool:
        """
        检测结巴（重复字符）

        Args:
            text: 文本

        Returns:
            是否有结巴
        """
        # 检测连续重复的字符（如"我我我"）
        pattern = re.compile(self.stutter_pattern)
        return bool(pattern.search(text))

    def _count_filler_words(self, text: str) -> Dict:
        """
        统计语气词

        Args:
            text: 文本

        Returns:
            {"count": int, "words": List[str]}
        """
        found_words = []

        for filler in self.filler_words:
            if filler in text:
                # 统计出现次数
                count = text.count(filler)
                found_words.extend([filler] * count)

        return {
            'count': len(found_words),
            'words': found_words
        }

    def _calculate_score(self, has_stutter: bool, filler_count: int,
                        speaking_rate: float, duration: float) -> float:
        """
        计算流畅度分数 (0-1)

        Args:
            has_stutter: 是否有结巴
            filler_count: 语气词数量
            speaking_rate: 语速
            duration: 时长

        Returns:
            流畅度分数
        """
        score = 1.0

        # 结巴扣分
        if has_stutter:
            score -= 0.3

        # 语气词扣分
        score -= min(filler_count * 0.1, 0.5)

        # 语速异常扣分
        if speaking_rate < self.min_speaking_rate or speaking_rate > self.max_speaking_rate:
            score -= 0.1

        # 太短的片段可能不完整
        if duration < 1.0:
            score -= 0.1

        return max(0.0, score)

    def select_best_version(self, repeat_group: List[Dict],
                          strategy: str = "last") -> Dict:
        """
        从重复片段中选择最好的版本

        Args:
            repeat_group: 重复片段组
                [seg1, seg2, ...]
            strategy: 选择策略
                - "last": 选择最后一个
                - "longest": 选择最长的
                - "smoothest": 选择最流畅的

        Returns:
            选中的片段
        """
        if not repeat_group:
            raise ValueError("重复片段组为空")

        if strategy == "last":
            return repeat_group[-1]

        elif strategy == "longest":
            # 选择文本最长的
            return max(repeat_group, key=lambda x: len(x['text']))

        elif strategy == "smoothest":
            # 分析每个片段的流畅度，选择分数最高的
            scores = []
            for segment in repeat_group:
                analysis = self.analyze_smoothness(segment)
                scores.append((segment, analysis['score']))

            return max(scores, key=lambda x: x[1][0])

        else:
            raise ValueError(f"未知的选择策略: {strategy}")

    def compare_segments(self, seg1: Dict, seg2: Dict) -> Dict:
        """
        比较两个片段的流畅度

        Args:
            seg1: 片段1
            seg2: 片段2

        Returns:
            比较结果
            {
                "better": "first" / "second",
                "reason": str,
                "score1": float,
                "score2": float
            }
        """
        analysis1 = self.analyze_smoothness(seg1)
        analysis2 = self.analyze_smoothness(seg2)

        if analysis1['score'] > analysis2['score']:
            better = "first"
            reason = self._get_better_reason(analysis1, analysis2)
        else:
            better = "second"
            reason = self._get_better_reason(analysis2, analysis1)

        return {
            'better': better,
            'reason': reason,
            'score1': analysis1['score'],
            'score2': analysis2['score'],
            'analysis1': analysis1,
            'analysis2': analysis2
        }

    def _get_better_reason(self, better_analysis: Dict, worse_analysis: Dict) -> str:
        """获取更好的原因"""
        reasons = []

        # 结巴
        if worse_analysis['has_stutter'] and not better_analysis['has_stutter']:
            reasons.append("无结巴")

        # 语气词
        if better_analysis['filler_word_count'] < worse_analysis['filler_word_count']:
            reasons.append(f"语气词更少 ({better_analysis['filler_word_count']} vs {worse_analysis['filler_word_count']})")

        # 语速
        better_rate = better_analysis['speaking_rate']
        worse_rate = worse_analysis['speaking_rate']
        if self.min_speaking_rate <= better_rate <= self.max_speaking_rate:
            if not (self.min_speaking_rate <= worse_rate <= self.max_speaking_rate):
                reasons.append(f"语速更自然 ({better_rate:.1f} 字/秒)")

        return "; ".join(reasons) if reasons else "综合评分更高"
