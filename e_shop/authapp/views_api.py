from django.http import HttpResponseRedirect
from djoser.views import UserViewSet
from e_shop.settings import SUCCESS_ACTIVATION_VIEW_URL


class ActivateUserViewSet(UserViewSet):
    def activation(self, request, *args, **kwargs):
        request.data.update(kwargs)
        super().activation(request, *args, **kwargs)
        return HttpResponseRedirect(SUCCESS_ACTIVATION_VIEW_URL)
