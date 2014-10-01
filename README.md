クワイン・マクラスキー法の実装
==================================

http://en.wikipedia.org/wiki/Quine%E2%80%93McCluskey_algorithm

インストール::

python setup.py install


使用法::

>>> import makurasan as qm
>>> a, b, c, d = qm.Bool.create('abcd')
>>> z = ~a & ~b & c & d | b & c & d | a & b & ~c | a & ~b & c & d
>>> obj = qm.QuineMcCluskey(z)
>>> obj.compute()
c & d | (a & b) & ~c