import json
import twilio
import sys
import time
import datetime
from flask import request, abort
from instant_server.server import app, login_manager
from instant_server.server.error_handler import prod_error_instant_mail
from instant_server.db import models
models.connect()
from mongoengine.queryset import DoesNotExist
from instant_server.twilio_api import send_sms, code_generator
from flask_login import login_required, current_user, login_user
from werkzeug.exceptions import HTTPException


@login_manager.user_loader
def load_user(userid):
    """ see https://flask-login.readthedocs.org/en/latest/#flask.ext.login.LoginManager """
    return models.User.objects.with_id(userid)

@app.route('/login', methods=['POST', 'GET'])
def login():
    #try:
    email = request.form['email']
    password_hash = request.form['password']
    os = request.form['os']
    reg_id = request.form['reg_id']
    app_version = request.form.get('app_version')
    print app_version
    try:
        user = models.User.objects.get(email=email)
        if user.password_hash == password_hash:
            user.set_reg_id_os_and_version(os, reg_id, app_version)
            login_user(user)
            return json.dumps({
                "user_id": str(user.id),
                "web_app_url": models.WebApp.get_server_url_from_plateform_instance(user.get_platform_instance()),
		"ios_version_needed": "1.0",
		"android_version_needed": "1.0",
		"force_update": "false",
		"aws_account_id":"090152412356",
		"cognito_pool_id":"us-east-1:a17c5334-6843-49c0-8336-fbb36c40a6eb",
		"cognito_role_unauth":"arn:aws:iam::090152412356:role/Cognito_TimeAppUnauth_DefaultRole",
		"cognito_role_auth":"arn:aws:iam::090152412356:role/Cognito_TimeAppAuth_DefaultRole",
		"bucket_name":"picteverbucket",
		"cloudfront":"http://d380gpjtb0vxfw.cloudfront.net/",
		"android_update_link": "https://play.google.com/store/apps/details?id=com.pict.ever",
		"ios_update_link": "https://itunes.apple.com/us/app/shyft-chat-with-the-future/id910033123"})
        else:
            #wrong password
            abort(401)
    except DoesNotExist:
        #email not in db
        abort(401)
    except HTTPException as e:
        prod_error_instant_mail(
            error_num=15,
            object="{} login ".format(e),
            details="{}".format(sys.exc_info()),
            critical_level="ERROR")
        raise e
    except:
        print "Unexpected error:", sys.exc_info()
        prod_error_instant_mail(
            error_num=17,
            object="500 login",
            details="{}".format(sys.exc_info()),
            critical_level="CRITICAL")
        abort(500)


@app.route('/signup', methods=['POST', 'GET'])
def sign_up():
    email = request.form['email']
    password_hash = request.form['password']
    if models.User.objects(email=email).count() > 0:
        print models.User.objects(email=email).count()
        abort(406)
    try:
        new_user = models.User(email=email, password_hash=password_hash, created_at=datetime.datetime.now)
        new_user.save(validate=False)
        return ""
    except:
        print "Unexpected error:", sys.exc_info()
        prod_error_instant_mail(
            error_num=16,
            object="500 sign_up",
            details="{}".format(sys.exc_info()),
            critical_level="CRITICAL")
        abort(500)


@app.route('/define_first_phone_number', methods=['POST'])
@login_required
def define_first_phone_number():
    os = request.form['os']
    reg_id = request.form['reg_id']
    phone_number = request.form['phone_number']
    code = code_generator() 
    print phone_number
    try:
	if current_user.get_platform_instance() is None:
	    if current_user.get_contact_from_num(phone_number) is not None:
                print "phone number {} already taken...".format(phone_number)
                abort(406)
	else:
	    if current_user.get_platform_instance().phone_num != phone_number and current_user.get_contact_from_num(phone_number)["user_id"] != str(current_user.id):
                print "phone number {} already taken...".format(phone_number)
                abort(406)
        platform = models.PlatformInstance(
            is_verified=False,
            verification_code=code,
            phone_num=phone_number,
            user_id=current_user.id,
            reg_id=reg_id,
            os=os)
        platform.save()
        current_user.platform_instance = platform.id
	current_user.check_bottles()
        current_user.save()
        return ""
    except HTTPException as e:
        print "Unexpected error:", sys.exc_info()
        prod_error_instant_mail(
            error_num=15,
            object="{} define_first_phone_number ".format(e),
            details="{}".format(sys.exc_info()),
            critical_level="ERROR")
        raise e
    except:
        print "Unexpected error:", sys.exc_info()
        prod_error_instant_mail(
            error_num=14,
            object="500 define_first_phone_number",
            details="{}".format(sys.exc_info()),
            critical_level="CRITICAL")
        abort(500)


#Envoi/reception messages

@app.route('/send', methods=['POST'])
@login_required
def send():
    message = request.form['message']
    receiver_ids = request.form['receiver_ids']
    delivery_option = request.form.get("delivery_option")
    photo_id = request.form.get('photo_id', default="")
    video_id = request.form.get('video_id', default="")
    sound_id = request.form.get('sound_id', default="")
    try:
        if delivery_option is not None:
            delivery_option = json.loads(delivery_option)
        receiver_ids = json.loads(receiver_ids)
        for receiver_id in receiver_ids:
            models.Message.add_to_db(current_user, message, receiver_id, delivery_option, photo_id,video_id,sound_id)
        return ""
    except HTTPException as e:
        prod_error_instant_mail(
            error_num=11,
            object="{} send".format(e),
            details="{}".format(sys.exc_info()),
            critical_level="ERROR")
        raise e
    except:
        print "Unexpected error:", sys.exc_info()
        prod_error_instant_mail(
            error_num=10,
            object="500 send",
            details="{}".format(sys.exc_info()),
            critical_level="CRITICAL")
        abort(500)

@app.route('/resend', methods=['POST'])
@login_required
def resend():
    message_id = request.form['message_id']
    try:
	models.Message.resend(message_id)
        return ""
    except HTTPException as e:
        prod_error_instant_mail(
            error_num=11,
            object="{} resend ".format(e),
            details="{}".format(sys.exc_info()),
            critical_level="ERROR")
        raise e
    except:
        print "Unexpected error:", sys.exc_info()
        prod_error_instant_mail(
            error_num=10,
            object="500 resend",
            details="{}".format(sys.exc_info()),
            critical_level="CRITICAL")
        abort(500)

@app.route('/receive_all', methods=['GET'])
@login_required
def receive_all():
    timestamp = request.args.get('ts')
    try:
        print timestamp
        timestamp = float(timestamp)
        now = time.time()
        messages = current_user.get_messages_since(timestamp, now)
        return json.dumps({"ts": now, "new_messages": messages})
    except HTTPException as e:
        prod_error_instant_mail(
            error_num=9,
            object="{} receive_all".format(e),
            details="{}".format(sys.exc_info()),
            critical_level="ERROR")
        raise e
    except:
        print "Unexpected error:", sys.exc_info()
        prod_error_instant_mail(
            error_num=8,
            object="500 receive_all",
            details="{}".format(sys.exc_info()),
            critical_level="CRITICAL")
        abort(500)

@app.route('/get_number_of_future_messages', methods=['GET'])
@login_required
def get_number_of_future_messages():
    try:
        counter = current_user.get_number_of_future_messages()
        return str(counter)
    except HTTPException as e:
        prod_error_instant_mail(
            error_num=20,
            object="{} get_number_of_future_messages ".format(e),
            details="{}".format(sys.exc_info()),
            critical_level="ERROR")
        raise e
    except:
        print "Unexpected error:", sys.exc_info()
        prod_error_instant_mail(
            error_num=21,
            object="500 future messages",
            details="{}".format(sys.exc_info()),
            critical_level="CRITICAL")
        abort(500)

@app.route('/get_my_status', methods=['GET'])
@login_required
def get_my_status():
    try:
        status = current_user.get_my_status()
	current_user.status = status
        current_user.save()
        return status
    except HTTPException as e:
        prod_error_instant_mail(
            error_num=22,
            object="{} get_my_status ".format(e),
            details="{}".format(sys.exc_info()),
            critical_level="ERROR")
        raise e
    except:
        print "Unexpected error:", sys.exc_info()
        prod_error_instant_mail(
            error_num=23,
            object="500 get_my_status",
            details="{}".format(sys.exc_info()),
            critical_level="CRITICAL")
        abort(500)


@app.route('/get_send_choices', methods=['GET'])
@login_required
def get_send_choices():
    try:
        choices = models.SendChoice.get_active_choices()
        return json.dumps(choices)
    except HTTPException as e:
        prod_error_instant_mail(
            error_num=7,
            object="{} get_send_choices ".format(e),
            details="{}".format(sys.exc_info()),
            critical_level="ERROR")
        raise e
    except:
        print "Unexpected error:", sys.exc_info()
        prod_error_instant_mail(
            error_num=6,
            object="500 send choices",
            details="{}".format(sys.exc_info()),
            critical_level="CRITICAL")
        abort(500)

@app.route('/block_contacts', methods=['POST'])
@login_required
def block_contacts():
    contact_json = request.form['contacts_to_block']
    print contact_json
    try:
        list_of_ids = json.loads(contact_json)	
        for id_to_block in list_of_ids:
	    for m in models.Message.objects(sender_id=current_user.id,receiver_id=id_to_block,notif_delivered=False):
		m.is_blocked = True
		m.save()
	    for m in models.Message.objects(sender_id=id_to_block,receiver_id=current_user.id,notif_delivered=False):
		m.is_blocked = True
		m.save()
        return "" 
    except HTTPException as e:
        prod_error_instant_mail(
            error_num=3,
            object="{} upload contact".format(e),
            details="{}".format(sys.exc_info()),
            critical_level="ERROR")
        raise e
    except:
        prod_error_instant_mail(
            error_num=2,
            object="500 upload contact",
            details="{}".format(sys.exc_info()),
            critical_level="CRITICAL")
        print "Unexpected error:", sys.exc_info()
        abort(500)

@app.route('/upload_contacts', methods=['POST'])
@login_required
def upload_contacts():
    contact_json = request.form['contacts']
    #print contact_json
    try:
        list_of_numbers = json.loads(contact_json)
        response = []
        for num in list_of_numbers:
            contact_info = models.User.get_contact_from_num(num)
            if contact_info is not None:
                response.append(contact_info)
        return json.dumps(response) 
    except HTTPException as e:
        prod_error_instant_mail(
            error_num=3,
            object="{} upload contact".format(e),
            details="{}".format(sys.exc_info()),
            critical_level="ERROR")
        raise e
    except:
        prod_error_instant_mail(
            error_num=2,
            object="500 upload contact",
            details="{}".format(sys.exc_info()),
            critical_level="CRITICAL")
        print "Unexpected error:", sys.exc_info()
        abort(500)

@app.route('/messages_waiting')
def messages_waiting():
    try:
        return str(models.Message.objects(notif_delivered=False).count())
    except HTTPException as e:
        raise e
    except:
        prod_error_instant_mail(
            error_num=1,
            object="messages_waiting",
            details="{}".format(sys.exc_info()),
            critical_level="INFO")
        print "Unexpected error:", sys.exc_info()
        abort(500)


@app.route('/hello')
def hello_world():
    try:
        return "hello"
    except HTTPException as e:
        raise e
    except:
        prod_error_instant_mail(
            error_num=1,
            object="server down",
            details="{}".format(sys.exc_info()),
            critical_level="INFO")
        print "Unexpected error:", sys.exc_info()
        abort(500)


@app.route('/test_mail')
@login_required
def test_mail():
    prod_error_instant_mail(
        error_num=0,
        object=" exemple de mail de debug/error",
        details="Ceci est un exemple de mail de debug",
        critical_level="INFO")
    return ""
