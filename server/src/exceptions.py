class LossException(Exception):
    def __init__(self, bytes_lost):
        super().__init__(f"LOSS EXCEPTION: {bytes_lost}")
        self.bytes_lost = bytes_lost
