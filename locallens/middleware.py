from django.utils.deprecation import MiddlewareMixin
from notifications.models import Notification

class NotificationMiddleware(MiddlewareMixin):
    def process_template_response(self, request, response):
        if hasattr(request, 'user') and request.user.is_authenticated:
            if hasattr(response, 'context_data') and response.context_data is not None:
                unread_count = request.user.notifications.filter(is_read=False).count()
                response.context_data['unread_notifications'] = unread_count
        return response