# AI智能口误去除工具

> 自动检测并去除视频中的重复/口误内容，保留流畅版本

## ✨ 功能特点

- 🔍 **智能识别重复**：基于AI语音识别（Whisper），自动发现重复说的句子
- ✂️ **精准剪辑**：剪掉口误部分，保留最后一次完整流畅版本
- ⏸️ **保留停顿**：智能保护自然停顿，不做过度剪辑
- 🎯 **多种策略**：支持多种保留策略（最后版本/最长版本/最流畅版本）
- 📝 **字幕生成**：可单独生成SRT/VTT字幕文件
- 📊 **详细报告**：生成剪辑报告，让你清楚了解哪些内容被剪掉

## 📖 使用场景

当你录制口播视频时，如果有口误，会把整句话重新说一遍：

```
原始视频：
"今天我们要讲的是Python基础（停顿）今天我们要讲的是Python基础入门教程..."

处理后：
"今天我们要讲的是Python基础入门教程..."
（自动剪掉前面口误的句子，保留后面的完整版本和停顿）
```

## 🚀 快速开始

### 安装依赖

```bash
# 克隆项目（或直接下载）
cd ai-video-cutter

# 安装依赖
pip install -r requirements.txt
```

### 基本使用

```bash
# 处理视频，去除口误
python main.py process input.mp4 -o output.mp4

# 查看视频信息
python main.py info input.mp4

# 仅生成字幕文件
python main.py subtitle input.mp4 -o subs.srt
```

## 📚 命令详解

### process - 处理视频

```bash
python main.py process [OPTIONS] INPUT_VIDEO

# 选项:
#   -o, --output PATH          输出视频路径
#   --similarity FLOAT         相似度阈值 (0-1)，默认0.7
#   --max-gap FLOAT            最大时间间隔（秒），默认10秒
#   --strategy [last|longest|smoothest]  保留策略，默认last
#   --keep-pauses / --no-keep-pauses     是否保留停顿，默认保留
#   --model [tiny|base|small|medium|large]  Whisper模型大小，默认base
#   --config PATH              配置文件路径
#   --preview                  预览模式，不实际剪辑
#   --report PATH              生成剪辑报告
```

**示例：**

```bash
# 基本用法
python main.py process input.mp4 -o output.mp4

# 提高相似度阈值（更严格）
python main.py process input.mp4 --similarity 0.8 -o output.mp4

# 选择最流畅版本
python main.py process input.mp4 --strategy smoothest -o output.mp4

# 预览模式（不实际剪辑，仅生成报告）
python main.py process input.mp4 --preview --report report.txt

# 使用更大的模型（更准确但更慢）
python main.py process input.mp4 --model medium -o output.mp4
```

### subtitle - 生成字幕

```bash
python main.py subtitle [OPTIONS] INPUT_VIDEO

# 选项:
#   -o, --output PATH          输出字幕路径
#   --format [srt|vtt]         字幕格式，默认srt
#   --model [tiny|base|small|medium|large]  模型大小
```

**示例：**

```bash
# 生成SRT字幕
python main.py subtitle input.mp4 -o subs.srt

# 生成VTT字幕
python main.py subtitle input.mp4 --format vtt -o subs.vtt
```

### info - 查看视频信息

```bash
python main.py info INPUT_VIDEO
```

## ⚙️ 配置文件

编辑 `config.yaml` 自定义行为：

```yaml
# 语音识别配置
speech:
  model: "base"              # 模型大小
  language: "zh"             # 语言代码
  device: "cpu"              # 运行设备

# 重复检测配置
detection:
  similarity_threshold: 0.7  # 相似度阈值
  max_time_gap: 10.0         # 最大时间间隔
  min_sentence_length: 5     # 最小句子长度

# 流畅度分析配置
analysis:
  pause_threshold: 0.5       # 停顿检测阈值
  filler_words:              # 语气词列表
    - "呃"
    - "啊"
    - "那个"
  preserve_strategy: "last"  # 保留策略

# 剪辑配置
editing:
  keep_pauses: true          # 保留停顿
  output_format: "mp4"       # 输出格式
  quality: "high"            # 视频质量
```

## 🎯 工作原理

1. **语音识别**：使用 Whisper 模型识别视频中的语音，生成带时间戳的字幕
2. **重复检测**：计算相邻字幕的文本相似度，找出重复内容
3. **策略选择**：根据配置的策略选择保留哪个版本
4. **时间线生成**：生成剪辑时间线，标记要保留和剪掉的片段
5. **视频剪辑**：使用 MoviePy 执行剪辑，拼接保留的片段

## 📊 输出示例

```
============================================================
AI智能口误去除工具
============================================================
输入: input.mp4
输出: output.mp4
相似度阈值: 0.7
保留策略: last
保留停顿: True
============================================================

📝 步骤 1/5: 语音识别...
   ✓ 识别完成，共 45 个片段

🔍 步骤 2/5: 检测重复内容...
   ✓ 检测到 3 处重复

⚙️  步骤 3/5: 生成剪辑时间线...
   ✓ 保留时长: 120.5秒 (85.2%)
   ✓ 剪掉时长: 21.0秒 (3处)

📊 步骤 4/5: 生成报告...
   ✓ 报告已保存: report.txt

🎬 步骤 5/5: 执行视频剪辑...
   ✓ 剪辑完成！
   ✓ 输出文件: output.mp4
```

## 🔧 高级用法

### 自定义相似度算法

修改 `config.yaml` 中的 `similarity_threshold`：

- **0.6-0.7**：较宽松，可能误判但不会漏掉重复
- **0.7-0.8**：中等，推荐设置（默认）
- **0.8-0.9**：较严格，减少误判但可能漏掉轻微重复

### 选择保留策略

- **last**：保留最后一次说的版本（默认，推荐）
- **longest**：保留文本最长的版本
- **smoothest**：保留流畅度最高的版本（无结巴、少语气词）

### 模型选择

| 模型 | 大小 | 速度 | 准确率 | 推荐场景 |
|------|------|------|--------|----------|
| tiny | ~74MB | 最快 | 较低 | 快速预览 |
| base | ~140MB | 快 | 中等 | 日常使用（推荐） |
| small | ~460MB | 中等 | 较高 | 重要视频 |
| medium | ~1.5GB | 慢 | 高 | 专业制作 |
| large | ~2.9GB | 最慢 | 最高 | 追求极致质量 |

## ❓ 常见问题

**Q: 检测不到重复怎么办？**
A: 尝试降低 `similarity_threshold` 到 0.6 或 0.65

**Q: 误判太多怎么办？**
A: 提高 `similarity_threshold` 到 0.8 或 0.85

**Q: 如何保留更多停顿？**
A: 在配置文件中增加 `pause_threshold` 值

**Q: 支持哪些视频格式？**
A: 支持 FFmpeg/MoviePy 支持的所有格式（MP4, AVI, MOV等）

**Q: 处理速度慢怎么办？**
A: 使用更小的模型（tiny/base），或安装 GPU 加速

## 🛠️ 开发

```bash
# 运行测试
pytest tests/

# 代码格式化
black src/
isort src/

# 类型检查
mypy src/
```

## 📄 许可证

MIT License

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📧 联系方式

如有问题或建议，请提交 Issue。

---

**祝你的视频制作更加高效！** 🎬
