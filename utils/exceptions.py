class NotFoundException(Exception):
    def __init__(self, detail: str):
        self.detail = detail


class ConflictException(Exception):
    def __init__(self, detail: str):
        self.detail = detail


class UnauthorizedException(Exception):
    def __init__(self, detail: str):
        self.detail = detail


class ForbiddenException(Exception):
    def __init__(self, detail: str):
        self.detail = detail