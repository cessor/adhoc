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

    def domains(self):
        yield self._name
        if not self._has_subdomain():
            yield 'www.' + self._name


class Hosts(object):
    def __init__(self, hosts):
        self._hosts = hosts

    def domains(self):
        for host in self._hosts:
            yield from host.domains()


class Lines(object):
    def __init__(self, path):
        self._path = path

    def __iter__(self):
        with self._path.open('r') as file:
            for line in file:
                if not line.strip():
                    continue
                yield line.strip()

    def append(self, entries):
        with self._path.open('a') as file:
            file.write(os.linesep)
            for entry in entries:
                line = f"{entry}{os.linesep}"
                file.write(line)

    def clear(self):
        # https://stackoverflow.com/a/4914288/1203756
        self._path.open('w').close()

    def overwrite(self, lines):
        # This is not ideal, here it leaks
        # That lines is a filelike abstraction.
        # I don't want to pass a path object, however.
        self._path.replace(lines._path)


class Localhost(object):
    def __str__(self):
        return '127.0.0.1'


class Program(object):
    def __init__(self, hosts_file, temp_file, block_with, hosts):
        self._hosts_file = hosts_file
        self._temp_file = temp_file
        self._blocking_entry = block_with
        self._hosts = hosts

    def block(self):
        '''Blocks the hosts'''
        self._hosts_file.append(
            (self._blocking_entry.entry(domain)
             for domain in self._hosts.domains())
        )

    def unblock(self):
        '''Unblocks the hosts'''
        domains = list(self._hosts.domains())
        self._temp_file.clear()
        self._temp_file.append(
            line for line in self._hosts_file
            if not any(domain in line for domain in domains)
        )
        self._temp_file.overwrite(self._hosts_file)

    def print(self):
        '''Displays the contents of the etc/hosts file'''
        print(os.linesep.join(self._hosts_file))

    def help(self):
        '''Prints this help'''
        methods = [
            method for method in dir(self)
            if not method.startswith('_')
        ]
        for method in sorted(methods):
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
        temp_file=Lines(
            Path('./tmp')
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

    if 'print' in sys.argv:
        program.print()
        exit()

    if 'block' in sys.argv:
        program.block()
        exit()

    if 'unblock' in sys.argv:
        program.unblock()
        exit()

    if len(sys.argv) == 1:
        program.help()
        exit()
