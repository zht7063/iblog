---
title: iblog：轻量级 Python 静态博客生成器
date: 2026-02-13
category: 项目介绍
tags: [Python, 静态博客, Markdown, 开源]
pinned: true
---

## 项目简介

`iblog` 是一个基于 Python 的轻量级静态博客生成工具，专注于将带有 Frontmatter 元数据的 Markdown 文件转换为结构化、美观的 HTML 页面。

## 核心特性

### 强大的 Markdown 支持

- 使用 `markdown-it-py` 进行高性能 Markdown 解析
- 支持标准 Markdown 语法和扩展特性
- 自动提取和解析 YAML Frontmatter 元数据

### 灵活的模板系统

基于 Jinja2 模板引擎，支持：
- 自定义页面布局
- 模块化模板组件
- 主题样式定制

### 多视图生成

自动生成多种类型的页面：
- **首页**：展示所有博客文章列表
- **博文详情页**：每篇文章的独立页面
- **分类索引**：按分类归档文章
- **标签云**：按标签聚合文章
- **关于页面**：独立的个人介绍页面

### 文章置顶功能

支持通过 `pinned: true` 元数据将重要文章置顶到首页，并提供独特的视觉标识。

## 技术架构

### 三层架构设计

项目采用清晰的分层架构，实现职责分离和代码复用：

1. **核心层 (Core Layer)**
   - 元数据解析器：统一的 Frontmatter 解析逻辑
   - 文件扫描器：批量扫描和处理 Markdown 文件
   - 模板渲染器：封装 Jinja2 渲染逻辑

2. **生成器层 (Generator Layer)**
   - 基础生成器：定义统一接口
   - 专用生成器：博文、首页、分类、标签、关于页面等

3. **命令层 (CLI Layer)**
   - 统一构建入口
   - 命令行参数处理

### 技术栈

- **环境管理**：[uv](https://github.com/astral-sh/uv) - 现代化的 Python 包管理工具
- **核心依赖**：
  - `jinja2`：模板渲染引擎
  - `markdown-it-py`：Markdown 解析器
  - `python-frontmatter`：元数据提取
  - `typer`：命令行界面
  - `loguru`：日志管理

## 快速开始

### 安装依赖

```bash
uv sync
```

### 构建博客

```bash
uv run iblog -i assets/markdown_files -o assets/html_files
```

### Markdown 文件格式

```markdown
---
title: 文章标题
date: 2026-02-13
category: 分类名称
tags: [标签1, 标签2]
pinned: false  # 可选，是否置顶
---

这里是文章正文内容，支持完整的 Markdown 语法...
```

## 扩展性

### 添加自定义生成器

只需三步即可添加新的页面类型：

1. 在 `src/iblog/generators/` 创建新生成器
2. 继承 `BaseGenerator` 类
3. 在 `build.py` 中注册

### 自定义模板

所有模板文件位于 `templates/` 目录，可以根据需求自由修改样式和布局。

## 设计理念

- **简单至上**：最小化配置，开箱即用
- **职责分离**：清晰的架构分层，易于维护
- **高效复用**：一次扫描，多次生成，避免重复 I/O
- **易于扩展**：插件化的生成器设计，灵活添加新功能

## 适用场景

- 个人技术博客
- 项目文档站点
- 知识库管理
- 静态网站生成

## 开源协议

本项目采用 MIT 许可证，欢迎自由使用和修改。

---

*Powered by iblog*
