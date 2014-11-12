import os
import string
import random
from postmark import PMMail

def prod_error_instant_mail(error_num, object, details, critical_level="INFO"):
    prod_error_mail(error_num, object, details, critical_level)

def prod_error_notif_mail(error_num, object, details, critical_level="INFO"):
    prod_error_mail(error_num, object, details, critical_level, server="NOTIF-ERR")


def prod_error_mail(error_num, object, details, critical_level=0, server="INSTANT-ERR"):
    message = PMMail(
        api_key="f7bc97f9-ea51-4f15-b9f0-c187c82d466e", #os.environ.get('POSTMARK_API_KEY'),
        subject="[{}] [{}] [#{}] {}".format(server, critical_level, error_num, object),
        sender="dev@pictever.com",
        to="dev@pictever.com",
        text_body=details,
        tag="")

    print "[{}] [{}] [#{}] {}".format(server, critical_level, error_num, object),
    message.send()

def prod_reset_mail(receiver,details):
    message = PMMail(
        api_key="f7bc97f9-ea51-4f15-b9f0-c187c82d466e",
        subject="Your verification code to reset your password",
        sender="dev@pictever.com",
        to=receiver,
        text_body=details,
        tag="")
    print "verification email sent"
    message.send()

def id_generator(size=4, chars=string.ascii_uppercase + string.digits):
	return ''.join(random.choice(chars) for _ in range(size))

  
