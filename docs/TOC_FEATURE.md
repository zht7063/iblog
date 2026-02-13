# 博客大纲（TOC）功能说明

## 功能概述

为博客文章页面添加了左侧可点击跳转的大纲（Table of Contents），提升阅读体验。

## 功能特性

### 1. 自动提取目录
- 自动从 Markdown 转换后的 HTML 内容中提取所有标题（h1-h6）
- 生成结构化的目录树，支持多层级嵌套
- 为每个标题自动生成唯一的锚点 ID

### 2. 左侧固定大纲
- 大纲显示在页面左侧，采用固定定位（sticky）
- 跟随页面滚动，始终可见
- 宽度固定为 240px，不影响文章主体阅读

### 3. 交互功能
- **点击跳转**：点击目录项可快速跳转到对应章节
- **平滑滚动**：使用 CSS `scroll-behavior: smooth` 实现平滑过渡
- **高亮显示**：滚动时自动高亮当前可见的章节（通过 JavaScript 实现）
- **视觉反馈**：
  - 鼠标悬停时显示灰色边框
  - 当前章节显示黑色边框和加粗字体

### 4. 层级缩进
- 根据标题级别（h1-h6）自动缩进
- h2: 10px
- h3: 25px
- h4: 40px
- h5: 55px
- h6: 70px

### 5. 响应式设计
- **桌面端**（>1024px）：显示左侧大纲
- **移动端**（≤1024px）：隐藏大纲，文章占满全宽
- 页面容器宽度从 900px 扩展到 1200px，适应新布局

### 6. 样式美化
- 简洁的黑白设计，与博客整体风格一致
- 自定义滚动条样式（仅 webkit 浏览器）
- 大纲标题有下划线分隔

## 技术实现

### 新增文件

#### `src/iblog/core/toc_generator.py`
目录生成器核心模块：

```python
class TocExtractor(HTMLParser):
    """从 HTML 中提取标题"""
    - 解析 HTML 内容
    - 提取所有标题标签（h1-h6）
    - 生成唯一 ID

class TocGenerator:
    """目录生成工具"""
    - extract_toc(): 提取目录结构
    - add_heading_ids(): 为标题添加 ID 属性
```

### 修改文件

#### 1. `src/iblog/generators/post_generator.py`
- 导入 `TocGenerator`
- 在 Markdown 转 HTML 后提取目录
- 为标题添加 ID 属性
- 将目录数据传递给模板渲染器

#### 2. `src/iblog/core/template_renderer.py`
- `render_post()` 方法新增 `toc` 参数
- 将目录数据传递给模板

#### 3. `templates/blog_post.html`
- 使用 flexbox 布局，分为左右两栏
- 左侧：目录侧边栏（`.toc-sidebar`）
- 右侧：文章内容（`.post-content`）
- 添加 JavaScript 实现滚动时高亮当前章节

#### 4. `templates/_base.html`
- 将 `body` 的 `max-width` 从 900px 扩展到 1200px

## 使用方法

### 自动生成
无需任何配置，重新构建博客即可：

```bash
uv run iblog -i assets/markdown_files -o assets/html_files
```

### 效果展示
打开任意博客文章（如 `blogs/markdown_intro.html`），可以看到：
- 左侧显示目录结构
- 点击目录项可跳转到对应章节
- 滚动时当前章节会自动高亮

### 注意事项
1. **标题要求**：文章中需要有标题（h1-h6）才会显示目录
2. **空目录处理**：如果文章没有标题，目录栏不会显示
3. **ID 生成规则**：
   - 标题文本转小写
   - 空格和特殊字符转为连字符 `-`
   - 重复标题自动添加数字后缀（如 `heading-1`, `heading-2`）

## 浏览器兼容性

- ✅ Chrome/Edge (推荐)
- ✅ Firefox
- ✅ Safari
- ⚠️ IE11 及以下不支持 sticky 定位

## 性能考虑

- 目录提取在构建时完成，不影响页面加载速度
- 滚动监听使用 `requestAnimationFrame` 优化性能
- 使用节流（throttling）避免频繁触发高亮更新

## 未来改进方向

1. 添加移动端折叠目录功能
2. 支持目录的展开/收起
3. 添加"返回顶部"按钮
4. 支持目录位置配置（左侧/右侧）
5. 支持目录深度配置（只显示 h2-h3 等）

---

*最后更新：2026-02-13*
