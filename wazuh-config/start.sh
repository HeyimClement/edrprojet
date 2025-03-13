#!/bin/bash

# Configuration de l'agent
sed -i "s/MANAGER_IP/192.168.68.77/g" /var/ossec/etc/ossec.conf

# Démarrage de l'agent
/var/ossec/bin/wazuh-control start

# Maintenir le conteneur en vie
tail -f /var/ossec/logs/ossec.log 