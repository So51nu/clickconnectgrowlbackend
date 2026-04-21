from rest_framework.permissions import BasePermission
from users.models import UserLoginProfile


class IsSourceManager(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False

        profile = UserLoginProfile.objects.filter(user=user).first()
        return bool(profile and profile.role == "source_manager")