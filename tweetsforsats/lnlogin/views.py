from django.shortcuts import render, redirect
from django.http import JsonResponse
from hashlib import sha256
from django.contrib.sessions.models import Session
from django.core.cache import cache
from lnurl import encode

from importlib import import_module
from django.conf import settings
SessionStore = import_module(settings.SESSION_ENGINE).SessionStore
from django.contrib.sessions.models import Session

import secrets
import ecdsa

from tweetsforsats import config

# Create your views here.
def auth(request):
    k1 = request.GET.get('k1')
    key = request.GET.get('key')
    sig = request.GET.get('sig')

    if k1 is None:
        return JsonResponse({'status': "ERROR", 'reason': "No challenge found."})

    if key is None:
        return JsonResponse({'status': "ERROR", 'reason': "No linking key found."})

    if sig is None:
        return JsonResponse({'status': "ERROR", 'reason': "No signature found."})
        
    cached_key = cache.get(k1)
    if cached_key is None:
        return JsonResponse({'status': "ERROR", 'reason': "Unrecognized challenge. Please scan a new qr code."})

    vk = ecdsa.VerifyingKey.from_string(bytearray.fromhex(key), curve=ecdsa.SECP256k1)

    try:
        if vk.verify_digest(signature=bytearray.fromhex(sig), digest=bytearray.fromhex(k1), sigdecode=ecdsa.util.sigdecode_der):
            cache.set(k1, key)
            return JsonResponse({'status': "OK"})
    except ecdsa.BadSignatureError as err:
        return JsonResponse({'status': "ERROR", 'reason': err.args[0]})

def login(request):
    k1 = secrets.token_hex(32)

    cache.get_or_set(k1, '', 120)

    url = f"{config.DEBUG_BASE_URL}/lnlogin/auth?tag=login&k1={k1}"
    lnurl = encode(url)
    context = {
        'lnurl': lnurl,
        'challenge': k1
    }
    return render(request, 'lnlogin/login.html', context)

def check(request):
    k1 = request.GET.get('k1')
    key = cache.get(k1)
    if not key is None and not key == '':
        # TODO: Tie this session to the ip and user agent string of the user
        # TODO: Decorator that checks the ip and user agent string to validate user
        # TODO: https://docs.djangoproject.com/en/4.0/ref/request-response/#django.http.HttpRequest.META
        request.session['key'] = key
        cache.delete(k1)
        return JsonResponse({'authenticated': True})
    return JsonResponse({'authenticated': False})

def logout(request):
    try:
        request.session.flush()
    except:
        pass
    return redirect("main:index")