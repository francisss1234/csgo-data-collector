import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
from tabulate import tabulate

class CSGODatabase:
    def __init__(self, db_path='csgo_items.db'):
        """初始化数据库连接"""
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
    
    def close(self):
        """关闭数据库连接"""
        if self.conn:
            self.conn.close()
    
    def get_all_items(self, limit=100):
        """获取所有物品"""
        query = """
        SELECT id, name, market_hash_name, item_type, category, rarity, price, volume 
        FROM csgo_items 
        ORDER BY price DESC
        LIMIT ?
        """
        self.cursor.execute(query, (limit,))
        columns = [desc[0] for desc in self.cursor.description]
        return pd.DataFrame(self.cursor.fetchall(), columns=columns)
    
    def get_items_by_category(self, category):
        """按类别获取物品"""
        query = """
        SELECT id, name, market_hash_name, item_type, rarity, price, volume 
        FROM csgo_items 
        WHERE category = ?
        ORDER BY price DESC
        """
        self.cursor.execute(query, (category,))
        columns = [desc[0] for desc in self.cursor.description]
        return pd.DataFrame(self.cursor.fetchall(), columns=columns)
    
    def get_categories(self):
        """获取所有物品类别"""
        query = """
        SELECT DISTINCT category, COUNT(*) as count
        FROM csgo_items
        GROUP BY category
        ORDER BY count DESC
        """
        self.cursor.execute(query)
        return self.cursor.fetchall()
    
    def get_item_price_history(self, item_id):
        """获取物品价格历史"""
        query = """
        SELECT ph.price, ph.volume, ph.timestamp
        FROM price_history ph
        WHERE ph.item_id = ?
        ORDER BY ph.timestamp
        """
        self.cursor.execute(query, (item_id,))
        columns = [desc[0] for desc in self.cursor.description]
        return pd.DataFrame(self.cursor.fetchall(), columns=columns)
    
    def search_items(self, keyword):
        """搜索物品"""
        query = """
        SELECT id, name, market_hash_name, item_type, category, rarity, price, volume 
        FROM csgo_items 
        WHERE name LIKE ? OR market_hash_name LIKE ?
        ORDER BY price DESC
        """
        keyword = f"%{keyword}%"
        self.cursor.execute(query, (keyword, keyword))
        columns = [desc[0] for desc in self.cursor.description]
        return pd.DataFrame(self.cursor.fetchall(), columns=columns)

def main():
    """主函数，测试数据库查询"""
    db = CSGODatabase()
    
    # 获取所有类别
    print("CSGO物品类别:")
    categories = db.get_categories()
    for category, count in categories:
        print(f"- {category}: {count}个物品")
    
    # 获取所有物品
    print("\n所有物品 (前10个):")
    all_items = db.get_all_items(10)
    if not all_items.empty:
        print(tabulate(all_items, headers='keys', tablefmt='psql'))
    else:
        print("没有找到物品")
    
    # 搜索物品
    keyword = "knife"
    print(f"\n搜索 '{keyword}':")
    search_results = db.search_items(keyword)
    if not search_results.empty:
        print(tabulate(search_results, headers='keys', tablefmt='psql'))
    else:
        print(f"没有找到包含 '{keyword}' 的物品")
    
    db.close()

if __name__ == "__main__":
    main()