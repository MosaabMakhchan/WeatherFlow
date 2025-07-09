import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Email service
def send_weather_email(weather_data: dict):
    """Send weather report via email"""
    try:
        msg = MIMEMultipart()
        msg['From'] = email_settings['sender_email']
        msg['To'] = ', '.join(email_settings['recipients'])
        msg['Subject'] = f"Daily Weather Report - {datetime.now().strftime('%Y-%m-%d')}"
        
        # Create email body
        body = "Daily Weather Report\n\n"
        for city, data in weather_data.items():
            body += f"{city}: {data['temperature']}°C, {data['description']}\n"
        
        msg.attach(MIMEText(body, 'plain'))
        
        # Send email
        server = smtplib.SMTP(email_settings['smtp_server'], email_settings['smtp_port'])
        server.starttls()
        server.login(email_settings['sender_email'], email_settings['sender_password'])
        server.send_message(msg)
        server.quit()
        
        print(f"Weather report sent to {email_settings['recipients']}")
    except Exception as e:
        print(f"Failed to send email: {str(e)}")
