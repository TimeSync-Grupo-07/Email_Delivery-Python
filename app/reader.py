import os
import time
import imaplib
import email
from email.header import decode_header
import quopri
import paramiko

# Função para enviar os arquivos via SCP
def send_file_via_scp(filename, filepath):
    # Lendo as variáveis de ambiente
    private_key_path = os.getenv("SSH_PRIVATE_KEY_PATH", "/path/to/private/key")
    ssh_host = os.getenv("SSH_HOST", "MAQUINA_PRIVADA_IP")
    ssh_user = os.getenv("SSH_USER", "USUARIO_SSH")

    # Criar a conexão SSH
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(ssh_host, username=ssh_user, key_filename=private_key_path)

    # Usando SCP para enviar o arquivo
    scp = paramiko.SFTPClient.from_transport(ssh.get_transport())
    scp.put(filepath, f'/path/to/remote/directory/{filename}')
    scp.close()
    ssh.close()
    print(f"Arquivo {filename} enviado para a máquina privada.")

# Função para buscar os e-mails
def fetch_emails(mail):
    status, messages = mail.search(None, "ALL")
    messages = messages[0].split()

    for msg_num in messages:
        res, msg_data = mail.fetch(msg_num, "(RFC822)")
        for response_part in msg_data:
            if isinstance(response_part, tuple):
                msg = email.message_from_bytes(response_part[1])

                # Mostrar o assunto
                subject, encoding = decode_header(msg["Subject"])[0]
                if isinstance(subject, bytes):
                    subject = subject.decode(encoding if encoding else "utf-8")
                print(f"Assunto: {subject}")

                # Verificar anexos
                if msg.is_multipart():
                    for part in msg.walk():
                        content_type = part.get_content_type()
                        content_disposition = str(part.get("Content-Disposition"))

                        # Se for um anexo
                        if "attachment" in content_disposition:
                            filename = part.get_filename()

                            try:
                                filename = filename.decode("utf-8")
                            except UnicodeDecodeError:
                                filename = filename.decode("latin-1", errors="ignore")
                                print(f"Problema ao decodificar o nome do arquivo: {filename}")

                            # Salvar o arquivo temporariamente
                            filepath = f"./downloads/{filename}"
                            with open(filepath, "wb") as f:
                                f.write(part.get_payload(decode=True))

                            # Enviar o arquivo para a máquina privada via SCP
                            send_file_via_scp(filename, filepath)

                            # Remover o arquivo local após envio
                            os.remove(filepath)

def main():
    # Conectar à caixa de entrada
    imap = imaplib.IMAP4_SSL("imap.gmail.com")
    imap.login("timesync.upload@gmail.com", "iqlbpslhqmekvted")

    # Selecionar a caixa de entrada
    imap.select("inbox")

    while True:
        fetch_emails(imap)
        time.sleep(300)  # Espera 5 minutos (300 segundos)

    imap.close()
    imap.logout()

if __name__ == "__main__":
    main()
