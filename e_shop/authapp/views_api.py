from djoser.views import UserViewSet


class ActivateUserViewSet(UserViewSet):
    def activation(self, request, *args, **kwargs):
        request.data.update(kwargs)
        return super().activation(request, *args, **kwargs)
