import json
import re
from bs4 import BeautifulSoup


def parse_html_file(file_path):
    """解析HTML文件并提取论文信息"""
    # 尝试不同的编码方式
    encodings = ['utf-8', 'iso-8859-1', 'windows-1252', 'latin-1']
    content = None
    
    for encoding in encodings:
        try:
            with open(file_path, 'r', encoding=encoding) as file:
                content = file.read()
            print(f"成功使用 {encoding} 编码读取文件")
            break
        except UnicodeDecodeError:
            continue
    
    if content is None:
        raise ValueError("无法使用任何编码读取文件")
    
    soup = BeautifulSoup(content, 'html.parser')
    papers = []
    
    # 查找所有论文条目
    # 论文条目以class="pHdr"的tr标签开始
    paper_headers = soup.find_all('tr', class_='pHdr')
    
    for header in paper_headers:
        paper = {}
        
        # 提取时间和论文编号
        time_info = header.find('a')
        if time_info:
            paper['time'] = time_info.text.strip()
            paper['paper_id'] = time_info.get('name', '')
        
        # 获取下一个兄弟元素，包含论文标题
        title_row = header.find_next_sibling('tr')
        if title_row:
            title_span = title_row.find('span', class_='pTtl')
            if title_span:
                title_link = title_span.find('a')
                if title_link:
                    paper['title'] = title_link.text.strip()
                    
                    # 从onclick属性中提取abstract ID
                    onclick = title_link.get('onclick', '')
                    abstract_id_match = re.search(r"viewAbstract\('(\d+)'\)", onclick)
                    if abstract_id_match:
                        abstract_id = abstract_id_match.group(1)
                        paper['abstract_id'] = abstract_id
                        
                        # 查找对应的摘要div
                        abstract_div = soup.find('div', id=f'Ab{abstract_id}')
                        if abstract_div:
                            # 提取关键词
                            keywords_span = abstract_div.find('span')
                            if keywords_span:
                                keywords_links = keywords_span.find_all('a')
                                paper['keywords'] = [link.text.strip() for link in keywords_links]
                            
                            # 提取摘要
                            abstract_text = abstract_div.get_text()
                            abstract_match = re.search(r'Abstract:\s*(.*)', abstract_text, re.DOTALL)
                            if abstract_match:
                                paper['abstract'] = abstract_match.group(1).strip()
        
        # 提取作者信息
        authors = []
        current_row = title_row.find_next_sibling('tr') if title_row else None
        
        # 跳过分隔线
        if current_row and current_row.find('hr'):
            current_row = current_row.find_next_sibling('tr')
        
        # 收集作者信息直到遇到摘要div或下一个论文
        while current_row:
            # 如果遇到摘要div的容器，停止
            if current_row.find('div', id=lambda x: x and x.startswith('Ab')):
                break
            
            # 如果遇到下一个论文头部，停止
            if current_row.get('class') == ['pHdr']:
                break
                
            # 如果是空行或只包含空白的行，跳过
            if current_row.get_text().strip() == '' or current_row.get_text().strip() == '&nbsp;':
                current_row = current_row.find_next_sibling('tr')
                continue
            
            # 提取作者信息
            tds = current_row.find_all('td')
            if len(tds) >= 2:
                author_link = tds[0].find('a')
                if author_link and 'AuthorIndexWeb' in author_link.get('href', ''):
                    author_name = author_link.text.strip()
                    affiliation = tds[1].text.strip()
                    authors.append({
                        'name': author_name,
                        'affiliation': affiliation
                    })
            
            current_row = current_row.find_next_sibling('tr')
        
        paper['authors'] = authors
        
        # 只添加有标题的论文
        if 'title' in paper:
            papers.append(paper)
    
    return papers


def save_to_json(papers, output_path):
    """保存论文数据到JSON文件"""
    with open(output_path, 'w', encoding='utf-8') as file:
        json.dump(papers, file, ensure_ascii=False, indent=2)


def print_paper_info(paper, index):
    """打印单个论文信息"""
    print(f"\n=== 论文 {index} ===")
    print(f"论文ID: {paper.get('paper_id', 'N/A')}")
    print(f"时间: {paper.get('time', 'N/A')}")
    print(f"标题: {paper.get('title', 'N/A')}")
    
    authors = paper.get('authors', [])
    print(f"作者 ({len(authors)} 人):")
    for author in authors:
        print(f"  - {author['name']} ({author['affiliation']})")
    
    keywords = paper.get('keywords', [])
    print(f"关键词 ({len(keywords)} 个): {', '.join(keywords)}")
    
    abstract = paper.get('abstract', '')
    if abstract:
        print(f"摘要 ({len(abstract)} 字符): {abstract[:200]}...")
    else:
        print("摘要: 无")


def parse_multiple_html_files(html_files):
    """解析多个HTML文件并合并结果"""
    all_papers = []
    
    for html_file in html_files:
        print(f"正在解析 {html_file}...")
        try:
            papers = parse_html_file(html_file)
            print(f"从 {html_file} 提取到 {len(papers)} 篇论文")
            
            # 为每篇论文添加源文件信息
            for paper in papers:
                paper['source_file'] = html_file
            
            all_papers.extend(papers)
        except Exception as e:
            print(f"解析 {html_file} 时出错: {e}")
            continue
    
    return all_papers


def get_day_from_filename(filename):
    """从文件名提取日期信息"""
    if '1.html' in filename:
        return 'Tuesday'
    elif '2.html' in filename:
        return 'Wednesday'
    elif '3.html' in filename:
        return 'Thursday'
    else:
        return 'Unknown'


if __name__ == "__main__":
    html_files = [
        "IROS25_ContentListWeb_1.html",
        "IROS25_ContentListWeb_2.html", 
        "IROS25_ContentListWeb_3.html"
    ]
    output_file = "iros25_papers_combined.json"
    
    print("开始解析多个HTML文件...")
    all_papers = parse_multiple_html_files(html_files)
    
    print(f"\n总共提取到 {len(all_papers)} 篇论文")
    
    # 统计各个文件的论文数量
    file_counts = {}
    for paper in all_papers:
        source = paper.get('source_file', 'Unknown')
        day = get_day_from_filename(source)
        key = f"{source} ({day})"
        file_counts[key] = file_counts.get(key, 0) + 1
    
    print("\n各文件论文数量统计:")
    for file_info, count in file_counts.items():
        print(f"  {file_info}: {count} 篇")
    
    print(f"\n正在保存到JSON文件...")
    
    # 创建包含元数据的结构
    result = {
        "metadata": {
            "conference": "2025 IEEE/RSJ International Conference on Intelligent Robots and Systems (IROS)",
            "date": "October 19-25, 2025",
            "location": "Hangzhou, China",
            "total_papers": len(all_papers),
            "extraction_date": "2025-10-25",
            "source_files": html_files
        },
        "papers": all_papers
    }
    
    save_to_json(result, output_file)
    
    print(f"论文信息已保存到 {output_file}")
    
    # 打印示例论文信息
    if all_papers:
        print("\n=== 示例论文信息 ===")
        for i, paper in enumerate(all_papers[:3]):
            print_paper_info(paper, i + 1)
