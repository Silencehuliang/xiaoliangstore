import base64
import pickle

from rest_framework.generics import GenericAPIView

from xiaoliangstore.xiaoliangstore.apps.cart.serializer import CartSerializer

from rest_framework.response import Response


class CartView(GenericAPIView):
    """购物车"""
    serializer_class = CartSerializer

    def perform_authentication(self, request):
        """将执行具体请求方法前的身份认证关掉，由视图自己来进行身份认证"""
        pass

    def post(self, request):
        """保存购物车"""
        # sku_id  count  selected
        # 校验
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        sku_id = serializer.validated_data['sku_id']
        count = serializer.validated_data['count']
        selected = serializer.validated_data['selected']
        # 判断用户登录状态
        # try:
        user = request.user  # 匿名用户 AnonymoseUser
        # except Exception:
        #     user = None
        # 保存
        if user and user.is_authenticated:
            # 如果用户已登录，保存到redis
            redis_conn = get_redis_connection('cart')
            pl = redis_conn.pipeline()
            # 用户购物车数据  redis hash哈希
            pl.hincrby('cart_%s' % user.id, sku_id, count)
            # 用户购物车勾选数据  redis  set
            if selected:
                pl.sadd('cart_selected_%s' % user.id, sku_id)
            pl.execute()
            return Response(serializer.data)
        else:
            # 如果用户未登录，保存到cookie  reponse = Response() response.set_cookie
            # 取出cookie中的购物车数据
            cart_str = request.COOKIES.get('cart')
            if cart_str:
                # 解析
                cart_str = cart_str.encode()  # str -> bytes
                cart_bytes = base64.b64decode(cart_str)  # b64decode(byes类型）
                cart_dict = pickle.loads(cart_bytes)
            else:
                cart_dict = {}
            if sku_id in cart_dict:
                # 如果商品存在购物车中，累加
                cart_dict[sku_id]['count'] += count
                cart_dict[sku_id]['selected'] = selected
            else:
                # 如果商品不在购物车中，设置
                cart_dict[sku_id] = {
                    'count': count,
                    'selected': selected
                }
            cart_cookie = base64.b64encode(pickle.dumps(cart_dict)).decode()
            # 设置cookie
            response = Response(serializer.data)
            response.set_cookie('cart', cart_cookie, max_age=constants.CART_COOKIE_EXPIRES)
            return response

    def merge_cart_cookie_to_redis(request, user, response):
        # 获取cookie中的购物车数据
        cookie_cart = request.COOKIES.get('cart')
        if not cookie_cart:
            return response
        cookie_cart_dict = pickle.loads(base64.b64decode(cookie_cart.encode()))
        # 获取redis中的购物车商品数量数据，hash
        redis_conn = get_redis_connection('cart')
        redis_cart = redis_conn.hgetall('cart_%s' % user.id)
        # 用来存储redis最终保存的商品数量信息的hash数据
        cart = {}
        for sku_id, count in redis_cart.items():
            cart[int(sku_id)] = int(count)
        # 用来记录redis最终操作时，哪些sku_id是需要勾选新增的
        redis_cart_selected_add = []
        # 用来记录redis最终操作时，哪些sku_id是需要取消勾选删除的
        redis_cart_selected_remove = []
        # 遍历cookie中的购物车
        for sku_id, count_selected_dict in cookie_cart_dict.items():
            #  处理商品的数量，维护在redis中购物车数据数量的最终字典
            cart[sku_id] = count_selected_dict['count']
            # 处理商品的勾选状态
            if count_selected_dict['selected']:
                # 如果cookie指明，勾选
                redis_cart_selected_add.append(sku_id)
            else:
                # 如果cookie指明，不勾选
                redis_cart_selected_remove.append(sku_id)
        if cart:
            # 执行redis操作
            pl = redis_conn.pipeline()
            # 设置hash类型
            pl.hmset('cart_%s' % user.id, cart)
            # 设置set类型
            if redis_cart_selected_remove:
                pl.srem('cart_selected_%s' % user.id, *redis_cart_selected_remove)
            if redis_cart_selected_add:
                pl.sadd('cart_selected_%s' % user.id, *redis_cart_selected_add)
            pl.execute()
        # 删除cookie
        response.delete_cookie('cart')
        return response

class CartView(GenericAPIView):
    def put(self, request):
        """修改购物车"""
        # sku_id, count, selected
        # 校验
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        sku_id = serializer.validated_data['sku_id']
        count = serializer.validated_data['count']
        selected = serializer.validated_data['selected']
        # 判断用户的登录状态
        try:
            user = request.user
        except Exception:
            user = None
        # 保存
        if user and user.is_authenticated:
            # 如果用户已登录，修改redis
            redis_conn = get_redis_connection('cart')
            pl = redis_conn.pipeline()
            # 处理数量 hash
            pl.hset('cart_%s' % user.id, sku_id, count)
            # 处理勾选状态 set
            if selected:
                # 表示勾选
                pl.sadd('cart_selected_%s' % user.id, sku_id)
            else:
                # 表示取消勾选, 删除
                pl.srem('cart_selected_%s' % user.id, sku_id)
            pl.execute()
            return Response(serializer.data)
        else:
            # 未登录，修改cookie
            cookie_cart = request.COOKIES.get('cart')
            if cookie_cart:
                # 表示cookie中有购物车数据
                # 解析
                cart_dict = pickle.loads(base64.b64decode(cookie_cart.encode()))
            else:
                # 表示cookie中没有购物车数据
                cart_dict = {}
            response = Response(serializer.data)
            if sku_id in cart_dict:
                cart_dict[sku_id] = {
                    'count': count,
                    'selected': selected
                }
                cart_cookie = base64.b64encode(pickle.dumps(cart_dict)).decode()
                # 设置cookie
                response.set_cookie('cart', cart_cookie, max_age=constants.CART_COOKIE_EXPIRES)
            return response

    def delete(self, request):
        """删除购物车"""
        # sku_id
        # 校验
        serializer = CartDeleteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        sku_id = serializer.validated_data['sku_id']
        # 判断用户的登录状态
        try:
            user = request.user
        except Exception:
            user = None
        # 删除
        if user and user.is_authenticated:
            # 已登录，删除redis
            redis_conn = get_redis_connection('cart')
            pl = redis_conn.pipeline()
            # 删除hash
            pl.hdel('cart_%s' % user.id, sku_id)
            # 删除set
            pl.srem('cart_selected_%s' % user.id, sku_id)
            pl.execute()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            # 未登录，删除cookie
            cookie_cart = request.COOKIES.get('cart')
            if cookie_cart:
                # 表示cookie中有购物车数据
                # 解析
                cart_dict = pickle.loads(base64.b64decode(cookie_cart.encode()))
            else:
                # 表示cookie中没有购物车数据
                cart_dict = {}
            response = Response(status=status.HTTP_204_NO_CONTENT)
            if sku_id in cart_dict:
                del cart_dict[sku_id]
                cart_cookie = base64.b64encode(pickle.dumps(cart_dict)).decode()
                # 设置cookie
                response.set_cookie('cart', cart_cookie, max_age=constants.CART_COOKIE_EXPIRES)
            return response

class CartSelectAllView(GenericAPIView):
    """
    购物车全选
    """
    serializer_class = CartSelectAllSerializer
    def perform_authentication(self, request):
        pass
    def put(self, request):
        # selected
        # 校验
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        selected = serializer.validated_data['selected']
        # 判断用户的登录状态
        try:
            user = request.user
        except Exception:
            user = None
        if user and user.is_authenticated:
            # 已登录，redis
            redis_conn = get_redis_connection('cart')
            redis_cart = redis_conn.hgetall('cart_%s' % user.id)
            sku_id_list = redis_cart.keys()
            if selected:
                # 全选， 所有的sku_id都添加到redis set
                redis_conn.sadd('cart_selected_%s' % user.id, *sku_id_list)
            else:
                # 取消全选，清空redis中的set数据
                redis_conn.srem('cart_selected_%s' % user.id, *sku_id_list)
            return Response({'message': 'OK'})
        else:
            # 未登录， cookie
            cookie_cart = request.COOKIES.get('cart')
            if cookie_cart:
                # 表示cookie中有购物车数据
                # 解析
                cart_dict = pickle.loads(base64.b64decode(cookie_cart.encode()))
            else:
                # 表示cookie中没有购物车数据
                cart_dict = {}
            response = Response({'message': 'OK'})
            if cart_dict:
                for count_selected_dict in cart_dict.values():
                     count_selected_dict['selected'] = selected
                cart_cookie = base64.b64encode(pickle.dumps(cart_dict)).decode()
                # 设置cookie
                response.set_cookie('cart', cart_cookie, max_age=constants.CART_COOKIE_EXPIRES)
            return response

