all: hash_executor

md5.o: md5.c
	gcc -c -std=c11 -Wall -O2 -o $@ $<

hash_executor: md5.o hash_executor.o
	ld -o $@ md5.o hash_executor.o

hash_executor.o: hash_executor.asm
	nasm -f elf64 -o $@ $<

clean:
	rm -f hash_executor md5.o hash_executor.o
