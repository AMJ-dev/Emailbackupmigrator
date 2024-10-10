#EML Importer Script

#Overview

This Python script imports .eml email files into specified email accounts using the IMAP protocol. It connects to a designated IMAP server, reads email files from a local directory, and appends them to the inbox of the respective accounts specified in a configuration file.

Requirements:
Python 3.x
imaplib (part of the Python standard library)
email (part of the Python standard library)
Configuration
Before running the script, ensure to update the following configurations:

IMAP_SERVER: The hostname of the IMAP server (e.g., test.example.com).
IMAP_PORT: The port number for IMAP, typically 993 for secure connections.
backup_dir: The path to the directory containing the account-specific subdirectories with .eml files.
accounts_file: The path to the text file containing account credentials in the format email:password.

File Structure
The accounts_list.txt file should contain entries like the following:
test@example.com:password123
john.doe@example.com:password456

The backup directory structure should look like this:
/path/to/backup-folder/
├── accounts_list.txt
└── test@example.com/
    ├── This is a webmail test.eml
    └── Another email.eml
└── john.doe@example.com/
    ├── Example email.eml
    
Functions
import_eml_file(imap_server, username, password, eml_file_path)
This function connects to the IMAP server, logs into the specified account, reads the .eml file, and appends the email to the inbox.

Parameters:

imap_server: The IMAP server hostname.
username: The email address of the account.
password: The password for the account.
eml_file_path: The full path to the .eml file to be imported.
Returns: None. It prints the success or failure of the import operation.

load_accounts(accounts_file)
This function reads the account credentials from the specified file and returns a list of tuples containing email addresses and their corresponding passwords.

Parameters:

accounts_file: The path to the accounts file.
Returns: A list of tuples, each containing an email address and password.

process_backup_files()
This function orchestrates the import process. It loads the accounts from the accounts_file, checks for the existence of .eml files in each account's directory, and calls import_eml_file for each valid file.

Returns: None. It prints the progress of processing each account and file.

Usage
To run the script:

Ensure the necessary configurations are set in the script.

Make sure your .eml files are organized as specified.

Execute the script in your terminal:

python3 emailbackupmigrator.py

Error Handling
The script includes error handling for various exceptions, including issues with IMAP connection, file access, and date parsing. In case of errors, descriptive messages will be printed to help diagnose the issue.

License
This script is provided as-is. Use it at your own risk.
