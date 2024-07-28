class FormatParser[OutType, OutData, InManifest]:
    extensions: list[str]

    def __init__(self, extensions: list[str]):
        self.extensions = extensions

    def parse(self, manifest: InManifest) -> OutType:
        pass

    def __parse(self, manifest: InManifest) -> OutData:
        pass

class Processor[OutType, OutData, InManifest]:
    parsers: list[FormatParser[OutType, OutData, InManifest]]
    __ext_lookup: dict[str, int]

    def __init__(self, parsers: list[FormatParser[OutType, OutData, InManifest]]):
        self.parsers = parsers

        for p in parsers:
            for ext in p.extensions:
                assert ext not in self.__ext_lookup
                self.__ext_lookup[ext] = p

    def format_from_ext(self, ext: str) -> FormatParser[OutType, OutData, InManifest]:
        assert ext in self.__ext_lookup
        return self.parsers[self.__ext_lookup[ext]]