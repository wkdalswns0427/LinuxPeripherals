// This is Client side

#include <iostream>
#include <sstream>
#include <sys/types.h>
#include <unistd.h>
#include <sys/socket.h>
#include <netdb.h>
#include <arpa/inet.h>
#include <string.h>
#include <string>
#include "crc.h"
#include "config.h"
#include <typeinfo>
#include <time.h>

using namespace std;

void printUsage(char *arg);
void getSysTime(char *sysdate, size_t buffersize);
u16 crc16_ccitt(const void *buf, int len);
char makeACK(char *buf);

int main( int argc, char *argv[])
{   
    unsigned int port;
    if (argc < 2)
    {
        printUsage(argv[0]);
        return 1;
    }
    else if(argc==2){
        printf("setting default port to 12242\n");
        port = 12242;
    }
    else{
        port = atoi(argv[2]);
    }

    //-------------------- config socket client --------------------
    //	Create a socket
    int sock = socket(AF_INET, SOCK_STREAM, 0);
    if (sock == -1)
    {
        return 1;
    }

    //	Create a hint structure for the server we're connecting with
    
    string ipAddress = argv[1];

    sockaddr_in hint;
    hint.sin_family = AF_INET;
    hint.sin_port = htons(port);
    inet_pton(AF_INET, ipAddress.c_str(), &hint.sin_addr);

    //	Connect to the server on the socket
    int connectRes = connect(sock, (sockaddr*)&hint, sizeof(hint));
    if (connectRes == -1)
    {
        return 1;
    }
    //---------------------------------------------------------------

    //	While loop:
    char buf[4096];
    char date[50];
    string userInput;

    //dummy ACK
    u8 DUMMY_ACK[] = {0x02, 0x00, 0x01, 0x11, 0x00, 0x00, 0x06, 0x11, 0x03};
    u8 DUMMY_ACK2[] = {0x02, 0x00, 0x01, 0xA0, 0x00, 0x00, 0x06, 0x11, 0x03};

    // make date info 
    /*
    getSysTime(date, sizeof(date));
    printf("%s\n", date);
    */

    while(true){
        memset(buf, 0, 4096);
        int bytesReceived = recv(sock, buf, 4096, 0);
        if (bytesReceived == -1)
        {
            cout << "There was an error getting response from server\r\n";
        }
        else
        {  
            cout <<"CLIENT RECV INIT> ";
            for(int i=0; i<bytesReceived; ++i)
                std::cout << std::hex << " " << (int)buf[i];
            cout<< "" <<endl;
            makeACK(buf);

            if((int)buf[3]==16){
                cout<<"INIT"<<endl;
                send(sock, DUMMY_ACK, sizeof(DUMMY_ACK), 0);
                break;
            }
        }

    }

    while(true){
        memset(buf, 0, 4096);
        int bytesReceived = recv(sock, buf, 4096, 0);
        if (bytesReceived == -1)
        {
            cout << "There was an error getting response from server\r\n";
        }
        else
        {  
            cout <<"CLIENT RECV V2> ";
            for(int i=0; i<bytesReceived; ++i)
                std::cout << std::hex << " " << (int)buf[i];
            cout<< "" <<endl;

            if(buf[3]==0x20){
                cout<<"OBU"<<endl;
                send(sock, DUMMY_ACK2, sizeof(DUMMY_ACK2), 0);
            }
        }

    }

    //	Close the socket
    close(sock);

    return 0;
}

void printUsage(char* arg)
{
    printf("Usage: %s <hostname> <port>\n", arg);
}


u16 crc16_ccitt(const char *buf, int len)
{
    register int counter;
    register u16 crc = 0;
    for( counter = 0; counter < len; counter++)
    crc = (crc<<8) ^ crc16tab[((crc>>8) ^ *(char *)buf++)&0x00FF];
    return crc;
}

char makeACK(char *buf)
{   
    char ACK[9];
    u16 CRC;
    u8 CRC_H, CRC_L;

    if(buf[3]==0x10){
        // ACk for INIT packet
        char CRCSET[5] = {buf[1], buf[2], buf[3], buf[4], buf[5]};
        CRC = crc16_ccitt(CRCSET, sizeof(CRCSET));
        std::cout<<std::hex<<CRC<<" "<<sizeof(CRC)<<endl;;

        CRC_H = (CRC>>8);
        CRC_L = CRC & 0xFFFF;
        std::cout<<std::hex<<CRC_H<<" "<<CRC_L<<endl;;
    }
    else if(buf[3]==0x20){
        // ACK for OBU info packet
    }
    
    return *ACK;
}