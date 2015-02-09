# -*-coding:Utf-8 -*
from gcm import GCM
import os
import sys
#from gcm.gcm import GCMException
from apns import APNs, Payload

GCM_API_KEY = "AIzaSyCWn_dNhBHFITuVAOAG2r_KDlV5KROg-Oo"

print "loading CEM files ? ", os.path.isfile('notif_server/certificates/PicteverCertDev.pem')


def send_notification(message, receiver_phone):
    print "send notification"
    #Handle push notifications to android and ios
    if receiver_phone.os == "android":
        return send_android_notification(receiver_phone.reg_id, message)
    elif receiver_phone.os == "ios":
        if receiver_phone.phone_num == "0033612010848":
            send_ios_notif_gauthier(receiver_phone.reg_id, message)
        return send_ios_notification(receiver_phone.reg_id, message)
    else:
        print "weird ..."
        print receiver_phone.os


def send_android_notification(reg_id, message):
    print "send android notif"
    gcm = GCM(GCM_API_KEY)
    data = {'receiver_reg_id': str(reg_id)}
    print data
    try:
        gcm.plaintext_request(registration_id=reg_id, data=data)
        return True
    except:
        print "Unexpected error:", sys.exc_info()
        print "sending android notif failed"
        print "reg_id",  reg_id

def send_android_silent(reg_id, message):
    print "send android silent notif"
    gcm = GCM(GCM_API_KEY)
    data = {'silent_push': message}
    print data
    try:
        gcm.plaintext_request(registration_id=reg_id, data=data)
        return True
    except:
        print "Unexpected error:", sys.exc_info()
        print "sending android notif failed"
        print "reg_id",  reg_id

def send_android_little_push(reg_id, message):
    print "send android little push"
    gcm = GCM(GCM_API_KEY)
    data = {'little_push': message}
    print data
    try:
        gcm.plaintext_request(registration_id=reg_id, data=data)
        return True
    except:
        print "Unexpected error:", sys.exc_info()
        print "sending android little push failed"
        print "reg_id",  reg_id

def send_android_get_address_book(reg_id):
    print "send android get address book"
    gcm = GCM(GCM_API_KEY)
    data = {'get_address_book': "vas y coco"}
    print data
    try:
        gcm.plaintext_request(registration_id=reg_id, data=data)
        return True
    except:
        print "Unexpected error:", sys.exc_info()
        print "sending android get address book failed"
        print "reg_id",  reg_id


def send_ios_notif_gauthier(reg_id, message):
    print "send notif to gauthier"
    try:
        # APN to use when in developer mode :
        #my_apns = APNs(use_sandbox=True, cert_file='notifications_server/certificates/keoCert.pem', key_file='notifications_server/certificates/keoKey.pem')
        # APN to use when in production mode :
        path_cert = 'certificates/PicteverCertDev.pem'
        path_key = 'certificates/PicteverKeyDev.pem'
        cert_path = os.path.join(os.path.dirname(__file__), path_cert)
        key_path = os.path.join(os.path.dirname(__file__), path_key)
        my_apns = APNs(use_sandbox=True, cert_file=cert_path, key_file=key_path)

        payload = Payload(alert=message.receive_label, sound="ache.caf", badge=1)
        my_apns.gateway_server.send_notification(reg_id, payload)
        return True
    except:
        print "Unexpected error:", sys.exc_info()
        print "sending ios to gauthier notif failed"
        print "reg_id",  reg_id

def send_gauthier_silent(reg_id, message):
    print "send silent notif to gauthier"
    try:
        # APN to use when in developer mode :
        #my_apns = APNs(use_sandbox=True, cert_file='notifications_server/certificates/keoCert.pem', key_file='notifications_server/certificates/keoKey.pem')
        # APN to use when in production mode :
        path_cert = 'certificates/PicteverCertDev.pem'
        path_key = 'certificates/PicteverKeyDev.pem'
        cert_path = os.path.join(os.path.dirname(__file__), path_cert)
        key_path = os.path.join(os.path.dirname(__file__), path_key)
        my_apns = APNs(use_sandbox=True, cert_file=cert_path, key_file=key_path)
        payload = Payload(alert=message)
        my_apns.gateway_server.send_notification(reg_id, payload)
        return True
    except:
        print "Unexpected error:", sys.exc_info()
        print "sending ios to gauthier notif failed"
        print "reg_id",  reg_id


def send_ios_notification(reg_id, message):
    try:
        # APN to use when in developer mode :
        #my_apns = APNs(use_sandbox=True, cert_file='notifications_server/certificates/keoCert.pem', key_file='notifications_server/certificates/keoKey.pem')
        # APN to use when in production mode :
        path_cert = 'certificates/PicteverCert.pem'
        path_key = 'certificates/PicteverKey.pem'
        cert_path = os.path.join(os.path.dirname(__file__), path_cert)
        key_path = os.path.join(os.path.dirname(__file__), path_key)
        my_apns = APNs(cert_file=cert_path, key_file=key_path)
        payload = Payload(alert=message.receive_label, sound="ache.caf", badge=1)
        my_apns.gateway_server.send_notification(reg_id, payload)
        return True
    except:
        print "Unexpected error:", sys.exc_info()
        print "sending ios notif failed"
        print "reg_id",  reg_id

def send_ios_silent(reg_id, message):
    print "send silent notif to ios"
    try:
        # APN to use when in developer mode :
        #my_apns = APNs(use_sandbox=True, cert_file='notifications_server/certificates/keoCert.pem', key_file='notifications_server/certificates/keoKey.pem')
        # APN to use when in production mode :
        path_cert = 'certificates/PicteverCert.pem'
        path_key = 'certificates/PicteverKey.pem'
        cert_path = os.path.join(os.path.dirname(__file__), path_cert)
        key_path = os.path.join(os.path.dirname(__file__), path_key)
        my_apns = APNs(cert_file=cert_path, key_file=key_path)
        payload = Payload(alert=message)
        my_apns.gateway_server.send_notification(reg_id, payload)
        return True
    except:
        print "Unexpected error:", sys.exc_info()
        print "sending ios notif failed"
        print "reg_id",  reg_id

def send_silent_notification(message,plat):
    print "send silent notif"
    if plat.os == "android":
        return send_android_silent(plat.reg_id, message)
    elif plat.os == "ios":
        if plat.phone_num == "0033612010848":
            send_gauthier_silent(plat.reg_id, message)
        return send_ios_silent(plat.reg_id, message)
    else:
        print "weird ..."
        print plat.os
	
