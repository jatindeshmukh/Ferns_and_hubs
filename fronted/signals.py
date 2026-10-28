from django.contrib.auth import get_user_model
from django.db.models.signals import post_migrate
from django.dispatch import receiver

@receiver(post_migrate)
def create_default_superuser(sender, **kwargs):
    if sender.name != "fronted":
        return
    
    User = get_user_model()

    email = "admin@fernshub.com"
    password = "Admin@123"

    if not User.objects.filter(email=email).exists():
        print("Creating Default SuperUser...")
        User.objects.create_superuser(
            email=email,
            password=password,
            username="admin"
        )
