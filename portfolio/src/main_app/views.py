from django.shortcuts import render


def test(request):
    template = "base.html"
    context = {
        "name": "test test1",
    }
    return render(request, template, context)