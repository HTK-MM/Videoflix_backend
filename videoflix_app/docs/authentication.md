# Authentication

## CookieJWTAuthentication(JWTAuthentication):
This class defines a custom authentication mechanism that uses JSON Web Tokens (JWT) stored in cookies to authenticate requests.

### def authenticate(self, request):
Overwrites the authenticate function from JWTAuthentication to get the access token from a cookie instead of the Authorization header. If no cookie is found, it returns None. If the token is invalid, it will raise an AuthenticationFailed exception.