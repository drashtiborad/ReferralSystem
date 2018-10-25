from django.db import models


class User(models.Model):
    id = models.AutoField(primary_key=True)
    email = models.EmailField(unique=True)
    referral_code = models.CharField(max_length=6, unique=True)
    used_referrals = models.IntegerField(default=0)
    course_credit = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True)

    class Meta:
        db_table = 'user'


class Referrals(models.Model):
    id = models.AutoField(primary_key=True)
    referring_partner = models.ForeignKey('User', on_delete='CASCADE')
    referred_partner = models.EmailField()
    converted = models.BooleanField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True)

    class Meta:
        db_table = 'referrals'
        unique_together = (('referring_partner', 'referred_partner'),)
