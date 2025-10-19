import sqlite3
import os
import json
import glob
from pathlib import Path

# 创建数据库连接
def create_database():
    """创建SQLite数据库并设置表结构"""
    conn = sqlite3.connect('csgo_items.db')
    cursor = conn.cursor()
    
    # 创建CSGO物品表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS csgo_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        market_hash_name TEXT NOT NULL UNIQUE,
        item_type TEXT,
        category TEXT,
        rarity TEXT,
        image_url TEXT,
        price REAL,
        volume INTEGER,
        last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # 创建价格历史表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS price_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        item_id INTEGER,
        price REAL,
        volume INTEGER,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (item_id) REFERENCES csgo_items (id)
    )
    ''')
    
    conn.commit()
    return conn

# 导入数据函数
def import_data():
    """从JSON文件导入CSGO物品数据到SQLite数据库"""
    conn = create_database()
    cursor = conn.cursor()
    
    # 获取数据文件路径
    data_dir = Path('data')
    if not data_dir.exists():
        print(f"数据目录 {data_dir} 不存在")
        return
    
    # 查找所有JSON文件
    json_files = list(data_dir.glob('**/*.json'))
    if not json_files:
        print(f"在 {data_dir} 中未找到JSON文件")
        return
    
    print(f"找到 {len(json_files)} 个JSON文件")
    
    # 导入每个文件的数据
    items_added = 0
    for json_file in json_files:
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # 处理不同格式的JSON文件
            if isinstance(data, list):
                items = data
            elif isinstance(data, dict) and 'results' in data:
                items = data.get('results', [])
            else:
                items = [data]
            
            for item in items:
                # 提取物品信息
                name = item.get('name', '')
                market_hash_name = item.get('market_hash_name', name)
                item_type = item.get('type', '')
                category = json_file.parent.name  # 使用父目录名作为分类
                rarity = item.get('rarity', '')
                image_url = item.get('icon_url', '')
                price = float(item.get('price', 0)) if item.get('price') else 0
                volume = int(item.get('volume', 0)) if item.get('volume') else 0
                
                # 插入数据
                try:
                    cursor.execute('''
                    INSERT OR IGNORE INTO csgo_items 
                    (name, market_hash_name, item_type, category, rarity, image_url, price, volume)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (name, market_hash_name, item_type, category, rarity, image_url, price, volume))
                    
                    if cursor.rowcount > 0:
                        items_added += 1
                        
                        # 获取插入的物品ID
                        item_id = cursor.lastrowid
                        
                        # 添加价格历史记录
                        if price > 0:
                            cursor.execute('''
                            INSERT INTO price_history (item_id, price, volume)
                            VALUES (?, ?, ?)
                            ''', (item_id, price, volume))
                except sqlite3.Error as e:
                    print(f"插入数据时出错: {e}, 物品: {market_hash_name}")
                    
        except Exception as e:
            print(f"处理文件 {json_file} 时出错: {e}")
    
    conn.commit()
    print(f"成功导入 {items_added} 个物品")
    conn.close()

if __name__ == "__main__":
    import_data()