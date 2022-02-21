from flask import request, flash, jsonify, session, abort

import bcrypt

import conf
from app.service.delivery import delivery
from utils import required_login

cursor = conf.db.cursor()


@delivery.route('/delivery/register', methods=['POST'])
def register():
    delivery_msg = request.form
    if (not delivery_msg['name']) or (not delivery_msg['password']):
        flash("请输入姓名或密码")
        abort(404)
    if len(delivery_msg['telephone']) != 11 or (not delivery_msg['telephone'].isdigit()):
        flash("请输入正确的电话号码")
        abort(404)
    try:
        sql = f"insert into delivery (name, telephone, working, income, password) " \
              f"values ('{delivery_msg['name']}', '{delivery_msg['telephone']}', ' '," \
              f" 0, '{bcrypt.hashpw(delivery_msg['password'].encode(), bcrypt.gensalt()).decode()}')"
        cursor.execute(sql)
        conf.db.commit()
        return jsonify({
            "status": 200,
            "msg": "ok",
            "data": [delivery_msg['name'], delivery_msg['telephone']]
        })
    except Exception as e:
        print("failed as %s" % e)
        return jsonify({
            "status": 500
        })


@delivery.route('/receive/<int:orderId>', methods=['POST'])
@required_login.auth.login_required
def receive(orderId):
    delivery_id = session['userId']
    sql = f"select shop_name, shop_address, username, user_address, delivery_time from `order` " \
          f"where id = {orderId}"
    try:
        cursor.execute(sql)
        result = cursor.fetchall()
        # work = {
        #     "shop": result[0][0],
        #     "send_to": result[0][1],
        #     "receiver": result[0][2],
        #     "receive_address": result[0][3],
        #     "receive_time": result[0][4] + " + 1h"
        #     }
        work = "shop: " + result[0][0] + ",send_to:" + result[0][1] + ",receive:" + result[0][2] +\
               ",receive_add" + result[0][3] + ",send_time" + result[0][4] + "+ 1h\n"
        commit = f"update delivery set working = CONCAT(working, '{work}') where id = {delivery_id}"
        cursor.execute(commit)
        change_status = f"update `order` set status = 1 where id = {orderId}"
        cursor.execute(change_status)
        conf.db.commit()
        return jsonify({
            "status": 200,
            "msg:": "ok",
            "data": work
        })
    except Exception as e:
        print("failed as %s" % e)
        return jsonify({"status": 500})


@delivery.route('/income/<int:orderId>', methods=['POST'])
@required_login.auth.login_required
def income(orderId):
    sql = f"select income from `order` where id = {orderId}"
    try:
        cursor.execute(sql)
        result = cursor.fetchone()
        incomes = f"update delivery set income = income + {result[0]}"
        cursor.execute(incomes)
        delete = f"delete from `order` where id = {orderId}"
        cursor.execute(delete)
        conf.db.commit()
        return jsonify({
                "status": 200,
                "msg": "ok",
                'income': result[0]
            })
    except Exception as e:
        print("failed as %s" % e)
        return jsonify({"status": 500})
