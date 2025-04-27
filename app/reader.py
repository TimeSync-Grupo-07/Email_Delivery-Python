import os
import imaplib
import email
from email.header import decode_header
import base64

# Configurações
EMAIL_SERVER = os.getenv("EMAIL_SERVER")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", 993))
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

# Pasta para salvar os anexos
DOWNLOAD_FOLDER = "./downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

def connect_mailbox():
    mail = imaplib.IMAP4_SSL(EMAIL_SERVER, EMAIL_PORT)
    mail.login(EMAIL_USER, EMAIL_PASSWORD)
    return mail

def fetch_emails(mail):
    mail.select("inbox")
    status, messages = mail.search(None, "ALL")

    if status != "OK":
        print("Nenhum e-mail encontrado.")
        return

    for num in messages[0].split():
        status, data = mail.fetch(num, "(RFC822)")
        if status != "OK":
            print(f"Erro ao buscar e-mail {num}")
            continue

        msg = email.message_from_bytes(data[0][1])

        for part in msg.walk():
            if part.get_content_maintype() == 'multipart':
                continue
            if part.get('Content-Disposition') is None:
                continue

            filename = part.get_filename()
            if filename:
                filename = decode_header(filename)[0][0]
                if isinstance(filename, bytes):
                    filename = filename.decode()
                if filename.lower().endswith(".pdf"):
                    filepath = os.path.join(DOWNLOAD_FOLDER, filename)
                    with open(filepath, "wb") as f:
                        f.write(part.get_payload(decode=True))
                    print(f"Salvo: {filepath}")

def main():
    mail = connect_mailbox()
    fetch_emails(mail)
    mail.logout()

if __name__ == "__main__":
    main()
