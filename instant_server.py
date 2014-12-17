import os
from instant_server.server import app

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    #debug = (port == 5000)
    debug = True
    app.run(host='0.0.0.0', port=port, debug=debug)
