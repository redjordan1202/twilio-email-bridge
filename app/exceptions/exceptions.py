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

class InvalidTwilioRequestException(Exception):
    def __init__(self, message):
        super().__init__(message)

    def __str__(self):
        return "Twilio request is invalid"

class RouteProcessingError(Exception):
    def __init__(self, message):
        super().__init__(message)

    def __str__(self):
        return "Unable to process routing"

class GoogleAuthError(Exception):
    def __init__(self, message):
        super().__init__(message)

    def __str__(self):
        return "Unable to authenticate with Google"

class ConfigNotFoundError(Exception):
    def __init__(self, message):
        super().__init__(message)

    def __str__(self):
        return "Unable to find config file"

class InvalidYamlError(Exception):
    def __init__(self, message):
        super().__init__(message)

    def __str__(self):
        return "YAML file is not valid"

class YamlMissingKeyError(Exception):
    def __init__(self, message, key):
        super().__init__(message)
        self.key = key

    def __str__(self):
        return f"YAML file is missing required key {self.key}"

class OrchestratorMissingMessageData(Exception):
    def __init__(self, message):
        super().__init__(message)

    def __str__(self):
        return "Message Data missing or blank"

class OrchestratorUnableToProcess(Exception):
    def __init__(self, message):
        super().__init__(message)

    def __str__(self):
        return "Orchestrator unable to process message"
