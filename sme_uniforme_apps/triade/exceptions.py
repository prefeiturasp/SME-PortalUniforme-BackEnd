class TriadeError(Exception):
    pass


class TriadePermanentError(TriadeError):
    pass


class TriadeConfigError(TriadePermanentError):
    pass


class TriadeRequestError(TriadePermanentError):
    pass


class TriadeSignatureError(TriadePermanentError):
    pass


class TriadeTransientError(TriadeError):
    pass


class TriadeCallbackTransientError(TriadeError):
    pass
