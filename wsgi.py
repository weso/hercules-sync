""" Entry point of the hercules_sync server.
"""

from hercules_sync import create_app

app = create_app()

if __name__ == '__main__':
    if app.config['ENV'] == 'production':
        from waitress import serve
        serve(app, host='0.0.0.0', port=5000)
    else:
        app.run(host='0.0.0.0')
