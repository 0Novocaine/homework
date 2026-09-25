"""SMTP backend with a standards-compliant hostname for the EHLO command."""

from django.conf import settings
from django.core.mail.backends.smtp import EmailBackend as DjangoEmailBackend


class EmailBackend(DjangoEmailBackend):
    """Use a safe hostname when an SMTP provider rejects the macOS device name."""

    def open(self):
        if self.connection:
            return False

        if self._partial_connection is not None:
            self._close_connection(self._partial_connection)
            self._partial_connection = None

        connection_params = {
            'local_hostname': settings.EMAIL_LOCAL_HOSTNAME,
        }
        if self.timeout is not None:
            connection_params['timeout'] = self.timeout
        if self.use_ssl:
            connection_params['context'] = self.ssl_context

        try:
            self._partial_connection = self.connection_class(
                self.host, self.port, **connection_params
            )
            if not self.use_ssl and self.use_tls:
                self._partial_connection.starttls(context=self.ssl_context)
            if self.username and self.password:
                self._partial_connection.login(self.username, self.password)

            self.connection = self._partial_connection
            self._partial_connection = None
            return True
        except OSError:
            if not self.fail_silently:
                raise
