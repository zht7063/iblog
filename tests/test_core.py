"""核心层单元测试"""

import unittest
from pathlib import Path
import tempfile
import shutil

from iblog.core.metadata_parser import MetadataParser
from iblog.core.file_scanner import FileScanner
from iblog.core.template_renderer import TemplateRenderer


class TestMetadataParser(unittest.TestCase):
    """测试元数据解析器"""
    
    def setUp(self):
        self.parser = MetadataParser()
    
    def test_parse_valid_frontmatter(self):
        """测试解析有效的 Frontmatter"""
        md_content = """---
title: 测试文章
date: 2026-02-13
tags: [test, python]
category: 测试
---

# 正文标题

这是正文内容。
"""
        metadata, content = self.parser.parse(md_content)
        
        self.assertEqual(metadata["title"], "测试文章")
        self.assertEqual(metadata["date"], "2026-02-13")
        self.assertEqual(metadata["tags"], ["test", "python"])
        self.assertEqual(metadata["category"], "测试")
        self.assertIn("正文标题", content)
    
    def test_parse_without_frontmatter(self):
        """测试解析没有 Frontmatter 的内容"""
        md_content = "# 只有正文\n\n这是正文。"
        metadata, content = self.parser.parse(md_content)
        
        # 应该返回空元数据和原始内容
        self.assertIsInstance(metadata, dict)
        self.assertIn("正文", content)
    
    def test_validate_metadata_defaults(self):
        """测试元数据验证和默认值"""
        metadata = {}
        validated = self.parser.validate_metadata(metadata)
        
        # 检查默认值
        self.assertEqual(validated["title"], "无标题")
        self.assertEqual(validated["category"], "未分类")
        self.assertEqual(validated["tags"], [])
        self.assertEqual(validated["date"], "")
    
    def test_validate_metadata_tags_normalization(self):
        """测试标签规范化"""
        # 字符串标签应转为列表
        metadata = {"tags": "python, test"}
        validated = self.parser.validate_metadata(metadata)
        self.assertIsInstance(validated["tags"], list)
        
        # 非列表标签应转为列表
        metadata = {"tags": 123}
        validated = self.parser.validate_metadata(metadata)
        self.assertIsInstance(validated["tags"], list)


class TestFileScanner(unittest.TestCase):
    """测试文件扫描器"""
    
    def setUp(self):
        self.parser = MetadataParser()
        self.scanner = FileScanner(self.parser)
        
        # 创建临时测试目录
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)
        
        # 创建测试文件
        self._create_test_files()
    
    def tearDown(self):
        # 清理临时目录
        shutil.rmtree(self.temp_dir)
    
    def _create_test_files(self):
        """创建测试用的 Markdown 文件"""
        # 文件1
        (self.temp_path / "post1.md").write_text(
            """---
title: 文章1
date: 2026-02-13
category: 技术
tags: [python]
---

内容1
""", encoding="utf-8")
        
        # 文件2
        (self.temp_path / "post2.md").write_text(
            """---
title: 文章2
date: 2026-02-12
category: 生活
tags: [life]
---

内容2
""", encoding="utf-8")
        
        # 文件3（无日期）
        (self.temp_path / "post3.md").write_text(
            """---
title: 文章3
category: 技术
---

内容3
""", encoding="utf-8")
    
    def test_scan_directory(self):
        """测试扫描目录"""
        posts = self.scanner.scan_directory(self.temp_path)
        
        self.assertEqual(len(posts), 3)
        self.assertTrue(all("file_path" in p for p in posts))
        self.assertTrue(all("metadata" in p for p in posts))
        self.assertTrue(all("content" in p for p in posts))
    
    def test_sort_by_date(self):
        """测试按日期排序"""
        posts = self.scanner.scan_directory(self.temp_path)
        sorted_posts = self.scanner.sort_by_date(posts, reverse=True)
        
        # 应该按日期降序排列（最新的在前）
        self.assertEqual(sorted_posts[0]["metadata"]["title"], "文章1")
        self.assertEqual(sorted_posts[1]["metadata"]["title"], "文章2")
    
    def test_group_by_category(self):
        """测试按分类分组"""
        posts = self.scanner.scan_directory(self.temp_path)
        grouped = self.scanner.group_by_category(posts)
        
        self.assertIn("技术", grouped)
        self.assertIn("生活", grouped)
        self.assertEqual(len(grouped["技术"]), 2)
        self.assertEqual(len(grouped["生活"]), 1)
    
    def test_group_by_tags(self):
        """测试按标签分组"""
        posts = self.scanner.scan_directory(self.temp_path)
        grouped = self.scanner.group_by_tags(posts)
        
        self.assertIn("python", grouped)
        self.assertIn("life", grouped)


class TestTemplateRenderer(unittest.TestCase):
    """测试模板渲染器"""
    
    def setUp(self):
        # 使用项目的模板目录
        template_dir = Path(__file__).parent.parent / "templates"
        self.renderer = TemplateRenderer(template_dir)
    
    def test_render_post(self):
        """测试渲染博文"""
        content_html = "<h1>测试标题</h1><p>测试内容</p>"
        metadata = {
            "title": "测试文章",
            "date": "2026-02-13",
            "tags": ["test"],
            "category": "测试"
        }
        
        html = self.renderer.render_post(content_html, metadata)
        
        self.assertIn("测试标题", html)
        self.assertIn("测试内容", html)
        self.assertIn("测试文章", html)
    
    def test_render_index(self):
        """测试渲染首页"""
        posts = [
            {
                "metadata": {
                    "title": "文章1",
                    "date": "2026-02-13",
                    "url": "blogs/post1.html"
                }
            },
            {
                "metadata": {
                    "title": "文章2",
                    "date": "2026-02-12",
                    "url": "blogs/post2.html"
                }
            }
        ]
        
        html = self.renderer.render_index(posts)
        
        self.assertIn("文章1", html)
        self.assertIn("文章2", html)
        self.assertIn("blogs/post1.html", html)


if __name__ == "__main__":
    unittest.main()
