#!/usr/bin/env python
"""
OWL Client

Communicate with an OWL system to both retrieve informations (query mode) or
control it (command mode).


Installation
Simply copy the owl_client.py script anywhere in your $PATH


Requirements
Python 2.6 or later.


Usage
    shell> owl_client.py -H <OWLD host> [-P <port>] <command> [<argument list>]


Commands (Introspection)
 * list_methods
    Return the list of all available OWL methods with their description.


Commands (Query Mode)
 * resources_get_list
    Reurn the list of all available compute reources managed by the given OWL
    installation.

Commands (Command Mode)

"""
import json
import time


# Constants
OWLD_PORT = 9999




def owl_client(argv, addr, port, verbose=False):
    """
    Communicate with a remote OWLD listening on `addr` at `port`. The command
    (together with optional arguments) are passed as a full argv list.

    Return
    The answer from the oremote OWLD.
    """

    # Connect to (addr, port) and send argv in JSON format.
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.connect((addr, port))
    if(verbose):
        print('Connecting to %s:%d' % (addr, port))

    # We need to send the command and its arguments as a list (i.e. the full
    # argv list) in JSON format, new-line terminated.
    cmd_spec = json.dumps(argv) + '\n'
    if(verbose):
        print('Sending %s' % (cmd_spec.strip()))

    sock.sendall(cmd_spec)

    # Now wait for the answer from the remote OWLD.
    # res = recv(sock, 1024)
    res = ''
    while(True):
        tmp = sock.recv(1024)
        if(not tmp):
            break
        res += tmp

    # Cleanup and quit.
    sock.close()
    print(json.loads(res))
    return(0)




if(__name__ == '__main__'):
    import optparse
    import socket
    import sys



    USAGE = __doc__
    parser = optparse.OptionParser(USAGE)
    parser.add_option('-H', '--host',
                      dest='host',
                      type='str',
                      help='OWLD hostname or IP address')
    parser.add_option('-P', '--port',
                      dest='port',
                      type='int',
                      help='OWLD port. Defaults to %s' % OWLD_PORT,
                      default=int(OWLD_PORT))
    # Verbose flag
    parser.add_option('-v',
                      action='store_true',
                      dest='verbose',
                      default=False)

    # Parse the command line args.
    (options, args) = parser.parse_args()

    # Sanity check: we need at least one command and we need to make sure that
    # the OWLD hostname makes sense.
    if(not options.host):
        parser.error('Please specify the address/hostname of the OWLD.')
    try:
        # If this works, host is an IP.
        dummy = socket.inet_aton(options.host)
        ipaddr = options.host
    except socket.error:
        # Did not work: host might be a hostname. Convert it to IP.
        try:
            ipaddr = socket.gethostbyname(options.host)
        except socket.gaierror:
            parser.error('Unable to parse %s into a valid IP address.' \
                         % (options.host))
    if(not args):
        parser.error('Please specify a command.')

    sys.exit(owl_client(addr=ipaddr, port=options.port, argv=args,
                        verbose=options.verbose))


