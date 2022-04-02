
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


;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
; Lights Test Menu

; Mapping from which test light entry to which actual light to activate.
.org 0x80012acc
    ; Body left/center/right lights.
    .dw 12
    .dw 9
    .dw 8
    ; Pad extra1/extra2/extra3/extra4 lights.
    .dw 6
    .dw 7
    .dw 4
    .dw 5
    ; Start button light.
    .dw 14
    ; Speaker light.
    .dw 16

; Labels for the lights test options.
.org 0x80012b08
    .asciiz "BODY LEFT"
.org 0x80012b14
    .asciiz "BODY CENTER"
.org 0x80012b24
    .asciiz "BODY RIGHT"
.org 0x80012b34
    .asciiz "EXTRA1"
.org 0x80012b44
    .asciiz "EXTRA2"
.org 0x80012b50
    .asciiz "EXTRA3"
.org 0x80012b60
    .asciiz "EXTRA4"
.org 0x80012b70
    .asciiz "START"
.org 0x80012b80
    .asciiz "SPEAKER"

; Skip displaying labels for lamps we don't have.
.org 0x8003a19c
    nop
.org 0x8003a1c0
    nop
.org 0x8003a1e4
    nop
.org 0x8003a208
    nop
.org 0x8003a22c
    nop
.org 0x8003a250
    nop

; Reposition "ALL" and "EXIT" according to the new layout.
.org 0x8003a25c
    li a2, 0x0
.org 0x8003a280
    li a2, 0x10

; Reference the correct cursor value for "ALL" and "EXIT".
.org 0x8003a270
    lw a0, 0x3c(sp)
.org 0x8003a294
    lw a0, 0x40(sp)

; Check for the correct cursor value to display green "current light" indicator
; if we are doing the "ALL" check.
.org 0x8003a010
    li v0, 0x9

; Wrap cursor around from top to bottom correctly.
.org 0x80039e14
    li v0, 0xA

; Wrap cursor around from bottom to top correctly.
.org 0x80039e44
    slti v0, v0, 0xB

; Run all test when "ALL" is selected.
.org 0x80039e78
    li v0, 0x9
.org 0x80039f60
    li v0, 0x9

; Exit when "EXIT" is selected.
.org 0x80039f04
    li v0, 0xA
.org 0x80039f50
    li v0, 0xA

; Initialize the all test frame counter to account for us only having 9 lights
; instead of 15, accounting for 60 frames per light being lit.
.org 0x80039f6c
    li v0, 0x21C
.org 0x80039ea4
    li v0, 0x21B
.org 0x80039ebc
    li a1, 0x8

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
; Lights mappings

; Map body right lower to body left, right higher and left lower to body center, and left higher to body right.
.org 0x8001666c
    .dw 0x00000002
    .dw 0x00000200
.org 0x80016664
    .dw 0x00000002
    .dw 0x00000400

; Map start 1p to correct solo start lights.
.org 0x8001667c
    .dw 0x00000002
    .dw 0x00000100

; Fix "speaker" light output to point at solo speaker neons.
.org 0x8001668c
    .dw 0x00000002
    .dw 0x00001000

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
; Lights activation functions for panel steppy

; Turn on all body lights when requested to isntead of 1P/2P side only.
.org 0x8009a304
    beq v0, zero, 0x8009a30c
.org 0x8009a328
    bne s0, v0, 0x8009a330

.if SWAP_EXTRA_LIGHTS == 1
; Turn on extra2 (left back) when left is pressed.
.org 0x8009a0c8
    li a0, 0x7

; Turn on extra4 (right back) when right is pressed.
.org 0x8009a078
    li a0, 0x5
.org 0x8009a094
    li a0, 0x5

; Turn on extra1 (left front) when up-left is pressed.
.org 0x8009a19c
    li a0, 0x6
.org 0x8009a1b8
    li a0, 0x6
.org 0x8009a1d0
    li a0, 0x6
.org 0x8009a1ec
    li a0, 0x6

; Turn on extra3 (right front) when up-right is pressed.
.org 0x8009a118
    li a0, 0x4
.org 0x8009a134
    li a0, 0x4
.org 0x8009a14c
    li a0, 0x4
.org 0x8009a168
    li a0, 0x4
.else
; Turn on extra4 (left back) when left is pressed.
.org 0x8009a0c8
    li a0, 0x5

; Turn on extra2 (right back) when right is pressed.
.org 0x8009a078
    li a0, 0x7
.org 0x8009a094
    li a0, 0x7

; Turn on extra3 (left front) when up-left is pressed.
.org 0x8009a19c
    li a0, 0x4
.org 0x8009a1b8
    li a0, 0x4
.org 0x8009a1d0
    li a0, 0x4
.org 0x8009a1ec
    li a0, 0x4

; Turn on extra1 (right front) when up-right is pressed.
.org 0x8009a118
    li a0, 0x6
.org 0x8009a134
    li a0, 0x6
.org 0x8009a14c
    li a0, 0x6
.org 0x8009a168
    li a0, 0x6
.endif

; Turn on extra1 and 3 (both forward lights) when up is pressed.
.org 0x8009a028
    li a0, 0x6
.org 0x8009a044
    li a0, 0x4
.org 0x8009a01c
    beq v0, zero, 0x8009a024
.org 0x8009a038
    bne s0, v0, 0x8009a040

; Turn on extra2 and 4 (both back lights) when down is pressed.
.org 0x80099fd8
    li a0, 0x7
.org 0x80099ff4
    li a0, 0x5
.org 0x80099fcc
    beq v0, zero, 0x80099fd4
.org 0x80099fe8
    bne s0, v0, 0x80099ff0
