import pwd
import os
import time
import string


def contains_any(seq, aset):
    """Check whether sequence seq contains ANY of the items in aset.
    """

    return any([x in aset for x in seq])


def unix_str(s):
    """Return a 'unix-friendly' version of string s.

    Examples:
    unix_str("abc") -> 'abc'
    unix_str("abc def") -> "'abc def'"
    unix_str("abc's def") -> AssertionError: String contains "'"
    """

    if contains_any(s, string.whitespace):
        return add_quotemarks(s)
    else:
        return s


def add_quotemarks(s):
    """Return string s with single quote marks added.
    Raises AssertionError if s contains any single quotes."""

    assert "'" not in s, "String contains \"'\""

    return "'%s'" % s


def create_shell_script(params=None, app='python', opts='-u', path='',
                        target='main.py', before=None, end=None,
                        headers=None, footers=None):
    """Creates the contents of a unix shell script that will
    run a python script with a set of pre-determined arguments
    and values.
    Args:
        params   - dictionary of parameter names and values that
                   you want to send to the python script.
        app      - name of app to run target on (default: 'python')
        opts     - string of options (default: '-u')
        path     - path string to target file (default: '')
        target   - filename of the script you want to run (default:
                   'main.py').
        before   - string will be added to beginning of main command
                   (default: None)
        end      - string will be added to end of main command
                   (default: None)
        headers  - list of strings that will be added as lines before
                   the app call.
        footers  - list of strings that will be added as lines after
                   the app call.
    Example:
    >>> params = {'model': 'LeNet', 'dataset': 'mnist'}
    >>> headers = ["LOGDIR='../logs/mnist/'", "mkdir -p $LOGDIR"]
    >>> end = "| tee $LOGDIR/log.out"
    >>> myscript = create_shell_script(params, headers=headers, end=end)
    >>> print(myscript)
    #!/bin/sh

    # This script was automatically generated
    # user: billtubbs
    # date: 2018-10-08 09:55

    LOGDIR='../logs/mnist/'
    mkdir -p $LOGDIR

    python -u main.py \
        --model LeNet \
        --dataset mnist \
        | tee $LOGDIR/log.out
    >>>
    """

    lines = []

    lines.append("#!/bin/sh")
    lines.append("")

    lines.append("# This script was automatically generated")
    lines.append("# user: %s" % pwd.getpwuid(os.getuid())[0])
    lines.append("# date: %s" % time.strftime("%Y-%m-%d %H:%M"))
    lines.append("")

    if headers is not None:
        lines.extend(headers)
        lines.append("")

    if before is not None:
        command = [before]
    else:
        command = []

    command.append(' '.join([app, opts, os.path.join(path, target)]))

    if params is not None:
        for key, value in params.items():
            command.append('    --%s %s' % (key, unix_str(str(value))))

    if end is not None:
        command.append('    %s' % str(end))

    lines.append(' \\\n'.join(command))
    lines.append("")

    if footers is not None:
        lines.extend(footers)
        lines.append("")

    return '\n'.join(lines)