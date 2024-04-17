#include <iostream>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/types.h>
#include <unistd.h>

#include <fcntl.h>// Contains file controls like O_RDWR
#include <errno.h> // Error integer and strerror() function
#include <termios.h> // Contains POSIX terminal control definitions
#include <unistd.h> // write(), read(), close()
#include <errno.h>
#include <cstring>

#include "config.h"
#include "PLCLOGIC.h"
#include "RS485SETUP.h"

using namespace std;

int PLCLOGIC::mode_numero(int port, int number){
    // contents
    const int *target = leisuwash_sg[number-1];
    send_data_over_serial(port, target);
    return 1;
}

int PLCLOGIC::port_watchdog(int port, char* buf){
    memset(&buf, '\0', sizeof(buf));
    int num_bytes = read(port, &buf, sizeof(buf));

    if (num_bytes < 0) {
      std::cout << "Error reading: %s" << strerror(errno) << std::endl;
      return 1;
    }
    return 0;
}


void PLCLOGIC::PLCCallback(int port){
  PLCLOGIC logic;
  char buffer[20];
  int res = logic.port_watchdog(port, buffer);

  // some logic reading kiosk input
}
