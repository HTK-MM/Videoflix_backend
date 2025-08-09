# Authentication

## CookieJWTAuthentication(JWTAuthentication):
This class defines a custom authentication mechanism that uses JSON Web Tokens (JWT) stored in cookies to authenticate requests.

### def authenticate(self, request):
Checks if the 'access_token' cookie exists and if it is valid. If the cookie is present and valid, it sets the 'Authorization' header with the access token and calls the parent class's authenticate method. If the cookie is not present or is invalid, it returns None.
    **Param Request:**
        - The request being processed.
    **Returns:**
        - The authenticated user and the access token if valid, None otherwise.