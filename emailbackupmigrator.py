import imaplib
import email
import os
import logging
from email import policy
from email.parser import BytesParser
from email.utils import parsedate_to_datetime
import concurrent.futures
import itertools
from functools import partial

# Try to import tqdm, if not available, use fallback
try:
    from tqdm import tqdm
    use_tqdm = True
except ImportError:
    print("Warning: 'tqdm' module not found. Progress bar will not be shown.")
    use_tqdm = False

# Configuration
IMAP_SERVER = "mail.example.com"
IMAP_PORT = 993
backup_dir = "/path/To/Migration-Folder/"
accounts_file = "/path/To/Migration-Folder/accounts_list.txt"
log_file = "/path/To/Migration-Folder/importer.log"
imported_files_log = "/path/To/Migration-Folder/imported_files.txt"
migrated_accounts_log = "/path/To/Migration-Folder/migrated_accounts.txt"

# Parallel processing configuration
MAX_WORKERS = 10  # Adjust based on your system's capabilities
BATCH_SIZE = 100  # Number of emails to process in a single IMAP connection

# Configure logging
logging.basicConfig(filename=log_file, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def load_imported_files():
    if os.path.exists(imported_files_log):
        with open(imported_files_log, 'r') as f:
            return set(line.strip() for line in f)
    return set()

def log_imported_file(eml_file_path):
    with open(imported_files_log, 'a') as f:
        f.write(eml_file_path + '\n')

def load_migrated_accounts():
    if os.path.exists(migrated_accounts_log):
        with open(migrated_accounts_log, 'r') as f:
            return set(line.strip() for line in f)
    return set()

def log_migrated_account(account):
    with open(migrated_accounts_log, 'a') as f:
        f.write(account + '\n')

def import_eml_batch(account, password, eml_file_paths):
    successful_imports = []
    try:
        with imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT) as imap:
            imap.login(account, password)
            imap.select("INBOX")

            for eml_file_path in eml_file_paths:
                try:
                    with open(eml_file_path, 'rb') as file:
                        email_content = file.read()

                    email_message = BytesParser(policy=policy.default).parsebytes(email_content)
                    date_str = email_message['Date']
                    if date_str:
                        date_time = parsedate_to_datetime(date_str)
                        if date_time is not None:
                            date_time_str = imaplib.Time2Internaldate(date_time.timestamp())
                        else:
                            raise ValueError("Date parsing failed.")
                    else:
                        raise ValueError("Date header is missing.")

                    result = imap.append("INBOX", '', date_time_str, email_content)

                    if result[0] == 'OK':
                        successful_imports.append(eml_file_path)
                    else:
                        logging.error(f"Failed to import: {eml_file_path}")
                except Exception as e:
                    logging.error(f"Error importing file {eml_file_path}: {str(e)}")

    except Exception as e:
        logging.error(f"Error processing batch for account {account}: {str(e)}")

    return successful_imports

def process_account(account, password, imported_files):
    account_dir = os.path.join(backup_dir, account)
    if not os.path.exists(account_dir):
        logging.error(f"Directory not found for account: {account}")
        return []

    eml_files = [os.path.join(account_dir, f) for f in os.listdir(account_dir) 
                 if f.endswith('.eml') and os.path.join(account_dir, f) not in imported_files]

    successful_imports = []
    for i in range(0, len(eml_files), BATCH_SIZE):
        batch = eml_files[i:i+BATCH_SIZE]
        successful_imports.extend(import_eml_batch(account, password, batch))

    return successful_imports

def load_accounts(accounts_file):
    accounts = []
    try:
        with open(accounts_file, 'r') as file:
            for line in file:
                email, password = line.strip().split(':')
                accounts.append((email, password))
    except Exception as e:
        logging.error(f"An error occurred while loading accounts: {str(e)}")
    return accounts

def process_backup_files():
    accounts = load_accounts(accounts_file)
    imported_files = load_imported_files()
    migrated_accounts = load_migrated_accounts()

    accounts_to_process = []
    for account, password in accounts:
        if account not in migrated_accounts:
            account_dir = os.path.join(backup_dir, account)
            if os.path.exists(account_dir):
                accounts_to_process.append((account, password))
            else:
                logging.warning(f"Skipping account {account}: Directory not found")

    total_files = sum(len([f for f in os.listdir(os.path.join(backup_dir, account)) 
                           if f.endswith('.eml') and os.path.join(backup_dir, account, f) not in imported_files])
                      for account, _ in accounts_to_process)

    if use_tqdm:
        pbar = tqdm(total=total_files, desc="Importing emails", unit="file")
    else:
        print(f"Total emails to import: {total_files}")

    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        future_to_account = {executor.submit(process_account, account, password, imported_files): account 
                             for account, password in accounts_to_process}
        
        for future in concurrent.futures.as_completed(future_to_account):
            account = future_to_account[future]
            try:
                successful_imports = future.result()
                for eml_file_path in successful_imports:
                    log_imported_file(eml_file_path)
                    if use_tqdm:
                        pbar.update(1)
                    else:
                        print(f"Imported: {eml_file_path}")
                
                account_dir = os.path.join(backup_dir, account)
                if len(successful_imports) == len([f for f in os.listdir(account_dir) if f.endswith('.eml')]):
                    log_migrated_account(account)
                    logging.info(f"Account fully migrated: {account}")
            except Exception as exc:
                logging.error(f"Account {account} generated an exception: {exc}")

    if use_tqdm:
        pbar.close()

if __name__ == "__main__":
    process_backup_files()
