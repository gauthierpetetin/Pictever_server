from notif_server import notif
from threading import Thread
import sys
from instant_server.db import models
models.connect()
from instant_server.server.error_handler import prod_error_notif_mail,prod_phone_mail
from datetime import datetime,timedelta
import time

def check_new_message():
    messages = models.Message.objects(notif_delivered=False,receiver_id__exists=True,delivery_time__lte=datetime.now())
    for message in messages:
        #print "sending notif for message : ", message.id, " content : ", message.content
        try:
	    if message.is_blocked==False:
		print message
            	ans = None
            	#send classic notification
		if message.receiver_id is None:
		    message.receiver_id = message.sender_id
            	receiver = models.User.objects.with_id(message.receiver_id)
	    	print message.receiver_id
            	if receiver is None:
		    receiver=models.User.objects.with_id(message.sender_id)
                    prod_error_notif_mail(
                    	error_num=106,
                    	object="Receiver does not exist anymore.",
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
			    if ans is None:
                    	        print "notification delivery failed"
		                details = "ans is None, reg_id={}".format(plat.reg_id)
                                prod_error_notif_mail(
                                    error_num=101,
                                    object="notification delivery failed",
                                    details=details,
                                    critical_level="CRITICAL")
                    else:
                        print "reg id is None"
                        prod_error_notif_mail(
                            error_num=100,
                            object="user without reg id",
                            details="{} {}".format(sys.exc_info(), message.receiver_id),
                            critical_level="CRITICAL")
	        else:
	            print "platform_instance is None"
		message.notif_delivered = True
                message.save()		    
        except:
            print "error when sending notification"
            prod_error_notif_mail(
                error_num=102,
                object="sending notification",
                details="{}".format(sys.exc_info()),
                critical_level="CRITICAL")
            print "Unexpected error:", sys.exc_info()


def message_check_loop():
    print " notification start"
    while True:
        try:
	    print "[]"
            check_new_message()
        except:
            prod_error_notif_mail(
                error_num=103,
                object=" main notification loop",
                details="{}".format(sys.exc_info()),
                critical_level="CRITICAL")
        time.sleep(5)

def send_no_phone_mail():
    while True:
	try:
	    for u in models.User.objects(created_at__gte=datetime.now() - timedelta(hours=64),created_at__lte=datetime.now() - timedelta(hours=24)):
                if u.get_platform_instance() is None and u.phone_mail_sent==False:
		    print u.email
		    prod_phone_mail(u.email)
		    u.phone_mail_sent=True
		    u.save()
	except:
            prod_error_notif_mail(
                error_num=103,
                object=" send no phone mail loop",
                details="{}".format(sys.exc_info()),
                critical_level="CRITICAL")
	time.sleep(60000)

if __name__ == '__main__':
    t1 = Thread(target = message_check_loop)
    t2 = Thread(target = send_no_phone_mail)
    t1.setDaemon(True)
    t2.setDaemon(True)
    t1.start()
    t2.start()
    while True:
        pass
    
