global _start

section .data
        align 8
        msg_input: db "Please enter your payload:", 0xA
        msg_input_len: equ $-msg_input
        msg_exec: db "Executing hash...", 0xA
        msg_exec_len: equ $-msg_exec

section .bss
        align 0x1000
        hash: resb 0x1000

section .note.GNU-stack noalloc noexec nowrite progbits

section .text
_start:
        ; align stack
        and rsp, 0xffffffffffffff00
        sub rsp, 0x200 ; size for user input (48) + MD5_ctx (152)

        ; print msg_input
        mov rdi, 1
        mov rsi, msg_input
        mov rdx, msg_input_len
        call sys_write

        ; read input
        mov rdx, 48 ; the order is important for solving the chall !
        mov rdi, 0
        mov rsi, rsp
        call sys_read
        mov r8, rax ; r8 keeps the user input size

        ; hash
        lea rdi, [rsp + 0x100]
        call MD5_Init

        lea rdi, [rsp + 0x100]
        mov rsi, rsp
        mov rdx, r8
        call MD5_Update

        mov rdi, hash
        lea rsi, [rsp + 0x100]
        call MD5_Final

        ; print msg_exec
        mov rdi, 1
        mov rsi, msg_exec
        mov rdx, msg_exec_len
        call sys_write

        ; mprotect
        mov rdi, hash
        mov rsi, 0x1000
        mov rdx, 5
        call sys_mprotect

        ; jump
        call hash

        ; exit
        mov rdi, 0
        call sys_exit

; void sys_read(fd, buf, count)
sys_read:
        mov rax, 0
        syscall
        ret

; void sys_write(fd, buf, count)
sys_write:
        mov rax, 1
        syscall
        ret

; void sys_exit(code)
sys_exit:
        mov rax, 60
        syscall
        ret

; void sys_mprotect(start, len, prot)
sys_mprotect:
        mov rax, 10
        syscall
        ret

extern MD5_Init
extern MD5_Update
extern MD5_Final
