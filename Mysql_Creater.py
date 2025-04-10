# 辅助工具。在mysql中创建表。 不是主程序的一部分

import mysql.connector
from mysql.connector import Error
from conf import DB_CONFIG
def create_tables():
    try:
        # 连接到MySQL数据库
        connection = mysql.connector.connect(
            host=DB_CONFIG['host'],
            user=DB_CONFIG['user'],  # 请替换为你的用户名
            password=DB_CONFIG['password'],  # 请替换为你的密码
            database=DB_CONFIG['database']  # 请替换为你的数据库名  
        )
        
        if connection.is_connected():
            cursor = connection.cursor()
            
            # 创建user表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS `user` (
                    user_id INT PRIMARY KEY AUTO_INCREMENT,
                    NAME VARCHAR(255) NOT NULL
                )
            """)
            
            # 创建group表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS `group` (
                    group_id INT PRIMARY KEY AUTO_INCREMENT,
                    NAME VARCHAR(255) NOT NULL
                )
            """)
            
            # 创建user_group表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_group (
                    user_id INT,
                    group_id INT,
                    PRIMARY KEY (user_id, group_id),
                    FOREIGN KEY (user_id) REFERENCES `user`(user_id),
                    FOREIGN KEY (group_id) REFERENCES `group`(group_id)
                )
            """)
            
            # 创建user_busy_slot表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_busy_slot (
                    user_id INT,
                    `date` DATE,
                    h8 TINYINT(1),
                    h9 TINYINT(1),
                    h10 TINYINT(1),
                    h11 TINYINT(1),
                    h12 TINYINT(1),
                    h13 TINYINT(1),
                    h14 TINYINT(1),
                    h15 TINYINT(1),
                    h16 TINYINT(1),
                    h17 TINYINT(1),
                    h18 TINYINT(1),
                    h19 TINYINT(1),
                    h20 TINYINT(1),
                    h21 TINYINT(1),
                    reason CHAR(255),
                    PRIMARY KEY (user_id, `date`),
                    FOREIGN KEY (user_id) REFERENCES `user`(user_id)
                )
            """)
            
            print("所有表创建成功！")
            
    except Error as e:
        print(f"发生错误: {e}")
        
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL连接已关闭")

if __name__ == "__main__":
    create_tables()