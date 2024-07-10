import statsd

from app.config import get_config


class Stats:
    def timing(self, key: str, value: int) -> None:
        raise NotImplementedError

    def inc(self, key: str, count: int = 1, rate: int = 1) -> None:
        raise NotImplementedError

    def dec(self, key: str, count: int = 1, rate: int = 1) -> None:
        raise NotImplementedError

    def gauge(self, key: str, value: int, delta: bool = False) -> None:
        raise NotImplementedError


class NoopStats(Stats):
    def timing(self, key: str, value: int) -> None:
        pass

    def inc(self, key: str, count: int = 1, rate: int = 1) -> None:
        pass

    def dec(self, key: str, count: int = 1, rate: int = 1) -> None:
        pass

    def gauge(self, key: str, value: int, delta: bool = False) -> None:
        pass


class Statsd(Stats):
    def __init__(self, host: str, port: int):
        self.client = statsd.StatsClient(host, port)

    def timing(self, key: str, value: int) -> None:
        self.client.timing(key, value)

    def inc(self, key: str, count: int = 1, rate: int = 1) -> None:
        self.client.incr(key, count, rate)

    def dec(self, key: str, count: int = 1, rate: int = 1) -> None:
        self.client.decr(key, count, rate)

    def gauge(self, key: str, value: int, delta: bool = False) -> None:
        self.client.gauge(key, value, delta)


_STATS: Stats = NoopStats()


def setup_stats() -> None:
    config = get_config()

    if config.stats.enabled is False:
        return

    config.stats.host = config.stats.host or "localhost"
    config.stats.port = config.stats.port or 8125

    global _STATS
    _STATS = Statsd(config.stats.host, config.stats.port)


def get_stats() -> Stats:
    global _STATS
    return _STATS
