from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.contrib.gis.geos import Point
from .models import Issue, IssueCategory, IssueComment, IssueUpvote

User = get_user_model()

class IssueModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.category = IssueCategory.objects.create(
            name='Test Category',
            slug='test-category'
        )
        self.issue = Issue.objects.create(
            title='Test Issue',
            description='Test description',
            category=self.category,
            reporter=self.user,
            location=Point(77.5946, 12.9716),
            address='Test Address',
            status='pending'
        )
    
    def test_issue_creation(self):
        self.assertEqual(self.issue.title, 'Test Issue')
        self.assertEqual(self.issue.status, 'pending')
        self.assertEqual(self.issue.upvotes, 0)
    
    def test_issue_str(self):
        expected = 'Test Issue - Pending'
        self.assertEqual(str(self.issue), expected)


class IssueViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.category = IssueCategory.objects.create(
            name='Test Category'
        )
    
    def test_home_view(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'LocalLens')
    
    def test_report_issue_view_authenticated(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/report/')
        self.assertEqual(response.status_code, 200)
    
    def test_report_issue_view_unauthenticated(self):
        response = self.client.get('/report/')
        self.assertEqual(response.status_code, 302)  # Redirect to login


class IssueAPITest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='apiuser',
            password='apipass123'
        )
        self.category = IssueCategory.objects.create(name='API Test')
    
    def test_api_list_issues(self):
        response = self.client.get('/api/issues/')
        self.assertEqual(response.status_code, 200)
    
    def test_api_create_issue_authenticated(self):
        self.client.login(username='apiuser', password='apipass123')
        data = {
            'title': 'API Test Issue',
            'description': 'Test description',
            'category': self.category.id,
            'latitude': 12.9716,
            'longitude': 77.5946,
            'address': 'Test Address',
            'image': None
        }
        response = self.client.post('/api/issues/', data)
        self.assertEqual(response.status_code, 201)