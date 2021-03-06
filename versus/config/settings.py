
__secret_key__ = 'none'
__version__ = '0.0.1'

# HOST IPs - Use first if you're running on vagrant instance
#       see http://stackoverflow.com/questions/5984217/
# vagrants-port-forwarding-not-working?rq=1
__instance_host_vagrant__ = '0.0.0.0'
__instance_host__ = '127.0.0.1'

__instance_port__ = 5000

LICENSE = "BSD (Three Clause)"

AUTHORS = {
    'Ryan Faulkner': 'bobs.ur.uncle@gmail.com'
}

ADMINS = {
    'Ryan Faulkner': 'bobs.ur.uncle@gmail.com'
}

USERS = {}

FLASK_LOG = '/var/log/flask.log'

HADOOP_USER = 'hduser'
MAX_BUFFER_SIZE = 1024

HDFS_BUFFER_FILE = '/var/local/text_learn_buff'
HDFS_STAGE = '/user/' + HADOOP_USER + '/stage'
HDFS_IN = '/user/' + HADOOP_USER + '/input'
HDFS_OUT = '/user/' + HADOOP_USER + '/output'
HDFS_STORE = '/user/' + HADOOP_USER + '/archive'