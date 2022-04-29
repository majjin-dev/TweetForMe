import os
from django.core.management.utils import get_random_secret_key

# SETINGS
SECRET_KEY = os.getenv("Settings_SecretKey", get_random_secret_key())
DEBUG = os.getenv("Settings_Debug", "False") == "True"
STATIC_ROOT = os.getenv("Settings_StaticRoot", "/home/static_files")
BASE_URL = os.getenv("Settings_BaseUrl", "http://localhost:8000/")

# TWITTER
TWITTER_ACCESS_TOKEN = os.getenv("Twitter_AccessToken")
TWITTER_ACCESS_TOKEN_SECRET = os.getenv("Twitter_AccessTokenSecret")
TWITTER_API_KEY = os.getenv("Twitter_ApiKey")
TWITTER_API_KEY_SECRET = os.getenv("Twitter_ApiKeySecret")
TWITTER_BEARER_TOKEN = os.getenv("Twitter_BearerToken")

# BTCPAY
BTCPAY_URL = os.getenv("BtcPay_Url")
BTCPAY_TOKEN = os.getenv("BtcPay_Token")
BTCPAY_STORE_ID = os.getenv("BtcPay_StoreId")

#LND
LND_URL = os.getenv("LND_Url")
LND_METADATA_MAC = os.getenv("LND_MetadataMac")