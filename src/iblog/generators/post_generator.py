"""博文生成器：将 Markdown 文件转换为 HTML 博文页面"""

from pathlib import Path
from loguru import logger

from .base_generator import BaseGenerator
from iblog.core.toc_generator import TocGenerator


class PostGenerator(BaseGenerator):
    """生成所有博文的 HTML 文件"""
    
    def generate(self, posts: list[dict], output_dir: Path):
        """生成所有博文的 HTML 文件
        
        Args:
            posts: 文章列表（包含 file_path, metadata, content）
            output_dir: 输出根目录
        """
        output_dir = Path(output_dir)
        # 使用配置的输出路径
        blogs_dir = output_dir / self.config.paths.output.posts
        blogs_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"开始生成博文，输出目录: {blogs_dir}")
        
        converted_count = 0
        for post in posts:
            try:
                # 将 Markdown 正文转换为 HTML
                content_html = self.md_parser.render(post["content"])
                
                # 提取目录（TOC）
                toc = TocGenerator.extract_toc(content_html)
                
                # 为标题添加ID以支持锚点跳转
                content_html = TocGenerator.add_heading_ids(content_html)
                
                # 使用模板渲染完整页面
                html = self.renderer.render_post(
                    content_html, 
                    post["metadata"], 
                    total_posts=len(posts),
                    toc=toc
                )
                
                # 生成输出文件路径
                output_path = blogs_dir / post["file_path"].with_suffix(".html").name
                
                # 写入文件
                output_path.write_text(html, encoding="utf-8")
                
                converted_count += 1
                logger.debug(f"已生成: {output_path.name}")
            except Exception as e:
                logger.error(f"生成博文 {post['file_path'].name} 失败: {e}")
                continue
        
        logger.success(f"博文生成完成，共 {converted_count}/{len(posts)} 篇")
