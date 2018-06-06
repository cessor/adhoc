import os
from pathlib import Path
from urllib.parse import urlparse

'''
    Blocks a couple of hosts by adding an entry to Windows' etc/hosts file
    that point to 127.0.0.1. I use this script to stop me from procrastinating.

    Todo:
    [ ] The lines-Abstraction made sense along the way but it broke. Could it
        be improved?
    [ ] Add a comment to the hosts file, that these parts were added using
        this script
    [ ] An automated switch could replace the HostsFile Object and make this
        script work for linux as well.
    [ ] I started procedural, moved to yegor style, and now it's quite
        procedural again. Could this be even more yegor style?
    [ ] Read in the hosts from an external config file
    [ ] Separate CLI from Program
'''


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


class Lines(object):
    def __init__(self, path):
        self._path = path

    def __iter__(self):
        with self._path.open('r') as file:
            for line in file:
                if not line.strip():
                    continue
                yield line.strip()

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
        '''List the hosts'''
        print("Lists of Hosts to block.")
        print("When blocking, www.* subdomains will be included automatically")
        print()
        print('\n'.join(self._hosts.names()))

    def help(self):
        '''Prints this help'''
        script = os.path.basename(__file__)

        methods = [
            method for method in dir(self)
            if not method.startswith('_')
        ]
        arguments = '|'.join(methods)
        usage = f"{script} [test] {{{arguments}}}\n"
        print("Usage:")
        print(usage)

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
