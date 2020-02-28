import sys
import os.path
import io
import datetime
import traceback


class MessageType:

    def __init__(self, name, identifier, code, level, icon):
        self.name = name
        self.identifier = identifier
        self.code = code
        self.level = level
        self.icon = icon

    def __str__(self):
        return self.identifier

    def __hash__(self):
        return hash(self.identifier)


EMERG_MSG_LEVEL = 0
ALERT_MSG_LEVEL = 1
CRIT_MSG_LEVEL = 2
ERR_MSG_LEVEL = 3
WARNING_MSG_LEVEL = 4
NOTICE_MSG_LEVEL = 5
SUCCESS_MSG_LEVEL = 6
INFO_MSG_LEVEL = 7
DEBUG_MSG_LEVEL = 8
NO_LOG_MSG_LEVEL = -1

EMERG_ID = '$$0'
ALERT_ID = '$$1'
CRIT_ID = '$$2'
ERR_ID = '$$3'
WARNING_ID = '$$4'
NOTICE_ID = '$$5'
SUCCESS_ID = '$$6'
INFO_ID = '$$7'
DEBUG_ID = '$$8'
NO_LOG_ID = '$$9'

EMERG_ICON = "[ EMERG ]"
ALERT_ICON = "[ ALERT ]"
CRIT_ICON = "[ CRIT  ]"
ERR_ICON = "[  ERR  ]"
WARNING_ICON = "[WARNING]"
NOTICE_ICON = "[NOTICE ]"
INFO_ICON = "[ INFO  ]"
DEBUG_ICON = "[ DEBUG ]"
SUCCESS_ICON = "[SUCCESS]"
NO_LOG_ICON = ''

EMERG_CODE = f'\033[1;31m{EMERG_ICON} '
ALERT_CODE = f'\033[1;31m{ALERT_ICON} '
CRIT_CODE = f'\033[1:31m{CRIT_ICON} '
ERR_CODE = f'\033[1;31m{ERR_ICON}\033[0m '
WARNING_CODE = f'\033[0m\033[1;33m{WARNING_ICON}\033[0m '
NOTICE_CODE = f'\033[0m\033[1;34m{NOTICE_ICON}\033[0m '
INFO_CODE = f'\033[0m\033[1;30m{INFO_ICON}\033[0m '
DEBUG_CODE = f'\033[0m\033[1m{DEBUG_ICON}\033[0m '
SUCCESS_CODE = f'\033[0m\033[1;32m{SUCCESS_ICON}\033[0m '
NO_LOG_CODE = f'\033[0m'

EMERG = MessageType('EMERG', EMERG_ID, EMERG_CODE, EMERG_MSG_LEVEL, EMERG_ICON)
ALERT = MessageType('ALERT', ALERT_ID, ALERT_CODE, ALERT_MSG_LEVEL, ALERT_ICON)
CRIT = MessageType('CRIT', CRIT_ID, CRIT_CODE, CRIT_MSG_LEVEL, CRIT_ICON)
ERR = MessageType('ERR', ERR_ID, ERR_CODE, ERR_MSG_LEVEL, ERR_ICON)
WARNING = MessageType('WARNING', WARNING_ID, WARNING_CODE, WARNING_MSG_LEVEL, WARNING_ICON)
NOTICE = MessageType('NOTICE', NOTICE_ID, NOTICE_CODE, NOTICE_MSG_LEVEL, NOTICE_ICON)
SUCCESS = MessageType('SUCCESS', SUCCESS_ID, SUCCESS_CODE, SUCCESS_MSG_LEVEL, SUCCESS_ICON)
INFO = MessageType('INFO', INFO_ID, INFO_CODE, INFO_MSG_LEVEL, INFO_ICON)
DEBUG = MessageType('DEBUG', DEBUG_ID, DEBUG_CODE, DEBUG_MSG_LEVEL, DEBUG_ICON)
NO_LOG = MessageType('NO_LOG', NO_LOG_ID, NO_LOG_CODE, NO_LOG_MSG_LEVEL, NO_LOG_ICON)

CODEBOOK = {
    EMERG_ID: EMERG,
    ALERT_ID: ALERT,
    CRIT_ID: CRIT,
    ERR_ID: ERR,
    WARNING_ID: WARNING,
    NOTICE_ID: NOTICE,
    SUCCESS_ID: SUCCESS,
    INFO_ID: INFO,
    DEBUG_ID: DEBUG,
    NO_LOG_ID: NO_LOG
}


class Logger(object):
    """
    Main working object. Splits input from print() statements in wrapped function to
    a logging buffer and stdout. Also optionally tags and timestamps messages
    """
    def __init__(self, verbosity, log_level, add_timestamp, default_msg_type):
        self.old_stdout = sys.stdout

        if type(verbosity) == MessageType:
            self.verbosity = verbosity.level
        elif verbosity is False or verbosity is None:
            self.verbosity = -1
        else:
            self.verbosity = verbosity

        if type(log_level) == MessageType:
            self.log_level = log_level.level
        elif log_level is False or log_level is None:
            self.log_level = -1
        else:
            self.log_level = log_level

        self.log_buffer = io.StringIO()
        self.stdout = sys.stdout
        sys.stdout = self
        self.add_timestamp = add_timestamp
        self.buffered_msg_type = None
        self.default_msg_type = default_msg_type
        print(DEBUG, f"Started new Logger. verbosity={self.verbosity}, log_level={self.log_level}, "
                     f"add_timestamp={add_timestamp}, default_msg_type={default_msg_type.name}")

    def __del__(self):
        """
        Returns stdout to its original state
        """
        sys.stdout = self.old_stdout

    def close(self):
        self.__del__()

    def write(self, data):
        """
        Intercepts output of print() calls inside decorated function and writes data
        to stdout and a log buffer.
        """
        ts = Logger.get_timestamp() if self.add_timestamp else ''
        if self.buffered_msg_type is not None:
            # print(a, b) puts a space AKA chr(32) between a and b--ignore
            if data == chr(32):
                return
            elif data in CODEBOOK:
                # MessageTypes and data are out-of-order. Should never get here.
                self.buffered_msg_type = CODEBOOK[data]
                return
            else:
                code = self.buffered_msg_type.code
                msg_level = self.buffered_msg_type.level
                icon = self.buffered_msg_type.icon
                self.buffered_msg_type = None
        elif data in CODEBOOK:
            self.buffered_msg_type = CODEBOOK[data]
            return
        else:
            # program ends with a newline character AKA chr(10)--ignore it
            if data == chr(10):
                return
            code = self.default_msg_type.code
            msg_level = self.default_msg_type.level
            icon = self.default_msg_type.icon

        if self.verbosity >= msg_level:
            if code == NO_LOG:
                self.stdout.write(f"{code}{data}\n")
            else:
                self.stdout.write(f"{code}{ts}{data}\n")

        if self.log_level >= msg_level and code != NO_LOG:
            self.log_buffer.write(f"{icon} {ts}{data}\n")

    def read(self):
        """
        returns:
            str: Contents of log buffer
        """
        return self.log_buffer.getvalue()

    def flush(self):
        self.stdout.flush()

    @staticmethod
    def get_timestamp():
        return f"{datetime.datetime.now()}: "


class barometer(object):
    """
    Main logging decorator. Adds verbosity control and logging by redirecting stdout
    """
    def __init__(self, wrapped):
        self.wrapped = wrapped

    # Called when decorating a class method
    def __get__(self, instance, owner):
        return self.__class__(self.wrapped.__get__(instance, owner))

    def __call__(self, *args, verbosity=7, log_level=False, add_timestamp=True,
                 logfile='log.txt', default_msg_type=NO_LOG, **kwargs):
        """
        args:
            verbosity: Maximum level of message that will be displayed on stdout.
                If a MessageType is passed in, will  be set to the level of that type.
                Displays nothing if set to False or None
            log_level: Maximum level of message that will be logged to file.
                If a MessageType is passed in, will  be set to the level of that type.
                Logs nothing if set to False or None
            add_timestamp (bool): Adds timestamps to messages if True
            logfile (str): Filename to save log buffer to. If None, returns
                (result, log) as a tuple
            default_msg_type (MessageType): Default MessageType if none specified
        """
        logger = Logger(verbosity, log_level, add_timestamp, default_msg_type,)
        result = None
        try:
            if args:
                if kwargs:
                    result = self.wrapped(*args, **kwargs)
                else:
                    result = self.wrapped(*args)
            else:
                if kwargs:
                    result = self.wrapped(**kwargs)
                else:
                    result = self.wrapped()
        except:
            tb = traceback.format_exc()
            print(ALERT, f"Unhandled exception!\n{tb}")
        finally:
            if log_level is not None and log_level is not False:
                # dumps contents of log buffer to "data"
                data = logger.read()
                if logfile is None:
                    return result, data
                if os.path.exists(logfile):
                    with open(logfile, 'a') as log:
                        log.write(data)
                else:
                    with open(logfile, 'w') as log:
                        log.write(data)
            logger.close()
        return result


if __name__=="__main__":
    print("barometer should not be run alone. Please read README.md!")
