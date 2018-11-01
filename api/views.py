import string
from datetime import datetime
from random import choice

from django.core.validators import EmailValidator
from django.db.utils import IntegrityError
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Referrals, User


def referral_code_generator(size, chars=string.ascii_uppercase + string.ascii_lowercase + string.digits):
    return ''.join(choice(chars) for _ in range(size))


class Register(APIView):

    def post(self, request):
        """
        Creates new user (without referral)
        :param request:
        :return: Success/Error message
        """
        user = User()
        user.email = request.data.get('email')
        user.referral_code = referral_code_generator(6)

        try:
            user.save()
            return Response({"message": f'{user.email} created'}, status=status.HTTP_201_CREATED)
        except IntegrityError:
            return Response({"message": "User already exists"}, status=status.HTTP_400_BAD_REQUEST)


class Referralcode(APIView):

    def get(self, request):
        """
        Retrive user referral code if user exists
        :param request: user_id
        :return: user referral code
        """
        try:
            user = User.objects.get(id=request.query_params.get('user_id'))
        except User.DoesNotExist:
            user = None

        if user:
            if not user.referral_code:
                user.referral_code = referral_code_generator(6)
                user.save()
            return Response({"referral_code": user.referral_code}, status=status.HTTP_200_OK)
        else:
            return Response({"message": "User does not exist"}, status=status.HTTP_400_BAD_REQUEST)


class Referral(APIView):

    def post(self, request):
        """
        Creates referrals using given referral code and referred partner email
        :param request: referral code, referred_email
        :return: Success/Error message
        """
        email = request.data.get('referred_email')
        code = request.data.get('referral_code')

        email_validator = EmailValidator()
        try:
            email_validator(email)
        except Exception:
            return Response({"message": "Invalid Email"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
            return Response({"message": "User already exists with the same email"}, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            pass

        try:
            user = User.objects.get(referral_code=code)
            if user.used_referrals < 5:
                try:
                    referral = Referrals()
                    referral.referring_partner = user
                    referral.referred_partner = email
                    referral.save()
                except IntegrityError as e:
                    existing_ref = Referrals.objects.get(referred_partner=email,
                                                         referring_partner_id=user.id)
                    if existing_ref.deleted_at:
                        existing_ref.deleted_at = None
                        existing_ref.save()
                    else:
                        return Response({"message": "Referral already exists"}, status=status.HTTP_400_BAD_REQUEST)

                user.used_referrals += 1
                user.save()
                return Response({"message": "Referral created"}, status=status.HTTP_201_CREATED)

            else:
                return Response({"message": "Referral code is already used 5 times"},
                                status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response({"message": "Invalid Referral Code"}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, ref_code=None, ref_email=None):
        """
        Deletes referrals using given referral code and referred partner email if:
            referral is not converted
            referral is valid
        :param request: referral code, referred_email
        :return: Success/Error message
        """
        email = ref_email
        code = ref_code

        email_validator = EmailValidator()
        try:
            email_validator(email)
        except Exception:
            return Response({"message": "Invalid Email"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(referral_code=code)
        except User.DoesNotExist:
            return Response({"message": "Invalid Referral Code"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            referral = Referrals.objects.get(referred_partner=email,
                                             deleted_at=None, referring_partner=user.id)
        except Referrals.DoesNotExist:
            return Response({"message": "Referral does not exist"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            if referral.converted == 0:
                user.used_referrals -= 1
                referral.deleted_at = datetime.now()
                user.save()
                referral.save()
                return Response({"message": "Referral is deleted"}, status=status.HTTP_200_OK)
            else:
                return Response({"message": "Converted referrals cannot be deleted"},
                                status=status.HTTP_400_BAD_REQUEST)
        except IntegrityError:
            return Response({"message": "Invalid Referral"}, status=status.HTTP_400_BAD_REQUEST)


class Conversion(APIView):

    def post(self, request):
        """
        Converts referred partner to new user and adds course credit to both referring and referred partner
        :param request: referral_code, referred_email
        :return: Success/Error message
        """
        email = request.data.get('email')
        code = request.data.get('referral_code')

        try:
            user = User.objects.get(referral_code=code)
        except User.DoesNotExist:
            return Response({"message": "Invalid Referral Code"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            referral = Referrals.objects.get(referred_partner=email, referring_partner_id=user.id, deleted_at=None)
            new_user = User()
            new_user.email = email
            new_user.course_credit = 1
            new_user.referral_code = referral_code_generator(6)
            user.course_credit += 1
            referral.converted = 1

            try:
                new_user.save()
            except IntegrityError as e:
                return Response({"message": "Referral already converted"}, status=status.HTTP_400_BAD_REQUEST)
            user.save()
            referral.save()
            return Response({"message": "Referral converted"}, status=status.HTTP_201_CREATED)
        except Referrals.DoesNotExist:
            return Response({"message": "Referral does not exist"}, status=status.HTTP_400_BAD_REQUEST)
