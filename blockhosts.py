import os
from pathlib import Path
from urllib.parse import urlparse


class BlockingEntry(object):
    def __init__(self, domain):
        self._domain = domain

    def entry(self, host):
        domain = str(self._domain)
        hostname = str(host)
        return f"{domain} {hostname}"


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


class Hosts(object):
    def __init__(self, hosts):
        self._hosts = hosts

    def __iter__(self):
        for host in self._hosts:
            yield from host


class Lines(object):
    def __init__(self, path):
        self._path = path

    def __iter__(self):
        with self._path.open('r') as file:
            for line in file:
                if not line.strip():
                    continue
                yield line.strip()

    def write(self, content):
        with self._path.open('w') as file:
            file.write(content)

    def print(self):
        print(self._path.open().read())


class Localhost(object):
    def __str__(self):
        return '127.0.0.1'


class Program(object):
    def __init__(self, hosts_file, block_with, hosts):
        self._hosts_file = hosts_file
        self._blocking_entry = block_with
        self._hosts = hosts

    def block(self):
        '''Blocks the hosts'''
        self._hosts_file.write(
            os.linesep.join(
                [
                    *[line for line in self._hosts_file],
                    *[self._blocking_entry.entry(host) for host in self._hosts]
                ]
            )
        )

    def unblock(self):
        '''Unblocks the hosts'''
        hosts = list(self._hosts)
        content = os.linesep.join(
            line for line in self._hosts_file
            if not any(host in line for host in hosts)
        )
        self._hosts_file.write(content)

    def print(self):
        '''Displays the contents of the etc/hosts file'''
        self._hosts_file.print()

    def hosts(self):
        '''List the hosts'''
        print(os.linesep.join(self._hosts))

    def help(self):
        '''Prints this help'''
        methods = [
            method for method in dir(self)
            if not method.startswith('_')
        ]
        for method in methods:
            print(method)
            print('\t', getattr(Program, method).__doc__)

        print('test')
        print('\t Use a local file to test (./etc_hosts)')


if __name__ == '__main__':
    import sys
    windows = os.environ.get('SYSTEMROOT')

    program = Program(
        hosts_file=Lines(
            Path('./etc_hosts') if 'test' in sys.argv else
            Path(windows) / "System32/drivers/etc/hosts"
        ),
        block_with=BlockingEntry(
            Localhost()
        ),
        hosts=Hosts(
            Host(name) for name in [
                "blog.fefe.de",
                "news.ycombinator.com",
                "facebook.com",
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
    except:
        program.help()
        exit()
