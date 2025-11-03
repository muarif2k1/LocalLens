from django import forms
from django.contrib.gis import forms as gis_forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Field
from .models import Issue, IssueComment

class IssueReportForm(forms.ModelForm):
    latitude = forms.FloatField(widget=forms.HiddenInput())
    longitude = forms.FloatField(widget=forms.HiddenInput())
    
    class Meta:
        model = Issue
        fields = ['title', 'description', 'category', 'image', 'address', 'privacy']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('title', css_class='form-group col-md-12 mb-3'),
            ),
            Row(
                Column('category', css_class='form-group col-md-6 mb-3'),
                Column('privacy', css_class='form-group col-md-6 mb-3'),
            ),
            Row(
                Column('description', css_class='form-group col-md-12 mb-3'),
            ),
            Row(
                Column('address', css_class='form-group col-md-12 mb-3'),
            ),
            Row(
                Column('image', css_class='form-group col-md-12 mb-3'),
            ),
            Field('latitude'),
            Field('longitude'),
            Submit('submit', 'Submit Issue', css_class='btn btn-primary mt-3')
        )
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        from django.contrib.gis.geos import Point
        instance.location = Point(
            float(self.cleaned_data['longitude']),
            float(self.cleaned_data['latitude'])
        )
        if commit:
            instance.save()
        return instance


class IssueCommentForm(forms.ModelForm):
    class Meta:
        model = IssueComment
        fields = ['comment']
        widgets = {
            'comment': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Add a comment...'}),
        }


class IssueFilterForm(forms.Form):
    category = forms.ModelChoiceField(
        queryset=None,
        required=False,
        empty_label="All Categories"
    )
    status = forms.ChoiceField(
        choices=[('', 'All Status')] + Issue.STATUS_CHOICES,
        required=False
    )
    date_from = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    date_to = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from .models import IssueCategory
        self.fields['category'].queryset = IssueCategory.objects.all()
