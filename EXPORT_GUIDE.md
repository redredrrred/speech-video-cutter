# 导出功能使用指南

## 📤 导出格式说明

AI视频剪辑工具支持多种导出格式，方便你在专业软件中手动微调。

---

## 1️⃣ 交互式HTML (推荐)

### 功能特点
- 🌐 在浏览器中查看和调整剪辑
- 🎬 视频预览
- 📊 可视化时间线
- 🔄 点击切换保留/删除
- 💾 导出为其他格式

### 使用方法

```bash
python main.py export input.mp4 --format html
```

### 生成的文件
```
input_editor.html  # 交互式HTML文件
```

### 如何使用
1. 双击打开 `input_editor.html`
2. 在浏览器中查看视频和时间线
3. 点击任意片段跳转到该位置
4. 查看哪些部分被标记为保留/删除
5. 可以导出调整后的时间线

### 示例
```bash
# 生成可编辑的HTML
python main.py export "C:/Users/lenovo/Desktop/飞书20260305-143742.qt" --format html

# 输出: 飞书20260305-143742_editor.html
```

---

## 2️⃣ EDL格式 (DaVinci Resolve)

### 功能特点
- 🎯 DaVinci Resolve原生支持
- 📝 记录所有剪辑点
- ✂️ 可在DaVinci中手动调整
- 🎨 支持后续调色、特效

### 使用方法

```bash
python main.py export input.mp4 --format edl -o project.edl
```

### 在DaVinci Resolve中使用

1. **打开DaVinci Resolve**
2. **导入视频**: File → Import Media → 选择原视频
3. **导入EDL**: File → Import Timeline → 选择 `project.edl`
4. **调整剪辑**:
   - 在时间线中查看所有剪辑点
   - 拖动调整剪辑边界
   - 撤销/恢复任意删减
5. **导出**: Deliver → 渲染最终视频

### EDL格式说明
```
001  001  V     C        00:00:00:00 00:00:10:00 00:00:00:00 00:00:10:00
 * FROM CLIP NAME: 文本内容
```
- `001`: 事件编号
- `C`: Cut（剪辑）
- 时间码格式: `HH:MM:SS:FF`

### 示例
```bash
# 生成EDL文件
python main.py export input.mp4 --format edl -o timeline.edl

# 在DaVinci中导入
# File → Import Timeline → timeline.edl
```

---

## 3️⃣ FCPXML格式 (Final Cut Pro / Premiere)

### 功能特点
- 🍎 Final Cut Pro格式
- 🎬 Premiere Pro支持
- 📊 完整的项目信息
- 🔄 跨平台兼容

### 使用方法

```bash
python main.py export input.mp4 --format xml -o project.xml
```

### 在Final Cut Pro中使用

1. 打开Final Cut Pro
2. File → Import → XML
3. 选择 `project.xml`
4. 在时间线中查看和调整

### 在Premiere Pro中使用

1. File → Import → 选择 `project.xml`
2. 选择 "Final Cut Pro XML" 格式
3. 导入后可在时间线编辑

### 示例
```bash
# 生成XML文件
python main.py export input.mp4 --format xml -o project.xml
```

---

## 4️⃣ JSON格式 (开发使用)

### 功能特点
- 💻 机器可读格式
- 🔧 便于二次开发
- 📊 包含完整数据
- 🔄 可转换其他格式

### 使用方法

```bash
python main.py export input.mp4 --format json -o timeline.json
```

### JSON结构
```json
{
  "timeline": [
    {
      "action": "keep",
      "start": 0.0,
      "end": 10.5,
      "text": "文本内容"
    },
    {
      "action": "cut",
      "start": 10.5,
      "end": 15.2,
      "text": "重复内容"
    }
  ],
  "repeats": [...]
}
```

### 用途
- 自定义脚本处理
- 数据分析
- 转换为其他格式

---

## 🎯 使用流程

### 推荐工作流

```
原视频
   ↓
1. AI检测重复
   python main.py export input.mp4 --format html
   ↓
2. 浏览器中查看
   打开 input_editor.html
   ↓
3. 选择导出格式
   - 需要简单查看 → HTML
   - 需要专业调色 → EDL (DaVinci)
   - 需要跨平台 → XML (FCP/Premiere)
   - 需要二次开发 → JSON
   ↓
4. 在专业软件中调整
   - DaVinci Resolve
   - Final Cut Pro
   - Premiere Pro
   ↓
5. 导出最终视频
```

---

## 📝 完整示例

### 场景1: 生成可交互的HTML报告

```bash
python main.py export "C:/Users/lenovo/Desktop/video.mp4" --format html
```

**结果：**
```
C:/Users/lenovo/Desktop/video_editor.html
```

**使用：**
1. 在浏览器中打开
2. 查看所有剪辑点
3. 点击预览视频片段

### 场景2: 导入DaVinci Resolve手动调整

```bash
# 步骤1: 生成EDL文件
python main.py export "C:/Users/lenovo/Desktop/video.mp4" --format edl -o project.edl

# 步骤2: 在DaVinci中
# - 打开DaVinci Resolve
# - File → Import Media → 导入原视频
# - File → Import Timeline → 导入project.edl
# - 手动调整剪辑点
# - 添加转场、调色、音效
# - Deliver → 导出最终视频
```

### 场景3: 导出多种格式

```bash
# 生成所有格式
python main.py export video.mp4 --format html -o video.html
python main.py export video.mp4 --format edl -o video.edl
python main.py export video.mp4 --format xml -o video.xml
python main.py export video.mp4 --format json -o video.json
```

---

## ⚙️ 高级选项

### 调整相似度阈值

```bash
# 更严格（减少误判）
python main.py export video.mp4 --similarity 0.8 --format html

# 更宽松（不漏掉重复）
python main.py export video.mp4 --similarity 0.6 --format html
```

### 使用更大模型（更准确）

```bash
python main.py export video.mp4 --model medium --format html
```

---

## 🎨 专业软件推荐

### DaVinci Resolve (免费)
- **优势：**
  - 完全免费
  - 专业级调色
  - 强大的音频编辑
  - 支持EDL/XML导入
- **下载：** https://www.blackmagicdesign.com/products/davinciresolve

### Final Cut Pro (付费)
- **优势：**
  - Mac平台最佳选择
  - 优秀的性能
  - 原生XML支持
- **适用：** Mac用户

### Premiere Pro (付费)
- **优势：**
  - 行业标准
  - 丰富的插件
  - 与Adobe生态集成
- **适用：** 专业制作

---

## 🔧 常见问题

### Q: EDL文件导入失败？
**A:** 确保视频文件路径正确，EDL文件需要能找到原视频文件。

### Q: XML格式不支持？
**A:** 不同的软件支持不同的XML版本。DaVinci Resolve对FCPXML支持最好。

### Q: HTML中视频无法播放？
**A:** 可能是浏览器安全限制。尝试用Chrome或Edge，或将HTML文件放到视频同目录。

### Q: 如何在专业软件中撤销某处删减？
**A:**
- **DaVinci:** 点击剪辑点 → 拖动调整 → 或按Delete删除
- **FCP:** 点击片段 → 按 Delete 删除
- **Premiere:** 点击剪辑点 → Ripple Edit工具调整

---

## 💡 提示

1. **先导出HTML预览** - 看效果再决定用什么格式
2. **保存原视频** - 专业软件需要访问原视频文件
3. **使用相对路径** - 移动文件时保持相对路径
4. **备份项目** - 保存好EDL/XML和原视频
5. **尝试不同软件** - 找到最适合你的工具

---

**Happy Editing! 🎬**
