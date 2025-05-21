class TagError(Exception):
    def __init__(self, tag_name: str, *, message: str = "") -> None:
        super().__init__(message)
        self.tag_name = tag_name


class TagCreationError(TagError):
    pass


class TagExistsError(TagError):
    def __init__(self, tag_name: str) -> None:
        super().__init__(tag_name, message=f"Tag '{tag_name}' already exists.")


class TagDeletionError(TagError):
    pass


class TagDoesNotExistError(TagError):
    def __init__(self, tag_name: str):
        super().__init__(tag_name, message=f"Tag '{tag_name}' does not exist.")
