from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework import exceptions


class CookieJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        """ Overwrites the authenticate function from JWTAuthentication to get the access token from a cookie instead of the Authorization header. 
        If no cookie is found, it returns None. If the token is invalid, it will raise an AuthenticationFailed exception.  """
        access_token = request.COOKIES.get("access_token")                    
        if not access_token:
            return None
        request.META['HTTP_AUTHORIZATION'] = f'Bearer {access_token}'
        try:
            return super().authenticate(request)
        except exceptions.AuthenticationFailed:
            return None