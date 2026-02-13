"""关于页面生成器：将 about.md 转换为独立的关于页面"""

from pathlib import Path
from loguru import logger
import frontmatter

from .base_generator import BaseGenerator


class AboutGenerator(BaseGenerator):
    """生成关于页面的 HTML 文件"""
    
    def generate(self, about_file: Path, output_dir: Path, total_posts: int = 0):
        """生成关于页面的 HTML 文件
        
        Args:
            about_file: about.md 文件路径
            output_dir: 输出根目录
            total_posts: 博客总数
        """
        about_file = Path(about_file)
        output_dir = Path(output_dir)
        # 使用配置的输出路径
        about_dir = output_dir / self.config.paths.output.about
        about_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"开始生成关于页面，输出目录: {about_dir}")
        
        try:
            # 读取并解析 about.md
            with open(about_file, "r", encoding="utf-8") as f:
                post = frontmatter.load(f)
            
            # 提取元数据和内容
            metadata = dict(post.metadata)
            content = post.content
            
            # 确保至少有 title
            if "title" not in metadata:
                metadata["title"] = "关于"
            
            # 将 Markdown 正文转换为 HTML
            content_html = self.md_parser.render(content)
            
            # 使用模板渲染完整页面
            html = self.renderer.render_about(content_html, metadata, total_posts=total_posts)
            
            # 生成输出文件路径（about/index.html）
            output_path = about_dir / "index.html"
            
            # 写入文件
            output_path.write_text(html, encoding="utf-8")
            
            logger.success(f"关于页面生成完成: {output_path}")
            
        except FileNotFoundError:
            logger.error(f"找不到文件: {about_file}")
            raise
        except Exception as e:
            logger.error(f"生成关于页面失败: {e}")
            raise
