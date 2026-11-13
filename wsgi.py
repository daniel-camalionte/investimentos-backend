"""Ponto de entrada WSGI (uWSGI/Passenger). O servidor procura o objeto `application`."""

from app import create_app

application = create_app()

# alias para servidores/configurações que esperam `app`
app = application

if __name__ == "__main__":  # execução local rápida: python wsgi.py
    application.run(host="127.0.0.1", port=5000)
