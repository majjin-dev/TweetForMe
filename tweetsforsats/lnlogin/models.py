from django.db import models
# from django.contrib.sessions.backends.db import SessionStore as DBStore
# from django.contrib.sessions.base_session import AbstractBaseSession

# # Create your models here.
# class LightningSession(AbstractBaseSession):
#     # Use the session key as k1
#     linking_key = models.CharField(max_length=33, null=True, db_index=True)
#     signature = models.CharField(max_length=74, null=True)

#     @classmethod
#     def get_session_store_class(cls):
#         return SessionStore

# class SessionStore(DBStore):
#     @classmethod
#     def get_model_class(cls):
#         return LightningSession

#     def create_model_instance(self, data):
#         obj = super().create_model_instance(data)
#         try:
#             linking_key = int(data.get('_auth_user_key'))
#             signature = int(data.get('_auth_user_sig'))
#         except (ValueError, TypeError):
#             linking_key = None
#             signature = None
#         obj.linking_key = linking_key
#         obj.signature = signature
#         return obj