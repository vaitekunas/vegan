"""
Vegan's email-handler.

Vegan's Email class handles email fetching and saving
"""

from vegan.parser import Parser

import getpass
import email
import imaplib as imap
import re


class Email(Parser):
    """Handles email fetching and saving operations."""

    host = ""
    port = 993
    user = ""
    ssl = True
    _imap = None

    def __init__(self, host=None, port=None, user=None, passw=None, ssl=True, logger=None, strip_patterns=None):
        """Initialize the Email class."""
        # Initialize parent
        # The parrent will create a logging facility self._log
        Parser.__init__(self, logger, strip_patterns)

        if host is not None and port is not None and user is not None:
            self.host = host
            self.port = port
            self.user = user
            self.ssl = ssl
        else:
            raise Exception(self._log("Missing IMAP information. Use Parser to parse data", True))

        # Create IMAP instance
        self._log("Initializing IMAP connection")
        try:
            self._init_imap()
        except Exception as e:
            raise Exception(self._log("Could not initiate IMAP instance:", str(e), True))

        # Get account password
        print("\n[?] Please provide password for", user)
        try:
            self._imap.login(user, getpass.getpass())
        except (KeyboardInterrupt, SystemExit):
            raise Exception(self._log("Password input aborted. Quiting.", True))
        except Exception as e:
            raise Exception(self._log("Authentication failed", True))

        print("\n[*] Login successful")

    def _init_imap(self):
        """Initialize the IMAP object."""
        if self.ssl:
            self._imap = imap.IMAP4_SSL(self.host, self.port)
        else:
            self._imap = imap.IMAP4(self.host, self.port)

    def _strip(self, msg):
        """Strip unwanted characters."""
        rep_patterns = [
                        ('<[^<]+?>', ''),
                        ('&[a-z]+', ''),
                        ('http[s]?://[\w@:%_\+.~#?&//=-]+', '_LINK_'),
                        ('www.[\w@:%_\+.~#?&//=-]+', '_LINK_'),
                        ('mailto://[\w@._-]+', '_LINK_'),
                        ('[^\w]+', ' '),
                        ('[\s]{2,}', ' '),
                        ('0d', ''),
                        ('[0-9]+', '')
                       ]

        msg = msg.lower()
        for pattern in rep_patterns:
            msg = re.sub(pattern[0], pattern[1], msg)

        return msg.lower()

    def _get_payload(self, msg):
        """Extract stripped payload from the body."""
        content = ""

        if msg.is_multipart():
            for payload in msg.get_payload():
                part = payload.get_payload()
                if isinstance(part, str):
                    content += self._strip(part)
                elif isinstance(part, list):
                    for item in part:
                        content += self._strip(item.get_payload())
        else:
            content += self._strip(msg.get_payload())

        return content

    def fetch(self, folder):
        """Fetch emails from a particular folder."""
        print("\n[*] Fetching emails from", folder)
        self._imap.select()

        _, uids = self._imap.uid("search", None, "ALL")
        uids = uids[0].split()
        print("\n[*] Found", len(uids), "messages")

        self._pb.reset()
        for i, uid in enumerate(uids):
            _, msg = self._imap.uid("fetch", uid, "(RFC822)")
            msg = email.message_from_bytes(msg[0][1])

            self.parse_message(msg)

            if i >= 50:
                print("\n")
                exit(0)

    def close(self):
        """Close existing IMAP connection."""
        if self._imap is None:
            raise("Nothing to close")

        try:
            self._imap.close()
            self._imap.logout()
        except Exception as e:
            print("[x] Could not close/logout:", str(e))
            exit(1)
