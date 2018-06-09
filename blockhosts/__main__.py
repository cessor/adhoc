#!/usr/bin/env python3
import os
from pathlib import Path
from urllib.parse import urlparse

'''
    Blocks a couple of hosts by adding an entry to Windows' etc/hosts file
    that point to 127.0.0.1. I use this script to stop me from procrastinating.

    Todo:
    [X] An automated switch could replace the HostsFile Object and make this
        script work for linux as well.
    [X] Read in the hosts from an external config file
    [ ] Add a comment to the hosts file, that these parts were added using
        this script
    [ ] The lines-Abstraction made sense along the way but it broke. Could it
        be improved?
    [ ] Separate CLI from Program
    [ ] Introduce a TEST Object
    [ ] Implement Selective Unblocking. Sometimes
        I just really needed AMAZON.com
    [ ] Introduce a Windows / Posix object, for post processing, e.g. flush dns
    [ ] Flush DNS after update:
        > ipconfig /flushdns
    [ ] I started procedural, moved to yegor style, and now it's quite
        procedural again. Could this be even more yegor style?
'''


class BlockingEntry(object):

    def __init__(self, domain):
        self._domain = domain

    def entry(self, host):
        domain = str(self._domain)
        hostname = str(host)
        return f"{domain} {hostname}"


class Config(object):

    def __init__(self, path):
        self._path = path

    def lines(self):
        if not self._path.is_file():
            return []
        # This is breaking the rules.
        # The Lines Object should be passed in
        # And the file should handle whether it exists
        # or not.
        # Example:
        # Lines(OptionalFile(Path(...))) ?
        return list(Lines(self._path))


class Host(object):

    def __init__(self, name):
        self._name = name

    def _has_subdomain(self):
        # True for www.heise.de
        # False for heise.de
        domain_parts = self._name.split('.')
        return len(domain_parts) > 2

    def __iter__(self):
        yield self._name
        if not self._has_subdomain():
            yield 'www.' + self._name

    def __str__(self):
        return self._name


class Hosts(object):

    def __init__(self, hosts):
        self._hosts = hosts

    def names(self):
        return sorted(str(host) for host in self._hosts)

    def __iter__(self):
        for host in self._hosts:
            yield from host


class HostsFile(object):
    '''The system's hosts file that is used to block the hosts '''
    # https://en.wikipedia.org/wiki/Hosts_%28file%29

    def _posix(self):
        return Path('/etc/hosts')

    def _windows(self):
        windows = os.environ.get('SYSTEMROOT')
        return Path(windows) / "System32/drivers/etc/hosts"

    def path(self):
        if os.name == 'posix':
            return self._posix()
        return self._windows()


class Lines(object):

    def __init__(self, path):
        self._path = path

    def __iter__(self):
        with self._path.open('r') as file:
            for line in file:
                line = line.strip()
                if line:
                    yield line

    def _content(self):
        with self._path.open('r') as file:
            return file.read()

    def _write(self, content):
        with self._path.open('w') as file:
            file.write(content)

    def remove(self, predicate):
        self._write(
            '\n'.join(
                line for line in self if not predicate(line)
            )
        )

    def append(self, lines):
        content = self._content() + '\n' + '\n'.join(lines)
        self._write(content)

    def print(self):
        print(self._path.open().read())


class Program(object):

    def __init__(self, hosts_file, block_with, hosts):
        self._hosts_file = hosts_file
        self._blocking_entry = block_with
        self._hosts = hosts

    def block(self):
        '''Blocks the hosts'''
        self._hosts_file.append(
            self._blocking_entry.entry(host) for host in self._hosts
        )

    def unblock(self):
        '''Unblocks the hosts'''
        hosts = list(self._hosts)
        self._hosts_file.remove(
            lambda line: any(host in line for host in hosts)
        )

    def print(self):
        '''Displays the contents of the etc/hosts file'''
        self._hosts_file.print()

    def hosts(self):
        '''Lists the hosts to block.

         If available, reads from ~/.blockhostsrc, else a default list

         When blocking, www.* subdomains will be
         included automatically'''
        print('\n'.join(self._hosts.names()))

    def help(self):
        '''Prints this help'''
        script = Path(__file__).name

        public_methods = [
            method for method in dir(self)
            if not method.startswith('_')
        ]

        arguments = '|'.join(public_methods)
        usage = f"{script} [test] {{{arguments}}}\n"
        print("Usage:")
        print(usage)

        for method in public_methods:
            print(method)
            print('\t', getattr(Program, method).__doc__)

        print('test')
        print('\t Use a local file to test (./etc_hosts)')


if __name__ == '__main__':
    import sys

    program = Program(
        hosts_file=Lines(
            Path('./etc_hosts') if 'test' in sys.argv else
            HostsFile().path()
        ),
        block_with=BlockingEntry(
            '127.0.0.1'
        ),
        hosts=Hosts(
            Host(name) for name in
            Config(Path.home() / ".blockhostsrc").lines()
            or [
                "amazon.com",
                "amazon.de",
                "blog.fefe.de",
                "facebook.com",
                "heise.de",
                "news.ycombinator.com",
                "rnz.de",
                "spiegel.de",
                "spon.de",
                "twitter.com",
                "youtube.com",
            ]
        )
    )

    try:
        argument = sys.argv[-1]
        getattr(program, argument)()
    except AttributeError:
        program.help()
        exit()
