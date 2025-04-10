from datetime import date, timedelta
import pandas as pd
import mysql.connector
from conf import DB_CONFIG

# # 用户表 user
# user_df = pd.DataFrame({
#     "user_id": [1, 2, 3],
#     "name": ["Alice", "Bob", "Charlie"]
# })

# # 用户忙碌时段表 user_busy_slot
# busy_slot_data = [
#     (1, date(2023, 10, 1), 0,1,1,1,0,0,0,0,0,1,1,1,0,0,"上课"),
#     (1, date(2023, 10, 2), 0,0,0,0,1,1,1,1,1,0,0,0,0,0,"班会"),
#     (2, date(2023, 10, 1), 1,1,0,0,0,1,1,1,1,0,0,0,0,0,"学习"),
#     (3, date(2023, 10, 3), 0,0,0,0,0,0,0,0,0,0,0,0,0,0,"旅游")
# ]

# busy_slot_df = pd.DataFrame(
#     busy_slot_data,
#     columns=[
#         "user_id", "date",
#         "h8", "h9", "h10", "h11", "h12",#h8表示从8-9是否有空，后面类推
#         "h13", "h14", "h15", "h16", "h17",
#         "h18", "h19", "h20", "h21","reason"
#     ]
# )


# 上面是测试数据

def get_db_connection():
    """获取数据库连接"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except mysql.connector.Error as err:
        print(f"数据库连接错误: {err}")
        return None

def get_user():
    """从数据库获取用户信息"""
    conn = get_db_connection()
    
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT user_id, name FROM user")
        rows = cursor.fetchall()
        df = pd.DataFrame(rows, columns=["user_id", "name"])
        return df
    except mysql.connector.Error as err:
        print(f"查询用户信息错误: {err}")
    finally:
        if conn:
            conn.close()

def get_time(start, end):
    """从数据库获取指定日期范围内的忙碌时段信息"""
    conn = get_db_connection()
    
    try:
        cursor = conn.cursor()
        query = """
        SELECT user_id, date, h8, h9, h10, h11, h12, h13, h14, h15, h16, h17, h18, h19, h20, h21, reason 
        FROM user_busy_slot 
        WHERE date BETWEEN %s AND %s
        ORDER BY date, user_id
        """
        cursor.execute(query, (start, end))
        rows = cursor.fetchall()
        return rows
    except mysql.connector.Error as err:
        print(f"查询时间信息错误: {err}")
    finally:
        if conn:
            conn.close()

user_df=get_user()

def get_person():
    return [1,2,3]

def get_day():
    start_date = date(2025, 4, 10)  # 示例起始日期
    end_date = date(2025, 4, 12)   # 示例结束日期
    return start_date, end_date

def get_name(id):
    for index, row in user_df.iterrows():
        if(row.iloc[0]==id):
            return row.iloc[1]
    print(f"未找到人{id}")
    return "Nan"

def get_main_person():
    return [1]

def get_time1(p, t):
    for tt in time_slot:
        if((tt[0]==p) & (tt[1]==t)):
            return tt[2:]
    print(f"数据库中未找到{get_name(p)}在{t}的时间安排,默认无时间")
    return [0 for _ in range(day_length)]

day_length = 14
dayL, dayR = get_day()
time_slot = get_time(dayL,dayR )

Time = [[0 for _ in range(day_length)] for _ in range((dayR - dayL).days + 1)]
Person = get_person()
Main_person = get_main_person()

current_date = dayL
for i in range((dayR - dayL).days + 1):
    for p in Person:
        T = get_time1(p,current_date)
        val = 1
        if p in Main_person:
            val = 1e9
        for t in range(day_length):
            Time[i][t] = Time[i][t] + T[t] * val
    current_date += timedelta(days=1)

val_with_position = []

for i in range((dayR - dayL).days + 1):
    for t in range(day_length):
        val_with_position.append((Time[i][t], (i, t)))

val_with_position.sort(key=lambda x: x[0], reverse=True)

for x, (i, j) in val_with_position:
    input("按回车继续")
    num=0
    a=[]
    if x != len(Person):
        for p in Person:
            T = get_time1(p,dayL + timedelta(days=i))
            if T[j] == 0:
                a.append(get_name(p))
            else:
                num=num+1
    print(f"时间({dayL+timedelta(days=i)},h{8+j})可有{num}人空闲")
    if(num!=len(Person)):
        print(f"{a}无法参会")