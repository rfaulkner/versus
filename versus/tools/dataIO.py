"""
Class family for Data IO classes to handle data ingestion and fetch events
"""

import redis
from versus.config import log

import pydoop.hdfs as hdfs

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


class DataIO(object):

    def __init__(self, **kwargs):
        pass

    def connect(self, **kwargs):
        pass

    def write(self, **kwargs):
        raise NotImplementedError()

    def read(self, **kwargs):
        raise NotImplementedError()


class DataIOHDFS(DataIO):
    """ Class implementing data IO for HDFS. """

    def __init__(self, **kwargs):
        super(DataIOHDFS, self).__init__(**kwargs)

    def connect(self, **kwargs):
        raise NotImplementedError()

    def write(self, **kwargs):
        """HDFS put for adding data to hdfs"""
        hdfs.put(kwargs['fs'], kwargs['hdfs'])

    def read(self, **kwargs):
        pass


class DataIORedis(DataIO):
    """ Class implementing data IO for Redis. """

    DEFAULT_HOST = 'localhost'
    DEFAULT_PORT = 6379
    DEFAULT_DB = 0

    def __init__(self, **kwargs):
        super(DataIORedis, self).__init__(**kwargs)

        self.conn = None

        self.host = kwargs['host'] if kwargs.has_key('host') else \
            self.DEFAULT_HOST
        self.port = kwargs['port'] if kwargs.has_key('port') else \
            self.DEFAULT_PORT
        self.db = kwargs['db'] if kwargs.has_key('db') else self.DEFAULT_DB

    def connect(self, **kwargs):
        self.conn = redis.Redis(host=self.host, port=self.port, db=self.db)

    def write(self, **kwargs):
        if self.conn:
            try:
                return self.conn.set(kwargs['key'], kwargs['value'])
            except KeyError as e:
                log.error('Missing param -> {0}'.format(e.message))
                return False
        else:
            log.error('No redis connection.')
            return False

    def read(self, **kwargs):
        if self.conn:
            try:
                return self.conn.get(kwargs['key'])
            except KeyError as e:
                log.error('Missing param -> {0}'.format(e.message))
                return False
        else:
            log.error('No redis connection.')
            return False


class DataIOMySQL(DataIO):
    """ Class implementing data IO for MySQL. Utilizes sqlalchemy [1].

     [1] http://docs.sqlalchemy.org
    """

    DEFAULTS = {
        'dialect': 'mysql',
        'driver': '',
        'host': 'localhost',
        'port': 3306,
        'db': 'default',
        'user': 'root',
        'pass': '',
    }

    def __init__(self, **kwargs):
        super(DataIOMySQL, self).__init__(**kwargs)

        self.engine = None
        self.sess = None

        for key in self.DEFAULTS.keys():
            if kwargs.has_key(key):
                setattr(self, key, kwargs[key])
            else:
                setattr(self, key, self.DEFAULTS[key])

    def connect(self, **kwargs):
        """ dialect+driver://username:password@host:port/database """
        if self.driver:
            connect_str = '{0}+{1}://{2}:{3}@{4}/{5}'.format(
                self.dialect,
                self.driver,
                self.user,
                self.pwrd,
                self.host,
                self.db,
            )
        else:
            connect_str = '{0}://{1}:{2}@{3}/{4}'.format(
                self.dialect,
                self.user,
                self.pwrd,
                self.host,
                self.db,
            )
        self.engine = create_engine(connect_str)
        self.sess = sessionmaker(bind=self.engine)

    @property
    def session(self):
        return self.sess
