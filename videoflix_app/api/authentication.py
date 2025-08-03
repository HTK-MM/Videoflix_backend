from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework import exceptions


class CookieJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        access_token = request.COOKIES.get("access_token")             
        print("Token from cookie:", access_token)    
        if not access_token:
            return None
        request.META['HTTP_AUTHORIZATION'] = f'Bearer {access_token}'
        try:
            return super().authenticate(request)
        except exceptions.AuthenticationFailed:
            return None