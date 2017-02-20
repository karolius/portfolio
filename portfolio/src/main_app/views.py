from django.shortcuts import render


def test(request):
    template = "base.html"
    context = {
        "name": "Andrzej Dududu",
    }
    return render(request, template, context)