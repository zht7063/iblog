"""首页生成器：生成博客文章列表首页"""

from pathlib import Path
from loguru import logger

from .base_generator import BaseGenerator


class IndexGenerator(BaseGenerator):
    """生成博客首页 index.html"""
    
    def generate(self, posts: list[dict], output_dir: Path):
        """生成首页 index.html
        
        Args:
            posts: 文章列表（应已按日期排序）
            output_dir: 输出根目录
        """
        output_dir = Path(output_dir)
        
        logger.info("开始生成首页")
        
        # 为每篇文章添加相对 URL（指向 blogs/ 子目录）
        posts_with_url = []
        for post in posts:
            metadata = post["metadata"].copy()
            metadata["url"] = f"blogs/{post['file_path'].stem}.html"
            posts_with_url.append({"metadata": metadata})
        
        # 渲染首页
        html = self.renderer.render_index(posts_with_url, total_posts=len(posts))
        
        # 写入文件
        index_path = output_dir / "index.html"
        index_path.write_text(html, encoding="utf-8")
        
        logger.success(f"首页已生成: {index_path}")
