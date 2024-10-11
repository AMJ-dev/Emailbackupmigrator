# Email Migration Script

## Overview

This script is designed to automate the migration of `.eml` files (email messages) from local directories to an IMAP server. It processes multiple email accounts in parallel, importing batches of emails into the corresponding account's inbox on the IMAP server. The script uses multithreading for efficient processing and logs each import operation for easy tracking and debugging.

## Features

- **Multithreaded Processing**: Leverages Python's `concurrent.futures.ThreadPoolExecutor` to process multiple accounts and emails in parallel.
- **Batch Import**: Emails are imported in batches, reducing the chance of hitting server limitations in a single session.
- **Progress Tracking**: If `tqdm` is installed, a progress bar is shown to monitor the email migration process.
- **Error Handling**: Logs errors and skips problematic emails, ensuring the script continues running without interruption.
- **Account and File Tracking**: Logs the accounts and email files that have already been migrated to avoid duplications.
- **Configurable**: Allows customization of IMAP server settings, directory paths, and logging.

## Requirements

- Python 3.x
- The following Python libraries:
  - `imaplib`
  - `email`
  - `concurrent.futures`
  - `tqdm` (optional for progress bar)
  - `logging`
  
You can install `tqdm` via pip:

```bash
pip install tqdm
```

## Script Configuration

Before running the script, update the following configuration variables:

- `IMAP_SERVER`: Your IMAP server address (e.g., `mail.example.com`).
- `IMAP_PORT`: The port for IMAP over SSL, typically `993`.
- `backup_dir`: Path to the folder where `.eml` files are stored for migration.
- `accounts_file`: Path to the file containing a list of accounts in the format `email:password`.
- `log_file`: Path where the logs of the script execution will be stored.
- `imported_files_log`: Path to the file that keeps track of imported `.eml` files.
- `migrated_accounts_log`: Path to the file that keeps track of fully migrated accounts.
- `MAX_WORKERS`: Number of parallel threads used for processing accounts.
- `BATCH_SIZE`: Number of emails processed in a single IMAP connection per account.

### Example Configuration:
```python
IMAP_SERVER = "mail.example.com"
IMAP_PORT = 993
backup_dir = "/path/To/Migration-Folder/"
accounts_file = "/path/To/Migration-Folder/accounts_list.txt"
log_file = "/path/To/Migration-Folder/importer.log"
imported_files_log = "/path/To/Migration-Folder/imported_files.txt"
migrated_accounts_log = "/path/To/Migration-Folder/migrated_accounts.txt"
```

## Files

- **`accounts_list.txt`**: Contains a list of email accounts and their passwords in the format:
  ```
  email@example.com:password
  another_email@example.com:password
  ```

- **Log files**:
  - `importer.log`: Stores detailed logs of the migration process, including errors.
  - `imported_files.txt`: Logs paths of successfully imported `.eml` files.
  - `migrated_accounts.txt`: Logs accounts that have had all their emails successfully migrated.

## How to Run the Script

1. Ensure all `.eml` files are stored in a folder named after each email account (e.g., `/backup_dir/account1@example.com/`).
2. Update the `accounts_list.txt` file with the correct account credentials.
3. Run the script:

```bash
python3 emailbackupmigrator.py
```

The script will automatically process all the accounts in `accounts_list.txt`, migrate their emails to the IMAP server, and log the progress.

## How It Works

1. **Account Loading**: The script reads the accounts and passwords from `accounts_list.txt`.
2. **Email Importing**: For each account, it checks for `.eml` files in the corresponding directory and processes them in batches. Each email is uploaded to the account's inbox on the IMAP server.
3. **Logging**: Each successfully imported email is logged to `imported_files.txt` to avoid re-importing in future runs. Once all emails for an account are processed, the account is marked as migrated in `migrated_accounts.txt`.
4. **Parallel Execution**: The script uses multithreading to process multiple accounts and email files in parallel, optimizing performance.

## Error Handling

- **Missing Files**: If the directory for an account does not exist, the account is skipped, and a warning is logged.
- **Import Failures**: If an email fails to import, the error is logged, and the script continues processing the rest of the emails.
  
## Customization

You can adjust the `MAX_WORKERS` and `BATCH_SIZE` parameters depending on the capacity of your system and the IMAP server to control the number of parallel threads and the number of emails processed in each batch.

## Logs

- **importer.log**: Captures detailed logs of each operation, including any errors or warnings.
- **imported_files.txt**: Keeps track of emails that have already been imported to prevent duplicate imports.
- **migrated_accounts.txt**: Tracks which accounts have been fully migrated.

## Troubleshooting

- **Progress Bar Not Showing**: If the progress bar doesn't appear, ensure that `tqdm` is installed or manually monitor the progress using log files.
- **Account or Email Not Migrating**: Check the `importer.log` file for any errors or warnings related to the specific account or email file.

## License

This script is open-source and can be freely used and modified as per your needs.
