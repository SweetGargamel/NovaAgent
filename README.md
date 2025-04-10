没有实现前端的写入逻辑

你需要提供一个conf.py 文件，内容如下：
```python
# 数据库配置信息
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',      # 请修改为你的用户名
    'password': '',  # 请修改为你的密码
    'database': 'time_manager'  # 请修改为你的数据库名
}

```
