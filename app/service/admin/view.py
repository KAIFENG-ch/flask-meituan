from flask import request, jsonify

import bcrypt

from app.service.admin import admin
import conf
from utils import required_login

cursor = conf.db.cursor()


@admin.route('/admin/register', methods=['POST'])
def register():
    name = request.form['name']
    password = request.form['password']
    sql = f"insert into admin (name, password) VALUES" \
          f" ('{name}', '{bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()}')"
    try:
        cursor.execute(sql)
        conf.db.commit()
        return jsonify({
            "status": 200,
            "msg": "ok",
            "data": name
        })
    except Exception as e:
        print("failed as %s" % e)
        return jsonify({"status": 500})


MAX_SIZE = 5


def dividePage(pg, sql):
    cursor.execute(sql)
    result = list(cursor.fetchall())
    if pg - 1 > int(len(result) / MAX_SIZE):
        goal = []
    elif pg - 1 == int(len(result) / MAX_SIZE):
        goal = result[(pg - 1) * MAX_SIZE: -1]
    else:
        goal = result[(pg - 1) * MAX_SIZE: pg * MAX_SIZE]
    return goal


@admin.route('/admin/read/user')
@required_login.auth.login_required
def readUser():
    pg = int(request.args.get('page'))
    sql = f'select name, sex, address, ID, birthday, mail, follower from user'
    try:
        goal = dividePage(pg, sql)
        return jsonify({
            "status": 200,
            "msg": 'ok',
            "data": goal
        })
    except Exception as e:
        print("failed as %s" % e)
        return jsonify({'status': 500})


@admin.route('/admin/read/shop')
@required_login.auth.login_required
def readShop():
    pg = int(request.args.get('page'))
    sql = 'select id, name, address from shop'
    try:
        goal = dividePage(pg, sql)
        return jsonify({
            "status": 200,
            "msg": 'ok',
            "data": goal
        })
    except Exception as e:
        print("failed as %s" % e)
        return jsonify({'status': 500})


@admin.route('/admin/read/delivery')
@required_login.auth.login_required
def readDelivery():
    pg = int(request.args.get('page'))
    sql = 'select id, name, telephone from delivery'
    try:
        goal = dividePage(pg, sql)
        return jsonify({
            "status": 200,
            "msg": 'ok',
            "data": goal
        })
    except Exception as e:
        print("failed as %s" % e)
        return jsonify({'status': 500})


@admin.route('/admin/read/comments')
@required_login.auth.login_required
def readComment():
    pg = int(request.args.get('page'))
    sql = 'select ID, shopId, user, userId, message, parentId, cast(times as char) from comments'
    try:
        goal = dividePage(pg, sql)
        return jsonify({
            "status": 200,
            "msg": 'ok',
            "data": goal
        })
    except Exception as e:
        print("failed as %s" % e)
        return jsonify({'status': 500})


@admin.route('/admin/read/commodity')
@required_login.auth.login_required
def readCommodity():
    pg = int(request.args.get('page'))
    sql = 'select id, shopid, name, price, message, photo, video, CAST(upload_time as char) from commodity'
    try:
        goal = dividePage(pg, sql)
        return jsonify({
            "status": 200,
            "msg": 'ok',
            "data": goal
        })
    except Exception as e:
        print("failed as %s" % e)
        return jsonify({'status': 500})


@admin.route('/admin/read/order')
@required_login.auth.login_required
def readOrder():
    pg = int(request.args.get('page'))
    sql = 'select id, commodity_id, commodity_name, shop_id, shop_name, shop_address, ' \
          'user_id, username, income, CAST(delivery_time as char), user_address, status from `order`'
    try:
        goal = dividePage(pg, sql)
        return jsonify({
            "status": 200,
            "msg": 'ok',
            "data": goal
        })
    except Exception as e:
        print("failed as %s" % e)
        return jsonify({'status': 500})


@admin.route('/admin/delete/user/<int:ID>', methods=['DELETE'])
@required_login.auth.login_required
def deleteUser(ID):
    sql = f"delete from user where id = {ID}"
    cursor.execute(sql)
    conf.db.commit()
    return jsonify({
        "status": 200,
        "msg": 'ok'
    })


@admin.route('/admin/delete/shop/<int:ID>', methods=['DELETE'])
@required_login.auth.login_required
def deleteShop(ID):
    sql = f"delete from shop where id = {ID}"
    cursor.execute(sql)
    conf.db.commit()
    return jsonify({
        "status": 200,
        "msg": 'ok'
    })


@admin.route('/admin/delete/delivery/<int:ID>', methods=['DELETE'])
@required_login.auth.login_required
def deleteDelivery(ID):
    sql = f"delete from delivery where id = {ID}"
    cursor.execute(sql)
    conf.db.commit()
    return jsonify({
        "status": 200,
        "msg": 'ok'
    })


@admin.route('/admin/delete/comments/<int:ID>', methods=['DELETE'])
@required_login.auth.login_required
def deleteComments(ID):
    sql = f"delete from comments where id = {ID}"
    cursor.execute(sql)
    conf.db.commit()
    return jsonify({
        "status": 200,
        "msg": 'ok'
    })


@admin.route('/admin/delete/commodity/<int:ID>', methods=['DELETE'])
@required_login.auth.login_required
def deleteCommodity(ID):
    sql = f"delete from commodity where id = {ID}"
    cursor.execute(sql)
    conf.db.commit()
    return jsonify({
        "status": 200,
        "msg": 'ok'
    })


@admin.route('/admin/delete/order/<int:ID>', methods=['DELETE'])
@required_login.auth.login_required
def deleteOrder(ID):
    sql = f"delete from `order` where id = {ID}"
    cursor.execute(sql)
    conf.db.commit()
    return jsonify({
        "status": 200,
        "msg": 'ok'
    })
