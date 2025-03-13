import re
from datetime import datetime, timedelta
import os
from collections import defaultdict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SuricataLogParser:
    def __init__(self, log_path="/var/log/suricata/fast.log"):
        self.log_path = log_path
        
    def parse_log_line(self, line):
        """Parse une ligne de log Suricata."""
        pattern = r'(\d{2}/\d{2}/\d{4}-\d{2}:\d{2}:\d{2}\.\d+)\s+\[\*\*\]\s+\[([^\]]+)\]\s+\[([^\]]+)\]\s+([^\[]+)\s+\[\*\*\]\s+\[Classification:\s+([^\]]+)\]\s+\[Priority:\s+(\d+)\]\s+{([^}]+)}\s+([^\s]+)\s+->\s+([^\s]+)'
        match = re.match(pattern, line)
        
        if match:
            timestamp, sid, msg_type, msg, classification, priority, protocol, src, dst = match.groups()
            return {
                'timestamp': timestamp,
                'sid': sid,
                'type': msg_type.strip(),
                'message': msg.strip(),
                'classification': classification.strip(),
                'priority': int(priority),
                'protocol': protocol,
                'source': src,
                'destination': dst
            }
        return None

    def get_recent_alerts(self, limit=None):
        """Récupère les alertes récentes du fichier de log."""
        alerts = []
        try:
            with open(self.log_path, 'r') as f:
                for line in f:
                    alert = self.parse_log_line(line.strip())
                    if alert:
                        alerts.append(alert)
            return alerts[-limit:] if limit else alerts
        except Exception as e:
            logger.error(f"Erreur lors de la lecture du fichier log: {e}")
            return []

    def get_statistics(self):
        """Génère des statistiques à partir des alertes."""
        alerts = self.get_recent_alerts()
        stats = {
            'total': len(alerts),
            'by_type': {},
            'by_source': {},
            'by_classification': {},
            'by_priority': {},
            'timeline': {},
            'recent_alerts': alerts[:10]
        }
        
        for alert in alerts:
            # Comptage par type
            alert_type = alert['type']
            stats['by_type'][alert_type] = stats['by_type'].get(alert_type, 0) + 1
            
            # Comptage par source
            source = alert['source']
            stats['by_source'][source] = stats['by_source'].get(source, 0) + 1
            
            # Comptage par classification
            classification = alert['classification']
            stats['by_classification'][classification] = stats['by_classification'].get(classification, 0) + 1
            
            # Comptage par priorité
            priority = alert['priority']
            stats['by_priority'][priority] = stats['by_priority'].get(priority, 0) + 1
            
            # Timeline (par heure)
            try:
                timestamp = datetime.strptime(alert['timestamp'], '%m/%d/%Y-%H:%M:%S.%f')
                hour_key = timestamp.strftime('%H:00')
                stats['timeline'][hour_key] = stats['timeline'].get(hour_key, 0) + 1
            except Exception as e:
                logger.error(f"Erreur lors du parsing de la date: {e}")

        return stats

class SuricataLogReader:
    def __init__(self, log_file):
        self.log_file = log_file
        self._ensure_log_file()

    def _ensure_log_file(self):
        """S'assure que le fichier de log existe et est accessible"""
        try:
            if not os.path.exists(self.log_file):
                logger.warning(f"Fichier de log non trouvé: {self.log_file}")
                directory = os.path.dirname(self.log_file)
                if not os.path.exists(directory):
                    os.makedirs(directory)
                open(self.log_file, 'a').close()
            
            # Log des informations de debug
            st = os.stat(self.log_file)
            logger.info(f"Fichier log: {self.log_file}")
            logger.info(f"Taille: {st.st_size}")
            logger.info(f"Permissions: {oct(st.st_mode)[-3:]}")
            logger.info(f"UID/GID: {st.st_uid}/{st.st_gid}")
            
        except Exception as e:
            logger.error(f"Erreur lors de la vérification du fichier: {str(e)}")

    def get_alerts(self, limit=100, since=None):
        """Récupère les alertes avec pagination et filtrage par date"""
        alerts = []
        try:
            if not os.path.exists(self.log_file):
                logger.error(f"Fichier de log introuvable: {self.log_file}")
                return alerts

            with open(self.log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                logger.info(f"Nombre de lignes lues: {len(lines)}")
                
                # Inverser l'ordre des lignes pour avoir les plus récentes en premier
                lines.reverse()
                
                # Afficher les 3 premières lignes pour debug
                for i, line in enumerate(lines[:3]):
                    logger.info(f"Exemple ligne {i+1}: {line.strip()}")
                
                for line in lines:
                    try:
                        alert = self._parse_alert(line)
                        if alert:
                            # Filtrer les alertes "SSH version string"
                            if not (alert.get('classification') == 'Generic Protocol Command Decode' 
                                   and 'SSH version string' in alert.get('message', '')):
                                # Vérifier la date si spécifiée
                                if since:
                                    alert_time = self._parse_timestamp(alert['timestamp'])
                                    if alert_time < since:
                                        continue
                                alerts.append(alert)
                    except Exception as e:
                        logger.warning(f"Ligne non parsée: {line}")

            logger.info(f"Nombre d'alertes trouvées (après filtrage): {len(alerts)}")

        except Exception as e:
            logger.error(f"Erreur lors de la lecture des alertes: {str(e)}")
            logger.exception(e)

        # Retourner les alertes (déjà dans l'ordre inverse car lines.reverse())
        return alerts[:limit] if limit else alerts

    def _parse_alert(self, line):
        """Parse une ligne de log en dictionnaire d'alerte"""
        try:
            # Pattern mis à jour pour correspondre au format exact des logs Suricata
            pattern = r'(\d{2}/\d{2}/\d{4}-\d{2}:\d{2}:\d{2}\.\d+)\s+\[\*\*\]\s+\[(\d+:\d+:\d+)\]\s+([^\[]+)\s+\[\*\*\]\s+\[Classification:\s+([^\]]+|\(null\))\]\s+\[Priority:\s+(\d+)\]\s+\{([^\}]+)\}\s+([^\s]+)\s+->\s+([^\s]+)'
            
            match = re.match(pattern, line)
            if match:
                # Nettoyer la classification si elle est (null)
                classification = match.group(4)
                if classification == '(null)':
                    classification = 'Non classifié'

                alert = {
                    'timestamp': match.group(1),
                    'signature_id': match.group(2),
                    'message': match.group(3).strip(),
                    'classification': classification,
                    'priority': match.group(5),
                    'protocol': match.group(6),
                    'source': match.group(7),
                    'destination': match.group(8).split(':')[0],  # Enlever le port de la destination
                    'raw': line
                }
                logger.debug(f"Alerte parsée: {alert}")
                return alert
            else:
                logger.debug(f"Ligne non parsée: {line}")
                
        except Exception as e:
            logger.error(f"Erreur lors du parsing: {str(e)}, ligne: {line}")
            logger.exception(e)
        
        return None

    def get_stats(self, hours=24):
        """Calcule les statistiques des alertes"""
        since = datetime.now() - timedelta(hours=hours)
        alerts = self.get_alerts(limit=1000, since=since)
        
        stats = {
            'total': len(alerts),
            'by_priority': defaultdict(int),
            'by_classification': defaultdict(int),
            'by_protocol': defaultdict(int),
            'timeline': defaultdict(int),
            
            # Statistiques SSH détaillées
            'ssh_stats': {
                'scans': len([
                    a for a in alerts 
                    if '[SCAN]' in a.get('message', '')
                ]),
                'auth_failures': len([
                    a for a in alerts 
                    if '[AUTH]' in a.get('message', '') 
                    and 'réussi' not in a.get('message', '').lower()
                ]),
                'bruteforce': len([
                    a for a in alerts 
                    if '[BRUTEFORCE]' in a.get('message', '')
                ]),
                'successful_logins': len([
                    a for a in alerts 
                    if '[AUTH]' in a.get('message', '') 
                    and 'réussi' in a.get('message', '').lower()
                ]),
                'dos_attempts': len([
                    a for a in alerts 
                    if '[DOS]' in a.get('message', '')
                ])
            }
        }

        for alert in alerts:
            stats['by_priority'][alert['priority']] += 1
            stats['by_classification'][alert['classification']] += 1
            stats['by_protocol'][alert['protocol']] += 1
            
            try:
                hour = self._parse_timestamp(alert['timestamp']).strftime('%Y-%m-%d %H:00')
                stats['timeline'][hour] += 1
            except:
                pass

        # Debug des alertes SSH
        ssh_alerts = [
            a for a in alerts 
            if ('SSH' in a.get('classification', '') or 'SSH' in a.get('message', ''))
        ]
        logger.info(f"Nombre total d'alertes SSH trouvées: {len(ssh_alerts)}")
        for alert in ssh_alerts[:5]:  # Afficher les 5 premières alertes SSH pour debug
            logger.info(f"Alerte SSH: {alert}")

        return stats

    def _parse_timestamp(self, timestamp):
        """Parse une chaîne timestamp en objet datetime"""
        try:
            return datetime.strptime(timestamp, '%m/%d/%Y-%H:%M:%S.%f')
        except ValueError as e:
            logger.error(f"Erreur parsing timestamp: {timestamp}, {str(e)}")
            return datetime.now() 