import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fernshub.settings')
django.setup()

from fronted.models import User, PlantCategory, Product

def setup_initial_data():
    # Create superuser if it doesn't exist
    if not User.objects.filter(email='admin@fernshub.com').exists():
        User.objects.create_superuser(
            username='admin',
            email='admin@fernshub.com',
            password='admin123',
        )
        print("✅ Created superuser admin@fernshub.com")
    
    # Create some basic categories
    categories = [
        {'name': 'Indoor Plants', 'description': 'Perfect for home decor'},
        {'name': 'Outdoor Plants', 'description': 'Ideal for gardens'},
        {'name': 'Succulents', 'description': 'Low maintenance beauties'},
    ]
    
    for cat_data in categories:
        cat, created = PlantCategory.objects.get_or_create(
            name=cat_data['name'],
            defaults={'description': cat_data['description']}
        )
        if created:
            print(f"✅ Created category: {cat.name}")

if __name__ == '__main__':
    setup_initial_data()