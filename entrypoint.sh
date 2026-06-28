#!/bin/bash

echo "Aguardando banco..."
while ! flask db upgrade; do
    echo "Falhou, tentando de novo em 2s..."
    sleep 2
done

echo "Banco pronto, subindo servidor..."
gunicorn -w 4 -b 0.0.0.0:8000 "app_factory:create_app()"