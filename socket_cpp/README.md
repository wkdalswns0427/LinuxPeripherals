# linux-socket

Ubuntu Mate targeted Linux Socket program

```
g++ -o <name> SocketClient.cpp
g++ -o <name> testserver.cpp
```

### Usage

- client
./name <ip> <port> : port default 12242
- server
./name <port> : port default 12242

CRC : CRC 16
Data Encryption method : custom AES128 format (custom S-Box matrix)
