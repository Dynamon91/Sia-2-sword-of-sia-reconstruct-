ENTRY(_start)
MEMORY { ROM (rx) : ORIGIN = 0x08000000, LENGTH = 32M
         RAM (rw) : ORIGIN = 0x02000000, LENGTH = 256K
         IWRAM (rwx) : ORIGIN = 0x03000000, LENGTH = 28K }
SECTIONS {
 .header : { KEEP(*(.header)) } > ROM
 .iwram : { . = ALIGN(4); __iwram_start = .; *(.text*) . = ALIGN(4); __iwram_end = .; } > IWRAM AT> ROM
 __iwram_load = LOADADDR(.iwram);
 .rodata : { *(.rodata*) } > ROM
 .bss (NOLOAD) : { . = ALIGN(4); __bss_start = .; *(.bss*) *(COMMON) . = ALIGN(4); __bss_end = .; } > RAM
 /DISCARD/ : { *(.comment*) *(.ARM.attributes*) *(.ARM.exidx*) *(.ARM.extab*) }
}
