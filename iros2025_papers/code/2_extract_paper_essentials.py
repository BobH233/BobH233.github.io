import json


def extract_essentials(input_file, output_file):
    """提取论文的核心信息：title, abstract, keywords"""
    
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 提取核心信息
    essential_papers = []
    
    for paper in data.get('papers', []):
        essential_info = {
            'title': paper.get('title', ''),
            'abstract': paper.get('abstract', ''),
            'keywords': paper.get('keywords', [])
        }
        
        # 只保留有标题的论文
        if essential_info['title']:
            essential_papers.append(essential_info)
    
    # 创建新的数据结构
    output_data = {
        'conference': 'IROS 2025',
        'description': '2025 IEEE/RSJ International Conference on Intelligent Robots and Systems',
        'total_papers': len(essential_papers),
        'papers': essential_papers
    }
    
    # 保存到新文件
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    
    print(f"已提取 {len(essential_papers)} 篇论文的核心信息")
    print(f"结果保存到: {output_file}")


if __name__ == "__main__":
    input_file = "iros25_papers_combined.json"
    output_file = "iros25_papers_essentials.json"
    
    extract_essentials(input_file, output_file)