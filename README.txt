REFERRALS

The API are built to establish a referral scheme to increase sales.
Existing students will be able to refer their friends, via Referral Credits and in return, the student and the friend they have referred will both receive credits for free Crypto University courses (only if the friend converts the referral).

The student with the referral code is known as the Referring Partner. The person given the referral code is known as the Referred Partner

Each student will have a referral code(random string of 6 alphanumeric characters) generated which can be used 5 times.

Deployment:

Project Dependencies
    MySQL
    Python3
    Pip3
    Gunicorn
    Django

To get the application running, just run the file "start.sh" given in project directory and it will install all the dependencies and start the server listening on "localhost:8000"


The different APIs are explained below:

> POST /api/register/
Body : Email of the user to be created in below format
{
	"email": "user@test.com"
}
Creates a new user and referral code is also automatically generated for the new user.

> GET /api/referral_code?user_id=2
Gives the referral code of the user with given user_id
If no user exists with such user_id, it would return a response with status 404

> POST /api/referral/
Body :  Referral code and referred email in below format.
{
	"referred_email": "user01@test.com",
	"referral_code" : "d4Mz5O"
}
Creates a new referral
A new referral will be created only if 
	The referral code of referring_partner is valid and has not exceeded the maximum usage limit of 5 times.
	The referred_email entered should be a valid email
	The referred_email should not be an exisiting user
If the above conditions are not fulfilled then it would return a response with status 404


> DELETE /api/referral/referral_code/referred_email
Eg : /api/referral/d4Mz5O/user01@test.com
Deletes an existing referral if not converted using the same referral code as in the referral. Once the referral is deleted successfully for the user, the referral credits are revived.
The referral will be deleted only if
	The referral code and the referral email form a valid existing referral
	The referral is not converted

> POST /api/conversion/
Body :  Referral code and email in below format.
{
	"email": "user01@test.com",
	"referral_code": "d4Mz5O"
}
Creates a new user who has been converted from referral and grants one course credit to each the referring partner and referred partner.
The referral will be converted only if it is a valid referral else will return a response with status 404.
