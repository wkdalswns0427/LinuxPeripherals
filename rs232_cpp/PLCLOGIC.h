#ifndef __PLCLOGIC_H__
#define __PLCLOGIC_H__

#include "RS485SETUP.h"

class PLCLOGIC : public RS485SETUP
{
    private:
        enum
        {
            // LOGIC_NUMBER = 1
            // BAUDRATE = 9600
        };


    public:
        // logics   
        int mode_numero(int port, int number);
        int port_watchdog(int port, char* buf);
        static void PLCCallback(int port);
};

#endif