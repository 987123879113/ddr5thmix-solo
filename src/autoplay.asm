.org 0x80012860
CheckAutoplayDipswitch:
    lb v0, 0x1f400004
    nop

    andi v0, 1
    beq v0, 0, _CheckAutoplayDipswitchEnd
    nop

    lb v0, 0x20(s3)
    nop

_CheckAutoplayDipswitchEnd:
    j CheckAutoplayDipswitchEnd
    nop

.org 0x8007f7f8
; Enable autoplay
    j CheckAutoplayDipswitch
    nop
CheckAutoplayDipswitchEnd:
.org 0x8007f914
; Disable random drops
    nop
.org 0x8007f8a8
; Disable randomness of timing
    li v0, 0
    nop
    nop
.org 0x8007f8f4
; Change allowable timing window of autoplay
; Default is 16 which will result in a mix of perfect and marvelous judgements
; 2 may possibly be a bit tight on real hardware, but MAX 300 is a pain and you get 1 or 2 goods at the end with a value of 4
    slti v0, s2, AUTOPLAY_TIMING

.org 0x80012a24
; Display "AUTOPLAY" as DIP1 setting on the DIP switch test menu.
    .asciiz "SW1  AUTOPLAY"

.org 0x80012d2c
OffText:
.org 0x80012d3c
OnText:

.org 0x80039bc8
    j ComputeAutoplayOnOff
    nop
ComputeAutoplayFinished:

.org 0x800102d0
.dw 0 ; Force the string to terminate

; Display "ON" or "OFF" depending on whether autoplay is on or off, on the DIP switch test menu.
ComputeAutoplayOnOff:
    andi v0, s3, 0x1
    beq v0, zero, _ComputeDisplayOn
    nop
    li v0, OffText
    jal draw_text
    sw v0, 0x14(sp)
    j ComputeAutoplayFinished
    nop
_ComputeDisplayOn:
    li v0, OnText
    jal draw_text
    sw v0, 0x14(sp)
    j ComputeAutoplayFinished
    nop
