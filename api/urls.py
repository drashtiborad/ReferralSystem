from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns

from .views import Register, Referralcode, Referral, Conversion

url_patterns = [
    path('api/register ', Register.as_view(), name='register'),
    path('api/referral_code', Referralcode.as_view(), name='referral_code'),
    path('api/referral', Referral.as_view(), name='referral'),
    path('api/conversion', Conversion.as_view(), name='conversion'),
]

urlpatterns = format_suffix_patterns(url_patterns)