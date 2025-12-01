#!/usr/bin/env python3
# _*_ coding:utf-8 _*_

import os
import sys
import json
import sqlite3
import threading
from datetime import datetime
from contextlib import contextmanager
from flask import Flask, request, jsonify

# 导入父目录的依赖
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)
from telecom_class import Telecom

# 使用线程本地存储，为每个线程创建独立的 Telecom 实例，支持高并发
_thread_local = threading.local()

# 数据库文件路径
DB_PATH = os.environ.get("DB_PATH", "./config/login_info.db")
DB_LOCK = threading.Lock()


def get_telecom_instance():
    """获取当前线程的 Telecom 实例"""
    if not hasattr(_thread_local, 'telecom'):
        _thread_local.telecom = Telecom()
    return _thread_local.telecom


def get_db_connection():
    """获取数据库连接，使用线程本地存储确保线程安全"""
    if not hasattr(_thread_local, 'db_conn'):
        _thread_local.db_conn = sqlite3.connect(
            DB_PATH,
            check_same_thread=False,
            timeout=10.0
        )
        _thread_local.db_conn.row_factory = sqlite3.Row
        # 启用 WAL 模式以提高并发性能
        _thread_local.db_conn.execute("PRAGMA journal_mode=WAL")
        _thread_local.db_conn.execute("PRAGMA synchronous=NORMAL")
        _thread_local.db_conn.execute("PRAGMA busy_timeout=5000")
    return _thread_local.db_conn


def init_database():
    """初始化数据库表结构"""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS login_info (
            phonenum TEXT PRIMARY KEY,
            phoneNbr TEXT,
            token TEXT,
            userId TEXT,
            userType TEXT,
            isDirectCon TEXT,
            phoneType TEXT,
            provinceCode TEXT,
            cityCode TEXT,
            provinceName TEXT,
            cityName TEXT,
            areaCode TEXT,
            nativeNet TEXT,
            netType TEXT,
            accessToken TEXT,
            memberType TEXT,
            operator TEXT,
            isNewUser TEXT,
            password TEXT,
            createTime TEXT,
            login_data TEXT
        )
    """)
    
    conn.commit()


def load_login_info():
    """从数据库加载所有登录信息"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM login_info")
        rows = cursor.fetchall()
        
        login_info = {}
        for row in rows:
            phonenum = row['phonenum']
            login_info[phonenum] = {
                'phoneNbr': row['phoneNbr'],
                'token': row['token'],
                'userId': row['userId'],
                'userType': row['userType'],
                'isDirectCon': row['isDirectCon'],
                'phoneType': row['phoneType'],
                'provinceCode': row['provinceCode'],
                'cityCode': row['cityCode'],
                'provinceName': row['provinceName'],
                'cityName': row['cityName'],
                'areaCode': row['areaCode'],
                'nativeNet': row['nativeNet'],
                'netType': row['netType'],
                'accessToken': row['accessToken'],
                'memberType': row['memberType'],
                'operator': row['operator'],
                'isNewUser': row['isNewUser'],
                'phonenum': row['phonenum'],
                'password': row['password'],
                'createTime': row['createTime']
            }
        return login_info
    except Exception as e:
        print(f"Error loading login info: {e}")
        return {}


def get_login_info(phonenum):
    """从数据库获取指定手机号的登录信息"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM login_info WHERE phonenum = ?", (phonenum,))
        row = cursor.fetchone()
        
        if row:
            return {
                'phoneNbr': row['phoneNbr'],
                'token': row['token'],
                'userId': row['userId'],
                'userType': row['userType'],
                'isDirectCon': row['isDirectCon'],
                'phoneType': row['phoneType'],
                'provinceCode': row['provinceCode'],
                'cityCode': row['cityCode'],
                'provinceName': row['provinceName'],
                'cityName': row['cityName'],
                'areaCode': row['areaCode'],
                'nativeNet': row['nativeNet'],
                'netType': row['netType'],
                'accessToken': row['accessToken'],
                'memberType': row['memberType'],
                'operator': row['operator'],
                'isNewUser': row['isNewUser'],
                'phonenum': row['phonenum'],
                'password': row['password'],
                'createTime': row['createTime']
            }
        return None
    except Exception as e:
        print(f"Error getting login info: {e}")
        return None


def save_login_info(phonenum, login_data, password=None):
    """保存登录信息到数据库"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 准备数据
        login_success = login_data.get("responseData", {}).get("data", {}).get("loginSuccessResult", {})
        
        # 如果没有传入 password，尝试从 request 获取
        if password is None:
            try:
                if request.method == "POST":
                    password = request.get_json().get("password")
                else:
                    password = request.args.get("password")
            except:
                pass
        
        cursor.execute("""
            INSERT OR REPLACE INTO login_info (
                phonenum, phoneNbr, token, userId, userType, isDirectCon,
                phoneType, provinceCode, cityCode, provinceName, cityName,
                areaCode, nativeNet, netType, accessToken, memberType,
                operator, isNewUser, password, createTime, login_data
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            phonenum,
            login_success.get("phoneNbr"),
            login_success.get("token"),
            login_success.get("userId"),
            login_success.get("userType"),
            login_success.get("isDirectCon"),
            login_success.get("phoneType"),
            login_success.get("provinceCode"),
            login_success.get("cityCode"),
            login_success.get("provinceName"),
            login_success.get("cityName"),
            login_success.get("areaCode"),
            login_success.get("nativeNet"),
            login_success.get("netType"),
            login_success.get("accessToken"),
            login_success.get("memberType"),
            login_success.get("operator"),
            login_success.get("isNewUser"),
            password,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            json.dumps(login_data, ensure_ascii=False)
        ))
        
        conn.commit()
    except Exception as e:
        print(f"Error saving login info: {e}")
        try:
            conn.rollback()
        except:
            pass

app = Flask(__name__)
app.json.ensure_ascii = False
app.json.sort_keys = False

# 初始化数据库
init_database()


@app.route("/login", methods=["POST", "GET"])
def login():
    """登录接口"""
    data = request.get_json() if request.method == "POST" else request.args
    phonenum, password = data.get("phonenum"), data.get("password")
    if not phonenum or not password:
        return jsonify({"message": "手机号和密码不能为空"}), 400

    telecom = get_telecom_instance()
    login_result = telecom.do_login(phonenum, password)
    if login_result.get("responseData", {}).get("resultCode") == "0000":
        save_login_info(phonenum, login_result, password)
        return jsonify(login_result), 200
    else:
        return jsonify(login_result), 400


def query_data(method_name, **kwargs):
    """
    查询数据，如果本地没有登录信息或密码不匹配，则尝试登录后再查询
    method_name: Telecom 类的方法名（字符串）
    """
    data = request.get_json() if request.method == "POST" else request.args
    phonenum, password = data.get("phonenum"), data.get("password")
    
    # 从数据库获取登录信息（快速读取，支持高并发）
    login_info = get_login_info(phonenum)
    telecom = get_telecom_instance()
    query_func = getattr(telecom, method_name)
    
    # 检查登录信息是否有效
    if (
        login_info
        and login_info.get("phonenum") == phonenum
        and login_info.get("password") == password
    ):
        telecom.set_login_info(login_info)
        result = query_func(**kwargs)
        if result.get("responseData"):
            return jsonify(result), 200
        elif result.get("headerInfos", {}).get("code") != "X201":
            # X201 = token 过期
            return jsonify(result), 400
    
    # 重新登录（写入操作，会排队但不会阻塞读取）
    data = request.get_json() if request.method == "POST" else request.args
    phonenum, password = data.get("phonenum"), data.get("password")
    
    telecom = get_telecom_instance()
    login_result = telecom.do_login(phonenum, password)
    
    if login_result.get("responseData", {}).get("resultCode") == "0000":
        save_login_info(phonenum, login_result, password)
        login_success = login_result["responseData"]["data"]["loginSuccessResult"]
        login_success["phonenum"] = phonenum
        login_success["password"] = password
        telecom.set_login_info(login_success)
        result = query_func(**kwargs)
        if result.get("responseData"):
            return jsonify(result), 200
        else:
            return jsonify(result), 400
    else:
        return jsonify(login_result), 400


@app.route("/qryImportantData", methods=["POST", "GET"])
def qry_important_data():
    """查询基本数据接口"""
    return query_data("qry_important_data")


@app.route("/userFluxPackage", methods=["POST", "GET"])
def user_flux_package():
    """查询流量包接口"""
    return query_data("user_flux_package")


@app.route("/qryShareUsage", methods=["POST", "GET"])
def qry_share_usage():
    """查询共享用量接口"""
    if request.method == "POST":
        data = request.get_json() or {}
    else:
        data = request.args
    return query_data("qry_share_usage", billing_cycle=data.get("billing_cycle"))


@app.route("/summary", methods=["POST", "GET"])
def summary():
    """查询基本数据简化接口"""
    important_data, status_code = query_data("qry_important_data")
    if status_code == 200:
        telecom = get_telecom_instance()
        data = telecom.to_summary(
            json.loads(important_data.data)["responseData"]["data"]
        )
        return jsonify(data), 200
    else:
        return important_data, status_code


if __name__ == "__main__":
    # 配置 Flask 以支持多线程（提高并发能力）
    # 注意：生产环境建议使用 gunicorn 或 uwsgi 等 WSGI 服务器
    app.run(
        debug=os.environ.get("DEBUG", False),
        host="0.0.0.0",
        port=10000,
        threaded=True,  # 启用多线程支持
        processes=1     # 单进程，多线程模式
    )
