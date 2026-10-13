# Day 3 dependency sources

Downloaded 13 October 2026. Files below are unmodified upstream copies.

MicroPython-lib commit: `90028be0829c6e988b5e239b28f39fb91b6b20e2`. The MIT license is included.

- `umqtt/simple.py`: [upstream](https://raw.githubusercontent.com/micropython/micropython-lib/90028be0829c6e988b5e239b28f39fb91b6b20e2/micropython/umqtt.simple/umqtt/simple.py); SHA-256 `5458b97fc074db01263e82ae898727aee2a15079ea5cff9d2f6d6abbea8ea217`.

- `ntptime.py`: [upstream](https://raw.githubusercontent.com/micropython/micropython-lib/90028be0829c6e988b5e239b28f39fb91b6b20e2/micropython/net/ntptime/ntptime.py); SHA-256 `aeae0fffa28a0a18bf2975f9140ab58af43b04e555d772ddc97601e209744c13`.

- `MicroPython-lib-LICENSE.txt`: [upstream](https://raw.githubusercontent.com/micropython/micropython-lib/90028be0829c6e988b5e239b28f39fb91b6b20e2/LICENSE); SHA-256 `a38cf48836aa313254cdcf3de9fb7c24da4a2eab75ead2cc0cecd998336e7800`.

- `certs/isrg-root-x1.pem`: [upstream](https://letsencrypt.org/certs/isrgrootx1.pem); SHA-256 `22b557a27055b33606b6559f37703928d3e4ad79f110b407d04986e1843543d1`.


The empty `umqtt/__init__.py` is a course packaging file.


ISRG Root X1 is public trust material, not a private key. The broker chain was verified against this root from the instructor computer; ESP32 TLS still needs rehearsal. Root certificate information: https://letsencrypt.org/certificates/ .
