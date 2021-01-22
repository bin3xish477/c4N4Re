"""
MIT License

Copyright (c) 2021 Alexis Rodriguez

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from smtplib import SMTP_SSL
from ssl import create_default_context

class Emailer():
    def __init__(self, smtp_server, smtp_port):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port

    def __enter__(self):
        context = create_default_context()
        self.server = SMTP_SSL(self.smtp_server, self.smtp_port, context=context)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.server.quit()
        return False

    def authenticate(self, sender_email, password):
        self.sender_email = sender_email
        try:
            self.server.login(self.sender_email, password)
        except:
            return False
        return True

    def send(self, recipient_email, subject, msg):
        # Using RFC822 email string
        msg = f"Subject:{subject}\n\n{msg}"
        try:
            self.server.sendmail(self.sender_email, recipient_email, msg)
        except:
            return False
        return True