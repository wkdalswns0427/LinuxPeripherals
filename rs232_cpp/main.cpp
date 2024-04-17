// C library headers
#include <iostream>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/types.h>
#include <unistd.h> 

// headers
#include "config.h"
#include "RS485SETUP.h"
#include "PLCLOGIC.h" 

using namespace std;

typedef void(*CALLBACK_FUNC)(int);
CALLBACK_FUNC cbf = NULL;

void RegisterCallback(CALLBACK_FUNC cb){
    cbf = cb;
}

void StartCallback(int port){
    if(cbf==NULL){
        cout<<"Callback Not Registered"<<endl;
        return;
    }

    cout<<"Callback Begin"<<endl;
    cbf(port);
}

int main(int argc, char *argv[]){
    
    PLCLOGIC controller;
    int port_485;
    const char *deviceName;

    if(argc<3){
        deviceName = PORT;
    }
    else{
        deviceName = const_cast<char*>(argv[1]);
    }
    
    port_485 = controller.init_port(deviceName);

    controller.set_interface_attribs(port_485, BAUDRATE);

    controller.mode_numero(port_485, atoi(argv[1]));

    return 0;
}
