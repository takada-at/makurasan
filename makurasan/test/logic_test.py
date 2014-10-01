# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

from .. import logic as qm

def test_Bool():
    a, b, c, d = qm.Bool.create('abcd')
    r = a | b
    assert r.name == 'a | b'

    r = a & b & c & (d | a)
    assert {a, b, c, d} == r.variables

    r = (b & c) & d
    assert [b, c, d] == r.children()

    r = a | a & c
    assert [a] == r.filter_children(r.children())

def test_normalize():
    a, b, c, d = qm.Bool.create('abcd')
    r = a | b
    assert r.normalize()==r

    r = (a | b) & c
    assert r.normalize() == a & c | b & c
    assert r.normalize().name == 'a & c | b & c'

    r = a & (b | c)
    assert r.normalize() == a & b | a & c
    assert r.normalize().name == 'a & b | a & c'

    r = a & (a | c)
    assert r.normalize() == a
    assert r.normalize().name == 'a'

    r = (a | b) & (a | c)
    #->a & (a|c) | b & (a|c)
    #->a | (b & a | a & c)
    #->a | b & c
    assert r.normalize() == a | b & c

    r = ~ (a & b)
    # -> ~a | ~b
    assert r.normalize() == ~a | ~b
    assert r.normalize().name == '~a | ~b'

    r = ~((a | b) & ~c)
    # -> ~(a | b) | ~~c
    # -> ~a & ~b | c
    r2 = r.normalize()
    assert r2 == ~a & ~b | c
    assert r2.name == '~a & ~b | c'

    r = ~(a | b & c)
    # -> ~a & ~(b & c)
    # -> ~a & (~b | ~c)
    # -> ~a & ~b | ~a & ~c
    assert r.normalize() == ~a & ~b | ~a & ~c

    r = (~(a | b & c) & d)
    # -> (~a & ~(b & c)) & d
    # -> (~a & (~b | ~c)) & d
    # -> (~a & ~b | ~a & ~c) & d
    # -> ~a & ~b & d | ~a & ~c & d
    r2 = r.normalize()
    assert r2 == ~a & ~b & d | ~a & ~c & d
    assert r2.name == '(~a & ~b) & d | (~a & ~c) & d'

    r = a | b | c | a
    r2 = r.normalize()
    assert r2 == a | b | c

    r = a | b | c | d & a
    r2 = r.normalize()
    assert r2 == a | b | c

    r = a & b & c & (d | a)
    r2 = r.normalize()
    assert r2 == a & b & c

    r = (c | b) & (c | b | d) & (c | d) & (b | d) & (c | a)
    # -> (c | bd) (c | a(b|d)) (b|d)
    # -> (c | bd) (c | ab | ad) (b|d)
    # -> (c | bd(ab|ad)) (b|d)
    # -> (c | abd) (b | d)
    # -> bc | cd | abd 
    r2 = r.normalize()
    expect = (b&c | c&d | a&b&d)
    assert {frozenset(child.children()) for child in expect.children()} == {frozenset(child.children()) for child in r2.children()} 

def test_normalize_random():
    from operator import and_, or_, invert
    import random
    num = random.randint(10, 30)
    atomics = qm.Bool.create('abcde')
    ops = [and_, or_, invert]
    # construct random form
    term = random.choice(atomics)
    for i in range(num):
        op = random.choice(ops)
        if op is invert:
            term = op(term)
        else:
            term = op(term, random.choice(atomics))

    nterm = term.normalize()
    print(term)
    print('-->', nterm)
    childs = nterm.children()
    # assert unique
    names = [k.name for k in childs]
    assert len(set(names))==len(names)
    for c in childs:
        assert not isinstance(c, qm.Or)
        names = [k.name for k in c.children()]
        assert len(set(names))==len(names)

def test_step0_minterms():
    a, b, c, d = qm.Bool.create('abcd')
    term = a & b | b & c
    term = term.normalize()
    assert a & b | b & c == term
    obj = qm.QuineMcCluskey(term)
    minterns = obj.step0_minterms()
    print(minterns)
    assert 3 == len(minterns)
    assert (1, 1, 1) == minterns[0] # a & b & c
    assert (1, 1, 0) == minterns[1] # a & b & ~c
    assert (0, 1, 1) == minterns[2] # ~a & b & c

def test_step1_prime_implicants():
    a, b, c, d = qm.Bool.create('abcd')
    obj = qm.QuineMcCluskey(a)
    T = [(0,1,0,0), (1,0,0,0), (1,0,0,1), (1,0,1,0), (1,1,1,0), (1,0,1,1), (1,1,0,0), (1,1,1,1)]
    primes = obj.step1_prime_implicants(T)
    c = qm.MergeTree.CHAR
    assert 4 == len(primes)
    print(primes)
    answer = {(c,1,0,0), (1,0,c,c), (1,c,c,0), (1,c,1,c)}
    assert answer == set(p.expr for p in primes)

def test_step2_essential_prime_implicants():
    a, b, c, d = qm.Bool.create('abcd')
    obj = qm.QuineMcCluskey(a&b&c&d)
    T = [(0,1,0,0), (1,0,0,0), (1,0,0,1), (1,0,1,0), (1,1,1,0), (1,0,1,1), (1,1,0,0), (1,1,1,1)]
    primes = obj.step1_prime_implicants(T)
    print(primes)
    essentials = obj.step2_essential_prime_implicants(primes)
    print(essentials)
    assert essentials
    assert {b&~c&~d, a&~b, a&c} == set(essentials.children())

def test_compute():
    a, b, c, d = qm.Bool.create('abcd')
    z = ~a & ~b & c & d | b & c & d | a & b & ~c | a & ~b & c & d
    obj = qm.QuineMcCluskey(z)
    z2 = obj.compute()
    assert z2 == c & d | a & b & ~c 
