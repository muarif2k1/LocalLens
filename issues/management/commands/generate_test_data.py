from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.contrib.gis.geos import Point
from issues.models import Issue, IssueCategory
from faker import Faker
import random

User = get_user_model()
fake = Faker()

class Command(BaseCommand):
    help = 'Generate test data for development'
    
    def add_arguments(self, parser):
        parser.add_argument('--issues', type=int, default=50, help='Number of issues to create')
    
    def handle(self, *args, **kwargs):
        num_issues = kwargs['issues']
        
        # Create test users if they don't exist
        citizen, _ = User.objects.get_or_create(
            username='citizen1',
            defaults={
                'email': 'citizen@example.com',
                'user_type': 'citizen'
            }
        )
        citizen.set_password('password123')
        citizen.save()
        
        authority, _ = User.objects.get_or_create(
            username='authority1',
            defaults={
                'email': 'authority@example.com',
                'user_type': 'authority',
                'ward': 'Ward 1',
                'zone': 'Zone A'
            }
        )
        authority.set_password('password123')
        authority.save()
        
        categories = list(IssueCategory.objects.all())
        if not categories:
            self.stdout.write(self.style.ERROR('No categories found. Run load_categories first.'))
            return
        
        statuses = ['pending', 'in_progress', 'resolved', 'closed']
        
        # India coordinates range
        lat_range = (8.4, 35.5)
        lng_range = (68.7, 97.4)
        
        for i in range(num_issues):
            lat = random.uniform(*lat_range)
            lng = random.uniform(*lng_range)
            
            issue = Issue.objects.create(
                title=fake.sentence(nb_words=6),
                description=fake.paragraph(nb_sentences=3),
                category=random.choice(categories),
                reporter=random.choice([citizen, authority]),
                location=Point(lng, lat),
                address=fake.address(),
                ward=f'Ward {random.randint(1, 10)}',
                zone=f'Zone {random.choice(["A", "B", "C", "D"])}',
                status=random.choice(statuses),
                privacy='public',
                upvotes=random.randint(0, 50)
            )
            
            self.stdout.write(
                self.style.SUCCESS(f'Created issue {i+1}/{num_issues}: {issue.title}')
            )
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {num_issues} test issues')
        )