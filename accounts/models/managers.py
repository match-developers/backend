from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.db import models
from django.utils.translation import gettext_lazy as _


class CustomUserManager(BaseUserManager):
    def create_user(self, email, username, first_name, last_name, password, profile_photo=None, bio=None, **other_fields):
        if not email:
            raise ValueError(_("Please provide an email address"))
        email = self.normalize_email(email)
        user = self.model(
            email=email, username=username, first_name=first_name, last_name=last_name, profile_photo=profile_photo, bio=bio, **other_fields
        )
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()  # 소셜 로그인 시 비밀번호 설정 불가
        user.save()
        return user

    def create_superuser(self, email, username, first_name, last_name, password, profile_photo=None, bio=None, **other_fields):
        other_fields.setdefault("is_staff", True)
        other_fields.setdefault("is_superuser", True)
        other_fields.setdefault("is_active", True)
        if other_fields.get("is_staff") is not True:
            raise ValueError(_("Please assign is_staff=True for superuser"))
        if other_fields.get("is_superuser") is not True:
            raise ValueError(_("Please assign is_superuser=True for superuser"))
        return self.create_user(email, username, first_name, last_name, password, profile_photo=profile_photo, bio=bio, **other_fields)
    
    def create_social_user(self, email, username, first_name, last_name, provider, social_id, profile_photo=None, bio=None, **other_fields):
        """
        소셜 로그인으로 사용자 생성
        """
        if not email:
            raise ValueError(_("Please provide an email address"))
        email = self.normalize_email(email)
        user = self.model(
            email=email, username=username, first_name=first_name, last_name=last_name, provider=provider, social_id=social_id, profile_photo=profile_photo, bio=bio, **other_fields
        )
        user.set_unusable_password()  # 소셜 로그인 시 비밀번호가 필요 없음
        user.save()
        return user