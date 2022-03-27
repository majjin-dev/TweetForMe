from django.shortcuts import render

# Create your views here.
def index(request):
    key = ''
    try:
        key = request.session['key']
    except KeyError:
        pass
    context = {
        'key': key
    }
    return render(request, 'main/index.html', context)