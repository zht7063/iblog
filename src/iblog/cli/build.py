"""统一构建入口：编排所有生成器"""

import typer
from pathlib import Path
from loguru import logger

# 导入配置系统
from iblog.core.config_loader import ConfigLoader
from iblog.core.config_models import Config

# 导入核心层
from iblog.core.metadata_parser import MetadataParser
from iblog.core.file_scanner import FileScanner
from iblog.core.template_renderer import TemplateRenderer

# 导入生成器层
from iblog.generators.post_generator import PostGenerator
from iblog.generators.index_generator import IndexGenerator
from iblog.generators.category_generator import CategoryGenerator
from iblog.generators.tag_generator import TagGenerator


app = typer.Typer(help="静态博客生成工具")


@app.command()
def build(
    input_dir: Path = typer.Option(
        ...,
        "--input",
        "-i",
        help="Markdown 文件所在目录",
        exists=True,
        file_okay=False,
        dir_okay=True,
        resolve_path=True,
    ),
    output_dir: Path = typer.Option(
        ..., "--output", "-o", help="HTML 输出目录", resolve_path=True
    ),
):
    """构建完整的博客站点"""
    logger.info("=" * 50)
    logger.info("开始构建博客站点")
    logger.info(f"输入目录: {input_dir}")
    logger.info(f"输出目录: {output_dir}")
    logger.info("=" * 50)

    # 加载配置文件
    try:
        config: Config = ConfigLoader.load_from_cwd()
    except Exception as e:
        logger.error(f"加载配置失败: {e}")
        raise typer.Exit(code=1)

    # 初始化核心组件（传入配置）
    parser = MetadataParser(config)
    scanner = FileScanner(parser, config)
    template_dir = Path(__file__).parent.parent.parent.parent / "templates"
    renderer = TemplateRenderer(template_dir, config)

    # 一次性扫描所有文章
    logger.info(f"扫描目录: {input_dir}")
    posts = scanner.scan_directory(input_dir)
    posts = scanner.sort_by_pinned_and_date(posts, reverse=True)
    logger.info(f"找到 {len(posts)} 篇文章")

    if len(posts) == 0:
        logger.warning("未找到任何 Markdown 文件，退出构建")
        return

    # 依次调用各个生成器（根据配置开关）
    if config.features.generators.posts:
        logger.info("=" * 50)
        PostGenerator(renderer, config).generate(posts, output_dir)
    else:
        logger.info("=" * 50)
        logger.info("博文生成器已禁用，跳过")

    if config.features.generators.index:
        logger.info("=" * 50)
        IndexGenerator(renderer, config).generate(posts, output_dir)
    else:
        logger.info("=" * 50)
        logger.info("首页生成器已禁用，跳过")

    if config.features.generators.categories:
        logger.info("=" * 50)
        CategoryGenerator(renderer, config).generate(posts, output_dir)
    else:
        logger.info("=" * 50)
        logger.info("分类生成器已禁用，跳过")

    if config.features.generators.tags:
        logger.info("=" * 50)
        TagGenerator(renderer, config).generate(posts, output_dir)
    else:
        logger.info("=" * 50)
        logger.info("标签生成器已禁用，跳过")

    # 检查并生成关于页面
    about_file = input_dir / "about.md"
    if config.features.generators.about and about_file.exists():
        logger.info("=" * 50)
        from iblog.generators.about_generator import AboutGenerator

        AboutGenerator(renderer, config).generate(
            about_file, output_dir, total_posts=len(posts)
        )
    else:
        logger.info("=" * 50)
        if not config.features.generators.about:
            logger.info("关于页生成器已禁用，跳过")
        elif not about_file.exists():
            logger.info("未找到 about.md，跳过关于页面生成")

    # 构建完成
    logger.info("=" * 50)
    logger.success("构建完成！")
    if config.features.generators.index:
        logger.success(f"首页: {output_dir / 'index.html'}")
    if config.features.generators.posts:
        logger.success(f"博文: {output_dir / config.paths.output.posts}")
    if config.features.generators.about and about_file.exists():
        logger.success(f"关于: {output_dir / config.paths.output.about / 'index.html'}")
    logger.info("=" * 50)


if __name__ == "__main__":
    app()
