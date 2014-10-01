クワイン・マクラスキー法の実装
==================================

論理式を簡単にするアルゴリズムです

http://ja.wikipedia.org/wiki/%E3%82%AF%E3%83%AF%E3%82%A4%E3%83%B3%E3%83%BB%E3%83%9E%E3%82%AF%E3%83%A9%E3%82%B9%E3%82%AD%E3%83%BC%E6%B3%95

http://en.wikipedia.org/wiki/Quine%E2%80%93McCluskey_algorithm

## インストール

```
git clone https://github.com/takada-at/makurasan.git
cd makurasan
python setup.py install
```


## 使用法

```
>>> import makurasan as qm
>>> a, b, c, d = qm.Bool.create('abcd')
>>> z = ~a & ~b & c & d | b & c & d | a & b & ~c | a & ~b & c & d
>>> obj = qm.QuineMcCluskey(z)
>>> obj.compute()
c & d | (a & b) & ~c
```