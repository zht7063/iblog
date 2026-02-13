"""生成器层集成测试"""

import unittest
from pathlib import Path
import tempfile
import shutil

from iblog.core.metadata_parser import MetadataParser
from iblog.core.file_scanner import FileScanner
from iblog.core.template_renderer import TemplateRenderer
from iblog.generators.post_generator import PostGenerator
from iblog.generators.index_generator import IndexGenerator


class TestPostGenerator(unittest.TestCase):
    """测试博文生成器"""
    
    def setUp(self):
        # 设置组件
        template_dir = Path(__file__).parent.parent / "templates"
        self.renderer = TemplateRenderer(template_dir)
        self.generator = PostGenerator(self.renderer)
        
        # 创建临时输出目录
        self.temp_dir = tempfile.mkdtemp()
        self.output_path = Path(self.temp_dir)
        
        # 准备测试数据
        self.posts = [
            {
                "file_path": Path("test1.md"),
                "metadata": {
                    "title": "测试文章1",
                    "date": "2026-02-13",
                    "tags": ["test"],
                    "category": "测试"
                },
                "content": "# 标题1\n\n这是内容1。"
            },
            {
                "file_path": Path("test2.md"),
                "metadata": {
                    "title": "测试文章2",
                    "date": "2026-02-12",
                    "tags": ["test"],
                    "category": "测试"
                },
                "content": "# 标题2\n\n这是内容2。"
            }
        ]
    
    def tearDown(self):
        # 清理临时目录
        shutil.rmtree(self.temp_dir)
    
    def test_generate_posts(self):
        """测试生成博文"""
        self.generator.generate(self.posts, self.output_path)
        
        # 检查 blogs 目录是否创建
        blogs_dir = self.output_path / "blogs"
        self.assertTrue(blogs_dir.exists())
        
        # 检查 HTML 文件是否生成
        html_files = list(blogs_dir.glob("*.html"))
        self.assertEqual(len(html_files), 2)
        
        # 检查文件内容
        test1_html = (blogs_dir / "test1.html").read_text(encoding="utf-8")
        self.assertIn("标题1", test1_html)
        self.assertIn("内容1", test1_html)


class TestIndexGenerator(unittest.TestCase):
    """测试首页生成器"""
    
    def setUp(self):
        # 设置组件
        template_dir = Path(__file__).parent.parent / "templates"
        self.renderer = TemplateRenderer(template_dir)
        self.generator = IndexGenerator(self.renderer)
        
        # 创建临时输出目录
        self.temp_dir = tempfile.mkdtemp()
        self.output_path = Path(self.temp_dir)
        
        # 准备测试数据
        self.posts = [
            {
                "file_path": Path("test1.md"),
                "metadata": {
                    "title": "测试文章1",
                    "date": "2026-02-13",
                    "description": "描述1"
                },
                "content": "内容1"
            },
            {
                "file_path": Path("test2.md"),
                "metadata": {
                    "title": "测试文章2",
                    "date": "2026-02-12",
                    "description": "描述2"
                },
                "content": "内容2"
            }
        ]
    
    def tearDown(self):
        # 清理临时目录
        shutil.rmtree(self.temp_dir)
    
    def test_generate_index(self):
        """测试生成首页"""
        self.generator.generate(self.posts, self.output_path)
        
        # 检查 index.html 是否生成
        index_path = self.output_path / "index.html"
        self.assertTrue(index_path.exists())
        
        # 检查文件内容
        index_html = index_path.read_text(encoding="utf-8")
        self.assertIn("测试文章1", index_html)
        self.assertIn("测试文章2", index_html)
        self.assertIn("blogs/test1.html", index_html)
        self.assertIn("blogs/test2.html", index_html)


class TestEndToEnd(unittest.TestCase):
    """端到端集成测试"""
    
    def setUp(self):
        # 创建临时输入和输出目录
        self.temp_input_dir = tempfile.mkdtemp()
        self.temp_output_dir = tempfile.mkdtemp()
        self.input_path = Path(self.temp_input_dir)
        self.output_path = Path(self.temp_output_dir)
        
        # 创建测试 Markdown 文件
        self._create_test_markdown_files()
        
        # 初始化组件
        self.parser = MetadataParser()
        self.scanner = FileScanner(self.parser)
        template_dir = Path(__file__).parent.parent / "templates"
        self.renderer = TemplateRenderer(template_dir)
    
    def tearDown(self):
        # 清理临时目录
        shutil.rmtree(self.temp_input_dir)
        shutil.rmtree(self.temp_output_dir)
    
    def _create_test_markdown_files(self):
        """创建测试用的 Markdown 文件"""
        (self.input_path / "post1.md").write_text(
            """---
title: 端到端测试文章1
date: 2026-02-13
category: 技术
tags: [test, python]
---

# 端到端测试

这是端到端测试的内容。
""", encoding="utf-8")
        
        (self.input_path / "post2.md").write_text(
            """---
title: 端到端测试文章2
date: 2026-02-12
category: 生活
---

## 第二篇文章

这是第二篇文章的内容。
""", encoding="utf-8")
    
    def test_full_build_pipeline(self):
        """测试完整构建流程"""
        # 1. 扫描文件
        posts = self.scanner.scan_directory(self.input_path)
        posts = self.scanner.sort_by_date(posts, reverse=True)
        
        self.assertEqual(len(posts), 2)
        
        # 2. 生成博文
        post_gen = PostGenerator(self.renderer)
        post_gen.generate(posts, self.output_path)
        
        # 3. 生成首页
        index_gen = IndexGenerator(self.renderer)
        index_gen.generate(posts, self.output_path)
        
        # 4. 验证输出
        # 检查 blogs 目录
        blogs_dir = self.output_path / "blogs"
        self.assertTrue(blogs_dir.exists())
        
        # 检查博文文件
        post1_html = blogs_dir / "post1.html"
        post2_html = blogs_dir / "post2.html"
        self.assertTrue(post1_html.exists())
        self.assertTrue(post2_html.exists())
        
        # 检查首页
        index_html = self.output_path / "index.html"
        self.assertTrue(index_html.exists())
        
        # 验证内容
        index_content = index_html.read_text(encoding="utf-8")
        self.assertIn("端到端测试文章1", index_content)
        self.assertIn("端到端测试文章2", index_content)


if __name__ == "__main__":
    unittest.main()
