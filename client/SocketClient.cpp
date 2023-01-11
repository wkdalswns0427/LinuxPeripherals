// This is Client side

#include <iostream>
#include <cstring>
#include <fstream>
#include <sstream>
#include <sys/types.h>
#include <unistd.h>
#include <sys/socket.h>
#include <netdb.h>
#include <arpa/inet.h>
#include <string.h>
#include <string>
#include <typeinfo>
#include <time.h>
#include <bitset>
#include <cstdio>
#include <ctime>
#include "../src/config.h"
#include "../src/crc.h"
#include "../src/structures.h"
#include "../src/AES128.h"

using namespace std;

#define INIT_ACK_SIZE 16
#define DATA_ACK_SIZE 9

void printUsage(char *arg);
void getSysTime(uint8_t *buf);
u16 crc16_ccitt(const void *buf, int len);
void makeACK(char *buf, int len, char *ACK,  int returnlen, int err = 0);
char* decodeAES128(char *buf);

// error count --> program shutdown at 5
uint8_t errcnt = 0;

int main( int argc, char *argv[])
{   
    //----------------------------------------- Set Socket Port ------------------------------------------------
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
    //--------------------------------------------------------------------------------------------------------

    //-------------------------------------- Config Socket Client ---------------------------------------------
    int sock = socket(AF_INET, SOCK_STREAM, 0);
    if (sock == -1)
    {
        return 1;
    }
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
    //--------------------------------------------------------------------------------------------------------

    //---------------------------------------------- Buffers!!! ----------------------------------------------
    char buf[50] = {0,};
    char ACK[20] = {0,};
    char NACK[10] = {0,};
    char* decrypted_buf;
    //--------------------------------------------------------------------------------------------------------

    //----------------------------------------- Initial Process Once -----------------------------------------
    while(true){
        int bytesReceived = recv(sock, buf, 50, 0);
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
                cout << "------------------ init ------------------" << endl;
                break;
            }
            else{
                continue;
            }
        }
    }
    //--------------------------------------------------------------------------------------------------------

    //------------------------------------------- Receive Data Loop ------------------------------------------
    while(true){
        if(errcnt > 5){
            break;
        }

        memset(buf, 0, 50);
        memset(ACK, 0, 20);
        int bytesReceived = recv(sock, buf, 50, 0);

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
                cout <<"CLIENT SEND ACK> ";
                for(int i=0; i<DATA_ACK_SIZE; ++i)
                    std::cout << std::hex << " " << (int)ACK[i];
                cout<< "" <<endl;

                decrypted_buf = decodeAES128(buf);
                cout <<"CLIENT RECV OBU DECODED> ";
                for(int i=0; i<16; ++i)
                    std::cout << std::hex << " " << (int)decrypted_buf[i];
                cout<< "" <<endl;
                
                int ret = send(sock, ACK, DATA_ACK_SIZE, 0);
                
                // ************************
                // * send data to DB here *
                // ************************

                // when failed to send data over socket, errcnt += 1 and retry
                if(ret<0){
                    errcnt++;
                    cout <<"!!! Send Failed Retry !!!"<<endl;
                    send(sock, ACK, DATA_ACK_SIZE, 0);
                }
            }
            // 0x20이 아닌 데이터 입력 시 errcnt += 1, NACK 전송
            else{
                errcnt++;
                cout <<"!!! Invalid OpCode !!!"<<endl;
                memset(NACK, 0, 10);
                makeACK(buf, bytesReceived, NACK, DATA_ACK_SIZE, -1);
                send(sock, NACK, DATA_ACK_SIZE, 0);
                continue;
            }
        }
        cout << "----------------------------------------" << endl;
    }
    //--------------------------------------------------------------------------------------------------------

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

// call in system time in yyyyMMddhhmmss format
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

void makeACK(char *buf, int len, char *ACK, int returnlen, int err)
{   
    u16 CRC;
    u8 CRC_H, CRC_L;
    uint8_t time[7] = {0,};

    // NACK
    if(err != 0){
        char outCRCSET[5];
        outCRCSET[0] = buf[1]; outCRCSET[1] = buf[2]; outCRCSET[3] = 0xa1;
        outCRCSET[4] = 0x00; outCRCSET[5] = 0x00;
        CRC = crc16_ccitt(outCRCSET, sizeof(outCRCSET));
        CRC_H = (CRC>>8);CRC_L = (CRC & 0xFF);

        ACK[0] = 0x02;
        for(int i = 0; i<5; i++){
            ACK[i+1] = outCRCSET[i];
        }
        ACK[returnlen-3] = CRC_H; ACK[returnlen-2] = CRC_L; ACK[returnlen-1] = 0x03;
        return;
    }

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
        char outCRCSET[5];
        for(int i = 0; i<(len-4); i++){
            CRCSET[i] = buf[i+1];
        }
        CRC = crc16_ccitt(CRCSET, sizeof(CRCSET));
        CRC_H = (CRC>>8); CRC_L = (CRC & 0xFF);
        //------------------------------------------

        // if CRC is verified, generate one for return ACK
        if((CRC_H == buf[len-3])&&(CRC_L==buf[len-2])){
            outCRCSET[0] = CRCSET[0]; outCRCSET[1] = CRCSET[1];
            outCRCSET[2] = 0xa0; outCRCSET[3] = 0x00; outCRCSET[4] = 0x00; 
            CRC = crc16_ccitt(outCRCSET, sizeof(outCRCSET));
            CRC_H = (CRC>>8);CRC_L = (CRC & 0xFF);
        }
        
        // return ACK 
        ACK[0] = 0x02;
        for(int i = 0; i<5; i++){
            ACK[i+1] = outCRCSET[i];
        }
        ACK[returnlen-3] = CRC_H; ACK[returnlen-2] = CRC_L; ACK[returnlen-1] = 0x03;
    }
    
}
