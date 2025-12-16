from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager


class UserManager(BaseUserManager):
    def create_user(self, email, nom, password=None):
        if not email:
            raise ValueError("L'email est obligatoire")

        user = self.model(
            email=self.normalize_email(email),
            nom=nom
        )
        user.set_password(password)  # ✅ Hash sécurisé
        user.save()
        return user

    def create_superuser(self, email, nom, password):
        user = self.create_user(email, nom, password)
        user.is_staff = True
        user.is_superuser = True
        user.save()
        return user


class User(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('agent', 'Agent'),
        ('user', 'User'),
    ]

    STATUS_CHOICES = [
        ('actif', 'Actif'),
        ('inactif', 'Inactif'),
        ('suspendu', 'Suspendu'),
    ]

    email = models.EmailField(unique=True)
    nom = models.CharField(max_length=150)

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='user')
    statut = models.CharField(max_length=20, choices=STATUS_CHOICES, default='actif')

    date_inscription = models.DateTimeField(auto_now_add=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nom']

    def __str__(self):
        return self.email
