import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

def test_email_connection():
    try:
        # Create a test email
        msg = MIMEMultipart()
        msg['From'] = os.getenv('GMAIL_EMAIL')
        msg['To'] = os.getenv('RECIPIENT_EMAIL')
        msg['Subject'] = 'Test Email from AI News Digest'
        msg.attach(MIMEText('This is a test email to verify the connection.', 'plain'))
        
        print(f"Sending email from {os.getenv('GMAIL_EMAIL')} to {os.getenv('RECIPIENT_EMAIL')}")
        
        # Connect to Gmail SMTP server
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(os.getenv('GMAIL_EMAIL'), os.getenv('GMAIL_APP_PASSWORD'))
            server.send_message(msg)
            print("Email sent successfully!")
            
    except Exception as e:
        print(f"Error sending email: {str(e)}")

if __name__ == "__main__":
    test_email_connection()
