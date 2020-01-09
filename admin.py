class Admin:

    @classmethod
    def setup(cls, up):
        cls._up = up

    @classmethod
    def kill(cls):
        cls._up.stop()
