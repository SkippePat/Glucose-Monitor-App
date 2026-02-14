from typing import Optional
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from twilio.rest import Client
from datetime import datetime

class AlertManager:
    """
    Handles glucose level alerts and notifications via SMS and Email
    """
    
    # Class variables for Twilio client and settings
    client = None
    from_number = None
    
    # Email settings
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    email_sender = "diabetes.monitor.alerts@gmail.com"
    email_password = None  # Will be set up later via environment variable
    
    @classmethod
    def _initialize_client(cls):
        """Initialize or reinitialize the Twilio client and email credentials"""
        try:
            # Set up Twilio
            account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
            auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
            cls.from_number = os.environ.get('TWILIO_PHONE_NUMBER')
            
            # Set up email password
            cls.email_password = os.environ.get('EMAIL_PASSWORD')
            
            if account_sid and auth_token:
                cls.client = Client(account_sid, auth_token)
                print("Twilio client initialized successfully")
            else:
                cls.client = None
                print("Missing Twilio credentials")
                
            if cls.email_password:
                print("Email credentials initialized successfully")
                
        except Exception as e:
            cls.client = None
            print(f"Failed to initialize alert clients: {str(e)}")
    
    @classmethod
    def can_send_alerts(cls) -> bool:
        """Check if the system is properly configured to send alerts (either SMS or email)"""
        # Try to initialize the clients if not already set up
        if cls.client is None or cls.email_password is None:
            cls._initialize_client()
            
        # Return true if either SMS or email is configured
        sms_configured = cls.client is not None and cls.from_number is not None
        email_configured = cls.email_password is not None
        
        return sms_configured or email_configured
    
    @classmethod
    def send_email_alert(cls, 
                       to_email: str, 
                       glucose_value: float,
                       timestamp: Optional[datetime] = None,
                       alert_type: str = "high") -> bool:
        """
        Send an email alert for glucose levels outside the target range
        
        Parameters:
        - to_email: Recipient's email address
        - glucose_value: Current glucose reading
        - timestamp: Time of the reading (default: current time)
        - alert_type: Type of alert ("high" or "low")
        
        Returns:
        - bool: True if email was sent successfully, False otherwise
        """
        if not to_email:
            print("No recipient email provided.")
            return False
            
        if not cls.email_password:
            print("Email password not configured, cannot send email alerts.")
            return False
            
        # Create the email content
        time_str = timestamp.strftime("%I:%M %p") if timestamp else datetime.now().strftime("%I:%M %p")
        date_str = timestamp.strftime("%B %d, %Y") if timestamp else datetime.now().strftime("%B %d, %Y")
        
        # Create subject line based on alert type
        if alert_type.lower() == "high":
            subject = f"HIGH GLUCOSE ALERT: {glucose_value:.0f} mg/dL"
            color = "#ff6b6b"  # Red for high
            alert_heading = "HIGH GLUCOSE ALERT"
        elif alert_type.lower() == "low":
            subject = f"LOW GLUCOSE ALERT: {glucose_value:.0f} mg/dL"
            color = "#ffc145"  # Amber for low
            alert_heading = "LOW GLUCOSE ALERT"
        else:
            subject = f"Glucose Alert: {glucose_value:.0f} mg/dL"
            color = "#4da6ff"  # Blue for normal
            alert_heading = "GLUCOSE ALERT"
            
        # Create a nice HTML email with styling
        html_message = f"""
        <html>
            <head>
                <style>
                    body {{
                        font-family: Arial, sans-serif;
                        margin: 0;
                        padding: 0;
                        background-color: #f4f4f4;
                    }}
                    .container {{
                        width: 90%;
                        max-width: 600px;
                        margin: 20px auto;
                        background: white;
                        border-radius: 10px;
                        overflow: hidden;
                        box-shadow: 0 0 10px rgba(0,0,0,0.1);
                    }}
                    .header {{
                        background-color: {color};
                        color: white;
                        padding: 20px;
                        text-align: center;
                    }}
                    .content {{
                        padding: 20px;
                    }}
                    .value {{
                        font-size: 48px;
                        font-weight: bold;
                        text-align: center;
                        margin: 20px 0;
                        color: {color};
                    }}
                    .details {{
                        margin: 20px 0;
                        border-top: 1px solid #ddd;
                        border-bottom: 1px solid #ddd;
                        padding: 15px 0;
                    }}
                    .footer {{
                        text-align: center;
                        font-size: 12px;
                        color: #999;
                        padding: 10px 20px 20px;
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>{alert_heading}</h1>
                    </div>
                    <div class="content">
                        <p>Your glucose level is currently:</p>
                        <div class="value">{glucose_value:.0f} mg/dL</div>
                        <div class="details">
                            <p><strong>Time:</strong> {time_str}</p>
                            <p><strong>Date:</strong> {date_str}</p>
                            <p><strong>Status:</strong> {alert_type.upper()}</p>
                        </div>
                        <p>Please take appropriate action according to your diabetes management plan.</p>
                    </div>
                    <div class="footer">
                        <p>This is an automated alert from your Diabetes Management Dashboard. Please do not reply to this email.</p>
                    </div>
                </div>
            </body>
        </html>
        """
        
        # Plain text alternative
        text_message = f"""
        {alert_heading}
        
        Your glucose level is currently: {glucose_value:.0f} mg/dL
        
        Time: {time_str}
        Date: {date_str}
        Status: {alert_type.upper()}
        
        Please take appropriate action according to your diabetes management plan.
        
        This is an automated alert from your Diabetes Management Dashboard.
        """
        
        try:
            # Create message container
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = cls.email_sender
            msg['To'] = to_email
            
            # Attach plain and HTML versions
            msg.attach(MIMEText(text_message, 'plain'))
            msg.attach(MIMEText(html_message, 'html'))
            
            # Connect to the server and send
            if cls.email_password:
                server = smtplib.SMTP(cls.smtp_server, cls.smtp_port)
                server.starttls()
                server.login(cls.email_sender, cls.email_password)
                server.send_message(msg)
                server.quit()
            
            print(f"Email alert sent to {to_email}")
            return True
        except Exception as e:
            print(f"Failed to send email alert: {str(e)}")
            return False
    
    @classmethod
    def send_glucose_alert(cls, 
                         to_number: Optional[str] = None, 
                         glucose_value: float = 0.0, 
                         timestamp: Optional[datetime] = None,
                         alert_type: str = "high",
                         to_email: Optional[str] = None) -> bool:
        """
        Send alerts for glucose levels outside the target range via SMS and email
        
        Parameters:
        - to_number: Recipient's phone number
        - glucose_value: Current glucose reading
        - timestamp: Time of the reading (default: current time)
        - alert_type: Type of alert ("high" or "low")
        - to_email: Optional recipient's email address
        
        Returns:
        - bool: True if at least one message was sent successfully, False otherwise
        """
        success = False
        
        # Try to send SMS alert
        if to_number:
            try:
                # Create alert message based on type
                time_str = timestamp.strftime("%I:%M %p") if timestamp else datetime.now().strftime("%I:%M %p")
                
                if alert_type.lower() == "high":
                    message = f"⚠️ HIGH GLUCOSE ALERT: Your glucose level is {glucose_value:.0f} mg/dL at {time_str}, which is above your target range."
                elif alert_type.lower() == "low":
                    message = f"⚠️ LOW GLUCOSE ALERT: Your glucose level is {glucose_value:.0f} mg/dL at {time_str}, which is below your target range."
                else:
                    message = f"GLUCOSE ALERT: Your glucose level is {glucose_value:.0f} mg/dL at {time_str}."
                
                # Make sure client is initialized
                if cls.client is None:
                    cls._initialize_client()
                
                if cls.client and cls.from_number:
                    # Send SMS via Twilio
                    sms = cls.client.messages.create(
                        body=message,
                        from_=cls.from_number,
                        to=to_number
                    )
                    print(f"Alert sent to {to_number}, SID: {sms.sid}")
                    success = True
                else:
                    print("SMS alerts not configured properly")
            except Exception as e:
                print(f"Failed to send SMS alert: {str(e)}")
        
        # Try to send email alert
        if to_email:
            try:
                email_sent = cls.send_email_alert(
                    to_email=to_email,
                    glucose_value=glucose_value,
                    timestamp=timestamp,
                    alert_type=alert_type
                )
                success = success or email_sent
            except Exception as e:
                print(f"Failed to send email alert: {str(e)}")
                
        return success