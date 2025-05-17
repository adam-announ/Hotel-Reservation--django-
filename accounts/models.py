from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Role(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return self.name

class Permission(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    roles = models.ManyToManyField(Role, related_name='permissions')
    
    def __str__(self):
        return self.name

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=20, blank=True)
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, blank=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username}'s profile"

class Client(models.Model):
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE)
    address = models.TextField(blank=True)
    is_loyal = models.BooleanField(default=False)
    loyalty_points = models.IntegerField(default=0)
    
    def __str__(self):
        return f"Client: {self.profile.user.username}"

class Employee(models.Model):
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE)
    position = models.CharField(max_length=100)
    hire_date = models.DateField()
    employee_id = models.CharField(max_length=20, unique=True)
    
    def __str__(self):
        return f"Employee: {self.profile.user.username} ({self.position})"

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        profile = Profile.objects.create(user=instance)
        # Par défaut, chaque nouvel utilisateur est un client
        client_role, _ = Role.objects.get_or_create(name='Client')
        profile.role = client_role
        profile.save()
        Client.objects.create(profile=profile)