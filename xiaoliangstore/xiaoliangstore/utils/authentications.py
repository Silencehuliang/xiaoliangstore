from rest_framework_jwt.authentication import JSONWebTokenAuthentication
class MyJSONWebTokenAuthentication(JSONWebTokenAuthentication):
    def authenticate(self, request):
        try:
            return super().authenticate(request)
        except:
            return None