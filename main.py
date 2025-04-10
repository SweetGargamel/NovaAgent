from flask import Flask, render_template, request, jsonify
import mysql.connector
from conf import DB_CONFIG
from datetime import datetime, timedelta

app = Flask(__name__)

def get_db_connection():
    """获取数据库连接"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except mysql.connector.Error as err:
        print(f"数据库连接错误: {err}")
        return None

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/query')
def query():
    return render_template('query.html')

@app.route('/api/groups')
def get_groups():
    """获取所有群组信息"""
    conn = get_db_connection()
    if conn is None:
        return jsonify([])
    
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT group_id, name FROM `group`")
        groups = cursor.fetchall()
        return jsonify(groups)
    except mysql.connector.Error as err:
        print(f"查询群组信息错误: {err}")
        return jsonify([])
    finally:
        if conn:
            conn.close()

@app.route('/api/group_users/<int:group_id>')
def get_group_users(group_id):
    """获取指定群组的用户信息"""
    conn = get_db_connection()
    if conn is None:
        return jsonify([])
    
    try:
        cursor = conn.cursor(dictionary=True)
        query = """
        SELECT u.user_id, u.name 
        FROM user u
        JOIN user_group ug ON u.user_id = ug.user_id
        WHERE ug.group_id = %s
        """
        cursor.execute(query, (group_id,))
        users = cursor.fetchall()
        return jsonify(users)
    except mysql.connector.Error as err:
        print(f"查询群组用户错误: {err}")
        return jsonify([])
    finally:
        if conn:
            conn.close()

@app.route('/api/query_time', methods=['POST'])
def query_time():
    """查询时间安排"""
    data = request.json
    group_id = data.get('group_id')
    start_date = datetime.strptime(data.get('start_date'), '%Y-%m-%d').date()
    end_date = datetime.strptime(data.get('end_date'), '%Y-%m-%d').date()
    
    conn = get_db_connection()
    if conn is None:
        return jsonify([])
    
    try:
        cursor = conn.cursor(dictionary=True)
        # 获取群组中的所有用户
        user_query = """
        SELECT u.user_id, u.name
        FROM user u
        JOIN user_group ug ON u.user_id = ug.user_id
        WHERE ug.group_id = %s
        """
        cursor.execute(user_query, (group_id,))
        users = cursor.fetchall()
        user_ids = [user['user_id'] for user in users]
        user_names = {user['user_id']: user['name'] for user in users}
        
        if not user_ids:
            return jsonify([])

        # 获取时间段数据
        placeholders = ', '.join(['%s'] * len(user_ids))
        time_query = f"""
        SELECT user_id, date, h8, h9, h10, h11, h12,
               h13, h14, h15, h16, h17, h18, h19,
               h20, h21, reason
        FROM user_busy_slot
        WHERE user_id IN ({placeholders}) AND date BETWEEN %s AND %s
        """
        query_params = user_ids + [start_date, end_date]
        cursor.execute(time_query, query_params)
        time_slots = cursor.fetchall()

        # 按照query.py的逻辑处理数据
        day_length = 14
        days = (end_date - start_date).days + 1
        Time = [[0 for _ in range(day_length)] for _ in range(days)]
        main_person = [1]  # 主要人员ID

        # 构建时间槽字典，方便查找
        time_slot_dict = {}
        for slot in time_slots:
            key = (slot['user_id'], slot['date'])
            time_slot_dict[key] = [slot[f'h{i}'] for i in range(8, 22)]

        # 计算每个时间段的权重
        current_date = start_date
        for i in range(days):
            for p in user_ids:
                key = (p, current_date)
                T = time_slot_dict.get(key, [0] * day_length)
                val = 1e9 if p in main_person else 1
                for t in range(day_length):
                    # 修改权重计算：空闲时记1，忙碌时记0
                    Time[i][t] += (0 if T[t] else 1) * val
            current_date += timedelta(days=1)

        # 生成位置权重对
        val_with_position = []
        for i in range(days):
            for t in range(day_length):
                val_with_position.append((Time[i][t], (i, t)))

        # 按权重排序（空闲人数多的排在前面）
        val_with_position.sort(key=lambda x: x[0], reverse=True)

        # 生成结果
        results = []
        for weight, (i, j) in val_with_position:
            current_date = start_date + timedelta(days=i)
            busy_users = []
            free_count = 0

            for user_id in user_ids:
                key = (user_id, current_date)
                time_data = time_slot_dict.get(key, [0] * day_length)
                if time_data[j]:  # 忙碌
                    busy_users.append(user_names[user_id])
                else:  # 空闲
                    free_count += 1

            results.append({
                'date': current_date.strftime('%Y-%m-%d'),
                'hour': j + 8,
                'free_count': free_count,
                'total_count': len(user_ids),
                'busy_users': busy_users
            })

        return jsonify(results)
        
    except mysql.connector.Error as err:
        print(f"查询时间安排错误: {err}")
        return jsonify({'error': str(err)}), 500
    finally:
        if conn:
            conn.close()

@app.route('/update')
def update():
    return render_template('update.html')

if __name__ == '__main__':
    app.run(debug=True)
