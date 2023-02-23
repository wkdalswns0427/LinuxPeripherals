# socket

Ubuntu Mate targeted Linux Socket program

```
g++ -o <name> ypassSocketClient.cpp
g++ -o <name> testserver.cpp
```

### Usage

- client
./name <ip> <port> : port default 12242
- server
./name <port> : port default 12242

---
need to compile local crc16 package for CRC16-CCTIIXMODEM

```
tar -xzf crc16-0.1.1.tar.gz
cd crc16-0.1.1
python setup.py build
sudo python setup.py install
```