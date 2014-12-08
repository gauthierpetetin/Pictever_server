import os
import string
import random
from postmark import PMMail

def prod_error_instant_mail(error_num, object, details, critical_level="INFO"):
    prod_error_mail(error_num, object, details, critical_level)

def prod_error_notif_mail(error_num, object, details, critical_level="INFO"):
    prod_error_mail(error_num, object, details, critical_level, server="NOTIF-ERR")


def prod_error_mail(error_num, object, details, critical_level=0, server="INSTANT-ERR"):
    try:
	message = PMMail(
            api_key="f7bc97f9-ea51-4f15-b9f0-c187c82d466e", #os.environ.get('POSTMARK_API_KEY'),
            subject="[{}] [{}] [#{}] {}".format(server, critical_level, error_num, object),
            sender="error@pictever.com",
            to="error@pictever.com",
            text_body=details,
            tag="")
        print "[{}] [{}] [#{}] {}".format(server, critical_level, error_num, object)
    	message.send()
    except:
	print "prod_error_mail failed"

def prod_reset_mail(receiver,details):
    try:   
 	message = PMMail(
            api_key="f7bc97f9-ea51-4f15-b9f0-c187c82d466e",
            subject="Your verification code to reset your password",
            sender="team@pictever.com",
            to=receiver,
            text_body=details,
            tag="")
    	message.send()
	print "verification email sent"
    except:
	print "signup email not valid"

def prod_facebook_mail(facebook_name):
    try:
 	message = PMMail(
            api_key="f7bc97f9-ea51-4f15-b9f0-c187c82d466e",
            subject="New user on Pictever - facebook!",
            sender="team@pictever.com",
            to="team@pictever.com",
            text_body=facebook_name,
            tag="")
    	message.send()
    except:
	print "prod_facebook_mail has failed"

def prod_signup_mail(email):
    try:
        message = PMMail(
            api_key="f7bc97f9-ea51-4f15-b9f0-c187c82d466e",
            subject="New user on Pictever - signup!",
            sender="team@pictever.com",
            to="team@pictever.com",
            text_body=email,
            tag="")
    	message.send()
        with open ("welcome_mail.txt", "r") as myfile:
    	    data=myfile.read()
        welcome = PMMail(
            api_key="f7bc97f9-ea51-4f15-b9f0-c187c82d466e",
            subject="Welcome on board !",
            sender="team@pictever.com",
            to=email,
            text_body=data,
            tag="")
    	welcome.send()
    except:
	print "prod_signup_mail has failed"
    

def prod_phone_mail(email):
    try:
        with open ("no_phone.txt", "r") as myfile:
    	    data=myfile.read()
        message = PMMail(
            api_key="f7bc97f9-ea51-4f15-b9f0-c187c82d466e",
            subject="Continue you experience on Pictever",
            sender="team@pictever.com",
            to=email,
            text_body=data,
            tag="")
    	message.send()
    except:
	print "prod_phone_mail has failed"

def id_generator(size=4, chars=string.ascii_uppercase + string.digits):
	return ''.join(random.choice(chars) for _ in range(size))

  
