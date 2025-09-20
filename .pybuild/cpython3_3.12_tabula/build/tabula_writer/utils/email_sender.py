import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os

def send_email(details, attachment_path):
    """
    Sends an email with an attachment.
    'details' is a dictionary containing: to, subject, body, smtp_server, port, username, password.
    Returns a tuple: (success: bool, message: str)
    """
    try:
        msg = MIMEMultipart()
        msg['From'] = details['username']
        msg['To'] = details['to']
        msg['Subject'] = details['subject']

        msg.attach(MIMEText(details['body'], 'plain'))

        # Attach the file
        filename = os.path.basename(attachment_path)
        with open(attachment_path, "rb") as attachment:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f"attachment; filename= {filename}")
        msg.attach(part)

        # Connect to server and send
        server = smtplib.SMTP(details['smtp_server'], int(details['port']))
        server.starttls() # Secure the connection
        server.login(details['username'], details['password'])
        text = msg.as_string()
        server.sendmail(details['username'], details['to'], text)
        server.quit()
        
        return (True, "Email sent successfully!")

    except smtplib.SMTPAuthenticationError:
        return (False, "Authentication failed. Please check your username and password. You may also need to enable 'less secure apps' or use an 'app password' for your email account.")
    except Exception as e:
        return (False, f"An error occurred: {e}")
