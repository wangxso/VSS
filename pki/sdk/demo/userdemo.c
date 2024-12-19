#include <stdio.h>
#include <string.h>
#include <time.h>
#include "ds_api.h"

#define CERT_TYPE   2      //输入证书类型:1 PC，2 AC ,3 保留
#define CERT_KEYID  0      //0~19 [0~jmax-1]
#define CERT_MODE   1      //模式：0 小模式,1 大模式


const static int kItsAid = 111;
void usr_hex_dump(const char *str,unsigned char *data, int datalen)
{
    int i;
    // int len = datalen-datalen%16;

    printf("%s L=%d | ",str,datalen);
    for(i=0;i<datalen;i++)
    {
        if(0 == i%16) printf("\n  ");
        printf("%02x ", data[i]);
    }
    printf("\n");
}
void saveToFile(const char * fileName, unsigned char * data, int dataLen){
    FILE * fp = fopen(fileName, "wb");
    if(fp != NULL){
        fwrite(data, dataLen, 1, fp);
        fclose(fp);
    }
}
#include <sys/time.h>
unsigned long long nowUs(void)                                                            
{                                                                                                   
    struct timeval tv;                                                                              
    gettimeofday(&tv, NULL);                                                                        
    return (((unsigned long long)tv.tv_sec * 1000000LL) + tv.tv_usec);                              
                
} 

long long cost = 0;
void tmStart()
{
    cost = nowUs();
}
void tmEnd(const char* title, int ret)
{
    cost = nowUs() - cost;
    printf("\n|| %s cost %lldus ret=%d\n\n", title, cost, ret);
}

void testGenSpduByParaCert(int mode);

const static int kPduLen = 512;
int main(int argc, char** argv)
{
    int ret = 0;
    printf("start demo\n");
    ret = DS_InitSecurityService("../data");
    if(Err_ok != ret)
    {
        printf("init fail\n");
        return -1;
    }

    testGenSpduByParaCert(1);
    testGenSpduByParaCert(0);
    // for(;;)
    //     sleep(1);
    return 0;
}

void testGenSpduByParaCert(int mode)
{
    unsigned char pdu[kPduLen];
    int pdulen = sizeof(pdu);
    unsigned char spdu[kPduLen + 1024];
    int spdulen = sizeof(spdu);
    int ret = 0;
    memset(pdu, 0x77, pdulen);
    
    //使用参数中证书签名
    // unsigned char newCert[] = {0x80,0x03,0x00,0x83,0x08,0x17,0xcf,0xc7,0x61,0xec,0x98,0xce,0x44,0x50,0x80,0x00,0x00,0x58,0xf7,0xf0,0x86,0x42,0x5c,0x7a,0x59,0xb0,0x85,0x00,0x00,0x00,0x00,0x03,0x21,0x4c,0x4a,0xc5,0x86,0x00,0x03,0x83,0x01,0x01,0x80,0x00,0x9c,0x01,0x02,0x00,0x01,0x6f,0x00,0x01,0x70,0x80,0x84,0x21,0x82,0x21,0x18,0x26,0xb9,0x5f,0xc6,0x25,0x0a,0xf1,0x56,0x60,0x2f,0x2d,0x83,0x6f,0xe7,0x4b,0x51,0x8d,0xac,0xb2,0xbc,0xbf,0xef,0xfe,0x04,0xa1,0xe7,0xa0,0x1d,0xe6,0x57,0x84,0x40,0x97,0x8e,0x6d,0x34,0x59,0x74,0xe3,0xd0,0xd3,0x60,0x9d,0x51,0xa6,0x42,0x1d,0x34,0x0d,0xea,0x33,0x4a,0xb5,0x73,0xcf,0x8a,0x34,0x12,0xcc,0xf2,0x2e,0x2b,0x6b,0x1d,0x93,0x8e,0x0e,0xcf,0xf7,0xe0,0xbc,0x9a,0x6c,0x3f,0xef,0xe4,0x5d,0x97,0xac,0xc0,0x7d,0x7b,0x05,0x60,0xc5,0x27,0x0b,0x52,0x2a,0xae,0xb6,0x92,0x78,0x17,0xd9,0xb1};
    // unsigned char newPrikey[] = {0x7d,0x71,0x0a,0x50,0x58,0x1b,0x8a,0x00,0xe3,0x8d,0x1b,0x54,0x50,0xd7,0xe3,0x4e,0x75,0x6e,0xba,0x8e,0x91,0x39,0xe5,0x52,0x88,0xe1,0x61,0x2e,0xa4,0xd2,0xb3,0xff};

    unsigned char newCert[1024] = {0};
    int certlen = 0;
    unsigned char newPrikey[1024] = {0};
    int prilen = 0;
    FILE * fp = fopen("../data/pccerts/pc_1/pc.oer", "r+");
    if(fp != NULL){
        certlen = fread(newCert, 1, 1024, fp);
        if(certlen <= 0)
        {
            printf("cert open failed\n");
        }
        fclose(fp);
    }else{
        printf("oer open failed\n");
    }
    printf("[BUFF]:certlen = %d\n", certlen);
    FILE * fpri = fopen("../data/pccerts/pc_1/sign.privatekey", "r+");
    if(fpri != NULL){
        prilen = fread(newPrikey, 1, 1024, fpri);
        if(prilen <= 0)
        {
            printf("pkey1 open failed\n");
        }
        fclose(fpri);
    }else{
        printf("pkey open failed\n");
    }
    printf("[BUFF]:prilen = %d\n",prilen);

    spdulen = sizeof(spdu);
    tmStart();
    ret = DS_SignEx(newCert, certlen, newPrikey, mode, kItsAid, pdu, sizeof(pdu), spdu, &spdulen);
    tmEnd("DS_SignEx", ret);
    if(Err_ok != ret)
    {
        printf("DS_SignEx generate spdu fail\n");
        return;
    }
    else
    {
        printf("DS_SignEx generate spdu success certType = %d\n", mode);
        usr_hex_dump("spdu",spdu, spdulen);
    }
    //验签SPDU
    memset(pdu, 0, sizeof(pdu));
    ret = DS_VerifySigned(kItsAid, spdu, spdulen, pdu, &pdulen);
    if(Err_ok != ret)
    {
        printf("verify spdu fail\n");
        return;
    }
    else
    {
        printf("DS_VerifySigned success= %d\n",pdulen);
        usr_hex_dump("pdu",pdu, pdulen);
        
    }
}

