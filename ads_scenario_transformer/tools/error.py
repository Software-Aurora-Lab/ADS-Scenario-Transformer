class ASTError(Exception):
    pass


class InvalidScenarioInputError(ASTError):

    def __init__(self, message):
        super().__init__(message)


class RoutingError(ASTError):

    def __init__(self, message):
        super().__init__(message)
