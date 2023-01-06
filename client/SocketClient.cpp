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
#include <bitset>
#include <cstdio>
#include <ctime>

using namespace std;

void printUsage(char *arg);
void getSysTime(char *sysdate, size_t buffersize);
u16 crc16_ccitt(const void *buf, int len);
void makeACK(char *buf, int len, char *ACK);
char decodeAES128(char *buf);

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
    char ACK[50];
    string userInput;

    //dummy ACK
    u8 DUMMY_ACK[] = {0x02, 0x00, 0x01, 0x11, 0x00, 0x00, 0x06, 0x11, 0x03};
    u8 DUMMY_ACK2[] = {0x02, 0x00, 0x01, 0xA0, 0x00, 0x00, 0x06, 0x11, 0x03};

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

            makeACK(buf, bytesReceived, ACK);

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
                makeACK(buf, bytesReceived, ACK);
                cout<<"OBU"<<endl;
                send(sock, ACK, sizeof(DUMMY_ACK2), 0);
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

void getSysTime(char *buf){
    std::time_t rawtime;
    std::tm* timeinfo;

    std::time(&rawtime);
    timeinfo = std::localtime(&rawtime);

    std::strftime(buf, 50,"%Y%m%d%H%M%S", timeinfo);
    std::puts(buf);

}

void makeACK(char *buf, int len, char *ACK)
{   
    u16 CRC;
    u8 CRC_H, CRC_L;
    char time[50];

    // ACk for INIT packet
    if(buf[3]==0x10){
        //CRC check : verify
        char CRCSET[len - 4] = {buf[1], buf[2], buf[3], buf[4], buf[5]};
        CRC = crc16_ccitt(CRCSET, sizeof(CRCSET));
        CRC_H = (CRC>>8);CRC_L = (CRC & 0xFF);

        if((CRC_H == buf[-3])&&(CRC_L==buf[-2])){
            // if CRC is verified, generate one for return ACK
            CRCSET[2] = 0x11;
            CRC = crc16_ccitt(CRCSET, sizeof(CRCSET));
            CRC_H = (CRC>>8);CRC_L = (CRC & 0xFF);
        }
        // generate ACK message

    }

    // ACK for OBU info packet
    else if(buf[3]==0x20){
        //CRC check : verify
        char CRCSET[len - 4];
        for(int i = 0; i<(len-4); i++){
            CRCSET[i] = buf[i+1];
        }
        CRC = crc16_ccitt(CRCSET, sizeof(CRCSET));
        CRC_H = (CRC>>8); CRC_L = (CRC & 0xFF);
        printf("%d , %d, bytes : %d\n", CRC_H, CRC_L, len);

        if((CRC_H == buf[len-3])&&(CRC_L==buf[len-2])){
            // if CRC is verified, generate one for return ACK
            CRCSET[2] = 0xa0;
            CRC = crc16_ccitt(CRCSET, sizeof(CRCSET));
            CRC_H = (CRC>>8);CRC_L = (CRC & 0xFF);
        }
        
        // return ACK 
        ACK[0] = 0x02;
        for(int i = 0; i<6; i++){
            ACK[i+1] = CRCSET[i];
        }
        ACK[6] = CRC_H; ACK[7] = CRC_L; ACK[8] = 0x03;
    }
    
}

char decodeAES128(char *buf){

    return 0;
}