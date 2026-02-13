"""标签生成器：生成按标签组织的文章视图"""

from pathlib import Path
from loguru import logger

from .base_generator import BaseGenerator


class TagGenerator(BaseGenerator):
    """生成标签视图页面"""
    
    def generate(self, posts: list[dict], output_dir: Path):
        """生成标签视图页面
        
        实现流程：
        1. 按标签分组文章（处理多对多关系）
        2. 计算每个标签的统计信息和字体大小
        3. 生成标签云索引页 tags/index.html
        4. 为每个标签生成详情页 tags/{标签名}.html
        
        Args:
            posts: 文章列表
            output_dir: 输出根目录
        """
        output_dir = Path(output_dir)
        tags_dir = output_dir / "tags"
        tags_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info("开始生成标签视图")
        
        if len(posts) == 0:
            logger.warning("没有文章，跳过标签页面生成")
            return
        
        # 1. 按标签分组文章
        tags_dict = self._group_by_tags(posts)
        logger.info(f"找到 {len(tags_dict)} 个标签")
        
        if len(tags_dict) == 0:
            logger.warning("没有找到任何标签")
            return
        
        # 2. 计算每个标签的统计信息
        tag_stats = self._calculate_tag_stats(tags_dict)
        
        # 3. 生成标签云索引页
        self._render_tags_index(tag_stats, tags_dir, total_posts=len(posts))
        
        # 4. 为每个标签生成详情页
        for name, tag_posts in tags_dict.items():
            self._render_tag_detail(name, tag_posts, tags_dir, total_posts=len(posts))
        
        logger.success(f"标签视图生成完成，共 {len(tags_dict)} 个标签")
    
    def _group_by_tags(self, posts: list[dict]) -> dict[str, list]:
        """按标签分组文章（一篇文章可属于多个标签）
        
        Args:
            posts: 文章列表
            
        Returns:
            dict[str, list]: 标签名到文章列表的映射
        """
        tags_dict = {}
        
        for post in posts:
            # 获取文章的标签列表
            tags = post["metadata"].get("tags", [])
            
            # 如果 tags 不是列表，跳过
            if not isinstance(tags, list):
                continue
            
            # 将文章添加到每个标签的列表中
            for tag in tags:
                if tag not in tags_dict:
                    tags_dict[tag] = []
                tags_dict[tag].append(post)
        
        return tags_dict
    
    def _calculate_tag_stats(self, tags_dict: dict) -> list[dict]:
        """计算标签统计信息，包括动态字体大小
        
        Args:
            tags_dict: 标签名到文章列表的映射
            
        Returns:
            list[dict]: 标签统计信息列表，包含 name, count, url, font_size
        """
        tag_stats = []
        
        # 找出最大文章数量，用于计算字体大小
        max_count = max(len(posts) for posts in tags_dict.values()) if tags_dict else 1
        
        for name, tag_posts in tags_dict.items():
            count = len(tag_posts)
            
            # 计算字体大小：0.9em ~ 1.7em
            # 最少文章的标签为 0.9em，最多文章的标签为 1.7em
            if max_count > 1:
                font_size = 0.9 + (count / max_count) * 0.8
            else:
                font_size = 1.2  # 如果只有一个标签或所有标签文章数相同，使用中等大小
            
            tag_stats.append({
                'name': name,
                'count': count,
                'url': f'{name}.html',
                'font_size': f'{font_size:.2f}em'
            })
        
        # 按文章数量降序排序
        tag_stats.sort(key=lambda x: x['count'], reverse=True)
        
        return tag_stats
    
    def _render_tags_index(self, tag_stats: list[dict], tags_dir: Path, total_posts: int = 0):
        """渲染标签云索引页
        
        Args:
            tag_stats: 标签统计信息列表
            tags_dir: tags 目录路径
            total_posts: 博客总数
        """
        html = self.renderer.render_tags(tag_stats, total_posts=total_posts)
        
        index_path = tags_dir / "index.html"
        index_path.write_text(html, encoding="utf-8")
        
        logger.success(f"标签云索引页已生成: {index_path}")
    
    def _render_tag_detail(self, tag_name: str, posts: list[dict], tags_dir: Path, total_posts: int = 0):
        """渲染单个标签的详情页
        
        Args:
            tag_name: 标签名称
            posts: 该标签下的文章列表
            tags_dir: tags 目录路径
            total_posts: 博客总数
        """
        # 按日期排序（最新的在前）
        sorted_posts = sorted(
            posts,
            key=lambda p: p["metadata"].get("date", ""),
            reverse=True
        )
        
        html = self.renderer.render_tag_detail(tag_name, sorted_posts, total_posts=total_posts)
        
        # 生成文件名
        output_path = tags_dir / f"{tag_name}.html"
        output_path.write_text(html, encoding="utf-8")
        
        logger.debug(f"已生成标签页: {tag_name} ({len(posts)} 篇文章)")
