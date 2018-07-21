#!/usr/bin/env python3
import os
from pathlib import Path
from urllib.parse import urlparse

'''
    Blocks a hosts by adding an entry to Windows' etc/hosts file
    that point to 127.0.0.1. I use this script to stop me from procrastinating.
'''


class BlockingEntry(object):

    def __init__(self, domain):
        self._domain = domain

    def entry(self, host):
        domain = str(self._domain)
        hostname = str(host)
        return f"{domain} {hostname}"


class Hostnames(object):
    def __init__(self, config, default):
        self._config = config
        self._default = default

    def _has_subdomain(self, domain):
        # True for www.example.com
        # False for example.com
        domain_parts = domain.split('.')
        return len(domain_parts) > 2

    def _hosts(self):
        try:
            hosts = list(self._config)
            assert hosts
            return hosts
        except:
            return list(self._default)

    def print(self):
        print(Lines(self._hosts()))

    def __iter__(self):
        for domain in self._hosts():
            yield domain
            if not self._has_subdomain(domain):
                yield 'www.' + domain


class File(object):
    def __init__(self, path):
        self._path = path

    def __iter__(self):
        with self._path.open('r') as file:
            for line in file:
                yield line.strip()

    def __str__(self):
        return self._path.read_text()

    def _write(self, content):
        self._path.write_text(content)

    def write_lines(self, lines):
        content = str(Lines(lines))
        self._write(content)


class HostsFile(object):
    '''The computer's hosts file is an operating system file that maps
    hostnames to IP addresses. It is used to block hosts'''
    # https://en.wikipedia.org/wiki/Hosts_%28file%29

    def __init__(self, file):
        self._file = file

    def append(self, lines):
        lines = list(self._file) + list(lines)
        self._file.write_lines(lines)

    def remove(self, predicate):
        lines = (line for line in self._file if not predicate(line))
        self._file.write_lines(lines)

    def print(self):
        print(self._file)


class Lines(object):
    def __init__(self, items):
        self._items = items

    def __str__(self):
        return '\n'.join(self._items)


class OperatingSystem():
    def hosts_file(self):
        return HostsFile(self._path())

    def _path(self):
        if os.name == 'posix':
            return self._posix()
        return self._windows()

    def _posix(self):
        return Path('/etc/hosts')

    def _windows(self):
        windows = os.environ.get('SYSTEMROOT')
        return Path(windows) / "System32/drivers/etc/hosts"


class Program(object):

    def __init__(self, hosts_file, block_with, hostnames):
        self._hosts_file = hosts_file
        self._blocking_entry = block_with
        self._hostnames = hostnames

    def block(self):
        '''Blocks the hosts'''
        self._hosts_file.append(
            self._blocking_entry.entry(hostname)
            for hostname in self._hostnames
        )

    def unblock(self):
        '''Unblocks the hosts'''
        hostnames = list(self._hostnames)
        self._hosts_file.remove(
            lambda line: any(host in line for host in hostnames)
        )

    def print(self):
        '''Displays the contents of the etc/hosts file'''
        self._hosts_file.print()

    def hosts(self):
        '''Lists the hosts to block.

        If available, reads from ~/.blockhostsrc, else a default list

        When blocking, www.* subdomains will be
        included automatically'''
        self._hostnames.print()

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
        hosts_file=HostsFile(
            File(
                Path('./etc_hosts') if 'test' in sys.argv else
                OperatingSystem().hosts_file()
            )
        ),
        block_with=BlockingEntry(
            '127.0.0.1'
        ),
        hostnames=Hostnames(
            File(
                Path.home() / ".blockhostsrc",
            ),
            default=[
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
