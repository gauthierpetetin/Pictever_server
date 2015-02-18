# -*-coding:Utf-8 -*
from notif_server import notif
from threading import Thread
import sys
import json
import datetime
from instant_server.db import models
models.connect()
from instant_server.server.error_handler import prod_error_notif_mail
import time
bfm=datetime.datetime(2015,2,18,16,00,00,00)

def who_is_on_pictever():
    for a in models.AddressBook.objects(need_to_refresh=True):
	a.need_to_refresh=False
	a.save()
	ta = Thread(target = update_address_book, args=(str(a.id),))
	ta.setDaemon(True)
	ta.start()

def update_address_book(a_id):
    try:
   	a = models.AddressBook.objects.with_id(a_id)
    	print "address_book of ",str(a.user_id), " currenlty checking "
    	list_contacts = json.loads(a.all_contacts)
    	on_pictever=[]
        for c in list_contacts:
	    plat = models.PlatformInstance.objects(phone_num=c.get("tel")).order_by('-id').first()
	    if plat is not None:
	    	infos = {}
		infos["name"] = c.get("name")
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
	    if plat.os=='android' and plat.reg_id is not None:
	        notif.send_android_get_address_book(plat.reg_id)
    	print "END FOR ",str(a.user_id)
    except:
	prod_error_notif_mail(
                error_num=300,
                object="update_address_books",
                details="{}{}".format(sys.exc_info(),str(a.id)),
                critical_level="CRITICAL")
	a.need_to_refresh=True
   	a.save()

def contact_check_loop():
    while True:
	print "[]"
    	try:
	    who_is_on_pictever()
    	except:
	    print sys.exc_info()
	    prod_error_notif_mail(
	     	error_num=203,
	     	object=" main contact loop",
	     	details="{}".format(sys.exc_info()),
	     	critical_level="CRITICAL")
    	time.sleep(1)

def check_new_contacts_in_address_books():
    while True:
	try:
	    print "on envoit les notifs pour avertir les gens que des contacts sont arrives sur l appli"
	    for a in models.AddressBook.objects(is_new=True):
		print "new address book detected",str(a.user_id)
		u = models.User.objects.with_id(a.user_id)
		if u.created_at > bfm:
		    print "user created after bfm"
		    json_contacts=json.loads(a.all_contacts)
                    for c in json_contacts:
                        plat = models.PlatformInstance.objects(phone_num=c.get("tel")).order_by('-id').first()
                        if plat is not None:
			    print "user a un contact sur Pictever, qui est : ",str(plat.user_id),plat.phone_num
			    if str(plat.user_id)!=str(u.id):
			        a_mec = models.AddressBook.objects(user_id=plat.user_id).first()
			        if a_mec is not None and u.get_platform_instance().phone_num in a_mec.all_contacts:
				    print "et user est dans l address book de ce contact"
			            message=""
			            for cont in json.loads(a_mec.all_contacts):
				        if cont.get('tel')==u.get_platform_instance().phone_num:
					    print "On a trouve le nom de user dans l address book du contact"
				            message=cont.get('name')
					    break
			            if message!="":
				        if plat.phone_num.startswith("0033"):
			    	            message+=" a rejoint Pictever!"
				        else:
				            message+=" joined Pictever!"
				        print "donc on envoit la notif a ce contact"
			    	        notif.send_silent_notification(message,plat)
			        else:
				    print "mais il n'a pas d addresse book ou user n est pas dans l address book de ce contact"
		a.is_new=False
		a.save()
	except:
            prod_error_notif_mail(
                error_num=303,
                object="check_new_contacts_in_address_books",
                details="{}".format(sys.exc_info()),
                critical_level="CRITICAL")
	time.sleep(21600)

if __name__ == '__main__':
    t1 = Thread(target = contact_check_loop)
    t2 = Thread(target = check_new_contacts_in_address_books)
    t1.setDaemon(True)
    t2.setDaemon(True)
    t1.start()
    t2.start()
    while True:
        pass
    
