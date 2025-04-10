import pandas as pd
import random
from datetime import datetime, timedelta
import mysql.connector
from mysql.connector import Error
from conf import DB_CONFIG

'''
下面是测试的数据
'''

# 设置随机种子保证可重复性
random.seed(42)

# 生成用户数据 (10个用户)
user_df = pd.DataFrame({
    'user_id': range(1, 11),
    'NAME': [f'User {i}' for i in range(1, 11)]
})

# 生成组数据 (2个组)
group_df = pd.DataFrame({
    'group_id': [1, 2],
    'NAME': ['Dev Team', 'QA Team']
})

# 生成用户-组关系数据 (随机分配)
user_group_data = []
for user_id in range(1, 11):
    # 每个用户随机加入1-2个组
    groups = random.sample([1, 2], k=random.randint(1, 2))
    user_group_data.extend([{'user_id': user_id, 'group_id': g} for g in groups])

user_group_df = pd.DataFrame(user_group_data).drop_duplicates()

# 生成用户忙时数据 (3天数据)
dates = [(datetime.today() + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(3)]
hours_columns = [f'h{h}' for h in range(8, 22)]  # h8到h21

busy_slots = []
for user_id in range(1, 11):
    for date in dates:
        # 随机生成小时数据（50%概率为忙碌）
        hours = {col: random.choices([0, 1], weights=[0.5, 0.5])[0] for col in hours_columns}
        
        # 如果有任意忙碌时段，生成原因
        reason = random.choice(['Meeting', 'Client Call', 'Code Review', 'Deployment', '']) if sum(hours.values()) > 0 else ''
        
        busy_slots.append({
            'user_id': user_id,
            'date': date,
            **hours,
            'reason': reason
        })

busy_slot_df = pd.DataFrame(busy_slots)

# 调整列顺序
column_order = ['user_id', 'date'] + hours_columns + ['reason']
busy_slot_df = busy_slot_df[column_order]


'''
测试数据结束
'''

# MySQL连接配置
def get_db_connection():
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

def update_user(user_id, name):
    """更新或插入用户数据"""
    connection = get_db_connection()
    if connection:
        try:
            cursor = connection.cursor()
            # 检查用户是否存在
            cursor.execute("SELECT user_id FROM user WHERE user_id = %s", (user_id,))
            if cursor.fetchone():
                # 更新现有用户
                cursor.execute("UPDATE user SET NAME = %s WHERE user_id = %s", (name, user_id))
            else:
                # 插入新用户
                cursor.execute("INSERT INTO user (user_id, NAME) VALUES (%s, %s)", (user_id, name))
            connection.commit()
        except Error as e:
            print(f"Error updating user: {e}")
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

def update_user_group(user_id, group_id):
    """更新用户和组的关联关系"""
    connection = get_db_connection()
    if connection:
        try:
            cursor = connection.cursor()
            # 检查关联是否已存在
            cursor.execute("SELECT * FROM user_group WHERE user_id = %s AND group_id = %s", 
                         (user_id, group_id))
            if not cursor.fetchone():
                # 如果关联不存在，则插入新关联
                cursor.execute("INSERT INTO user_group (user_id, group_id) VALUES (%s, %s)", 
                             (user_id, group_id))
                connection.commit()
        except Error as e:
            print(f"Error updating user-group relationship: {e}")
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

def update_group(group_id, name):
    """更新或插入组数据"""
    connection = get_db_connection()
    if connection:
        try:
            cursor = connection.cursor()
            # 检查组是否存在
            cursor.execute("SELECT group_id FROM `group` WHERE group_id = %s", (group_id,))
            if cursor.fetchone():
                # 更新现有组
                cursor.execute("UPDATE `group` SET NAME = %s WHERE group_id = %s", (name, group_id))
            else:
                # 插入新组
                cursor.execute("INSERT INTO `group` (group_id, NAME) VALUES (%s, %s)", (group_id, name))
            connection.commit()
        except Error as e:
            print(f"Error updating group: {e}")
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

def update_busy_slot(user_id, date, hours, reason):
    """更新或插入用户忙时数据"""
    connection = get_db_connection()
    if connection:
        try:
            cursor = connection.cursor()
            # 检查该日期是否已有记录
            cursor.execute("SELECT * FROM user_busy_slot WHERE user_id = %s AND date = %s", 
                         (user_id, date))
            if cursor.fetchone():
                # 更新现有记录
                update_query = "UPDATE user_busy_slot SET "
                for hour, value in hours.items():
                    update_query += f"{hour} = %s, "
                update_query = update_query.rstrip(", ") + ", reason = %s WHERE user_id = %s AND date = %s"
                
                values = list(hours.values()) + [reason, user_id, date]
                cursor.execute(update_query, values)
            else:
                # 插入新记录
                columns = ['user_id', 'date'] + list(hours.keys()) + ['reason']
                placeholders = ', '.join(['%s'] * len(columns))
                insert_query = f"INSERT INTO user_busy_slot ({', '.join(columns)}) VALUES ({placeholders})"
                
                values = [user_id, date] + list(hours.values()) + [reason]
                cursor.execute(insert_query, values)
            
            connection.commit()
        except Error as e:
            print(f"Error updating busy slot: {e}")
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

if __name__ == "__main__":
    # 先写入组数据
    for _, row in group_df.iterrows():
        update_group(int(row['group_id']), row['NAME'])
        print(f"已添加组: {row['NAME']}")

    # 写入用户数据
    for _, row in user_df.iterrows():
        update_user(int(row['user_id']), row['NAME'])
        print(f"已添加用户: {row['NAME']}")

    # 写入用户-组关系数据
    for _, row in user_group_df.iterrows():
        update_user_group(int(row['user_id']), int(row['group_id']))
        print(f"已添加用户 {row['user_id']} 到组 {row['group_id']}")

    # 写入用户忙时数据
    for _, row in busy_slot_df.iterrows():
        # 提取小时数据
        hours = {col: int(row[col]) for col in hours_columns}
        update_busy_slot(
            user_id=int(row['user_id']),
            date=row['date'],
            hours=hours,
            reason=row['reason']
        )
        print(f"已添加用户 {row['user_id']} 在 {row['date']} 的忙时数据")

    print("所有测试数据已成功写入数据库！")