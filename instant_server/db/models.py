# -*-coding:Utf-8 -*
import mongoengine as db
try:
    from instant_server.server.error_handler import prod_error_instant_mail
except:
    def prod_error_instant_mail(a, b, c, d):
        print a, b, c, d 
import datetime
import random
import time

def connect(read_only=False):
    if read_only:
        READONLY_URI = 'mongodb://readdb:passittothenextlevel@ds051160.mongolab.com:51160/heroku_app31307485'
        print "connecting to pictever database (read only)..."
        db.connect('picteverdb', host=READONLY_URI)
    else:
        PRODUCTION_URI = 'mongodb://testdb:test@ds051160.mongolab.com:51160/heroku_app31307485'
        print "connecting to pictever database ..."
        db.connect('picteverdb', host=PRODUCTION_URI)

class Message(db.Document):
    created_at = db.DateTimeField(default=datetime.datetime.now, required=True)
    delivery_time = db.DateTimeField(default=datetime.datetime.now, required=True)
    is_blocked = db.BooleanField(default=False)
    sender_id = db.ObjectIdField()
    receiver_id = db.ObjectIdField()
    message = db.StringField(required=True)
    photo_id = db.StringField(default="", required=True)
    video_id = db.StringField(default="", required=True)
    sound_id = db.StringField(default="", required=True)
    notif_delivered = db.BooleanField(default=False, required=True)
    receive_label = db.StringField()
    receive_color = db.StringField()
    version = db.StringField()

    meta = {
        'indexes': ['-created_at', 'receiver_id'],
        'ordering': ['-delivery_time']
    }

    @staticmethod
    def resend(message_id):
        mes = Message.objects.with_id(message_id)
	rand = random.randint(2678400, 8035200)
	t = time.mktime(mes.delivery_time.utctimetuple()) + rand
	r = ReceiveLabel.get_receive_label(rand)
	mes.receive_label = r.label
	mes.receive_color = r.color
	mes.delivery_time = datetime.datetime.fromtimestamp(t)
	mes.notif_delivered = False
	mes.save()
	return mes.id
	

    @staticmethod
    def add_to_db(current_user, message, receiver_id, delivery_option,photo_id,video_id,sound_id):
        if receiver_id[:2] == "id":
            print "id detected"
            receiver_id = receiver_id[2:]
            receiver_phone = None
	    is_blocked = False
        elif receiver_id[:3] == "num":
            print "phone number then"
            receiver_phone = receiver_id[3:]
            receiver_id = current_user.id
	    is_blocked = True	
        else:
            print "error cannot understand id"
            prod_error_instant_mail(
                error_num=100,
                object="add_to_db",
                details="{}".format("error cannot understand id : {}".format(receiver_id)),
                critical_level="ERROR")
            return None
        delivery_time_ts, receive_label,receive_color = SendChoice.process_delivery_option(delivery_option)
        delivery_time = datetime.datetime.fromtimestamp(delivery_time_ts)
        mes = Message(
            message=message,
            receiver_id=receiver_id,
            receiver_phone=receiver_phone,
            delivery_time=delivery_time,
            sender_id=current_user.id,
	    is_blocked=is_blocked,
            photo_id=photo_id,
	    video_id=video_id,
	    sound_id=sound_id,
            receive_label=receive_label,
            receive_color=receive_color,
            version="1.0"
        )
        mes.save()
        if receiver_phone is not None:
            bottle = Bottle(message_id=mes.id, phone_num=receiver_phone)
            bottle.save()
        print "saved message to db"
	return mes.id


class PlatformInstance(db.Document):
    """ represent one installed app on a phone 
    a User can have several of these """
    is_verified = db.BooleanField(default=False, required=True)
    verification_code = db.StringField(max_length=100, required=True)  
    phone_num = db.StringField(default="", required=True)
    os = db.StringField(max_length=255, default=None)
    app_version = db.StringField(default=None)
    reg_id = db.StringField(max_length=255, default=None)
    user_id = db.ObjectIdField(required=True)

class Bottle(db.Document):
#    """ store a phone and a Message id corresponding to a message that was 
#    sent to someone without the app at the time"""
    message_id = db.ObjectIdField(required=True)
    phone_num = db.StringField(max_length=50, required=True)
    active = db.BooleanField(default=True)

class User(db.Document):
    email = db.StringField(required=True) 
    password_hash = db.StringField(max_length=255, required=True)
    active = db.BooleanField(default=True, required=True)
    created_at = db.DateTimeField(default=datetime.datetime.fromtimestamp(1412121600),required=True)
    platform_instance = db.ObjectIdField(default=None) 
    status = db.StringField(default="Newbie")

    def check_bottles(self):
        """ loop over all Bottles to check for messages already pending"""
        num = self.get_platform_instance().phone_num
        for b in Bottle.objects(active=True, phone_num=num):
            mes = Message.objects.with_id(b.message_id)
            mes.receiver_id = self.id
	    mes.is_blocked = False
	    mes.save()

#    def check_messages_in_a_bottle(self):
#        """ loop over all messages to check if the"""
#        num = self.get_platform_instance().phone_num
#        for m in Message.objects(receiver_phone=num):
#            m.receiver_id = self.id
#	    m.is_blocked = False
#	    m.save()

    def get_number_of_future_messages(self):
        """ get the number of future messages"""
	counter = 0
        for m in Message.objects(receiver_id=self.id,notif_delivered=False):
            if str(time.mktime(m.created_at.utctimetuple()))!=str(time.mktime(m.delivery_time.utctimetuple())):
	        if m.is_blocked:
		    print "message bloque ne compte pas"
		else:
	            counter += 1
	return counter
    
    def get_my_status(self):
        """ the status of the user depends on the number of messages sent - and not yet delivered - by the user in the future"""
	if self.get_platform_instance().phone_num == "0033668648212" or self.get_platform_instance().phone_num == "0033612010848":
	    return "Founder"
	else:
	    counter = 0
            for m in Message.objects(sender_id=self.id,notif_delivered=False):
		if m.delivery_time > m.created_at:
		    counter += 1
		else:
		    print "send now not counted"
	    status = Status.get_current_status(counter)
	    return status

    def set_reg_id_os_and_version(self, os, reg_id,app_version):
        """ set the reg id of the first phone number ... """
        if self.platform_instance is not None:
            platform = PlatformInstance.objects.with_id(self.platform_instance)
            if reg_id is not None:
                platform.reg_id = reg_id
            else:
                raise("error no reg_id")
            platform.os = os
            platform.app_version = app_version
            platform.save()

    def get_messages_since(self, timestamp, now_ts):
        previous = datetime.datetime.fromtimestamp(timestamp)
        now = datetime.datetime.fromtimestamp(now_ts)
        messages = Message.objects(receiver_id=self.id, delivery_time__gte=previous, delivery_time__lte=now,is_blocked=False)
        print messages.count() 
        answer = []
        for m in messages:
            sender = User.objects.with_id(m.sender_id)
            d = {
		"message_id": str(m.id),
		"received_at": str(time.mktime(m.delivery_time.utctimetuple())),
                "from_email": sender.email,
                "from_numero": sender.get_platform_instance().phone_num,
                "from_id": str(sender.id), 
                "message": m.message,
                "created_at": str(time.mktime(m.created_at.utctimetuple())),
                "photo_id": str(m.photo_id),
                "video_id": str(m.video_id),
                "sound_id": str(m.sound_id),
                "receive_label": m.receive_label,
                "receive_color":m.receive_color,
                "version": m.version
            }
            answer.append(d)
        return answer

    def get_platform_instance(self):
        try:
            return PlatformInstance.objects.with_id(self.platform_instance)
        except:
            return None

    def is_authenticated(self):
        return True

    def is_active(self):
        return self.active
    
    def is_anonymous(self):
        """ no anonymous users for now """
        return False

    def get_id(self):
        """ we use the mongodb objectid as the id for flask-login (as a unicode)"""
        return unicode(self.id)

    def get_contact_info(self, num=None):
        infos = {}
        
        if num is None:
            num = PlatformInstance.objects.with_id(self.platform_instance)

        infos["phoneNumber1"] = num.phone_num
        infos["email"] = self.email
	infos["status"] = self.status
        infos["user_id"] = str(self.id)
        return infos

    @staticmethod
    def get_contact_from_num(num):
        try:
            plat = PlatformInstance.objects(phone_num=num).order_by('-id').first()
            user = User.objects.with_id(plat.user_id)
            return user.get_contact_info(plat)
        except:
            return None


class Status(db.Document):
    active = db.BooleanField(default=False)
    label = db.StringField(default="",required=True)
    inf = db.IntField(required=True)
    sup = db.IntField(required=True)

    @staticmethod
    def get_current_status(my_counter):
	print str(my_counter)
	current_status="Newbie"
        for status in Status.objects(active=True):
            if my_counter >= status.inf and my_counter <= status.sup :
                current_status = status.label
        return current_status

class ReceiveLabel(db.Document):
    active = db.BooleanField(default=False)
    label = db.StringField(default="",required=True)
    color = db.StringField(default="",required=True)
    inf = db.IntField(required=True)
    sup = db.IntField(required=True)

    @staticmethod
    def get_receive_label(counter):
	print str(counter)
	return_label = ReceiveLabel.objects().order_by('id').first()
        for r in ReceiveLabel.objects(active=True):
            if counter >= r.inf and counter <= r.sup :
       		 return r
        return return_label
   	

class SendChoice(db.Document):
    active = db.BooleanField(default=False)
    order_id = db.IntField(required=True)
    send_label = db.StringField(default="", required=True)
    receive_label = db.StringField(default="", required=True)
    receive_color = db.StringField(default="", required=True)
    key = db.StringField(required=False)
    # indicate if the time_delay is absolute (ie since 1970 UTC) or relative
    time_absolute = db.BooleanField(default=False, required=True)  
    time_random = db.BooleanField(default=False)
    #int in second for the time delay to send a message
    time_delay = db.IntField(required=False)

    @staticmethod
    def get_active_choices():
        choices = []
        for choice in SendChoice.objects(active=True):
            d = {}
            d["order_id"] = str(choice.order_id)
            d["key"] = str(choice.id)
            d["send_label"] = choice.send_label
            #d["receive_label"] = choice.receive_label
            choices.append(d)
        return choices

    @staticmethod
    def process_delivery_option(delivery_option):
        if delivery_option["type"] == "calendar":
	    receive_counter = int(delivery_option["parameters"]) - time.time()
	    r = ReceiveLabel.get_receive_label(receive_counter)
            return (int(delivery_option["parameters"]),r.label,r.color)
        elif delivery_option["type"] == "resend":
	    rand = random.randint(2678400, 8035200) # between 1 month and 3 months
	    r = ReceiveLabel.get_receive_label(rand)
            delivery_time = time.time()+rand
            return (delivery_time,r.label,r.color)
	elif delivery_option["type"] == "experimental": 
	    rand = random.randint(150000, 1200000) # random in few days
	    r = ReceiveLabel.get_receive_label(rand)
            delivery_time = time.time() + rand
            return (delivery_time,r.label,r.color)
        else:
            send_choice = SendChoice.objects.with_id(delivery_option["type"])
	    dt = send_choice.get_delivery_time(time.time())
	    r = ReceiveLabel.get_receive_label(dt-time.time())
            return (dt,r.label,r.color)

    def get_delivery_time(self, send_time):
        if self.time_random:
            time_delay = random.randint(2678400, 8035200)  # between 1 month and 3 months
            return send_time + time_delay
        if self.time_absolute:
            return self.time_delay
        else:
            return send_time + self.time_delay


class WebApp(db.Document):
    """ contains the url corresponding to a given version and os. """

    url = db.StringField(required=True)
    supported_version = db.ListField(default=[])

    @staticmethod
    def get_server_url_from_plateform_instance(plateform_instance=None):
        if plateform_instance is None:
            return WebApp.objects().order_by('id').first().url
        else:
            app = WebApp.objects(supported_version=plateform_instance.app_version).first() 
            if app is not None:
                return app.url
            else:
                return WebApp.objects().order_by('id').first().url





