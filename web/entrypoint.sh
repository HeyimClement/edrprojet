#!/bin/bash

# Attendre que le dossier de logs soit disponible
while [ ! -d "/var/log/suricata" ]; do
    echo "En attente du dossier /var/log/suricata..."
    sleep 2
done

# S'assurer que les permissions sont correctes
touch /var/log/suricata/fast.log
chown -R nobody:nogroup /var/log/suricata

# Démarrer Gunicorn
exec gunicorn --bind 0.0.0.0:5000 app:app 