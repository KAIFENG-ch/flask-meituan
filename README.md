# 这是一个通过flask实现外卖网站后端的项目
## 此项目使用flask设计一个类似美团的外卖网站的后端

## 接口文档
### [美团接口文档](https://documenter.getpostman.com/view/18742402/UVkmPwcb)

## 项目主要功能介绍
### 1. 用户
#### * 注册、登录、注销
#### * 修改各类资料，头像上传
#### * 修改密码（提高->需要邮箱验证）
#### * 用户间可以相互关注（提高->好友系统）
#### * 点餐
### 2. 商家
#### * 上传物品信息，包括物品图片（20级还需可上传视频）
#### * 商家标签分类
#### * 评论（提高->多级评论）
#### * 点赞、收藏、转发
#### * 商家、物品搜索（20必做）
### 3. 骑手
#### * 接单（为简化系统，可直接定时送达）
#### * 收益
### 4. 后台
#### * 搜索各类信息
#### * 审核删除各类信息

## 项目主要依赖
### Flask==2.0.2
### Flask_HTTPAuth==4.5.0
### PyJWT==2.3.0
### PyMySQL==1.0.2
### python_bcrypt==0.3.2
### PyYAML==6.0
### redis==4.1.2

## 项目结构

```shell
meituan/
├── app
│  ├── service
│     ├── user
│     ├── shop
│     ├── delivery
│     ├── admin
|  ├── template
│  ├── static
│     ├── css
│     ├── img
│     ├── js
├── log
├── pkg
├── utils
``` 
 
- app : 封装应用服务
- log : 存放日志文件
- pkg : 存放错误码
- utils : 存放工具函数

## 配置文件
```
DB:
  host : 127.0.0.1
  username : root
  password :
  port : 3306
  database : meituan

Redis:
  host : 127.0.0.1
  port : 6379

server:
  port : 8000

email:
  addr : 3184218074@qq.com
  password : 
```
## 说明
### MySQL存储用户，商品，评论数据
### redis存储点赞，收藏，转发的数据

## 入口文件
### main.py

## uwsgi部署文件
### run.ini
