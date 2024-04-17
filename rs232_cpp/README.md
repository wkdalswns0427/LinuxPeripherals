# PLC control 8 channel relay controller

ubuntu native g++ compiler

```bash
# build
cd 485 && make

# clear .o files
make clean

# run
./plc_control <mode-number[1~14] : required> <port[default /dev/ttyS0] : optional>
```
