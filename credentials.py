def python_postgresql():
    connect_str = "dbname='mircs' user='mircs' host='localhost' " + \
              "password='serrelab'"
    return connect_str


def postgresql_credentials():
    return {
            'username': 'imagedatabase',
            'password': 'serrelab'
           }


def postgresql_connection(port=''):
    unpw = postgresql_credentials()
    params = {
        'database': 'imagedatabase',
        'user': unpw['username'],
        'password': unpw['password'],
        'host': 'localhost',
        'port': port,
    }
    return params


def x7_credentials():
    return {
            'username': 'imagedatabase',
            'password': 'serrelab',
            'ssh_address': 'x7.clps.brown.edu'
           }

