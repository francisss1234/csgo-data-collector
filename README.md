# CSGO数据收集器

这是一个用于收集和分析CSGO物品市场数据的工具，支持从Steam社区市场获取物品信息，并提供数据存储和分析功能。

## 功能特点

- 从Steam社区市场收集CSGO物品数据
- 支持代理IP池，解决API请求限制问题
- 多线程并行收集数据，提高效率
- SQLite数据库存储和查询功能
- 支持按类别、名称搜索物品

## 使用方法

### 安装依赖

```bash
pip install requests beautifulsoup4 pandas matplotlib tabulate
```

### 收集数据

```bash
python collector.py
```

### 导入数据到数据库

```bash
python db_setup.py
```

### 查询数据

```bash
python db_query.py
```

## 文件说明

- `collector.py`: 主要的数据收集脚本
- `db_setup.py`: 数据库设置和数据导入脚本
- `db_query.py`: 数据查询和分析脚本
- `UPDATE_LOG.md`: 更新日志，记录每次更新的时间和内容

## 更新日志

详细的更新记录请查看 [UPDATE_LOG.md](UPDATE_LOG.md) 文件。

## 许可证

MIT