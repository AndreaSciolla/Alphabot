import paramiko

def esegui_comando_remoto(hostname, username, password, comando):
    
    client = paramiko.SSHClient()
    
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        
        client.connect(hostname, username=username, password=password)
        print(f"Connesso a {hostname} come {username}")
        
        client.exec_command('ulimit -u unlimited; ulimit -n unlimited')
        
        stdin, stdout, stderr = client.exec_command(comando)
        
        output = stdout.read().decode('utf-8')
        errori = stderr.read().decode('utf-8')

        if output:
            print(f"Output:\n{output}")
        if errori:
            print(f"Errori:\n{errori}")
    
    except Exception as e:
        print(f"Errore nella connessione o nell'esecuzione del comando: {e}")
    
    finally:
      
        client.close()

hostname = '192.168.1.137'
username = 'pi'
password = 'raspberry'
comando = 'sudo shutdown -h now'  

esegui_comando_remoto(hostname, username, password, comando)
