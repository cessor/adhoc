from nose.tools import *
from kazookid import Substitute
from blockhosts.__main__ import Hostnames


def test_hosts_uses_the_config():
    hosts = Hostnames(config=['a', 'b'], default=[])
    assert_equal(list(hosts._hosts()), ['a', 'b'])


def test_hosts_uses_default_if_config_if_both_given():
    hosts = Hostnames(config=['a', 'b'], default=['c', 'd'])
    assert_equal(list(hosts._hosts()), ['a', 'b'])


def test_hosts_uses_default_if_config_empty():
    hosts = Hostnames(config=[], default=['a', 'b'])
    assert_equal(list(hosts._hosts()), ['a', 'b'])


def test_hosts_returns_common_sub_domains_as_well():
    hosts = ['example.com']
    hosts = Hostnames(config=hosts, default=[])
    hosts = list(hosts)
    assert_equal(hosts, ['example.com', 'www.example.com'])


def test_hosts_returns_specific_domains():
    hosts = ['example1.example.com']
    hosts = Hostnames(config=hosts, default=[])
    hosts = list(hosts)
    assert_equal(hosts, ['example1.example.com'])


def test_failover_in_case_of_exception():
    class Iterator(object):
        def __iter__(self):
            raise FileNotFoundError()

    file = Substitute()
    file.yields(Iterator())
    hosts = Hostnames(config=file, default=['a', 'b'])
    assert_equal(list(hosts._hosts()), ['a', 'b'])