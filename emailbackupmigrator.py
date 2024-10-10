import imaplib
import email
import os
from email import policy
from email.parser import BytesParser
from email.utils import parsedate_to_datetime

# Configuration
IMAP_SERVER = "webmail.example.com"
IMAP_PORT = 993  # Standard port for IMAPS
backup_dir = "/path/to/backup-folder/"
accounts_file = "/path/to/users/accounts_list.txt"

def import_eml_file(imap_server, username, password, eml_file_path):
    try:
        # Connect to the IMAP server
        with imaplib.IMAP4_SSL(imap_server, IMAP_PORT) as imap:
            # Login
            imap.login(username, password)
            print(f"Logged in as {username}")

            # Select the inbox (or another folder if needed)
            imap.select("INBOX")

            # Read the .eml file
            with open(eml_file_path, 'rb') as file:
                email_content = file.read()

            # Parse the email
            email_message = BytesParser(policy=policy.default).parsebytes(email_content)

            # Parse the date using parsedate_to_datetime
            date_str = email_message['Date']
            if date_str:
                date_time = parsedate_to_datetime(date_str)
                if date_time is not None:
                    date_time_str = imaplib.Time2Internaldate(date_time.timestamp())
                else:
                    raise ValueError("Date parsing failed.")
            else:
                raise ValueError("Date header is missing.")

            # Append the email to the mailbox
            result = imap.append(
                "INBOX",
                '',
                date_time_str,
                email_content
            )

            if result[0] == 'OK':
                print(f"Successfully imported: {eml_file_path}")
            else:
                print(f"Failed to import: {eml_file_path}")

    except imaplib.IMAP4.error as e:
        print(f"IMAP error occurred while importing {eml_file_path}: {str(e)}")
    except Exception as e:
        print(f"An unexpected error occurred while importing {eml_file_path}: {str(e)}")

def load_accounts(accounts_file):
    accounts = []
    with open(accounts_file, 'r') as file:
        for line in file:
            email, password = line.strip().split(':')
            accounts.append((email, password))
    return accounts

def process_backup_files():
    accounts = load_accounts(accounts_file)
    
    for account, password in accounts:
        account_dir = os.path.join(backup_dir, account)
        if os.path.exists(account_dir):
            print(f"Processing account: {account}")
            for eml_file in os.listdir(account_dir):
                eml_file_path = os.path.join(account_dir, eml_file)
                if eml_file.endswith('.eml'):
                    print(f"Importing {eml_file_path}...")
                    import_eml_file(IMAP_SERVER, account, password, eml_file_path)
        else:
            print(f"Directory not found for account: {account}")

if __name__ == "__main__":
    process_backup_files()
