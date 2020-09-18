class Device:
    def __init__(self, endpoints=None):
        if endpoints is None:
            endpoints = []
        self.endpoints = endpoints


class ZclEndpoint:
    def __init__(self, id, in_clusters=None, out_clusters=None):
        if in_clusters is None:
            in_clusters = []
        if out_clusters is None:
            out_clusters = []
        self.id = id
        self.in_clusters = in_clusters
        self.out_clusters = out_clusters


class ZclCluster:
    def __init__(self, id, name=None, attributes=None, commands=None):
        if attributes is None:
            attributes = []
        if commands is None:
            commands = []
        self.id = id
        self.name = name
        self.attributes = attributes
        self.commands = commands


class ZclAttribute:
    def __init__(self, id, name=None, type=None):
        self.id = id
        self.name = name
        self.type = type


class ZclCommand:
    def __init__(self, id, name=None, payload=None):
        self.id = id
        self.name = name
        self.payload = payload


class ZclPayload:
    def __init__(self, name=None, type=None):
        self.name = name
        self.type = type