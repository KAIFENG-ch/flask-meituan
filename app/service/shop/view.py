import time

import bcrypt
import os

from flask import request, abort, jsonify, session

import conf
from utils import file_process
from utils import required_login
from app.service.shop import shop

cursor = conf.db.cursor()


@shop.route('/shop/register', methods=['POST'])
def register():
    shop_msg = request.form
    if (not shop_msg['shopname']) or (not shop_msg['password']) or (not shop_msg['address']):
        abort(404)
    try:
        sql = f"insert into shop (name, password, address) values ('%s', '%s', '%s')" % \
              (shop_msg['shopname'], bcrypt.hashpw(shop_msg['password'].encode(), bcrypt.gensalt()).decode(),
               shop_msg['address'])
        cursor.execute(sql)
        conf.db.commit()
        conf.r.set(shop_msg['shopname'] + 'likes', 0)
        conf.r.set(shop_msg['shopname'] + 'collect', 0)
        conf.r.set(shop_msg['shopname'] + 'transmit', 0)
    except Exception as e:
        print("failed %s" % e)
    return jsonify({
        "status": 200,
        "msg": "ok",
        "data": [shop_msg['shopname'], shop_msg['address']]
    })


@shop.route('/shop/login/commodity', methods=['POST'])
@required_login.auth.login_required
def commodity():
    shop_id = session['userId']
    commodity_name = request.form['name']
    price = request.form['price']
    message = request.form['message']
    file_dir = os.path.join(file_process.basedir, 'upload')
    if not os.path.exists(file_dir):
        os.makedirs(file_dir)
    photo_file = request.files['photo']
    photo_path = file_process.photo_process(photo_file, file_dir)
    video_file = request.files['video']
    video_path = file_process.video_process(video_file, file_dir)
    time_now = time.localtime(int(time.time()))
    dt = time.strftime("%Y-%m-%d %H:%M:%S", time_now)
    sql = f"insert into commodity (shopId, name, price, message, photo, video, upload_time) values " \
          f"({shop_id}, '{commodity_name}', '{price}', '{message}', '{photo_path}','{video_path}', '{dt}')"
    try:
        cursor.execute(sql)
        conf.db.commit()
        return jsonify({
                "status": 200,
                "msg": "ok",
                "data": [shop_id, commodity_name, price, message, photo_path, video_path, time.time()]
            })
    except Exception as e:
        print("failed as %s" % e)
        return jsonify({
            "status": 500,
            "msg": "error",
        })


@shop.route('/shop/login/label', methods=['POST'])
@required_login.auth.login_required
def label():
    shopname = session['username']
    labels = request.form['label']
    conf.r.lpush(shopname + 'label', labels)
    return jsonify({
        "status": 200,
        "msg": "ok",
        "data": conf.r.lrange(shopname + 'label', 0, -1)
    })
