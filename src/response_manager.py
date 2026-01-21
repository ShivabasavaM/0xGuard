import os
import subprocess
import time

class ResponseManager:
    def __init__(self):
        self.threat_db = {} # {ip: {'strikes': 0, 'last_seen': time}}
        self.BLOCK_THRESHOLD = 2

    def notify(self, title, message):
        """Native macOS Notification"""
        cmd = f'display notification "{message}" with title "{title}" sound name "Ping"'
        subprocess.run(["osascript", "-e", cmd])

    def block_ip(self, ip):
        """Simulates Blocking an IP"""
        print(f"⛔ [FIREWALL] BLOCKING IP: {ip}")
        self.notify("🛡️ THREAT BLOCKED", f"IP {ip} has been banned.")
        # Actual command (commented out for safety):
        # os.system(f"sudo echo 'block drop from {ip} to any' | pfctl -f -")

    def handle_threat(self, ip):
        now = time.time()
        #if ip.startswith("192.168.") or ip == "127.0.0.1":
            #return # Ignore local IPs
        if ip not in self.threat_db:
            self.threat_db[ip] = {'strikes': 0, 'last_seen': now}
        
        # Reset strikes if quiet for 60s
        if now - self.threat_db[ip]['last_seen'] > 60:
            self.threat_db[ip]['strikes'] = 0
            
        self.threat_db[ip]['last_seen'] = now
        self.threat_db[ip]['strikes'] += 1
        strikes = self.threat_db[ip]['strikes']

        if strikes == 1:
            print(f"⚠️ Warning: Suspicious activity from {ip}")
            self.notify("Security Warning", f"Unusual traffic from {ip}")
        elif strikes == 2:
            print(f"🚨 CRITICAL: Persistence from {ip}")
            self.notify("CRITICAL ALERT", f"Next detection will trigger BLOCK: {ip}")
        elif strikes > self.BLOCK_THRESHOLD:
            self.block_ip(ip)