import sys


class URLBuilder:
    def __init__(self):
        self._protocol = str()
        self._hostname = str()
        self._port = None
        self._path_segments = list()
        self._query_params = dict()

    def protocol(self, protocol):
        self._protocol = protocol
        return self

    def hostname(self, hostname):
        self._hostname = hostname
        return self

    def port(self, port):
        self._port = port
        return self

    def path_segment(self, segment):
        self._path_segments.append(segment)
        return self

    def query_params(self, **kwargs):
        self._query_params = kwargs
        return self

    def build(self):
        if self._protocol is "" or self._hostname is "":
            print("A protocol and hostname are required", file=sys.stderr)

        # Proto & hostname
        url = "{}://{}".format(self._protocol, self._hostname)

        # Port
        if self._port is not None:
            url = "{}:{}".format(url, self._port)

        # Path
        for p in self._path_segments:
            url = "{}/{}".format(url, p)

        # Queries
        if len(self._query_params.keys()) > 0:
            url += "?"
            for i in range(0, len(self._query_params.keys())):
                k = list(self._query_params.keys())[i]
                v = self._query_params[k]
                url = "{}{}={}".format(url, k, v)
                if i < len(self._query_params.keys()) - 1:
                    url += "&"

        return url
