"""Vegan's main message parser."""

from vegan.base import Base

import re
import email
from os import listdir
from os.path import isdir, isfile, join
from collections import Counter
import numpy as np
from pandas import DataFrame


class Parser(Base):
    """Parses emails and creates classification-ready datasets."""

    """Patterns that are stripped away from email subject and bodies"""
    _strip_patterns = [
                    ('<[^<]+?>', ''),
                    ('&[a-z]+', ''),
                    ('["\']+', ''),
                    ('http[s]?://[\w@:%_\+.~#?&//=-]+', 'LINK'),
                    ('www.[\w@:%_\+.~#?&//=-]+', 'LINK'),
                    ('mailto://[\w@._-]+', 'LINK'),
                    ('[^\w]+|[_-]+', ' '),
                    ('[\s]{2,}', ' '),
                    ('0d', ''),
                    ('[0-9]+', '')
                   ]

    """Parsed messages"""
    _parsed = []

    """Errors parsing messages"""
    _parse_errors = []

    def __init__(self, logger=None, strip_patterns=None):
        """Initialize the parser."""
        # Initialize base
        Base.__init__(self, logger)

        if strip_patterns is not None and isinstance(strip_patterns, list):
            self._strip_patterns = strip_patterns

    def _strip(self, msg):
        """Strip unwanted characters."""
        msg = msg.lower()
        for pattern in self._strip_patterns:
            msg = re.sub(pattern[0], pattern[1], msg)

        return msg

    def _get_payload(self, msg):
        """Extract stripped payload from the body."""
        if not isinstance(msg, email.message.Message):
            raise Exception(self._log("Expecting email.message.Message type", True))

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

    def _clean_address(self, dirty_address):
        """Clean and parse an email address.

        The pattern used here will not work with all edge cases,
        but since addresses can be spoofed anyway, this is enough.
        """
        found = re.search('(?i)([a-z0-9-_.]+)@([a-z0-9-_.]*)\.([a-z]{2,})', dirty_address.lower())
        if found is not None:
            address = found.group()
            domain = found.group(2)
            tld = found.group(3)
        else:
            address = ''
            domain = ''
            tld = ''
        return {'address': address, 'domain': domain, 'tld': tld}

    def parse_message(self, msg, spam=False, silent=True):
        """Extract relevant information from email.message.Message."""
        sender = None
        subject = None
        clean = None

        if not isinstance(msg, email.message.Message):
            err = "Cannot parse message of type %s" % str(type(msg))
            if not silent:
                self._log(err, True)
            return err

        try:
            sender = self._clean_address(msg['From'])
            subject = Counter(self._strip(msg['Subject']).split())
            clean = Counter(self._get_payload(msg).split())
        except Exception as e:
            err = "Could not extract a clean message"
            if not silent:
                self._log(err, True)
            return err

        self._parsed.append({
            'spam': 1 if spam else 0,
            'sender': sender,
            'subject': subject,
            'message': clean
        })

    def parse_folder(self, folder=None, spam=False):
        """Parse all the files contained in the folder."""
        if not isdir(folder):
            raise Exception(self._log("'%s' is not a folder" % folder))
        try:
            files = listdir(folder)
        except Exception as e:
            raise Exception(self._log("Could not read folder %s: %s" % (folder, str(e)), True))

        self._log("Found %d files in '%s' containing %s" % (len(files), folder, ('' if spam else 'not ')+'spam'))
        if len(files) == 0:
            return

        # Parse all files
        self._progress.reset()
        for i, filename in enumerate(files):
            try:
                err = self.parse_file(join(folder, filename), spam)
                if err is not None:
                    self._parse_errors.append(err)
            except Exception as e:
                raise Exception(self._log("Could not parse folder %s: %s" % (folder, str(e)), True))
            self._progress.set(i+1, len(files))
        self._progress.reset()

    def parse_file(self, file="", spam=False, silent=True):
        """Read and parse a single file containing an email (with headers)."""
        if not isfile(file):
            err = "'%s' is not a file"
            if not silent:
                self._log(err, True)
            return err

        fcontent = ""
        try:
            with open(file, "r") as f:
                fcontent = f.read()
        except Exception as e:
            err = "Could not read file '%s': %s" % (file, str(e))
            if not silent:
                self._log(err, True)
            return err

        msg = None
        try:
            msg = email.message_from_string(fcontent)
        except Exception as e:
            err = "Could not convert file '%s' to a message: %s" % (file, str(e))
            if not silent:
                self._log(err, True)
            return err

        return self.parse_message(msg, spam, silent)

    def parse_errors(self, silent=True):
        """Tell how many parse errors occurred."""
        if not silent:
            if len(self._parse_errors) > 0:
                self._log("Got %d errors while parsing messages" % len(self._parse_errors), True)
            else:
                self._log("There were no errors parsing messages")

        return len(self._parse_errors)

    def show_parse_errors(self):
        """Show parse errors."""
        for err in self._parse_errors:
            self._log(err, True)

    def shuffle(self):
        """Shuffle parsed data."""
        pass

    def purge(self):
        """Clear parsed data."""
        self._parsed = []

    def aggregate(self):
        """Aggregate data into a pandas DataFrame."""
        ccommon = Counter()
        cspam = Counter()
        for entry in self._parsed:
            ccommon.update([k for k in entry['message'].elements() if len(k) > 3 and len(k) < 30])
            if entry['spam'] == 1:
                cspam.update([k for k in entry['message'].elements() if len(k) > 3 and len(k) < 30])

        df = DataFrame(np.zeros(shape=(len(ccommon), 5),dtype=int))
        df.columns = ['spam', 'not_spam', 'entry', 'prior', 'posterior']
        df['entry'].loc[:] = ""

        for i, word in enumerate(ccommon):
            scount = cspam[word]
            nscount = ccommon[word]-scount

            df.iloc[i, 0] = scount
            df.iloc[i, 1] = nscount
            df.iloc[i, 2] = word

        df.iloc[:, 3] = df.iloc[:, 0]/(df.iloc[:, 0]+df.iloc[:, 1])
        print(df.loc[df.prior > 0.75].sort_values('spam', ascending=False).head(20))        
