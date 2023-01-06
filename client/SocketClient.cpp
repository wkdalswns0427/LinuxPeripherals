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

#define INIT_ACK_SIZE 16
#define DATA_ACK_SIZE 9

void printUsage(char *arg);
void getSysTime(uint8_t *buf);
u16 crc16_ccitt(const void *buf, int len);
void makeACK(char *buf, int len, char *ACK,  int returnlen);
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
   
            if((int)buf[3]==0x10){
                makeACK(buf, bytesReceived, ACK, INIT_ACK_SIZE);
                send(sock, ACK, INIT_ACK_SIZE, 0);
                break;
            }
            else{
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
            cout <<"CLIENT RECV OBU> ";
            for(int i=0; i<bytesReceived; ++i)
                std::cout << std::hex << " " << (int)buf[i];
            cout<< "" <<endl;

            if(buf[3]==0x20){
                makeACK(buf, bytesReceived, ACK, DATA_ACK_SIZE);
                send(sock, ACK, DATA_ACK_SIZE, 0);
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

void getSysTime(uint8_t *buf){
    time_t t = time(0);
    struct tm* lt = localtime(&t);
    char time_str[15];

    buf[0] = 20;//(lt->tm_year + 1900)
    buf[1] = (lt->tm_year - 100);
    buf[2] = (lt->tm_mon + 1);
    buf[3] = (lt->tm_mday);
    buf[4] = (lt->tm_hour + 9);
    buf[5] = (lt->tm_min);
    buf[6] = (lt->tm_sec);    
}

void makeACK(char *buf, int len, char *ACK, int returnlen)
{   
    u16 CRC;
    u8 CRC_H, CRC_L;
    uint8_t time[7];

    // ACk for INIT packet
    if(buf[3]==0x10){
        //---------- CRC check : verify //----------
        char CRCSET[5] = {buf[1], buf[2], buf[3], buf[4], buf[5]};
        CRC = crc16_ccitt(CRCSET, sizeof(CRCSET));
        CRC_H = (CRC>>8);CRC_L = (CRC & 0xFF);
        //------------------------------------------

        // if CRC is verified, generate one for return ACK
        if((CRC_H == buf[len-3])&&(CRC_L==buf[len-2])){
            CRCSET[2] = 0x11;
            CRC = crc16_ccitt(CRCSET, sizeof(CRCSET));
            CRC_H = (CRC>>8);CRC_L = (CRC & 0xFF);
        }
        getSysTime(time);

        // generate ACK message
        ACK[0] = 0x02;
        for(int i = 0; i<3; i++){
            ACK[i+1] = CRCSET[i];
        }
        ACK[4] = 0x00; ACK[5] = 0x07;
        // date 7 bytes
        for(int i = 0; i < 7; i++){
            ACK[i+6] = time[i];
        }
        ACK[returnlen-3] = CRC_H; ACK[returnlen-2] = CRC_L; ACK[returnlen-1] = 0x03;
    }

    // ACK for OBU info packet
    else if(buf[3]==0x20){
        //---------- CRC check : verify //----------
        char CRCSET[len - 4];
        for(int i = 0; i<(len-4); i++){
            CRCSET[i] = buf[i+1];
        }
        CRC = crc16_ccitt(CRCSET, sizeof(CRCSET));
        CRC_H = (CRC>>8); CRC_L = (CRC & 0xFF);
        //------------------------------------------

        // if CRC is verified, generate one for return ACK
        if((CRC_H == buf[len-3])&&(CRC_L==buf[len-2])){
            CRCSET[2] = 0xa0;
            CRC = crc16_ccitt(CRCSET, sizeof(CRCSET));
            CRC_H = (CRC>>8);CRC_L = (CRC & 0xFF);
        }
        
        // return ACK 
        ACK[0] = 0x02;
        for(int i = 0; i<6; i++){
            ACK[i+1] = CRCSET[i];
        }
        ACK[returnlen-3] = CRC_H; ACK[returnlen-2] = CRC_L; ACK[returnlen-1] = 0x03;
    }
    
}

char decodeAES128(char *buf){

    return 0;
}