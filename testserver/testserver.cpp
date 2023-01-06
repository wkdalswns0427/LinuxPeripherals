// This is mock server
// To be replaced by APCU

#include <iostream>
#include <sys/types.h>
#include <unistd.h>
#include <sys/socket.h>
#include <netdb.h>
#include <arpa/inet.h>
#include <string.h>
#include <string>
#include <typeinfo>
#include "data.h"
#include "crc.h"
 #define ARRAY_LEN(a) (sizeof(a) / sizeof((a)[0]))

using namespace std;

u16 crc16_ccitt(const char *buf, int len);

int main(int argc, char *argv[])
{   
    unsigned int port;
    if (argc < 2)
    {
        printf("Usage: %s <port> -> setting default to 12242\n", argv[0]);
        port = 12242;
    }
    else if(argc == 2)
    {
        port = atoi(argv[1]);
    }
    else{
        printf("Usage: %s <port> \n", argv[0]);
        return 1;
    }
    
    //--------------------------------------------------------------------------------------------------
    // Create a socket
    int listening = socket(AF_INET, SOCK_STREAM, 0);
    if (listening == -1)
    {
        cerr << "Can't create a socket! Quitting" << endl;
        return -1;
    }
 
    // Bind the ip address and port to a socket
    sockaddr_in hint;
    hint.sin_family = AF_INET;
    hint.sin_port = htons(port);
    inet_pton(AF_INET, "0.0.0.0", &hint.sin_addr);
 
    bind(listening, (sockaddr*)&hint, sizeof(hint));
 
    // Tell Winsock the socket is for listening
    listen(listening, SOMAXCONN);
 
    // Wait for a connection
    sockaddr_in client;
    socklen_t clientSize = sizeof(client);
 
    int clientSocket = accept(listening, (sockaddr*)&client, &clientSize);
 
    char host[NI_MAXHOST];      // Client's remote name
    char service[NI_MAXSERV];   // Service (i.e. port) the client is connect on

    // set socket timeout
    timeval tv;
    tv.tv_sec  = 5;
    tv.tv_usec = 0;
    setsockopt(clientSocket, SOL_SOCKET, SO_RCVTIMEO, (char*)&tv, sizeof(timeval));
 
    memset(host, 0, NI_MAXHOST); // same as memset(host, 0, NI_MAXHOST);
    memset(service, 0, NI_MAXSERV);
 
    if (getnameinfo((sockaddr*)&client, sizeof(client), host, NI_MAXHOST, service, NI_MAXSERV, 0) == 0)
    {
        cout << host << " connected on port " << service << endl;
    }
    else
    {
        inet_ntop(AF_INET, &client.sin_addr, host, NI_MAXHOST);
        cout << host << " connected on port " << ntohs(client.sin_port) << endl;
    }
 
    // Close listening socket
    close(listening);
    //--------------------------------------------------------------------------------------------------
    char buf[4096];
    u16 CRC;
    u8 CRC_H, CRC_L;
 
    while (true)
    {
        memset(buf, 0, 4096);
        // Wait for client to send data
        //-------- make usable dummy ----------
        char INITCRC[sizeof(CU2KIOSK_INIT-4)];
        int len = sizeof(CU2KIOSK_INIT);
        for(int i = 0; i < len-4; i++){
            INITCRC[i] = CU2KIOSK_INIT[i+1];
        }
        CRC = crc16_ccitt(INITCRC, len-4);
        CRC_H = (CRC>>8);CRC_L = (CRC & 0xFF);
        CU2KIOSK_INIT[len-3] = CRC_H; CU2KIOSK_INIT[len-2] = CRC_L;
        //-------------------------------------

        send(clientSocket, CU2KIOSK_INIT, len, 0);
        int bytesReceived = recv(clientSocket, buf, 4096, 0);

        if (bytesReceived == -1)
        {
            cerr << "Error in recv(). Quitting" << endl;
            break;
        }
 
        if (bytesReceived == 0)
        {
            cout << "Client disconnected " << endl;
            break;
        }

        cout <<"SERVER RECV> ";
        for(int i=0; i<bytesReceived; ++i)
            std::cout << std::hex << " " << (int)buf[i];
        cout<< "" <<endl;
        
        if(buf[3]==0x11){
            cout << "INIT ACK" << endl;
            break;
        }
    }

    //-------- make usable dummy ----------
    char OBUCRC[sizeof(CU2KIOSK_OBUINFO-4)];
    int OBUlen = sizeof(CU2KIOSK_OBUINFO);
    for(int i = 0; i < OBUlen-4; i++){
        OBUCRC[i] = CU2KIOSK_OBUINFO[i+1];
    }
    CRC = crc16_ccitt(OBUCRC, OBUlen-4);
    CRC_H = (CRC>>8);CRC_L = (CRC & 0xFF);
    CU2KIOSK_OBUINFO[OBUlen-3] = CRC_H; CU2KIOSK_OBUINFO[OBUlen-2] = CRC_L;
    //-------------------------------------
    send(clientSocket, CU2KIOSK_OBUINFO, sizeof(CU2KIOSK_OBUINFO), 0);
    for(int i = 0; i < 3; i++){
        int bytesReceived = recv(clientSocket, buf, 4096, 0);

        if (bytesReceived == -1)
        {
            cerr << "Error in recv(). Quitting" << endl;
            break;
        }
        if (bytesReceived == 0)
        {
            cout << "Client disconnected " << endl;
            break;
        }

        cout <<"SERVER RECV V2> ";
        for(int i=0; i<bytesReceived; ++i)
            std::cout << std::hex << " " << (int)buf[i];
        cout<< "" <<endl;
        
        if(buf[3]==0xA0){
            cout << "DATA ACK" << endl;
        }
    }
 
    // Close the socket
    close(clientSocket);
 
    return 0;
}

u16 crc16_ccitt(const char *buf, int len)
{
    register int counter;
    register u16 crc = 0;
    for( counter = 0; counter < len; counter++)
    crc = (crc<<8) ^ crc16tab[((crc>>8) ^ *(char *)buf++)&0x00FF];
    return crc;
}