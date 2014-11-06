from gcm import GCM
import os
import sys
#from gcm.gcm import GCMException
from apns import APNs, Payload
from instant_server.db import models
models.connect()

GCM_API_KEY = "AIzaSyCWn_dNhBHFITuVAOAG2r_KDlV5KROg-Oo"

print "loading CEM files ? ", os.path.isfile('notif_server/certificates/ShyftCertdev.pem')


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
    sender_id = message.sender_id
    sender = models.User.objects.with_id(sender_id)
    data = {'sender_email': sender.email,
            'sender_phone': str(sender.get_platform_instance().phone_num),
	    'receiver_reg_id': str(reg_id)}
    print data
    try:
        gcm.plaintext_request(registration_id=reg_id, data=data)
        return True
    except:
        print "Unexpected error:", sys.exc_info()
        print "sending android notif failed"
        print "reg_id",  reg_id


def send_ios_notif_gauthier(reg_id, message):
    print "send notif to gauthier"
    try:
        # APN to use when in developer mode :
        #my_apns = APNs(use_sandbox=True, cert_file='notifications_server/certificates/keoCert.pem', key_file='notifications_server/certificates/keoKey.pem')
        
        # APN to use when in production mode :
        path_cert = 'certificates/ShyftCertdev.pem'
        path_key = 'certificates/ShyftKeydev.pem'
        cert_path = os.path.join(os.path.dirname(__file__), path_cert)
        key_path = os.path.join(os.path.dirname(__file__), path_key)
        my_apns = APNs(use_sandbox=True, cert_file=cert_path, key_file=key_path)

        payload = Payload(alert=message.receive_label, sound="default", badge=1)
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
        path_cert = 'certificates/ShyftCert.pem'
        path_key = 'certificates/ShyftKey.pem'
        cert_path = os.path.join(os.path.dirname(__file__), path_cert)
        key_path = os.path.join(os.path.dirname(__file__), path_key)
        
        my_apns = APNs(cert_file=cert_path, key_file=key_path)

        payload = Payload(alert=message.receive_label, sound="default", badge=1)
        my_apns.gateway_server.send_notification(reg_id, payload)
        return True
    except:
        print "Unexpected error:", sys.exc_info()
        print "sending ios notif failed"
        print "reg_id",  reg_id
