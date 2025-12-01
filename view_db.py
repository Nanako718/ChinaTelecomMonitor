#!/usr/bin/env python3
# _*_ coding:utf-8 _*_
"""
简单的数据库查看工具
用于查看 login_info.db 中的数据
"""

import sqlite3
import json
import os
import sys

DB_PATH = os.environ.get("DB_PATH", "./config/login_info.db")


def view_all_users():
    """查看所有用户信息"""
    if not os.path.exists(DB_PATH):
        print(f"数据库文件不存在: {DB_PATH}")
        return
    
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM login_info")
        rows = cursor.fetchall()
        
        if not rows:
            print("数据库中没有用户信息")
            return
        
        print(f"\n找到 {len(rows)} 个用户:\n")
        print("=" * 80)
        
        for i, row in enumerate(rows, 1):
            print(f"\n【用户 {i}】")
            print(f"  手机号: {row['phonenum']}")
            print(f"  用户ID: {row['userId']}")
            print(f"  省份: {row['provinceName']}")
            print(f"  城市: {row['cityName']}")
            print(f"  创建时间: {row['createTime']}")
            print(f"  用户类型: {row['userType']}")
            print(f"  省份代码: {row['provinceCode']}")
            print(f"  城市代码: {row['cityCode']}")
            print("-" * 80)
        
        conn.close()
        
    except Exception as e:
        print(f"读取数据库出错: {e}")


def view_user_detail(phonenum):
    """查看指定用户的详细信息"""
    if not os.path.exists(DB_PATH):
        print(f"数据库文件不存在: {DB_PATH}")
        return
    
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM login_info WHERE phonenum = ?", (phonenum,))
        row = cursor.fetchone()
        
        if not row:
            print(f"未找到手机号 {phonenum} 的用户信息")
            return
        
        print(f"\n【用户详细信息 - {phonenum}】")
        print("=" * 80)
        for key in row.keys():
            if key == 'login_data':
                # login_data 是 JSON 字符串，格式化显示
                try:
                    data = json.loads(row[key])
                    print(f"\n{key}:")
                    print(json.dumps(data, ensure_ascii=False, indent=2))
                except:
                    print(f"{key}: {row[key]}")
            else:
                print(f"{key}: {row[key]}")
        print("=" * 80)
        
        conn.close()
        
    except Exception as e:
        print(f"读取数据库出错: {e}")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        # 查看指定用户
        phonenum = sys.argv[1]
        view_user_detail(phonenum)
    else:
        # 查看所有用户
        view_all_users()

