from nose.tools import *
from kazookid import Substitute

from pathlib import Path
from blockhosts.__main__ import File, Hostnames, HostsFile, BlockingEntry, Program


def setup_module():
    test_dir = Path(__file__).parent
    (test_dir / '.test').write_text('')


def test_program():
    test_dir = Path(__file__).parent
    program = Program(
        hosts_file=HostsFile(File(test_dir / 'etc_hosts')),
        block_with=BlockingEntry('127.0.0.1'),
        hostnames=Hostnames(
            File(Path('.blockhostsrc')),
            default=[
                'example.com'
            ]
        )
    )
    program.help()
    program.hosts()
    program.block()
    program.print()
    program.unblock()
    program.print()
