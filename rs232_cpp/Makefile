CC=g++
CFLAGS=-g -Wall
# LDFLAGS= LINK_OPTIONS
# LDLIBS= LINK_LIBRARY
OBJS=RS485SETUP.o PLCLOGIC.o main.o
TARGET=plc_control

all : $(TARGET)

PLCLOGIC.o: PLCLOGIC.h RS485SETUP.h PLCLOGIC.cpp
PLCRELAY.o: RS485SETUP.h RS485SETUP.cpp
main.o: main.cpp

$(TARGET): $(OBJS)
	$(CC) -o $@ $(OBJS)


clean:
	rm -f *.o
#	rm -f $(TARGET)