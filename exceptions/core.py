




class InvalidInitDataException(Exception):
    message = "InitData невалидна"


class InvalidToken(Exception):
    message = "Токен невалидный"


class ExpiredToken(Exception):
    message = "Время действия токена закончилось"


class EntityNotFound(Exception):
    message: str = "Сущность не найдена"
    by_field: str
    entity: str

    def __init__(self, entity: str, by_field: str, *args):
        self.by_field = by_field
        self.entity = entity
        super(EntityNotFound, self).__init__(*args)