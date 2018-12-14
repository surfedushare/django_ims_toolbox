# from jwt.exceptions import InvalidTokenError
#
# from django.contrib.auth.backends import RemoteUserBackend
# from rest_framework.authentication import BaseAuthentication
# from rest_framework_jwt.authentication import (JSONWebTokenAuthentication, jwt_decode_handler,
#                                                jwt_get_username_from_payload)
#
#
# class Auth0JWTAuthenticationBackend(RemoteUserBackend, BaseAuthentication):
#
#     def authenticate(self, request):
#         authenticator = JSONWebTokenAuthentication()
#         jwt_value = authenticator.get_jwt_value(request)
#         try:
#             jwt_payload = jwt_decode_handler(jwt_value)
#         except InvalidTokenError:
#             return None
#         username = jwt_get_username_from_payload(jwt_payload)
#         super().authenticate(request, remote_user=username)
#         auth = authenticator.authenticate(request)
#         if auth is None:
#             return auth
#         user, token = auth
#         if not user.is_staff or not user.is_superuser:
#             user.is_staff = jwt_payload.get("https://portbase.com/bds_graph_staff", False)
#             user.is_superuser = jwt_payload.get("https://portbase.com/bds_graph_superuser", False)
#             user.save()
#         return user, token
#
#
# class Auth0JWTAdminBackend(Auth0JWTAuthenticationBackend):
#
#     def authenticate(self, request):
#         auth = super().authenticate(request)
#         if auth is None:
#             return None
#         user, token = auth
#         return user
