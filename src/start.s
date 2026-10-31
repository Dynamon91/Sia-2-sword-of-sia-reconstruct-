.syntax unified
.cpu arm7tdmi
.section .header,"ax"
.arm
.global _start
_start:
    b boot
    .space 188
boot:
    mov r0, #0x12
    msr cpsr_c, r0
    ldr sp, =0x03007fa0
    mov r0, #0x1f
    msr cpsr_c, r0
    ldr sp, =0x03007f00
    ldr r0, =__bss_start
    ldr r1, =__bss_end
    mov r2, #0
1:  cmp r0,r1
    strlo r2,[r0],#4
    blo 1b
    ldr r0, =__iwram_load
    ldr r1, =__iwram_start
    ldr r2, =__iwram_end
3:  cmp r1,r2
    ldrlo r3,[r0],#4
    strlo r3,[r1],#4
    blo 3b
    ldr r0, =main
    bx r0
2:  b 2b
.pool
