from django.shortcuts import render

from orders.models import UserCheckout


def homeView(request):
    template = "base.html"
    user = request.user
    if user.is_authenticated:
        request.session["user_name"] = user.username
    else:
        user_checkout_id = request.session.get("user_checkout_id")
        if user_checkout_id is not None:
            request.session["guest_email"] = UserCheckout.objects.get(id=user_checkout_id).email
    return render(request, template, {})