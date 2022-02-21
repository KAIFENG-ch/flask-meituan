from flask import request, flash, render_template, session, make_response, jsonify

import bcrypt

import conf
from pkg import code
from utils import util
from utils import JWT

cursor = conf.db.cursor()

identity = ['user', 'shop', 'delivery', 'admin']


@util.route('/login/<int:ident>', methods=['GET', 'POST'])
def login(ident):
    if request.method == 'POST':
        username = request.form['name']
        password = request.form['password']
        if (not username) or (not password):
            flash('账号密码不许为空！')
            return render_template('app/templates/login.html')
        try:
            sql = f"select password, ID from {identity[ident]} where name = '{username}'"
            cursor.execute(sql)
            result = list(cursor.fetchall())
            if not result:
                flash('用户名错误！')
                return render_template('app/templates/loginFail.html')
            u = list(filter(lambda pwd: bcrypt.checkpw(password.encode(), pwd[0].encode()), result))
            if len(u) != 1:
                flash('密码错误！')
                return render_template('app/templates/loginFail.html')
            token = JWT.create_token(username)
            session['userId'] = u[0][1]
            session['username'] = username
            response = make_response(jsonify({
                "code": code.SUCCESS,
                "status": "已登录",
                "data": {'token': token},
                "msg": f'Logged in as {username}'
            }))
            return response
        except Exception as e:
            print("Failed%s" % e)
    return render_template('app/templates/login.html'), 200
