import requests
import json
import os
import time
import random
import re
import concurrent.futures
import urllib3
from bs4 import BeautifulSoup
from datetime import datetime

class ProxyPool:
    def __init__(self, min_proxies=5, max_proxies=20):
        self.proxies = []
        self.min_proxies = min_proxies
        self.max_proxies = max_proxies
        self.current_index = 0
        self.validation_url = "https://steamcommunity.com/market/"
        self._get_proxies()
    
    def _get_proxies(self):
        """从多个来源获取代理IP"""
        sources = [
            self._get_kuaidaili_proxies,
            self._get_89ip_proxies
        ]
        
        for source in sources:
            if len(self.proxies) >= self.min_proxies:
                break
            try:
                source()
            except Exception as e:
                print(f"从代理源获取代理时出错: {e}")
        
        if self.proxies:
            print(f"成功获取 {len(self.proxies)} 个有效代理")
        else:
            print("警告: 未能获取任何有效代理")
    
    def _get_kuaidaili_proxies(self):
        """从快代理获取免费代理IP"""
        url = "https://www.kuaidaili.com/free/inha/"
        try:
            response = requests.get(url, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            rows = soup.select('table tbody tr')
            
            proxies = []
            for row in rows:
                ip = row.select_one('td[data-title="IP"]').text.strip()
                port = row.select_one('td[data-title="PORT"]').text.strip()
                proxy = f"{ip}:{port}"
                proxies.append(proxy)
            
            self._validate_proxies(proxies)
        except Exception as e:
            print(f"从快代理获取代理时出错: {e}")
    
    def _get_89ip_proxies(self):
        """从89IP获取免费代理"""
        url = "https://www.89ip.cn/index_1.html"
        try:
            response = requests.get(url, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            rows = soup.select('table tbody tr')
            
            proxies = []
            for row in rows:
                columns = row.select('td')
                if len(columns) >= 2:
                    ip = columns[0].text.strip()
                    port = columns[1].text.strip()
                    proxy = f"{ip}:{port}"
                    proxies.append(proxy)
            
            self._validate_proxies(proxies)
        except Exception as e:
            print(f"从89IP获取代理时出错: {e}")
    
    def _validate_proxies(self, proxy_list):
        """验证代理是否可用"""
        valid_proxies = []
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
            future_to_proxy = {executor.submit(self._check_proxy, proxy): proxy for proxy in proxy_list}
            for future in concurrent.futures.as_completed(future_to_proxy):
                proxy = future_to_proxy[future]
                try:
                    is_valid = future.result()
                    if is_valid:
                        valid_proxies.append(proxy)
                        # 如果已经找到足够的有效代理，提前结束
                        if len(self.proxies) + len(valid_proxies) >= self.max_proxies:
                            break
                except Exception as e:
                    print(f"验证代理 {proxy} 时出错: {e}")
        
        # 添加有效代理到代理池
        for proxy in valid_proxies:
            if len(self.proxies) < self.max_proxies:
                self.proxies.append({"http": f"http://{proxy}", "https": f"http://{proxy}"})
            else:
                break
    
    def _check_proxy(self, proxy):
        """检查单个代理是否可用"""
        proxies = {"http": f"http://{proxy}", "https": f"http://{proxy}"}
        try:
            response = requests.get(self.validation_url, proxies=proxies, timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def get_proxy(self):
        """获取一个代理"""
        if not self.proxies:
            return None
        
        # 轮换使用代理
        proxy = self.proxies[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.proxies)
        return proxy
    
    def remove_proxy(self, proxy):
        """从代理池中移除无效代理"""
        if proxy in self.proxies:
            self.proxies.remove(proxy)
            print(f"移除无效代理，剩余 {len(self.proxies)} 个代理")
            
            # 如果代理数量低于最小值，尝试获取更多代理
            if len(self.proxies) < self.min_proxies:
                self._get_proxies()

class SteamMarketCollector:
    def __init__(self, use_proxy=False, proxy=None, enable_proxy_pool=False):
        self.session = requests.Session()
        self.use_proxy = use_proxy
        self.proxy_pool = None
        
        # 如果启用代理池
        if enable_proxy_pool:
            self.proxy_pool = ProxyPool()
            self.use_proxy = True
        
        # 如果使用代理但未指定，从代理池获取
        if self.use_proxy:
            if proxy:
                self.session.proxies = proxy
            elif self.proxy_pool:
                self.session.proxies = self.proxy_pool.get_proxy()
        
        # 扩展User-Agent列表
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.164 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Safari/605.1.15",
            "Mozilla/5.0 (X11; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36"
        ]
        
        self.session.headers.update({
            "User-Agent": random.choice(self.user_agents),
            "Accept-Language": "en-US,en;q=0.9",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        })
    
    def _rotate_user_agent(self):
        self.session.headers.update({"User-Agent": random.choice(self.user_agents)})
    
    def _rotate_proxy(self):
        if self.proxy_pool:
            self.session.proxies = self.proxy_pool.get_proxy()
    
    def search_items(self, appid, query="", category=None, start=0, count=10):
        url = f"https://steamcommunity.com/market/search/render/"
        
        params = {
            "appid": appid,
            "norender": 1,
            "start": start,
            "count": count
        }
        
        if query:
            params["query"] = query
        
        if category:
            params["category_"+appid+"_Item"] = category
        
        # 随机延迟1-3秒
        delay = random.uniform(1, 3)
        time.sleep(delay)
        
        # 轮换User-Agent
        self._rotate_user_agent()
        
        # 如果使用代理池，获取新代理
        if self.proxy_pool:
            self._rotate_proxy()
        
        max_retries = 5
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                response = self.session.get(url, params=params, timeout=15)  # 增加超时时间
                
                if response.status_code == 429:  # Too Many Requests
                    print(f"遇到429错误，等待并更换代理...")
                    time.sleep(5)  # 等待5秒
                    
                    # 更换代理
                    if self.proxy_pool:
                        current_proxy = self.session.proxies
                        self._rotate_proxy()
                        print(f"更换代理: {current_proxy} -> {self.session.proxies}")
                    
                    retry_count += 1
                    continue
                
                response.raise_for_status()
                return response.json()
                
            except requests.exceptions.SSLError as e:
                print(f"SSL错误: {e}，更换代理并重试...")
                if self.proxy_pool:
                    current_proxy = self.session.proxies
                    self._rotate_proxy()
                    print(f"更换代理: {current_proxy} -> {self.session.proxies}")
                
            except requests.exceptions.RequestException as e:
                print(f"请求错误: {e}，重试...")
                if self.proxy_pool:
                    current_proxy = self.session.proxies
                    self._rotate_proxy()
                    print(f"更换代理: {current_proxy} -> {self.session.proxies}")
            
            retry_count += 1
            time.sleep(2)  # 等待2秒后重试
        
        print(f"达到最大重试次数 {max_retries}，返回空结果")
        return {"success": False, "results": []}
    
    def get_item_price_history(self, appid, market_hash_name):
        url = f"https://steamcommunity.com/market/pricehistory/"
        
        params = {
            "appid": appid,
            "market_hash_name": market_hash_name
        }
        
        # 随机延迟2-5秒
        delay = random.uniform(2, 5)
        time.sleep(delay)
        
        # 轮换User-Agent
        self._rotate_user_agent()
        
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"获取物品价格历史时出错: {e}")
            return None

def process_item_type(collector, item_type, appid=730, max_pages=10, items_per_page=10, save_dir="data/categories"):
    """处理单个物品类型的数据收集"""
    print(f"正在获取 {item_type} 类型的物品...")
    
    # 创建保存目录
    os.makedirs(save_dir, exist_ok=True)
    
    # 生成文件名，包含日期
    date_str = datetime.now().strftime("%Y%m%d")
    filename = f"{save_dir}/{item_type}_{date_str}.json"
    
    all_items = []
    total_count = 0
    
    # 检查是否存在已保存的文件
    if os.path.exists(filename):
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                all_items = json.load(f)
                total_count = len(all_items)
                print(f"从文件加载了 {total_count} 个物品")
        except Exception as e:
            print(f"加载文件时出错: {e}")
            all_items = []
            total_count = 0
    
    # 计算起始页
    start_page = total_count // items_per_page
    
    # 获取物品数据
    for page in range(start_page, max_pages):
        start = page * items_per_page
        print(f"正在获取第 {page+1}/{max_pages} 页，起始索引: {start}")
        
        result = collector.search_items(
            appid=appid,
            category=item_type,
            start=start,
            count=items_per_page
        )
        
        if not result.get("success", False):
            print(f"获取第 {page+1} 页失败，跳过")
            continue
        
        items = result.get("results", [])
        if not items:
            print(f"第 {page+1} 页没有物品，可能已到达末尾")
            break
        
        all_items.extend(items)
        
        # 保存当前进度
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(all_items, f, ensure_ascii=False, indent=2)
        
        print(f"已保存 {len(all_items)} 个物品到 {filename}")
        
        # 随机等待5-10秒，避免请求过于频繁
        wait_time = random.uniform(5, 10)
        print(f"等待 {wait_time:.2f} 秒...")
        time.sleep(wait_time)
    
    return all_items

def get_csgo_item_categories(collector, max_workers=5, max_pages=500, all_items=True):
    """获取CSGO物品种类列表"""
    # CSGO物品类型
    item_types = [
        "Pistol", "SMG", "Rifle", "Sniper Rifle", "Shotgun", "Machinegun",
        "Container", "Key", "Pass", "Gift", "Tag", "Tool",
        "Sticker", "Music Kit", "Weapon Case", "Graffiti", "Patch",
        "Collectible", "Gloves", "Agents", "Knives"
    ]
    
    # 如果需要获取所有物品，扩展物品类型列表
    if all_items:
        item_types.extend([
            "Hands", "Crate", "Operation Pass", "Sealed Graffiti",
            "Sticker Capsule", "Pin", "Souvenir Package", "Autograph Capsule",
            "Patch Pack", "Storage Unit", "Viewer Pass", "Map Token",
            "Name Tag", "Case Key", "Ticket", "Medal", "Coin"
        ])
    
    # 创建保存目录
    save_dir = "data/categories"
    os.makedirs(save_dir, exist_ok=True)
    
    # 使用线程池并行处理多个物品类型
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        # 为每个物品类型创建一个任务
        future_to_type = {executor.submit(
            process_item_type, collector, item_type, 730, max_pages, 100, save_dir
        ): item_type for item_type in item_types}
        
        # 处理完成的任务
        for future in concurrent.futures.as_completed(future_to_type):
            item_type = future_to_type[future]
            try:
                items = future.result()
                print(f"完成 {item_type} 类型，获取了 {len(items)} 个物品")
            except Exception as e:
                print(f"{item_type} 类型处理时出错: {e}")

def main():
    # 创建收集器实例，启用代理池
    collector = SteamMarketCollector(enable_proxy_pool=True)
    
    # 获取CSGO物品数据
    get_csgo_item_categories(collector)

if __name__ == "__main__":
    main()