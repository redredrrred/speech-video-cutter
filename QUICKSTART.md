# 快速开始指南

## 安装步骤

### 1. 确保已安装 Python 3.8+

```bash
python --version
```

### 2. 安装依赖

```bash
cd ai-video-cutter
pip install -r requirements.txt
```

### 3. 测试运行

```bash
# 查看帮助
python main.py --help

# 查看视频信息
python main.py info your_video.mp4
```

## 基本使用

### 第一次使用：预览模式

建议先使用预览模式查看效果，不实际剪辑视频：

```bash
python main.py process your_video.mp4 --preview --report report.txt
```

这会：
- 识别语音
- 检测重复内容
- 生成剪辑报告到 `report.txt`
- **不会**修改或创建视频文件

查看报告后，确认无误再进行实际剪辑。

### 正式剪辑

```bash
python main.py process your_video.mp4 -o output.mp4
```

## 常用参数组合

### 1. 基本剪辑（推荐）
```bash
python main.py process input.mp4 -o output.mp4
```

### 2. 更严格的重复检测
```bash
python main.py process input.mp4 -o output.mp4 --similarity 0.8
```

### 3. 选择最流畅版本
```bash
python main.py process input.mp4 -o output.mp4 --strategy smoothest
```

### 4. 生成详细报告
```bash
python main.py process input.mp4 -o output.mp4 --report report.txt
```

### 5. 仅生成字幕
```bash
python main.py subtitle input.mp4 -o subs.srt
```

## 参数说明

### 相似度阈值 (--similarity)

控制重复检测的敏感度：

- **0.6**：较宽松，可能误判但不会漏掉重复
- **0.7**：默认值，平衡准确率和召回率
- **0.8**：较严格，减少误判但可能漏掉轻微重复
- **0.9**：非常严格，只检测高度相似的内容

### 保留策略 (--strategy)

选择保留哪个版本：

- **last**：保留最后一次说的版本（默认，推荐）
- **longest**：保留文本最长的版本
- **smoothest**：保留流畅度最高的版本

### 模型大小 (--model)

选择 Whisper 模型：

- **tiny**：最快，但准确率较低（~74MB）
- **base**：推荐，速度和准确率平衡（~140MB）
- **small**：较准确，但较慢（~460MB）
- **medium**：高准确率，慢（~1.5GB）
- **large**：最高准确率，非常慢（~2.9GB）

## 配置文件

你可以编辑 `config.yaml` 来默认参数，这样每次运行时不需要重复输入：

```yaml
detection:
  similarity_threshold: 0.8  # 设置你常用的阈值

editing:
  keep_pauses: true
  quality: "high"
```

## 故障排除

### 问题：识别不准确

**解决方案：**
- 使用更大的模型：`--model medium`
- 如果是英文视频，在配置文件中设置 `language: "en"`

### 问题：检测不到重复

**解决方案：**
- 降低相似度阈值：`--similarity 0.6`
- 增加最大时间间隔：`--max-gap 15.0`

### 问题：误判太多

**解决方案：**
- 提高相似度阈值：`--similarity 0.85`
- 检查配置文件中的语气词列表

### 问题：处理速度慢

**解决方案：**
- 使用更小的模型：`--model tiny`
- 考虑使用 GPU（需要在配置文件中设置 `device: "cuda"`）

## 工作流程建议

1. **首次使用**：用预览模式查看效果
   ```bash
   python main.py process input.mp4 --preview --report report.txt
   ```

2. **查看报告**：检查 `report.txt`，确认检测是否准确

3. **调整参数**：根据报告调整相似度阈值等参数

4. **正式剪辑**：确认无误后进行实际剪辑
   ```bash
   python main.py process input.mp4 -o output.mp4
   ```

5. **验证结果**：播放输出视频，检查效果

## 下一步

- 阅读 [README.md](README.md) 了解更多功能
- 编辑 [config.yaml](config.yaml) 自定义行为
- 查看生成的报告文件了解详细情况

---

祝使用愉快！🎬
