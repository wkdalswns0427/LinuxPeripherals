#ifndef __RS485SETUP_H__
#define __RS485SETUP_H__

class RS485SETUP
{

private:
    // 멤버 상수
    // enum
    // {
    //     constanfVariable = 20,
    // };
    
    // 맴버 변수
    int port_485;
    char buf[1024];
    int cnt;
    
public:
    // 맴버 함수
    int init_port(const char* devicename);
    int set_interface_attribs(int fd, int speed);
    void set_mincount(int fd, int mcount);
    int send_data_over_serial(int fd, const int data[]);
};

#endif