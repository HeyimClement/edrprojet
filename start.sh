#!/bin/bash

# Créer les répertoires de logs si nécessaire
mkdir -p /var/log/suricata
chmod 755 /var/log/suricata

# Créer les fichiers de log s'ils n'existent pas
touch /var/log/suricata/fast.log
touch /var/log/suricata/eve.json
touch /var/log/suricata/suricata.log
chmod 644 /var/log/suricata/*.log
chmod 644 /var/log/suricata/eve.json

# Vérifier les règles
echo "Vérification des règles Suricata..."
suricata -T -c /etc/suricata/suricata.yaml -v

# Démarrer SSH
/usr/sbin/sshd

# Démarrer Suricata en mode verbose
suricata -c /etc/suricata/suricata.yaml -i eth0 -v

# Attendre que Suricata démarre
sleep 2

# Vérifier que Suricata est en cours d'exécution
if ! pgrep suricata > /dev/null; then
    echo "Erreur: Suricata n'a pas démarré correctement"
    exit 1
fi

echo "Suricata démarré avec succès"

# Suivre les logs
tail -f /var/log/suricata/suricata.log /var/log/suricata/fast.log 