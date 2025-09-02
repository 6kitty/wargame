```python
from Crypto.Util.number import long_to_bytes
enc2 = 332075826660041992234163956636404156206918624
y = enc2 ** (1/5)

print(y)

key=long_to_bytes(802134974)

class Vigenere_Cipher:
    def __init__(self, key):
        self._key = key

    def encrypt(self, msg):
        enc = b""
        for i in range(len(msg)):
            enc += bytes([(msg[i] - self._key[i % len(self._key)]) % 256])
        return enc

vgn = Vigenere_Cipher(key)
enc1 = long_to_bytes(25889043021335548821260878832004378483521260681242675042883194031946048423533693101234288009087668042920762024679407711250775447692855635834947612028253548739678779)

dec1=vgn.encrypt(enc1)

print(dec1)
```
해캠에서 다들 드림핵도 하길래 나도 간만에 CTF 신청하고 크립토부터 풀었다. 