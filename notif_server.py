from notif_server import notif
import sys
from instant_server.db import models
models.connect()
from instant_server.server.error_handler import prod_error_notif_mail
from datetime import datetime
import time


def check_new_message():
    messages = models.Message.objects(is_blocked=False,notif_delivered=False, receiver_id__exists=True, delivery_time__lte=datetime.now())
    print messages
    for message in messages:
        #print "sending notif for message : ", message.id, " content : ", message.content
        try:
            ans = None
            #send classic notification
            receiver = models.User.objects.with_id(message.receiver_id)
	    print receiver.id
            if receiver is None:
                prod_error_notif_mail(
                    error_num=106,
                    object="User does not exist anymore.",
                    details="user with id {} does not exist anymore, deleting message.".format(message.receiver_id),
                    critical_level="ERROR")
                message.delete()
                print "id {}".format(message.receiver_id)
	    plat = receiver.get_platform_instance()
	    if plat is not None:
                if plat.reg_id is not None:
		    if plat.reg_id=="" or plat.reg_id=="(null)":
                        prod_error_notif_mail(
                            error_num=100,
                            object="reg id is empty or null",
                            details="{} {}".format(sys.exc_info(), message.receiver_id),
                            critical_level="CRITICAL")
		    else:
                        ans = notif.send_notification(message, plat)
                else:
                    print "reg id is None"
                    prod_error_notif_mail(
                        error_num=100,
                        object="user without reg id",
                        details="{} {}".format(sys.exc_info(), message.receiver_id),
                        critical_level="CRITICAL")
	    else:
	        print "platform_instance is None"
                    prod_error_notif_mail(
                        error_num=100,
                        object="user without platform_instance",
                        details="{} {}".format(sys.exc_info(), message.receiver_id),
                        critical_level="CRITICAL")
            message.notif_delivered = True
            message.save()
            if ans is None:
                print "notification delivery failed"
		details = "ans is None"
                prod_error_notif_mail(
                    error_num=101,
                    object="notification delivery failed",
                    details=details,
                    critical_level="CRITICAL")
        except:
            print "error when sending notification"
            prod_error_notif_mail(
                error_num=102,
                object="sending notification",
                details="{}".format(sys.exc_info()),
                critical_level="CRITICAL")
            print "Unexpected error:", sys.exc_info()

def message_check_loop():
    prod_error_notif_mail(
        error_num=0,
        object=" notification start",
        details="{}".format("Le service d'envoit de notification vient de demarrer."),
        critical_level="INFO")
    while True:
        try:
            check_new_message()
        except:
            prod_error_notif_mail(
                error_num=103,
                object=" main notification loop",
                details="{}".format(sys.exc_info()),
                critical_level="CRITICAL")
        time.sleep(5)


if __name__ == '__main__':
    message_check_loop()
