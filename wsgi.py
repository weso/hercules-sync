""" Entry point of the hercules_sync server.
"""

from hercules_sync import create_app

app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0')
