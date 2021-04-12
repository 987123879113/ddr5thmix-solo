
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
; Custom code area
; Shares a very close space to the code location used in solo.asm
; so be careful that the two don't collide.

.org 0x80038e44
PanelIoFix:
    nor a1, zero, a1
    nor a2, zero, a2
    nor v0, zero, v0

    ; This masks out unwanted inputs
    andi a1, 0xffff8f1f

    ; This converts the select l/r button inputs
    andi v1, a2, 0x200
    sll v1, 4
    or a1, v1
    xor a2, v1

    andi v1, v0, 0x200
    sll v1, 5
    or a1, v1
    xor v0, v1

    ; Had to reuse v1 to not mess up any other registers, so read the value again
    lhu v1, 0x1f400004
    nop
    nor v1, zero, v1

    j PanelIoFixEnd
    nop

; End custom code area
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

.org 0x800b0424
    j PanelIoFix
    nop
    nop
    nop
    nop
PanelIoFixEnd:
