- 项目背景

  一个朋友要给自己现在的数码产品店店做一个商城，他找到了我，于是我基于Python3.6，Django2.2采用DRF框架给他搭建了一个小型的商城，本项目是商场的后端相关内容

- 安装与使用

  - ### Pipenv

    1. **克隆项目到本地**

       ```
       https://github.com/Silencehuliang/xiaoliangstore.git
       ```

    2. **安装 Pipenv（已安装跳过）**

       ```
       pip install pipenv
       ```

    3. **安装项目依赖**

       ```
       cd xiaoliangstore
       pipenv install -r requirements.txt
       ```

    4. **迁移数据库**

       在项目根目录运行如下命令迁移数据库：

       ```
       pipenv run python manage.py migrate
       ```

    5. **创建后台管理员账户**

       在项目根目录运行如下命令创建后台管理员账户

       ```
       pipenv run python manage.py createsuperuser
       ```

    6. **运行开发服务器**

       在项目根目录运行如下命令开启开发服务器：

       ```
       pipenv run python manage.py runserver
       ```

       在浏览器访问：[http://127.0.0.1:8000](http://127.0.0.1:8000/)

    7. **进入后台发布商品**

       在浏览器访问：http://127.0.0.1:8000/admin

       使用第 5 步创建的后台管理员账户登录后台。

- 主要项目负责人

  @silencehuliang

  