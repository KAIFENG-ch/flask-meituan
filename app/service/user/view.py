import logging
import os.path
import random
import smtplib
import time
import bcrypt
from email.mime.text import MIMEText

from flask import request, abort, jsonify, session, render_template, flash

import conf
from pkg import code
from utils import file_process
from utils import required_login
from app.service.user import user


user.secret_key = "affedasafafqwe"

cursor = conf.db.cursor()


@user.route('/user/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        users = request.form
        if not users['name'] or not users['password'] or not users['mail']:
            abort(400)
        if not users['sex']:
            users['sex'] = '未知'
        if not users['birthday']:
            users['birthday'] = '未知'
        if not users['address']:
            users['address'] = '外星'
        sql = "INSERT INTO user(name, password, sex, birthday, address, mail) VALUES " \
              "('%s', '%s', '%s', '%s', '%s', '%s')" % \
              (users['name'], bcrypt.hashpw(users['password'].encode(), bcrypt.gensalt()).decode(), users['sex'],
               users['birthday'], users['address'], users['mail'])
        try:
            cursor.execute(sql)
            conf.commit()
        except AttributeError:
            conf.e()
        return jsonify({
            "status": code.SUCCESS,
            "msg": "ok",
            "data": [users['name'], users['sex'], users['birthday'], users['address'], users['mail']]
        })
    return render_template('app/templates/register.html')


@user.route("/")
def index():
    if 'username' in session:
        return f'Logged in as {session["username"]}'
    return "you are not logged in"


@user.route("/user/logout", methods=['GET'])
@required_login.auth.login_required
def logout():
    session.clear()
    return render_template('app/templates/quitLogin.html')


@user.route("/user/login/cancel", methods=['DELETE'])
@required_login.auth.login_required
def cancel():
    sql = f"delete from user where name = '{session['username']}'"
    cursor.execute(sql)
    conf.db.commit()
    session.clear()
    return jsonify({
        "status": 200,
        "msg": "删除成功！"
    })


@user.route("/user/login/headFile", methods=['POST'])
@required_login.auth.login_required
def head_file():
    username = session['username']

    file_dir = os.path.join(file_process.basedir, 'upload')  # 拼接成合法文件夹地址
    if not os.path.exists(file_dir):
        os.makedirs(file_dir)
    f = request.files['myfile']
    new_path = file_process.photo_process(f, file_dir)
    try:
        sql = f"update user set headPhoto = '{new_path}' where name = '{username}'"
        cursor.execute(sql)
        conf.db.commit()
    except Exception as e:
        print("Failed%s" % e)
    return jsonify({"status": 200, "msg": "上传成功"})


@user.route("/user/login/verify", methods=['POST'])
@required_login.auth.login_required
def verify():
    username = session['username']
    old_pwd = request.form['oldpwd']

    sql = f"select password, mail from user where name = '{username}'"
    cursor.execute(sql)
    result = list(cursor.fetchall())
    u = list(filter(lambda users: bcrypt.checkpw(old_pwd.encode(), users[0].encode()), result))
    if not u:
        flash('请输入正确的密码')
    s = ''
    for i in range(6):
        num = random.randint(0, 9)
        s = s + str(num)
    msg = MIMEText(f'验证码：{s}')
    msg["subject"] = "修改密码验证"
    msg["from"] = "美团"
    from_addr = conf.x['EMAIL']['addr']
    password = conf.x['EMAIL']['password']
    smtp_server = 'smtp.qq.com'
    to_addr = [result[0][1]]
    try:
        server = smtplib.SMTP_SSL(smtp_server, 465, timeout=2)
        server.login(from_addr, password)
        server.sendmail(from_addr, to_addr, msg.as_string())
        server.quit()
        logging.info("EMAIL SUCCESS")
        session['verify'] = s
        return render_template('app/templates/changePwd.html')
    except Exception as e:
        if e is None:
            logging.error("EMAIL FAIL")
            return {"code": "200", "info": "success"}
        else:
            print('Failed:%s' % e)
            return {"code": "500", "info": "fail"}


@user.route('/user/login/verify/change', methods=['POST'])
@required_login.auth.login_required
def change():
    username = session['username']
    verify_code = session.get('verify')
    if not verify_code:
        abort(400)
    verify_in = request.form['验证码']
    new_pwd = request.form['新密码']
    new_pwd_again = request.form['再次输入新密码']
    if verify_in != verify_code or new_pwd != new_pwd_again:
        abort(404)
    try:
        sql = f"update user set password = '{bcrypt.hashpw(new_pwd.encode(), bcrypt.gensalt()).decode()}'" \
              f" where name = '{username}'"
        cursor.execute(sql)
        conf.db.commit()
        session.clear()
        return jsonify({
            "status": 200,
            "msg": "修改成功"
        })
    except Exception as e:
        print('Failed:%s' % e)
        return jsonify({"status": 500})


@user.route('/user/login/followers/<int:Id>', methods=['POST'])
@required_login.auth.login_required
def ListFollowing(Id):
    username = session['username']
    sql_follower = f"select name from user where ID = {Id}"
    cursor.execute(sql_follower)
    result = cursor.fetchone()
    method = request.args.get('method')
    if method == 'follow':
        conf.r.zadd(result[0], {username: session['userId']})
        return jsonify({
            "msg": "关注成功！",
            "His follower": conf.r.zcard(result[0][0]) + 1
        })
    elif method == 'delete':
        conf.r.zrem(result[0][0], username)
        return jsonify({
            "msg": "取关成功！",
            "His follower": conf.r.zcard(result[0][0])
        })
    else:
        abort(400)


@user.route('/user/login/followerList')
@required_login.auth.login_required
def followList():
    username = session['username']
    return jsonify({
        "follower list": conf.r.zrange(username, 0, -1, withscores=True)
    })


@user.route('/user/login/likes/<int:shopId>', methods=['POST'])
@required_login.auth.login_required
def likes(shopId):
    method = request.args.get('method', None)
    sql = f"select * from shop where ID = {shopId}"
    try:
        cursor.execute(sql)
        result = list(cursor.fetchall())
        shopname = result[0][1]
        conf.r.incr(shopname + method)
        return jsonify({
            "msg": method + " success!",
            "status": 200,
            f"{method}": conf.r.get(shopname + method)
        })
    except Exception as e:
        print("Failed %s" % e)


time_now = time.localtime(int(time.time()))
dt = time.strftime("%Y-%m-%d %H:%M:%S", time_now)


@user.route('/user/login/comment/<int:shop_Id>', methods=['POST'])
@required_login.auth.login_required
def comment(shop_Id):
    username = session['username']
    user_id = session['userId']
    msg = request.form['message']

    sql = f"insert into comments (shopId, user, userId, message, times) values " \
          f"({shop_Id}, '{username}', {user_id}, '{msg}', '{dt}')"
    try:
        cursor.execute(sql)
        conf.db.commit()
        return jsonify({
            "status": 200,
            "msg": 'ok',
            "data": msg
        })
    except Exception as e:
        print("failed as %s" % e)
        return jsonify({'status': 500})


@user.route('/user/login/comment/childComment/<int:shop_Id>/<int:parent_Id>', methods=['POST'])
@required_login.auth.login_required
def childComment(shop_Id, parent_Id):
    username = session['username']
    user_id = session['userId']
    msg = request.form['message']
    sql = f"insert into comments (shopId, user, userId, message, parentId, times) " \
          f"values ({shop_Id}, '{username}', {user_id}, '{msg}', {parent_Id}, '{dt}')"
    try:
        cursor.execute(sql)
        conf.db.commit()
        return jsonify({
            "status": 200,
            "msg": 'ok',
            "data": msg
        })
    except Exception as e:
        print("failed as %s" % e)
        return jsonify({'status': 500})


@user.route('/user/login/query/commodity')
@required_login.auth.login_required
def queryCommodity():
    query = request.form['find']
    sql = f"select ID, shopId, name, price, message, photo, video from commodity where name" \
          f" like '{query}' or message like '{query}'"
    try:
        cursor.execute(sql)
        result = cursor.fetchall()
        return jsonify({
            "status": code.SUCCESS,
            "msg": "ok",
            "data": result
        })
    except Exception as e:
        print("failed as %s" % e)
        return jsonify({
            "status": code.ERROR
        })


@user.route('/user/login/query/shop')
def queryShop():
    query = request.form['find']
    sql = f"select name, address from shop where name like '{query}' or address like '{query}'"
    try:
        cursor.execute(sql)
        result = cursor.fetchall()
        return jsonify({
            "status": 200,
            "msg": "ok",
            "data": result
        })
    except Exception as e:
        print("failed as %d" % e)
        return jsonify({"status": 500})


@user.route('/user/login/order/<int:shop_id>/<int:commodity_id>', methods=['POST'])
@required_login.auth.login_required
def order(shop_id, commodity_id):
    address = request.form['address']
    shop_query = f"select name, address from shop where ID = {shop_id}"
    cursor.execute(shop_query)
    shop_result = cursor.fetchone()
    commodity_query = f"select name, price from commodity where ID = {commodity_id}"
    cursor.execute(commodity_query)
    commodity_result = cursor.fetchone()
    sql = f"insert into `order` (commodity_id, commodity_name, shop_id, shop_name," \
          f" shop_address, user_id, username, income, delivery_time, user_address, status) values " \
          f"({commodity_id}, '{commodity_result[0]}', {shop_id}, '{shop_result[0]}', '{shop_result[1]}'," \
          f"{session['userId']}, '{session['username']}', {commodity_result[1] * 0.1}, " \
          f"'{str(dt)}', '{address}', 0)"
    try:
        cursor.execute(sql)
        conf.db.commit()
        return jsonify({
            "status": 200,
            "msg": "ok",
        })
    except Exception as e:
        print("failed as %s" % e)
        return jsonify({"status": 500})
