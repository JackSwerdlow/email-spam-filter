"""Script to download personal emails via IMAP and save them to disk.

To make this script works with your own email address, please change the details in the
user_config.yml file.

The script requires an IMAP application password saved in the system keyring
under the service name ``virgin-imap``.  Store it once with::
    python -m keyring set example-imap your_username@example.com

Also before running ensure you have correctly installed the dev dependencies group with poetry.

!!!!!!!!!!!!!!!!!!!!!!!!!!!!! WARNING !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
Currently this has only been tested for the Virgin Media email client.
"""

from __future__ import annotations

from email_spam_filter.common import logger
from email_spam_filter.data.collection.personal import fetch_and_save_emails

if __name__ == "__main__":
    logger()
    number_of_emails_to_fetch = 10
    fetch_and_save_emails(number_of_emails_to_fetch)
