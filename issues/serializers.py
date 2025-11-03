from rest_framework import serializers
from .models import Issue, IssueCategory, IssueComment, IssueUpvote
from django.contrib.gis.geos import Point

class IssueCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = IssueCategory
        fields = ['id', 'name', 'slug', 'icon', 'description']


class IssueSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    reporter_username = serializers.CharField(source='reporter.username', read_only=True)
    latitude = serializers.FloatField(write_only=True)
    longitude = serializers.FloatField(write_only=True)
    upvote_count = serializers.IntegerField(source='upvotes', read_only=True)
    comment_count = serializers.IntegerField(source='comments.count', read_only=True)
    
    class Meta:
        model = Issue
        fields = [
            'id', 'title', 'description', 'category', 'category_name',
            'reporter', 'reporter_username', 'latitude', 'longitude',
            'address', 'ward', 'zone', 'image', 'status', 'privacy',
            'upvote_count', 'comment_count', 'is_duplicate', 'duplicate_of',
            'created_at', 'updated_at', 'resolved_at'
        ]
        read_only_fields = ['reporter', 'upvotes', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        latitude = validated_data.pop('latitude')
        longitude = validated_data.pop('longitude')
        validated_data['location'] = Point(longitude, latitude)
        return super().create(validated_data)


class IssueCommentSerializer(serializers.ModelSerializer):
    user_username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = IssueComment
        fields = ['id', 'issue', 'user', 'user_username', 'comment', 'created_at', 'updated_at']
        read_only_fields = ['user', 'created_at', 'updated_at']


class IssueMapSerializer(serializers.ModelSerializer):
    lat = serializers.SerializerMethodField()
    lng = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Issue
        fields = ['id', 'title', 'description', 'status', 'status_display', 
                  'lat', 'lng', 'upvotes', 'image']
    
    def get_lat(self, obj):
        return obj.location.y
    
    def get_lng(self, obj):
        return obj.location.x
