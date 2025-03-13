import psutil
import platform
from datetime import datetime

class SystemStats:
    def get_stats(self):
        return {
            'cpu': self._get_cpu_stats(),
            'memory': self._get_memory_stats(),
            'disk': self._get_disk_stats(),
            'network': self._get_network_stats(),
            'system': self._get_system_info()
        }

    def _get_cpu_stats(self):
        return {
            'percent': psutil.cpu_percent(interval=1),
            'cores': psutil.cpu_count(),
            'load': psutil.getloadavg()
        }

    def _get_memory_stats(self):
        mem = psutil.virtual_memory()
        return {
            'total': mem.total,
            'available': mem.available,
            'percent': mem.percent,
            'used': mem.used
        }

    def _get_disk_stats(self):
        disk = psutil.disk_usage('/')
        return {
            'total': disk.total,
            'used': disk.used,
            'free': disk.free,
            'percent': disk.percent
        }

    def _get_network_stats(self):
        net_io = psutil.net_io_counters()
        return {
            'bytes_sent': net_io.bytes_sent,
            'bytes_recv': net_io.bytes_recv,
            'packets_sent': net_io.packets_sent,
            'packets_recv': net_io.packets_recv
        }

    def _get_system_info(self):
        return {
            'system': platform.system(),
            'release': platform.release(),
            'version': platform.version(),
            'machine': platform.machine(),
            'processor': platform.processor(),
            'uptime': datetime.fromtimestamp(psutil.boot_time()).strftime("%Y-%m-%d %H:%M:%S")
        } 