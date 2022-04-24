import configparser

# Read from config.ini
config = configparser.ConfigParser()
config.read('tweetsforsats/config.ini')

# TWITTER
TWITTER_ACCESS_TOKEN = ""
TWITTER_ACCESS_TOKEN_SECRET = ""
TWITTER_API_KEY = ""
TWITTER_API_KEY_SECRET = ""
TWITTER_BEARER_TOKEN = ""

# BTCPAY
BTCPAY_URL = ""
BTCPAY_TOKEN = ""
BTCPAY_STORE_ID = ""

#LND
LND_URL = ""
LND_METADATA_MAC = ""

# OTHER
DEBUG_BASE_URL = "http://localhost/"

try:
    # TWITTER
    TWITTER_ACCESS_TOKEN = config['TWITTER']['AccessToken']
    TWITTER_ACCESS_TOKEN_SECRET = config['TWITTER']['AccessTokenSecret']
    TWITTER_API_KEY = config['TWITTER']['ApiKey']
    TWITTER_API_KEY_SECRET = config['TWITTER']['ApiKeySecret']
    TWITTER_BEARER_TOKEN = config['TWITTER']['BearerToken']

    # BTCPAY
    BTCPAY_URL = config['BTCPAY']['Url']
    BTCPAY_TOKEN = config['BTCPAY']['Token']
    BTCPAY_STORE_ID = config['BTCPAY']['StoreId']

    LND_URL = config['LND']['Url']
    LND_METADATA_MAC = config['LND']['MetadataMac']

    # OTHER
    DEBUG_BASE_URL = config['DEBUG']['BaseUrl']
except KeyError:
    pass