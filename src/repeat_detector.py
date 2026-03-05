"""
重复检测模块 - 检测重复的语音片段
"""

import re
import Levenshtein
from difflib import SequenceMatcher
from typing import List, Dict, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class RepeatDetector:
    """重复内容检测器"""

    def __init__(self,
                 similarity_threshold: float = 0.7,
                 max_time_gap: float = 10.0,
                 min_sentence_length: int = 5):
        """
        初始化重复检测器

        Args:
            similarity_threshold: 相似度阈值 (0-1)
            max_time_gap: 最大时间间隔（秒）
            min_sentence_length: 最小句子长度（字符）
        """
        self.similarity_threshold = similarity_threshold
        self.max_time_gap = max_time_gap
        self.min_sentence_length = min_sentence_length

    def calculate_similarity(self, text1: str, text2: str, method: str = "hybrid") -> float:
        """
        计算两段文本的相似度

        Args:
            text1: 文本1
            text2: 文本2
            method: 计算方法 (levenshtein/sequence/hybrid)

        Returns:
            相似度 (0-1)
        """
        # 清理文本
        text1 = self._clean_text(text1)
        text2 = self._clean_text(text2)

        if not text1 or not text2:
            return 0.0

        if method == "levenshtein":
            return self._levenshtein_similarity(text1, text2)
        elif method == "sequence":
            return self._sequence_similarity(text1, text2)
        elif method == "hybrid":
            return self._hybrid_similarity(text1, text2)
        else:
            raise ValueError(f"未知的相似度计算方法: {method}")

    def _clean_text(self, text: str) -> str:
        """清理文本，去除标点和多余空格"""
        # 去除标点符号
        text = re.sub(r'[^\w\s\u4e00-\u9fff]', '', text)
        # 去除多余空格
        text = ' '.join(text.split())
        return text

    def _levenshtein_similarity(self, text1: str, text2: str) -> float:
        """使用 Levenshtein 距离计算相似度"""
        try:
            ratio = Levenshtein.ratio(text1, text2)
            return ratio
        except:
            # 如果 Levenshtein 库不可用，使用 SequenceMatcher
            return self._sequence_similarity(text1, text2)

    def _sequence_similarity(self, text1: str, text2: str) -> float:
        """使用 SequenceMatcher 计算相似度"""
        return SequenceMatcher(None, text1, text2).ratio()

    def _hybrid_similarity(self, text1: str, text2: str) -> float:
        """
        混合相似度计算策略
        结合编辑距离和开头匹配（口误通常会重头开始说）
        """
        # 基础编辑距离相似度
        base_sim = self._levenshtein_similarity(text1, text2)

        # 检查开头是否相似（前10个字符）
        min_len = min(len(text1), len(text2), 10)
        if min_len > 0:
            start_match = text1[:min_len] == text2[:min_len]
            if start_match:
                # 如果开头相同，提高相似度权重
                base_sim = min(1.0, base_sim * 1.15)

        # 检查是否一个文本包含另一个（常见于补充完整的情况）
        if text1 in text2 or text2 in text1:
            base_sim = max(base_sim, 0.8)

        return base_sim

    def detect_repeats(self, segments: List[Dict]) -> List[Dict]:
        """
        检测重复的语音片段

        Args:
            segments: 语音片段列表
                [{"start": 0.0, "end": 3.5, "text": "..."}, ...]

        Returns:
            重复检测结果列表
            [
                {
                    "first": {"start": 0.0, "end": 3.5, "text": "..."},
                    "second": {"start": 4.0, "end": 8.2, "text": "..."},
                    "similarity": 0.85,
                    "time_gap": 0.5,
                    "recommended": "second"
                },
                ...
            ]
        """
        repeats = []
        n = len(segments)

        logger.info(f"开始检测重复，共 {n} 个片段")

        # 过滤掉太短的片段
        valid_segments = [
            seg for seg in segments
            if len(seg['text']) >= self.min_sentence_length
        ]

        if len(valid_segments) < n:
            logger.info(f"过滤掉 {n - len(valid_segments)} 个过短片段")

        # 两两比较检测重复
        for i in range(len(valid_segments)):
            seg1 = valid_segments[i]

            for j in range(i + 1, len(valid_segments)):
                seg2 = valid_segments[j]

                # 检查时间间隔
                time_gap = seg2['start'] - seg1['end']

                if time_gap > self.max_time_gap:
                    # 超过最大时间间隔，不再检查后续片段
                    break

                if time_gap < 0:
                    # 时间重叠，跳过
                    continue

                # 计算相似度
                similarity = self.calculate_similarity(seg1['text'], seg2['text'])

                if similarity >= self.similarity_threshold:
                    # 判断推荐保留哪个版本
                    recommended = self._select_version(seg1, seg2)

                    repeat_info = {
                        'first': seg1,
                        'second': seg2,
                        'similarity': similarity,
                        'time_gap': time_gap,
                        'recommended': recommended
                    }
                    repeats.append(repeat_info)

                    logger.debug(
                        f"发现重复: [{i}] '{seg1['text'][:20]}...' "
                        f"-> [{j}] '{seg2['text'][:20]}...' "
                        f"(相似度: {similarity:.2f})"
                    )

        logger.info(f"检测完成，发现 {len(repeats)} 处重复")
        return repeats

    def _select_version(self, seg1: Dict, seg2: Dict) -> str:
        """
        选择保留哪个版本

        默认策略：保留第二次（通常是修正后的版本）
        可扩展：根据流畅度、长度等选择

        Args:
            seg1: 第一个片段
            seg2: 第二个片段

        Returns:
            "first" 或 "second"
        """
        # 默认保留第二个（后面的版本）
        # 可以根据其他因素调整：
        # - seg2 通常更长、更完整
        # - seg2 可能是修正后的版本

        len1 = len(seg1['text'])
        len2 = len(seg2['text'])

        # 如果第二个版本明显更长，优先选择
        if len2 > len1 * 1.2:
            return "second"
        # 如果第一个版本更长，选择第一个
        elif len1 > len2 * 1.2:
            return "first"
        else:
            # 长度相近，默认选择第二个（后面的版本）
            return "second"

    def filter_overlapping_repeats(self, repeats: List[Dict]) -> List[Dict]:
        """
        过滤掉重叠的重复检测结果

        例如：如果 A-B 和 B-C 都被检测为重复，只保留 A-B

        Args:
            repeats: 重复检测结果列表

        Returns:
            过滤后的重复列表
        """
        if not repeats:
            return []

        # 按开始时间排序
        sorted_repeats = sorted(repeats, key=lambda x: x['first']['start'])

        filtered = []
        last_end = -1

        for repeat in sorted_repeats:
            first_end = repeat['first']['end']
            second_start = repeat['second']['start']

            # 检查是否与上一个重复重叠
            if second_start > last_end:
                filtered.append(repeat)
                last_end = repeat['second']['end']
            else:
                logger.debug("跳过重叠的重复检测结果")

        return filtered

    def generate_report(self, repeats: List[Dict]) -> str:
        """
        生成重复检测报告

        Args:
            repeats: 重复检测结果列表

        Returns:
            报告文本
        """
        if not repeats:
            return "未检测到重复内容。"

        lines = [
            "=" * 60,
            "重复检测报告",
            "=" * 60,
            f"共发现 {len(repeats)} 处重复内容：\n"
        ]

        for i, repeat in enumerate(repeats, 1):
            lines.append(f"[{i}] 重复 #{i}")
            lines.append(f"    第一遍: {repeat['first']['text']}")
            lines.append(f"            时间: {repeat['first']['start']:.2f}s - {repeat['first']['end']:.2f}s")
            lines.append(f"    第二遍: {repeat['second']['text']}")
            lines.append(f"            时间: {repeat['second']['start']:.2f}s - {repeat['second']['end']:.2f}s")
            lines.append(f"    相似度: {repeat['similarity']:.2%}")
            lines.append(f"    建议保留: {'第一遍' if repeat['recommended'] == 'first' else '第二遍'}")
            lines.append("")

        lines.append("=" * 60)

        return "\n".join(lines)


# 便捷函数
def detect_repeats(segments: List[Dict],
                  similarity_threshold: float = 0.7,
                  max_time_gap: float = 10.0) -> List[Dict]:
    """
    便捷函数：检测重复片段

    Args:
        segments: 语音片段列表
        similarity_threshold: 相似度阈值
        max_time_gap: 最大时间间隔

    Returns:
        重复检测结果列表
    """
    detector = RepeatDetector(
        similarity_threshold=similarity_threshold,
        max_time_gap=max_time_gap
    )
    return detector.detect_repeats(segments)
