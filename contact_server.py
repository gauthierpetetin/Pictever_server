# -*-coding:Utf-8 -*
from notif_server import notif
from threading import Thread
import sys
from instant_server.db import models
models.connect()
from instant_server.server.error_handler import prod_error_notif_mail
from datetime import datetime,timedelta
import time

def who_is_on_pictever():
    for a in models.AddressBook.objects(need_to_refresh=True):
	list_contacts = json.loads(a.all_contacts)
    	on_pictever=[]
    	for c in list_contacts:
	    plat = models.PlatformInstance.objects(phone_num=c.get("tel")).order_by('-id').first()
	    if plat is not None:
                infos = {}
                infos["phoneNumber1"] = c.get("tel")
            	infos["email"] = ""
            	infos["facebook_id"] = ""
            	infos["facebook_name"] = ""
            	infos["status"] = plat.status
            	infos["user_id"] = str(plat.user_id)
            	on_pictever.append(infos)
    	a.on_pictever=json.dumps(on_pictever)
	a.need_to_refresh=False
    	a.save()
	plat = models.PlatformInstance.objects(user_id=a.user_id).order_by('-id').first()
	if plat is not None:
	    if plat.os='android' and plat.reg_id is not None:
	    	notif.send_android_get_address_book(plat.reg_id)

def contact_check_loop():
    print " notification start"
    try:
	print "[]"
	who_is_on_pictever()
	contact_check_loop()
    except:
	prod_error_notif_mail(
	     error_num=203,
	     object=" main contact loop",
	     details="{}".format(sys.exc_info()),
	     critical_level="CRITICAL")

def check_new_contacts_in_address_books():
    while True:
	try:
	    print "la normalement on envoit des notifs pour avertir les gens que des contacts sont arrives sur l appli"
	except:
            prod_error_notif_mail(
                error_num=303,
                object="check_new_contacts_in_address_books",
                details="{}".format(sys.exc_info()),
                critical_level="CRITICAL")
	time.sleep(86400)

if __name__ == '__main__':
    t1 = Thread(target = contact_check_loop)
    t2 = Thread(target = check_new_contacts_in_address_books)
    t1.setDaemon(True)
    t2.setDaemon(True)
    t1.start()
    t2.start()
    while True:
        pass
    
