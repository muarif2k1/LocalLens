from django.core.management.base import BaseCommand
from issues.models import IssueCategory

class Command(BaseCommand):
    help = 'Load initial issue categories'
    
    def handle(self, *args, **kwargs):
        categories = [
            {'name': 'Pothole', 'icon': 'fa-road', 'description': 'Road damage and potholes'},
            {'name': 'Streetlight', 'icon': 'fa-lightbulb', 'description': 'Street lighting issues'},
            {'name': 'Garbage', 'icon': 'fa-trash', 'description': 'Waste management and garbage'},
            {'name': 'Water Supply', 'icon': 'fa-water', 'description': 'Water supply and drainage'},
            {'name': 'Traffic Signal', 'icon': 'fa-traffic-light', 'description': 'Traffic signal problems'},
            {'name': 'Illegal Construction', 'icon': 'fa-building', 'description': 'Unauthorized construction'},
            {'name': 'Stray Animals', 'icon': 'fa-dog', 'description': 'Stray animal issues'},
            {'name': 'Public Safety', 'icon': 'fa-shield-alt', 'description': 'Public safety concerns'},
            {'name': 'Park Maintenance', 'icon': 'fa-tree', 'description': 'Park and garden maintenance'},
            {'name': 'Other', 'icon': 'fa-ellipsis-h', 'description': 'Other civic issues'},
        ]
        
        for cat_data in categories:
            category, created = IssueCategory.objects.get_or_create(
                name=cat_data['name'],
                defaults={
                    'icon': cat_data['icon'],
                    'description': cat_data['description']
                }
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Created category: {category.name}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Category already exists: {category.name}')
                )
        
        self.stdout.write(self.style.SUCCESS('Successfully loaded categories'))
