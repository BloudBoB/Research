# -*- coding: utf-8 -*-
"""
Copyright 2016 Amazon.com, Inc. or its affiliates. All Rights Reserved.
"""

from __future__ import print_function

import decimal
import imp
import json
import logging
import math
import os
import site
import socket
import sys
import time
import traceback

import runtime as lambda_runtime

import wsgi


def _get_handlers(handler, mode, invokeid, throttled=False):
    lambda_runtime.report_user_init_start()
    init_handler = lambda: None

    """
    This is the old way we were loading modules.
    It was causing intermittent build failures for unknown reasons.
    Using the imp module seems to remove these failures.
    The imp module appears to be more extreme in that it reloads
    the module if it is already loaded, and it likely doesn't use any caches when
    searching for the module but does a full directory search, which is what we want.
    """
    # m = imp.load_module(modname, globals(), locals(), [])

    try:
        (modname, fname) = handler.rsplit('.', 1)
    except ValueError as e:
        fault = wsgi.FaultException("Bad handler '{}'".format(handler), str(e), None)
        request_handler = make_fault_handler(fault)
        lambda_runtime.report_user_init_end()
        return init_handler, request_handler

    file_handle, pathname, desc = None, None, None
    try:
        # Recursively loading handler in nested directories
        for segment in modname.split('.'):
            if pathname is not None:
                pathname = [pathname]
            file_handle, pathname, desc = imp.find_module(segment, pathname)
        if file_handle is None:
            module_type = desc[2]
            if module_type == imp.C_BUILTIN:
                request_handler = make_fault_handler(wsgi.FaultException(
                    "Cannot use built-in module {} as a handler module".format(modname),
                    None,
                    None
                ))
                lambda_runtime.report_user_init_end()
                return init_handler, request_handler
        m = imp.load_module(modname, file_handle, pathname, desc)
    except Exception as e:
        request_handler = load_handler_failed_handler(e, modname)
        lambda_runtime.report_user_init_end()
        # if the module load failed, usually we'd defer the error to the first INVOKE
        # if the throttled flag is set, there's another service tracking error states,
        # so we'll report the fault and exit to fail the INIT.
        #
        # request_handler constructed by load_handler_failed handler should always throw wsgi.FaultException.
        # This exception type has a .fatal field which signals if the runtime believes the error is not rety-able.
        # the report_fault helper returns this as it's 3rd return value.
        if throttled:
            try:
                request_handler()
            except Exception as e:
                errortype, result, fatal = report_fault(invokeid, e)
                if fatal:
                    lambda_runtime.report_done(invokeid, errortype, result, 1)
                    sys.exit(1)
        return init_handler, request_handler
    finally:
        if file_handle is not None:
            file_handle.close()

    try:
        init_handler = getattr(m, 'init')
    except AttributeError as e:
        pass

    try:
        request_handler = make_final_handler(getattr(m, fname), mode)
    except AttributeError as e:
        fault = wsgi.FaultException("Handler '{}' missing on module '{}'".format(fname, modname), str(e), None)
        request_handler = make_fault_handler(fault)
    lambda_runtime.report_user_init_end()
    return init_handler, request_handler


# Run a function called 'init', if provided in the same module as the request handler. This is an
# undocumented feature, existed to keep backward compatibility.
def run_init_handler(init_handler, invokeid):
    try:
        init_handler()
    except wsgi.FaultException as e:
        lambda_runtime.report_fault(invokeid, e.msg, e.except_value, e.trace)


class number_str(float):
    def __init__(self, o):
        self.o = o

    def __repr__(self):
        return str(self.o)

# Python 2.7.13 introduced a change for serializing classes that inherit form float type: https://bugs.python.org/issue27934
# Switch to int as the parent class to keep the same behavior for serializing Decimal types across Python 2 runtimes.
# The JSON serializer will call __str__ to get the JSON numeric representation. The Decimal will not be converted to an int,
# thus there is no precision loss.
class number_str_compatibility(int):
    def __str__(self):
        # Replicate behavior from Python's encoder_encode_float.
        # https://github.com/python/cpython/blob/e6239a3ab3e009a1b15918c1b8182290bb8a2e91/Modules/_json.c#L1948-L1962
        float_nr = float(self.decimal_nr)
        if not math.isinf(float_nr) and not math.isnan(float_nr):
            return str(self.decimal_nr)
        elif float_nr > 0:
            return "Infinity"
        elif float_nr < 0:
            return "-Infinity"
        else:
            return "NaN"


def decimal_serializer(o):
    if isinstance(o, decimal.Decimal):
        if sys.version_info[0] >= 3:
            return number_str(o)
        else:
            val = number_str_compatibility()
            val.decimal_nr = o
            return val
    raise TypeError(repr(o) + " is not JSON serializable")


def load_handler_failed_handler(e, modname):
    if isinstance(e, ImportError):
        return make_fault_handler(wsgi.FaultException("Unable to import module '{}'".format(modname), str(e), None))
    elif isinstance(e, SyntaxError):
        trace = "File \"%s\" Line %s\n\t%s" % (e.filename, e.lineno, e.text)
        fault = wsgi.FaultException("Syntax error in module '{}'".format(modname), str(e), trace)
    else:
        exc_info = sys.exc_info()
        trace = traceback.format_list(traceback.extract_tb(exc_info[2]))
        fault = wsgi.FaultException("module initialization error", str(e), trace[1:], fatal=True)
    return make_fault_handler(fault)


def make_fault_handler(fault):
    def result(*args):
        raise fault

    return result


def set_environ(credentials):
    key, secret, session = credentials.get('key'), credentials.get('secret'), credentials.get('session')
    # TODO delete from environ if params not found
    if credentials.get('key'):
        os.environ['AWS_ACCESS_KEY_ID'] = key
    if credentials.get('secret'):
        os.environ['AWS_SECRET_ACCESS_KEY'] = secret
    if credentials.get('session'):
        os.environ['AWS_SESSION_TOKEN'] = session
        os.environ['AWS_SECURITY_TOKEN'] = session


'''
PYTHONPATH may have paths that were not available when the interpreter was launched.
This would force the path importer cache get updated.
'''


def force_path_importer_cache_update():
    for path in os.environ.get("PYTHONPATH", "").split(":"):
        if path == os.environ["LAMBDA_RUNTIME_DIR"]:
            continue
        importer = sys.path_importer_cache.get(path, None)
        if not importer or isinstance(importer, imp.NullImporter):
            sys.path_importer_cache.pop(path, None)


def wait_for_start():
    (invokeid, mode, handler, suppress_init, throttled, credentials) = lambda_runtime.receive_start()
    force_path_importer_cache_update()
    set_environ(credentials)
    lambda_runtime.report_running(invokeid)

    return (invokeid, mode, handler, suppress_init, throttled, credentials)


def wait_for_invoke():
    (
        invokeid,
        data_sock,
        credentials,
        event_body,
        context_objs,
        invoked_function_arn,
        x_amzn_trace_id
    ) = lambda_runtime.receive_invoke()

    set_environ(credentials)

    return (invokeid, x_amzn_trace_id, data_sock, credentials, event_body, context_objs, invoked_function_arn)


def make_final_handler(handlerfn, mode):
    if mode == "http":
        def result(sockfd):
            invoke_http(handlerfn, sockfd)
    elif mode == "event":
        return handlerfn
    else:
        def result(sockfd):
            raise wsgi.FaultException("specified mode is invalid: " + mode)
    return result


def invoke_http(handlerfn, sockfd):
    fault_data = wsgi.handle_one(sockfd, ('localhost', 80), handlerfn)
    if fault_data:
        raise wsgi.FaultException(fault_data.msg, fault_data.except_value, fault_data.trace)


def try_or_raise(function, error_message):
    try:
        return function()
    except Exception as e:
        raise JsonError(sys.exc_info(), error_message)


def make_error(errorMessage, errorType, stackTrace):  # stackTrace is an array
    result = {}
    if errorMessage:
        result['errorMessage'] = errorMessage
    if errorType:
        result['errorType'] = errorType
    if stackTrace:
        result['stackTrace'] = stackTrace
    return result


def handle_http_request(request_handler, invokeid, sockfd):
    try:
        request_handler(sockfd)
    except wsgi.FaultException as e:
        lambda_runtime.report_fault(invokeid, e.msg, e.except_value, e.trace)
    finally:
        try:
            os.close(sockfd)
        except Exception as e:
            print("Error closing original data connection descriptor", file=sys.stderr)
            traceback.print_exc()
        finally:
            lambda_runtime.report_done(invokeid, None, None, 0)


def to_json(obj):
    return json.dumps(obj, default=decimal_serializer)

# convert an exception into a fault response, and report to the slicer
# returns error_type (string), result (json repsonse), and fatal (boolean)
def report_fault(invokeid, e):
    fatal = False
    if isinstance(e, wsgi.FaultException):
        lambda_runtime.report_fault(invokeid, e.msg, e.except_value, None)
        report_xray_fault_helper("LambdaValidationError", e.msg, [])
        result = make_error(e.msg, None, None)
        result = to_json(result)
        errortype = "unhandled"
        fatal = e.fatal
    elif isinstance(e, JsonError):
        result = report_fault_helper(invokeid, e.exc_info, e.msg)
        result = to_json(result)
        errortype = "unhandled"
    else:
        result = report_fault_helper(invokeid, sys.exc_info(), None)
        result = to_json(result)
        errortype = "unhandled"
    return errortype, result, fatal

def handle_event_request(request_handler, invokeid, event_body, context_objs, invoked_function_arn):
    lambda_runtime.report_user_invoke_start()
    errortype = None
    fatal = False
    try:
        client_context = context_objs.get('client_context')
        if client_context:
            client_context = try_or_raise(lambda: json.loads(client_context), "Unable to parse client context")
        context = LambdaContext(invokeid, context_objs, client_context, invoked_function_arn)
        json_input = try_or_raise(lambda: json.loads(event_body), "Unable to parse input as json")
        result = request_handler(json_input, context)
        result = try_or_raise(lambda: to_json(result), "An error occurred during JSON serialization of response")
    except Exception as e:
        errortype, result, fatal = report_fault(invokeid, e)

    lambda_runtime.report_user_invoke_end()
    lambda_runtime.report_done(invokeid, errortype, result, 1 if fatal else 0)
    if fatal:
        sys.exit(1)


def craft_xray_fault(ex_type, ex_msg, working_dir, tb_tuples):
    stack = []
    files = set()
    for t in tb_tuples:
        tb_file, tb_line, tb_method, tb_code = t
        tb_xray = {
            'label': tb_method,
            'path': tb_file,
            'line': tb_line
        }
        stack.append(tb_xray)
        files.add(tb_file)

    formatted_ex = {
        'message': ex_msg,
        'type': ex_type,
        'stack': stack
    }
    xray_fault = {
        'working_directory': working_dir,
        'exceptions': [formatted_ex],
        'paths': list(files)
    }
    return xray_fault


def report_xray_fault_helper(etype, msg, tb_tuples):
    xray_fault = craft_xray_fault(etype, msg, os.getcwd(), tb_tuples)
    xray_json = to_json(xray_fault)
    try:
        lambda_runtime.report_xray_exception(xray_json)
    except:
        # Intentionally swallowing
        # We don't report exception to the user just because Xray reported an exception.
        pass


def report_fault_helper(invokeid, exc_info, msg):
    etype, value, tb = exc_info
    if msg:
        msgs = [msg, str(value)]
    else:
        msgs = [str(value), etype.__name__]

    tb_tuples = extract_traceback(tb)

    if sys.version_info[0] >= 3:
        awesome_range = range
    else:
        awesome_range = xrange

    for i in awesome_range(len(tb_tuples)):
        if "/bootstrap.py" not in tb_tuples[i][0]:  # filename of the tb tuple
            tb_tuples = tb_tuples[i:]
            break

    lambda_runtime.report_fault(
        invokeid,
        msgs[0],
        msgs[1],
        (
            "Traceback (most recent call last):\n"
            + ''.join(traceback.format_list(tb_tuples))
            + ''.join(traceback.format_exception_only(etype, value))
        )
    )
    report_xray_fault_helper(etype.__name__, msgs[0], tb_tuples)

    return make_error(str(value), etype.__name__, tb_tuples)


def extract_traceback(tb):
    frames = traceback.extract_tb(tb)

    if sys.version_info[0] >= 3:
        # Python3 returns a list of SummaryFrames instead of a list of tuples
        # for traceback.extract_tb() calls.
        # To make it consistent, we map the list of frames to a list of tuples just like python2
        frames = [(frame.filename, frame.lineno, frame.name, frame.line) for frame in frames]

    return frames


class CustomFile(object):
    def __init__(self, fd):
        self._fd = fd

    def __getattr__(self, attr):
        return getattr(self._fd, attr)

    def write(self, msg):
        lambda_runtime.log_bytes(msg, self._fd.fileno())
        self._fd.flush()

    def writelines(self, msgs):
        for msg in msgs:
            lambda_runtime.log_bytes(msg, self._fd.fileno())
            self._fd.flush()


class CognitoIdentity(object):
    __slots__ = ["cognito_identity_id", "cognito_identity_pool_id"]


class Client(object):
    __slots__ = ["installation_id", "app_title", "app_version_name", "app_version_code", "app_package_name"]


class ClientContext(object):
    __slots__ = ['custom', 'env', 'client']


def make_obj_from_dict(_class, _dict, fields=None):
    if _dict is None:
        return None
    obj = _class()
    set_obj_from_dict(obj, _dict)
    return obj


def set_obj_from_dict(obj, _dict, fields=None):
    if fields is None:
        fields = obj.__class__.__slots__
    for field in fields:
        setattr(obj, field, _dict.get(field, None))


def byte_len(s):
    """ return the length of string s in bytes
    :param s: (str) string or (unicode) unicode literal
    :return (int) length of string in bytes
    """
    if sys.version_info[0] < 3:
        if (isinstance(s, unicode)):
            try:
                return len(s.encode('utf-8'))
            except:
                print("Malformed unicode string. Logs may be truncated")

        return len(s)
    else:
        # Python 3 treats surrogate pairs as length of 1, but in C the length is 2
        return len(s.encode())


class LambdaContext(object):
    def __init__(self, invokeid, context_objs, client_context, invoked_function_arn=None):
        self.aws_request_id = invokeid
        self.log_group_name = os.environ.get('AWS_LAMBDA_LOG_GROUP_NAME')
        self.log_stream_name = os.environ.get('AWS_LAMBDA_LOG_STREAM_NAME')
        self.function_name = os.environ.get("AWS_LAMBDA_FUNCTION_NAME")
        self.memory_limit_in_mb = os.environ.get('AWS_LAMBDA_FUNCTION_MEMORY_SIZE')
        self.function_version = os.environ.get('AWS_LAMBDA_FUNCTION_VERSION')
        self.invoked_function_arn = invoked_function_arn

        self.client_context = make_obj_from_dict(ClientContext, client_context)
        if self.client_context is not None:
            self.client_context.client = make_obj_from_dict(Client, self.client_context.client)
        self.identity = make_obj_from_dict(CognitoIdentity, context_objs)

    def get_remaining_time_in_millis(self):
        return lambda_runtime.get_remaining_time()

    def log(self, msg):
        str_msg = str(msg)
        lambda_runtime.send_console_message(str_msg, byte_len(str_msg))


class LambdaLoggerHandler(logging.Handler):
    def __init__(self):
        logging.Handler.__init__(self)

    def emit(self, record):
        msg = self.format(record)
        lambda_runtime.send_console_message(msg, byte_len(msg))


class LambdaLoggerFilter(logging.Filter):
    def filter(self, record):
        record.aws_request_id = _GLOBAL_AWS_REQUEST_ID or ""
        return True


class JsonError(Exception):
    def __init__(self, exc_info, msg):
        self.exc_info = exc_info
        self.msg = msg


_GLOBAL_DEFAULT_TIMEOUT = socket._GLOBAL_DEFAULT_TIMEOUT
_GLOBAL_AWS_REQUEST_ID = None


def log_info(msg):
    lambda_runtime.log_sb("[INFO] ({}) {}".format(__file__, msg))


def is_pythonpath_set():
    return "PYTHONPATH" in os.environ


def get_opt_site_packages_directory():
    return '/opt/python/lib/python{}.{}/site-packages'.format(sys.version_info.major, sys.version_info.minor)


def get_opt_python_directory():
    return '/opt/python'


# set default sys.path for discoverability
# precedence: /var/task -> /opt/python/lib/pythonN.N/site-packages -> /opt/python -> LAMBDA_RUNTIME_DIR
def set_default_sys_path():
    if not is_pythonpath_set():
        sys.path.insert(0, os.environ["LAMBDA_RUNTIME_DIR"])
        sys.path.insert(0, get_opt_python_directory())
        sys.path.insert(0, get_opt_site_packages_directory())
    # '/var/task' is function author's working directory
    # we add it first in order to mimic the default behavior of populating sys.path and make modules under '/var/task'
    # discoverable - https://docs.python.org/3/library/sys.html#sys.path
    sys.path.insert(0, os.environ['LAMBDA_TASK_ROOT'])


def add_default_site_directories():
    # Set '/var/task as site directory so that we are able to load all customer .pth files
    site.addsitedir(os.environ["LAMBDA_TASK_ROOT"])
    if not is_pythonpath_set():
        site.addsitedir(get_opt_site_packages_directory())
        site.addsitedir(get_opt_python_directory())


def set_default_pythonpath():
    if not is_pythonpath_set():
        # keep consistent with documentation: https://docs.aws.amazon.com/lambda/latest/dg/current-supported-versions.html
        os.environ["PYTHONPATH"] = os.environ["LAMBDA_RUNTIME_DIR"]


def main():
    if sys.version_info[0] < 3:
        reload(sys)
        sys.setdefaultencoding('utf-8')

    sys.stdout = CustomFile(sys.stdout)
    sys.stderr = CustomFile(sys.stderr)

    logging.Formatter.converter = time.gmtime
    logger = logging.getLogger()
    logger_handler = LambdaLoggerHandler()
    logger_handler.setFormatter(logging.Formatter(
        '[%(levelname)s]\t%(asctime)s.%(msecs)dZ\t%(aws_request_id)s\t%(message)s\n',
        '%Y-%m-%dT%H:%M:%S'
    ))
    logger_handler.addFilter(LambdaLoggerFilter())
    logger.addHandler(logger_handler)

    global _GLOBAL_AWS_REQUEST_ID

    # Remove lambda internal environment variables
    for env in [
        "_LAMBDA_CONTROL_SOCKET",
        "_LAMBDA_SHARED_MEM_FD",
        "_LAMBDA_LOG_FD",
        "_LAMBDA_SB_ID",
        "_LAMBDA_CONSOLE_SOCKET",
        "_LAMBDA_RUNTIME_LOAD_TIME",
        "_LAMBDA_DISABLE_INTERNAL_LOGGING"
    ]:
        os.environ.pop(env, None)

    (invokeid, mode, handler, suppress_init, throttled, credentials) = wait_for_start()

    set_default_sys_path()
    add_default_site_directories()
    set_default_pythonpath()

    if suppress_init:
        init_handler, request_handler = lambda: None, None
    else:
        init_handler, request_handler = _get_handlers(handler, mode, invokeid, throttled)
    run_init_handler(init_handler, invokeid)
    lambda_runtime.report_done(invokeid, None, None, 0)
    log_info("init complete at epoch {0}".format(int(round(time.time() * 1000))))

    while True:
        (invokeid, x_amzn_trace_id, sockfd, credentials, event_body, context_objs, invoked_function_arn) = wait_for_invoke()
        _GLOBAL_AWS_REQUEST_ID = invokeid

        if x_amzn_trace_id != None:
            os.environ['_X_AMZN_TRACE_ID'] = x_amzn_trace_id
        elif '_X_AMZN_TRACE_ID' in os.environ:
            del os.environ['_X_AMZN_TRACE_ID']

        # If the handler hasn't been loaded yet, due to init suppression, load it now.
        if request_handler is None:
            init_handler, request_handler = _get_handlers(handler, mode, invokeid)
            run_init_handler(init_handler, invokeid)

        if mode == "http":
            handle_http_request(request_handler, invokeid, sockfd)
        elif mode == "event":
            handle_event_request(request_handler, invokeid, event_body, context_objs, invoked_function_arn)


if __name__ == '__main__':
    log_info("main started at epoch {0}".format(int(round(time.time() * 1000))))
    main()
