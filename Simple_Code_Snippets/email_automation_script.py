import smtplib
import imaplib
import email
import schedule
import time
import os
import logging
import json
import csv
import io
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import base64
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.auth.transport.requests import Request
from datetime import datetime
import re
from collections import defaultdict
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
import pdfplumber

# Ensure NLTK resources are downloaded (run once)
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('vader_lexicon')
except LookupError:
    nltk.download('vader_lexicon')


# Configuration (Move to a separate config file/database for production)
CONFIG_FILE = "config.json"

def load_config(config_file):
    with open(config_file, 'r') as f:
        return json.load(f)

config = load_config(CONFIG_FILE)


# Logging Setup
logging.basicConfig(filename=config['log_file'], level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Email Sending Functions (SMTP)

def create_oauth2_message(user_id, access_token, message):
    """Creates OAuth2 authenticated message."""
    auth_string = base64.urlsafe_b64encode(f'user={user_id}\x01auth=Bearer {access_token}\x01\x01'.encode()).decode('ascii')
    return message.as_bytes() + b'\r\n.\r\n' + f'AUTH XOAUTH2 {auth_string}'.encode()

def send_email(recipient, subject, body, attachment_paths=None, cc=None, bcc=None, is_html=False):
    """Sends an email using SMTP with OAuth2 authentication."""
    try:
        credentials = Credentials.from_authorized_user_file(config['token_path'], config['scopes'])
        if not credentials or not credentials.valid:
            if credentials and credentials.expired and credentials.refresh_token:
                credentials.refresh(Request())
            else:
                print('Please run the authentication script to generate a token.')
                logging.error("OAuth2 token invalid or missing.  Ensure authentication is completed.")
                return False
            with open(config['token_path'], 'w') as token:
                json.dump(credentials.to_json(), token)


        message = MIMEMultipart()
        message['to'] = recipient
        message['from'] = config['sender_email']
        message['subject'] = subject

        if cc:
            message['cc'] = cc
        if bcc:
            message['bcc'] = bcc


        if is_html:
            message.attach(MIMEText(body, 'html'))
        else:
            message.attach(MIMEText(body, 'plain'))

        if attachment_paths:
            for attachment_path in attachment_paths:
                try:
                    with open(attachment_path, "rb") as attachment:
                        part = MIMEBase("application", "octet-stream")
                        part.set_payload(attachment.read())
                        encoders.encode_base64(part)
                        part.add_header(
                            "Content-Disposition",
                            f"attachment; filename= {os.path.basename(attachment_path)}",
                        )
                        message.attach(part)
                except FileNotFoundError:
                    logging.error(f"Attachment file not found: {attachment_path}")
                    print(f"Attachment file not found: {attachment_path}")
                    return False



        # Gmail's SMTP server requires SSL.
        try:
            service = build('gmail', 'v1', credentials=credentials)
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
            send_message = {'raw': raw_message}
            message = service.users().messages().send(userId="me", body=send_message).execute()
            logging.info(f"Email sent successfully to {recipient}, Message Id: {message['id']}")
            print(f"Email sent successfully to {recipient}, Message Id: {message['id']}")
            return True
        except HttpError as error:
             logging.error(f"An error occurred: {error}")
             print(f"An error occurred: {error}")
             return False

    except Exception as e:
        logging.error(f"Error sending email: {e}")
        print(f"Error sending email: {e}")
        return False


def send_bulk_emails(recipients, subject, body, data_source, data_mapping, attachment_paths=None, is_html=False):
    """Sends personalized emails to multiple recipients using data from a CSV or other data source."""
    try:
        with open(data_source, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                recipient = row[data_mapping['recipient']]
                personalized_subject = subject.format(**row)
                personalized_body = body.format(**row)

                if not send_email(recipient, personalized_subject, personalized_body, attachment_paths, is_html=is_html):
                    logging.error(f"Failed to send email to {recipient}")
                    print(f"Failed to send email to {recipient}")

        logging.info("Bulk emails sent (or attempted) to all recipients.")
        print("Bulk emails sent (or attempted) to all recipients.")
        return True

    except FileNotFoundError:
        logging.error(f"Data source file not found: {data_source}")
        print(f"Data source file not found: {data_source}")
        return False
    except Exception as e:
        logging.error(f"Error sending bulk emails: {e}")
        print(f"Error sending bulk emails: {e}")
        return False


# Email Receiving and Processing (IMAP)

def authenticate_imap():
    """Authenticates with the IMAP server using OAuth2."""
    try:
        credentials = Credentials.from_authorized_user_file(config['token_path'], config['scopes'])
        if not credentials or not credentials.valid:
            if credentials and credentials.expired and credentials.refresh_token:
                credentials.refresh(Request())
            else:
                print('Please run the authentication script to generate a token.')
                logging.error("OAuth2 token invalid or missing.  Ensure authentication is completed.")
                return None
            with open(config['token_path'], 'w') as token:
                json.dump(credentials.to_json(), token)

        # Generate the XOAUTH2 string
        auth_string = base64.b64encode(f'user={config["sender_email"]}\x01auth=Bearer {credentials.token}\x01\x01'.encode()).decode('ascii')

        mail = imaplib.IMAP4_SSL(config['imap_server'])
        mail.debug = 4 # For verbose debugging
        mail.authenticate('XOAUTH2', lambda x: auth_string.encode())
        return mail

    except Exception as e:
        logging.error(f"IMAP Authentication Error: {e}")
        print(f"IMAP Authentication Error: {e}")
        return None



def process_emails(mail, rules):
    """Processes emails in the inbox based on predefined rules."""
    try:
        mail.select('inbox')
        status, messages = mail.search(None, 'ALL')
        if status == 'OK':
            for num in messages[0].split():
                try:
                    status, data = mail.fetch(num, '(RFC822)')
                    if status == 'OK':
                        msg = email.message_from_bytes(data[0][1])

                        email_id = num.decode('utf-8') # Unique ID from IMAP

                        # Extract email information
                        from_addr = str(email.utils.parseaddr(msg['from'])[1])
                        subject = str(msg['subject'])
                        body = ""
                        attachments = []

                        # Process email body and attachments
                        if msg.is_multipart():
                            for part in msg.walk():
                                content_type = part.get_content_type()
                                content_disposition = str(part.get("Content-Disposition"))

                                if content_type == "text/plain":
                                    try:
                                        body += part.get_payload(decode=True).decode()
                                    except:
                                        body += part.get_payload(decode=True).decode('latin-1')
                                elif content_type == "text/html":
                                    try:
                                        body += part.get_payload(decode=True).decode()
                                    except:
                                        body += part.get_payload(decode=True).decode('latin-1')
                                elif "attachment" in content_disposition:
                                    filename = part.get_filename()
                                    if filename:
                                        filepath = os.path.join(config['attachment_dir'], filename)
                                        with open(filepath, 'wb') as f:
                                            f.write(part.get_payload(decode=True))
                                        attachments.append(filepath)

                        else:
                             try:
                                body = msg.get_payload(decode=True).decode()
                             except:
                                body = msg.get_payload(decode=True).decode('latin-1')

                        # Apply rules to the email
                        for rule in rules:
                            if re.search(rule['condition']['from'], from_addr) and re.search(rule['condition']['subject'], subject):
                                logging.info(f"Rule matched for email from {from_addr} with subject {subject}")
                                print(f"Rule matched for email from {from_addr} with subject {subject}")

                                if rule['action'] == 'reply':
                                    reply_subject = f"Re: {subject}"
                                    reply_body = rule['reply_message'].format(sender_name=from_addr.split('@')[0])
                                    send_email(from_addr, reply_subject, reply_body)
                                    logging.info(f"Replied to email from {from_addr}")
                                    print(f"Replied to email from {from_addr}")

                                if rule['action'] == 'forward':
                                    forward_subject = f"FW: {subject}"
                                    forward_body = f"Original email from {from_addr}:\n\n{body}"
                                    send_email(rule['forward_to'], forward_subject, forward_body, attachments)
                                    logging.info(f"Forwarded email from {from_addr} to {rule['forward_to']}")
                                    print(f"Forwarded email from {from_addr} to {rule['forward_to']}")

                                if rule['action'] == 'delete':
                                    mail.store(num, '+FLAGS', '\\Deleted') # Mark as deleted
                                    mail.expunge() # Permanently delete
                                    logging.info(f"Deleted email from {from_addr}")
                                    print(f"Deleted email from {from_addr}")

                                if rule['action'] == 'extract_data':
                                    for attachment in attachments:
                                        if attachment.endswith('.pdf'):
                                            data = extract_data_from_pdf(attachment)
                                            print(f"Extracted data from {attachment}: {data}")
                                            logging.info(f"Extracted data from {attachment}: {data}")
                                        elif attachment.endswith('.csv'):
                                            data = extract_data_from_csv(attachment)
                                            print(f"Extracted data from {attachment}: {data}")
                                            logging.info(f"Extracted data from {attachment}: {data}")


                        # After all rule processing, mark as read (optional)
                        # mail.store(num, '+FLAGS', '\\Seen')

                except Exception as e:
                    logging.error(f"Error processing email {num}: {e}")
                    print(f"Error processing email {num}: {e}")



    except Exception as e:
        logging.error(f"Error processing emails: {e}")
        print(f"Error processing emails: {e}")
    finally:
        try:
            mail.close()
        except:
            pass
        mail.logout()


# Attachment Processing

def extract_data_from_pdf(pdf_path):
    """Extracts text data from a PDF attachment."""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            text = ""
            for page in pdf.pages:
                text += page.extract_text()
        return text
    except Exception as e:
        logging.error(f"Error extracting data from PDF {pdf_path}: {e}")
        print(f"Error extracting data from PDF {pdf_path}: {e}")
        return None

def extract_data_from_csv(csv_path):
    """Extracts data from a CSV attachment."""
    try:
        data = []
        with open(csv_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                data.append(row)
        return data
    except Exception as e:
        logging.error(f"Error extracting data from CSV {csv_path}: {e}")
        print(f"Error extracting data from CSV {csv_path}: {e}")
        return None


# Email Summarization and Reporting

def generate_email_summary(mail):
    """Generates a summary of unread emails in the inbox."""
    try:
        mail.select('inbox')
        status, messages = mail.search(None, 'UNSEEN')  # Only unseen emails

        if status == 'OK':
            email_count = len(messages[0].split())
            summary = f"You have {email_count} unread emails.\n"
            subjects = []

            for num in messages[0].split():
                status, data = mail.fetch(num, '(RFC822)')
                if status == 'OK':
                    msg = email.message_from_bytes(data[0][1])
                    subjects.append(msg['subject'])

            summary += "Subjects of unread emails:\n" + "\n".join(subjects)
            return summary
        else:
            return "Error retrieving email summary."

    except Exception as e:
        logging.error(f"Error generating email summary: {e}")
        print(f"Error generating email summary: {e}")
        return f"Error generating email summary: {e}"

def analyze_email_sentiment(text):
    """Analyzes the sentiment of the email content using NLTK's VADER."""
    sid = SentimentIntensityAnalyzer()
    scores = sid.polarity_scores(text)
    return scores

def generate_email_report(mail, report_file="email_report.txt"):
    """Generates a detailed report of email activity."""
    try:
        mail.select('inbox')
        status, messages = mail.search(None, 'ALL')
        if status == 'OK':
            num_emails = len(messages[0].split())
            report = f"Email Report - {datetime.now()}\n"
            report += f"Total emails in inbox: {num_emails}\n\n"

            positive_count = 0
            negative_count = 0
            neutral_count = 0

            for num in messages[0].split():
                status, data = mail.fetch(num, '(RFC822)')
                if status == 'OK':
                    msg = email.message_from_bytes(data[0][1])
                    subject = str(msg['subject'])
                    body = ""
                    if msg.is_multipart():
                        for part in msg.walk():
                            content_type = part.get_content_type()
                            if content_type == "text/plain":
                                try:
                                    body += part.get_payload(decode=True).decode()
                                except:
                                    body += part.get_payload(decode=True).decode('latin-1')
                            elif content_type == "text/html":
                                try:
                                    body += part.get_payload(decode=True).decode()
                                except:
                                    body += part.get_payload(decode=True).decode('latin-1')


                    else:
                        try:
                            body = msg.get_payload(decode=True).decode()
                        except:
                            body = msg.get_payload(decode=True).decode('latin-1')


                    sentiment = analyze_email_sentiment(body)
                    if sentiment['compound'] >= 0.05:
                        positive_count += 1
                    elif sentiment['compound'] <= -0.05:
                        negative_count += 1
                    else:
                        neutral_count += 1
            report += f"Sentiment Analysis:\n"
            report += f"  Positive: {positive_count}\n"
            report += f"  Negative: {negative_count}\n"
            report += f"  Neutral: {neutral_count}\n"

            with open(report_file, 'w') as f:
                f.write(report)

            logging.info(f"Email report generated at {report_file}")
            print(f"Email report generated at {report_file}")
            return report

    except Exception as e:
        logging.error(f"Error generating email report: {e}")
        print(f"Error generating email report: {e}")
        return f"Error generating email report: {e}"

# Scheduling

def scheduled_task():
    """Example scheduled task to process emails."""
    print("Running scheduled email processing...")
    logging.info("Running scheduled email processing...")
    mail = authenticate_imap()
    if mail:
        process_emails(mail, config['rules'])
        summary = generate_email_summary(mail)
        print(summary)
        logging.info(summary)
        generate_email_report(mail)
    else:
        print("Authentication failed. Skipping email processing.")
        logging.error("Authentication failed. Skipping email processing.")


# Main Execution

if __name__ == '__main__':
    # Example Usage
    if not os.path.exists(config['attachment_dir']):
        os.makedirs(config['attachment_dir'])

    # Schedule the task (e.g., every hour)
    schedule.every(config['processing_interval']).minutes.do(scheduled_task)

    print("Email automation script started.  Check logs for details.")
    logging.info("Email automation script started.")

    # Initial run
    scheduled_task()

    while True:
        schedule.run_pending()
        time.sleep(1)