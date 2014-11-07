# Procedure a suivre pour installer le depot et les acces a heroku.

### Linux/MacOs
installer git, python, pip, virtualenv et virtualenvwrapper. 
(pour deploiement : installer heroku , configurer identifiants, demander acces a l'application.)
optionnel : configuer github pour utiliser des cles ssh (permet d'eviter de taper son mdp a chaque push/pull)

cloner le depot

    cd src
    git clone git@github.com:gauthierpetetin/pictever_server.git
    (ou https://github.com/gauthierpetetin/pictever_server.git si pas de ssh)
    cd pictever_server

savoir dans quelle branche on se trouve:

    git branch

-> une seule branche pour le moment :master

rajouter la remote de l'application heroku : sur le site de heroku / app / settings /info se trouve une url : 
(notif -> git@heroku.com:notif-server.git)
(instant_server -> git@heroku.com:instant-server.git)

    git remote add heroku_instant git@heroku.com:instant-pictever.git
    git remote add heroku_notif git@heroku.com:notif-pictever.git

test : voir les logs de l'appli heroku

    heroku logs --app instant-pictever --tail
    heroku logs --app notif-pictever --tail

developpement : 
 petit changement -> a faire dans la branche master

    git checkout master 
    
pour verifier 
    
    git branch

faire des pushs tres souvent, max 1h (sinon cf moyen/gros changements)

moyen/gros changement -> creer une branche

    git checkout -b mon_changement_a_moi
    ... travail...

une fois finis, merge dans master

    git checkout master
    git merge mon_changement_a_moi
    ... resolution des conflit...
    git commit -am "mon_changement_a_moi est fini"
    git push origin master


####deploiement
Le deploiement est independant du developpement, TOUJOURS pusher sur github avant heroku : verifier dans votre historique si la derniere commande est git push origin master

changer de branch pour la version de production.
instant_server :

    git checkout instant_server_prod

notification :

    git checkout notif_server_prod

pour verifier 

    git branch

merge master dans la branche de production

    git merge master
    ...resolution des conflits

verifier le Procfile ( pour savoir quelle application sera lancee)

    cat Procfile

si vous etes dans instant_server vous devez voir 

    web: python instant_server.py

ou 

    web: gunicorn instant_server.server:app --workers 3 --log-file -

sinon pour les notifications

    notif: python notif_server.py

deploiement:
push heroku puis push github
notification

    git push heroku_notif notif_server_prod:master
    git push origin notif_server_prod

instant_server

    git push heroku_instant instant_server_prod:master
    git push origin instant_server_prod

retour dans la branche master

   git checkout master


Description des urls :

    Android GCM API Key : AIzaSyCWn_dNhBHFITuVAOAG2r_KDlV5KROg-Oo
    Android GCM SENDER_ID (Project Number) : 952675823733

#Inscription/Login

###0. SIGN UP :
    requete: POST
    url: "\signup"
    fields : "email", "password"
    response: 
        success -> http200
        error -> http406 (mail deja utilise)
-> creer un compte pour l’utilisateur : (recoit mail et hash du mdp)

###1.  define_first_phone_number
    requete: POST
    @login_required
    url: "\define_first_phone_number"
    fields : "phone_number", "reg_id", "os"
    response: 
        success -> http200
        error -> http406 (le numero de telephone est deja pris par un autre compte)
-> definit le numero de telephone de l’utilisateur

###3. LOGIN : 
    requete: POST
    url: "\login"
    fields : "email", "password", "os", "reg_id","app_version"
    response: 
        success -> http200
        wrong credentials -> http401
    return : "user_id","web_app_url","ios_version_needed","android_version_needed",
	     "force_update","amazon_app_id","aws_account_id","cognito_pool_id","cognito_role_unauth","cognito_role_auth",
	     "bucket_name","cloudfront","android_update_link","ios_update_link"
-> to login into an account. 


#Envoi/reception de message$

###10. SEND: 
    requete: POST
    @login_required
    url: "\send"
    fields :"message",
            "photo_id",  -- not necessary
            "video_id",  -- not necessary
            "sound_id",  -- not necessary
            "receiver_ids", (list of ids) 
   			list contenant un id ou un numero : un id est precede de "id" et un numero de "num" ["id045sfdgfg", "num00336456548"]
            "delivery_option" : JSON 
		  	{
            		"type" : "hour"  # chaine de caractere du style (“min”, “hour”, “day”, “week”, ….)
            		"time_zone" : 0  #entier en heure, offset par rapport a UTC.
            		"parameters" : ... #(differents parametres specifique au choix d'envoi du message)
        		}
    response: 
        success -> http200
        wrong credentials -> http401
-> envoit un message
###11. RECEIVE_ALL: 
    requete: GET
    @login_required
    url: "\receive_all"
    fields :"ts" : timestamp de la derniere reception de messages. 
    response: 
        success -> http200 + JSON
        wrong credentials -> http401
    return:
    {
    	“ts”:timestamp de la requete a la base de donnee ( a enregistrer pour une prochaine requete )
    	“new_messages” :
    	[{“from_email”: “bob@bob.com”, (oblige dans le cas ou l’envoyeur n’est pas dans les contacts)
    	“from_numero” : “0033678457865” (num de l’envoyeur, meme remarque),
    	“from_id” : “1231rfwsdr32r3q4wf24” (id de l’envoyeur),
    	“message” : “blabla”,
    	“created_at” :timestamp de l’envoit, etabli par le server (a voir avec le fuseau horaire) ( le but est de l’affiche dans le fuseau du client qui recoit le message)
    	“photo_id” : “id...”,
	“video_id” : “id...”,
	“sound_id” : “id...”,
    	}]
    }

###12. RESEND: 
    requete: POST
    @login_required
    url: "\resend"
    fields :"message_id"
    response: 
        success -> http200
        wrong credentials -> http401
-> update le delivery_time et le notif_delivered du message en question pour le renvoyer dans le futur.

###13. GET_SEND_CHOICES: 
    requete: GET
    @login_required
    url: "\get_send_choices"
    response : 
        success -> http200 + JSON
        wrong credentials -> http401
reponse : list de JSON : 
(+ "calendar" qui doit toujours etre affiche par les applis)
    [
    {
        "order_id" : "0",
        "key" : "s5s421sdg14sg",
        "send_label" : "One Day"
     },
    ]

#Reglages/Contacts/...

###14. GET_NUMBER_OF_FUTURE_MESSAGES: 
    requete: GET
    @login_required
    url: "\get_number_of_future_messages"
    response : 
        success -> http200 + str(nombre de messages en attente)
        wrong credentials -> http401
    return : nombre de messages en attente (i.e notif_delivered=False)

###15. GET_MY_STATUS: 
    requete: GET
    @login_required
    url: "\get_my_status"
    response : 
        success -> http200 + status
        wrong credentials -> http401
    return : statut de l'utilisateur (depend du nombre de messages envoyes actuellement en attente)

###15. BLOCK_CONTACTS: 
    requete: POST
    @login_required
    url: "\block_contacts"
    fields : "contacts_to_block"
    response : 
        success -> http200
        wrong credentials -> http401
-> bloque tous les messages en attente qui ont été soit émis par le contact à bloquer à destination du current user, soit émis par le current user à destination du contact à bloquer. 

###21.UPLOAD_CONTACTS:
    requete: POST
    @login_required
    url: "\upload_contacts"
    fields :"contacts" 
    response: 
        success -> http200 + JSON
        wrong credentials -> http401
-> Envoit une liste de NUMEROS DE TEL depuis l’application (format JSON)
ex de "contacts" : 
    [“00336930303030”, “004454635645662” …] 
retourne un Json de la forme:
    [
    	{
    	  	"phoneNumber1" : "00336930303030",
        	"email" : "truc@bidule.com",
        	“user_id”:”fsd14dsf43gt435g3dg” 
    	}
    ]
Les contacts qui ne sont pas sur Pictever ne sont pas presents dans cette liste.





