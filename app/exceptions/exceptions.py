class RequiresClientException(Exception):
    def __init__(self, message):
        super().__init__(message)

    def __str__(self):
        return "Twilio client required for function call"

class MissingCredentialsException(Exception):
    def __init__(self, message):
        super().__init__(message)

    def __str__(self):
        return "Twilio credentials are not set as environment variables"

class ClientAuthenticationException(Exception):
    def __init__(self, message):
        super().__init__(message)

    def __str__(self):
        return "Twilio client authentication failed"

class ResourceNotFoundException(Exception):
    def __init__(self, message):
        super().__init__(message)

    def __str__(self):
        return "Resource not found"