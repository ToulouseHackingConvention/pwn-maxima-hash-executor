FROM debian:jessie

# full upgrade
RUN apt-get update && apt-get upgrade -y

# install dependencies and create user chall
RUN apt-get install -y gcc nasm socat && useradd -ms /bin/sh chall

ADD src/hash_executor.asm /home/chall/hash_executor.asm
ADD src/md5.c /home/chall/md5.c
ADD src/flag /home/chall/flag

WORKDIR /home/chall

# Compilation
RUN gcc -c -std=c11 -Wall -O2 -o md5.o md5.c && \
    nasm -f elf64 -o hash_executor.o hash_executor.asm && \
    ld -o hash_executor md5.o hash_executor.o && \
    rm hash_executor.asm hash_executor.o md5.c md5.o && \
    chmod 755 hash_executor && \
    chmod 644 flag && \
    apt-get purge -y --auto-remove gcc nasm

EXPOSE 5555

CMD socat TCP-LISTEN:5555,fork EXEC:"/home/chall/hash_executor",stderr,user=chall
