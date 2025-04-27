import time
import imaplib
import email
from email.header import decode_header
import quopri

def fetch_emails(mail):
    status, messages = mail.search(None, "ALL")
    messages = messages[0].split()

    for msg_num in messages:
        res, msg_data = mail.fetch(msg_num, "(RFC822)")
        for response_part in msg_data:
            if isinstance(response_part, tuple):
                msg = email.message_from_bytes(response_part[1])

                subject, encoding = decode_header(msg["Subject"])[0]
                if isinstance(subject, bytes):
                    subject = subject.decode(encoding if encoding else "utf-8")
                print(f"Assunto: {subject}")

                if msg.is_multipart():
                    for part in msg.walk():
                        content_type = part.get_content_type()
                        content_disposition = str(part.get("Content-Disposition"))

                        if "attachment" in content_disposition:
                            filename = part.get_filename()

                            try:
                                filename = filename.decode("utf-8")
                            except UnicodeDecodeError:
                                filename = filename.decode("latin-1", errors="ignore")
                                print(f"Problema ao decodificar o nome do arquivo: {filename}")

                            with open(f"./downloads/{filename}", "wb") as f:
                                f.write(part.get_payload(decode=True))

def main():
    imap = imaplib.IMAP4_SSL("imap.gmail.com")
    imap.login("timesync.upload@gmail.com", "iqlbpslhqmekvted")

    imap.select("inbox")

    while True:
        fetch_emails(imap)
        time.sleep(300)

    imap.close()
    imap.logout()

if __name__ == "__main__":
    main()
