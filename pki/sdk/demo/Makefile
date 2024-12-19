TARGET=../bin/sdpf_demo
CC=x86_64-w64-mingw32-g++

CFLAG=-g -Wall 
SRC=userdemo.c
LIB=  -ldatasec -lXdjaKeyApi -lpthread

LDFLAGS = -L../bin
all:
	$(CC) $(CFLAG) $(SRC) -static-libstdc++ -static-libgcc $(LDFLAGS) $(LIB) -o $(TARGET)
