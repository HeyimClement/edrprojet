FROM ubuntu:22.04

# Installation des dépendances
RUN apt-get update && apt-get install -y \
    suricata \
    openssh-server \
    sudo \
    net-tools \
    iproute2 \
    logrotate \
    && rm -rf /var/lib/apt/lists/*

# Configuration SSH
RUN mkdir -p /var/run/sshd
RUN echo 'root:password' | chpasswd
RUN sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config
RUN sed -i 's/#PasswordAuthentication yes/PasswordAuthentication yes/' /etc/ssh/sshd_config

# Création des répertoires nécessaires
RUN mkdir -p /var/log/suricata /var/lib/suricata/rules && \
    chown -R root:root /var/log/suricata && \
    chmod 755 /var/log/suricata

# Copier d'abord les fichiers de configuration
COPY suricata.yaml /etc/suricata/
COPY rules/local.rules /var/lib/suricata/rules/local.rules
COPY start.sh /start.sh

# Vérifier les permissions des fichiers
RUN chmod 644 /var/lib/suricata/rules/local.rules && \
    chmod 644 /etc/suricata/suricata.yaml

# Supprimer les règles par défaut après avoir copié nos règles
RUN rm -f /etc/suricata/rules/*.rules

# Vérifier que les fichiers existent
RUN ls -la /var/lib/suricata/rules/local.rules && \
    ls -la /etc/suricata/suricata.yaml

# Vérifier la configuration
RUN suricata -T -c /etc/suricata/suricata.yaml -v

# Rendre le script de démarrage exécutable
RUN chmod +x /start.sh

# Exposer le port SSH
EXPOSE 22

# Démarrer SSH et Suricata
CMD ["/start.sh"] 