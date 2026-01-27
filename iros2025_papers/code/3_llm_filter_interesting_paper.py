#!/usr/bin/env python3
"""
IROS 2025 论文筛选脚本
根据指定的研究兴趣，使用LLM API筛选相关论文
支持批处理、断点续传和进度显示
"""

import json
import os
import sys
import time
from typing import List, Dict, Any, Optional
from datetime import datetime
import requests
from tqdm import tqdm

class PaperFilter:
    def __init__(self, 
                 api_url: str = "https://api.deepseek.com/v1/",
                 api_key: str = "<你的deepseek_api_key>",
                 batch_size: int = 50,
                 model: str = "deepseek-chat"):
        """
        初始化论文筛选器
        
        Args:
            api_url: API接口地址
            api_key: API密钥
            batch_size: 每批处理的论文数量
            model: 使用的模型名称
        """
        self.api_url = api_url.rstrip('/') + '/chat/completions'
        print("self.api_url", self.api_url)
        self.api_key = api_key
        self.batch_size = batch_size
        self.model = model
        self.headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        
        # 加载提示词
        self.system_prompt = self._load_prompt()
        
        # 进度文件
        self.progress_file = "filter_progress.json"
        self.output_file = "filtered_papers.json"
        
    def _load_prompt(self) -> str:
        """加载筛选提示词"""
        try:
            with open('filter_paper_prompt.txt', 'r', encoding='utf-8') as f:
                return f.read().strip()
        except FileNotFoundError:
            print("错误：找不到 filter_paper_prompt.txt 文件")
            sys.exit(1)
    
    def _load_papers(self) -> List[Dict[str, Any]]:
        """加载论文数据"""
        try:
            with open('iros25_papers_essentials.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('papers', [])
        except FileNotFoundError:
            print("错误：找不到 iros25_papers_essentials.json 文件")
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"错误：JSON文件格式错误 - {e}")
            sys.exit(1)
    
    def _load_progress(self) -> Dict[str, Any]:
        """加载处理进度"""
        if os.path.exists(self.progress_file):
            try:
                with open(self.progress_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                print("警告：进度文件损坏，将从头开始处理")
        
        return {
            'processed_batches': 0,
            'total_batches': 0,
            'filtered_papers': [],
            'last_update': None
        }
    
    def _save_progress(self, progress: Dict[str, Any]):
        """保存处理进度"""
        progress['last_update'] = datetime.now().isoformat()
        with open(self.progress_file, 'w', encoding='utf-8') as f:
            json.dump(progress, f, ensure_ascii=False, indent=2)
    
    def _save_results(self, filtered_papers: List[Dict[str, Any]]):
        """保存筛选结果"""
        result = {
            'conference': 'IROS 2025',
            'filter_date': datetime.now().isoformat(),
            'total_filtered': len(filtered_papers),
            'filtered_papers': filtered_papers
        }
        
        with open(self.output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
    
    def _create_batch_prompt(self, papers: List[Dict[str, Any]]) -> str:
        """为一批论文创建提示词"""
        papers_json = json.dumps(papers, ensure_ascii=False, indent=2)
        return f"{self.system_prompt}\n\n{papers_json}"
    
    def _call_api(self, prompt: str, max_retries: int = 3) -> Optional[str]:
        """调用API"""
        for attempt in range(max_retries):
            try:
                payload = {
                    "model": self.model,
                    "messages": [
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.1,
                    "max_tokens": 4000
                }
                
                print(f"第 {attempt + 1} 次API调用尝试...")
                
                response = requests.post(
                    self.api_url,
                    headers=self.headers,
                    json=payload,
                    timeout=60
                )
                
                if response.status_code == 200:
                    try:
                        result = response.json()
                        if 'choices' in result and len(result['choices']) > 0:
                            return result['choices'][0]['message']['content']
                        else:
                            print(f"❌ API响应格式异常:")
                            print(f"   完整响应: {result}")
                    except json.JSONDecodeError as e:
                        print(f"❌ API响应JSON解析失败: {e}")
                        print(f"   原始响应内容: {response.text}")
                else:
                    # 详细的错误分析
                    print(f"❌ API请求失败")
                    print(f"   状态码: {response.status_code}")
                    print(f"   请求URL: {self.api_url}")
                    print(f"   请求头: {self.headers}")
                    
                    # 尝试解析错误响应
                    try:
                        error_data = response.json()
                        print(f"   错误详情: {json.dumps(error_data, ensure_ascii=False, indent=2)}")
                        
                        # 分析具体错误类型
                        if response.status_code == 502:
                            print(f"   ⚠️  502 Bad Gateway 错误分析:")
                            print(f"      - 这通常表示API网关或上游服务暂时不可用")
                            print(f"      - 可能是服务器过载或维护中")
                            print(f"      - 建议等待更长时间后重试")
                            
                        elif response.status_code == 429:
                            print(f"   ⚠️  429 Too Many Requests 错误:")
                            print(f"      - API请求频率过高，已被限流")
                            print(f"      - 建议增加请求间隔")
                            
                        elif response.status_code == 401:
                            print(f"   ⚠️  401 Unauthorized 错误:")
                            print(f"      - API密钥可能无效或已过期")
                            print(f"      - 请检查API密钥是否正确")
                            
                        elif response.status_code == 400:
                            print(f"   ⚠️  400 Bad Request 错误:")
                            print(f"      - 请求参数可能有误")
                            print(f"      - 检查模型名称、消息格式等")
                            
                    except json.JSONDecodeError:
                        print(f"   原始响应内容: {response.text}")
                
            except requests.Timeout:
                print(f"❌ 第 {attempt + 1} 次请求超时 (60秒)")
                
            except requests.ConnectionError as e:
                print(f"❌ 第 {attempt + 1} 次连接失败: {e}")
                print(f"   可能的原因:")
                print(f"   - 网络连接问题")
                print(f"   - API服务器不可达")
                print(f"   - DNS解析失败")
                
            except requests.RequestException as e:
                print(f"❌ 第 {attempt + 1} 次请求失败: {e}")
            
            # 重试策略
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt
                if response.status_code == 502:
                    # 502错误等待更长时间
                    wait_time = max(wait_time, 10)
                    
                print(f"   ⏱️  等待 {wait_time} 秒后重试...")
                time.sleep(wait_time)
            else:
                print(f"   ❌ 已达到最大重试次数 ({max_retries})，放弃此批次")
        
        return None
    
    def _parse_api_response(self, response: str) -> List[Dict[str, Any]]:
        """解析API响应"""
        try:
            # 尝试提取JSON内容
            start = response.find('[')
            end = response.rfind(']') + 1
            
            if start != -1 and end > start:
                json_str = response[start:end]
                return json.loads(json_str)
            else:
                # 如果没找到JSON数组，尝试整个响应
                return json.loads(response)
                
        except json.JSONDecodeError as e:
            print(f"解析API响应失败: {e}")
            print(f"原始响应: {response[:500]}...")
            return []
    
    def filter_papers(self, resume: bool = True):
        """
        筛选论文主函数
        
        Args:
            resume: 是否从上次中断的地方继续
        """
        # 加载数据和进度
        papers = self._load_papers()
        progress = self._load_progress() if resume else {
            'processed_batches': 0,
            'total_batches': 0,
            'filtered_papers': [],
            'last_update': None
        }
        
        total_papers = len(papers)
        total_batches = (total_papers + self.batch_size - 1) // self.batch_size
        progress['total_batches'] = total_batches
        
        print(f"总共 {total_papers} 篇论文，分为 {total_batches} 个批次处理")
        print(f"每批处理 {self.batch_size} 篇论文")
        
        if resume and progress['processed_batches'] > 0:
            print(f"从第 {progress['processed_batches'] + 1} 批开始继续处理")
        
        # 创建进度条
        pbar = tqdm(
            total=total_batches,
            initial=progress['processed_batches'],
            desc="筛选论文",
            unit="批次"
        )
        
        try:
            for batch_idx in range(progress['processed_batches'], total_batches):
                # 准备当前批次的论文
                start_idx = batch_idx * self.batch_size
                end_idx = min(start_idx + self.batch_size, total_papers)
                batch_papers = papers[start_idx:end_idx]
                
                # 为API调用准备论文数据（只包含title和abstract）
                api_papers = []
                for paper in batch_papers:
                    api_papers.append({
                        'title': paper.get('title', ''),
                        'abstract': paper.get('abstract', '')
                    })
                
                # 创建提示词并调用API
                prompt = self._create_batch_prompt(api_papers)
                response = self._call_api(prompt)
                
                if response is None:
                    print(f"\n批次 {batch_idx + 1} 处理失败，跳过")
                    continue
                
                # 解析响应
                filtered_batch = self._parse_api_response(response)
                
                if filtered_batch:
                    progress['filtered_papers'].extend(filtered_batch)
                    print(f"\n批次 {batch_idx + 1}: 筛选出 {len(filtered_batch)} 篇相关论文")
                
                # 更新进度
                progress['processed_batches'] = batch_idx + 1
                self._save_progress(progress)
                
                # 更新进度条
                pbar.update(1)
                pbar.set_postfix({
                    '已筛选': len(progress['filtered_papers']),
                    '当前批次': f"{batch_idx + 1}/{total_batches}"
                })
                
                # 避免请求过于频繁
                time.sleep(1)
        
        except KeyboardInterrupt:
            print("\n\n用户中断处理，进度已保存")
            return
        
        finally:
            pbar.close()
        
        # 保存最终结果
        self._save_results(progress['filtered_papers'])
        
        print(f"\n筛选完成！")
        print(f"总共处理了 {total_papers} 篇论文")
        print(f"筛选出 {len(progress['filtered_papers'])} 篇相关论文")
        print(f"结果已保存到 {self.output_file}")
        
        # 清理进度文件
        if os.path.exists(self.progress_file):
            os.remove(self.progress_file)


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='IROS 2025 论文筛选工具')
    parser.add_argument('--restart', action='store_true', 
                       help='从头开始处理，忽略之前的进度')
    parser.add_argument('--batch-size', type=int, default=50,
                       help='每批处理的论文数量 (默认: 50)')
    parser.add_argument('--model', type=str, default='deepseek-chat',
                       help='使用的模型名称')
    
    args = parser.parse_args()
    
    # 创建筛选器
    filter_instance = PaperFilter(
        batch_size=args.batch_size,
        model=args.model
    )
    
    # 开始筛选
    filter_instance.filter_papers(resume=not args.restart)


if __name__ == "__main__":
    main()