"""目录（TOC）生成器：从HTML内容中提取标题生成目录"""

import re
from html.parser import HTMLParser
from typing import List, Dict


class TocItem:
    """目录项数据类"""
    
    def __init__(self, level: int, text: str, id: str):
        self.level = level
        self.text = text
        self.id = id


class TocExtractor(HTMLParser):
    """HTML标题提取器"""
    
    def __init__(self):
        super().__init__()
        self.toc_items: List[TocItem] = []
        self.current_tag = None
        self.current_text = []
        self.heading_counter = {}  # 用于生成唯一ID
    
    def handle_starttag(self, tag, attrs):
        """处理开始标签"""
        if tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            self.current_tag = tag
            self.current_text = []
    
    def handle_data(self, data):
        """处理文本数据"""
        if self.current_tag:
            self.current_text.append(data)
    
    def handle_endtag(self, tag):
        """处理结束标签"""
        if tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6'] and self.current_tag == tag:
            level = int(tag[1])
            text = ''.join(self.current_text).strip()
            
            if text:
                # 生成唯一ID
                heading_id = self._generate_id(text)
                self.toc_items.append(TocItem(level, text, heading_id))
            
            self.current_tag = None
            self.current_text = []
    
    def _generate_id(self, text: str) -> str:
        """从标题文本生成唯一ID"""
        # 转换为小写，替换空格和特殊字符
        base_id = re.sub(r'[^\w\s-]', '', text.lower())
        base_id = re.sub(r'[\s_]+', '-', base_id)
        base_id = base_id.strip('-')
        
        # 如果为空，使用默认值
        if not base_id:
            base_id = 'heading'
        
        # 确保唯一性
        if base_id not in self.heading_counter:
            self.heading_counter[base_id] = 0
            return base_id
        else:
            self.heading_counter[base_id] += 1
            return f"{base_id}-{self.heading_counter[base_id]}"


class TocGenerator:
    """目录生成器"""
    
    @staticmethod
    def extract_toc(html_content: str) -> List[Dict]:
        """从HTML内容中提取目录
        
        Args:
            html_content: HTML内容
            
        Returns:
            目录项列表，每项包含 level, text, id
        """
        extractor = TocExtractor()
        extractor.feed(html_content)
        
        return [
            {
                'level': item.level,
                'text': item.text,
                'id': item.id
            }
            for item in extractor.toc_items
        ]
    
    @staticmethod
    def add_heading_ids(html_content: str) -> str:
        """为HTML中的标题添加ID属性
        
        Args:
            html_content: HTML内容
            
        Returns:
            添加了ID的HTML内容
        """
        extractor = TocExtractor()
        extractor.feed(html_content)
        
        # 为每个标题添加ID
        result = html_content
        for item in extractor.toc_items:
            # 匹配标题标签，并添加ID
            pattern = rf'(<h{item.level})(>.*?{re.escape(item.text)}.*?</h{item.level}>)'
            replacement = rf'\1 id="{item.id}"\2'
            result = re.sub(pattern, replacement, result, count=1)
        
        return result
