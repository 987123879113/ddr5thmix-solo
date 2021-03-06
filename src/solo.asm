; TODO: Remap solo scores to save as doubles?

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
; Custom code area

.org 0x80038ce4
SoloRatingPatch:
    li v1, 2
    move v0, a0

    bne a1, v1, SoloRatingNormalPath
    nop

    j SoloRatingNormalRead
    addi v0, 0x04

SoloRatingNormalPath:
    sll v0, a1, 0x2
    addu v0, a0, v0

SoloRatingNormalRead:
    lh v0, 0x10(v0)
    sll v1, a2, 0x2

    j SoloRatingPatchEnd
    nop

InputTestMenu:
    ; Up-Left
    clear a0
    li a2,-0x1e
    li v0, UpLeftText
    sw s1,0x10(sp)
    sw v0,0x14(sp)
    lw a1,0x0(s0)
    jal draw_text
    li a3,0x1000

    li a2,-0x1e
    li a3,0x1000
    lw a0,0x120(sp)
    nop
    srl a0,a0,16
    andi a0,a0,0x0001
    sltu a0,zero,a0
    li v0,0x80012d2c
    sll a1,a0,4
    add v0, a1
    lw a1,0x0(s0)
    sw s1,0x10(sp)
    sw v0,0x14(sp)
    sll a0,a0,0x1
    addiu a1,a1,0x48
    jal draw_text
    nop

    ; Up-Right
    clear a0
    li a2,-0x16
    li v0, UpRightText
    sw s1,0x10(sp)
    sw v0,0x14(sp)
    lw a1,0x0(s0)
    jal draw_text
    li a3,0x1000

    li a2,-0x16
    li a3,0x1000
    lw a0,0x120(sp)
    nop
    srl a0,a0,16
    andi a0,a0,0x0002
    sltu a0,zero,a0
    li v0,0x80012d2c
    sll a1,a0,4
    add v0, a1
    lw a1,0x0(s0)
    sw s1,0x10(sp)
    sw v0,0x14(sp)
    sltu a0,zero,a0
    sll a0,a0,0x1
    jal draw_text
    addiu a1,a1,0x48

    jal 0x80029728
    nop

    j InputTestMenuEnd
    nop

UpLeftText:
    .asciiz "UP-LEFT"
UpRightText:
    .asciiz "UP-RIGHT"


; End custom code area
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

.org 0x8001c174
this_machine_is_solo:
    ; Always return 1 to enable solo machine mode
    li v0, 1


.org 0x800909ec
    ; Allow for selecting 6 panel mode on style select screen
    nop


.org 0x8009b400
    nop
    j SoloRatingPatch
    nop
    nop
SoloRatingPatchEnd:


.org 0x8002b898
    ; Disable 2nd player start button during style select screen
    jr ra
    clear v0


; Use small stage number at top during gameplay
.org 0x800571b0
    b 0x800571cc


; Reposition arrows to be centered and evenly spaced around smaller stage number
.org 0x80014110
    .dh 0xffac - 7
    .dh 0xffe1 - 2
    .dh 0xffff
    .dh 0x0034 + 5
    .dh 0xffc7 - 5
    .dh 0xff5f
    .dh 0x0019 + 3
    .dh 0xff5f
.org 0x80014120
    .dh 0xffc2 - 3
    .dh 0xffe1 - 2
    .dh 0xffff
    .dh 0x001e + 1


; Change graphics for 4 panel and 6 panel mode on style select screen
.org 0x80016144
; 4 Panel/Single
    .dh 0x0001 ; 4 Panel/Single flag
    .dh 0x002c + 0x63 ; Layer absolute x
    .dh 0x00fb ; Layer absolute y
    .dh 0x001c ; Character relative x
    .dh 0x0033 ; Character relative y
    .dh 0
    .dh 0
    .dh 0
    .dh 0
    .dh 0
    .db 0x04 ; Stages bubble design + tail direction
    .db 0x78 ; More bubble relative y??
    .dh 0xffbe ; Bubble relative x
    .dh 0x000e ; Bubble relative y
; 6 Panel
    .dh 0x000a ; 6 Panel
    .dh 0x00cd + 0x63
    .dh 0x00c0
    .dh 0x001c
    .dh 0x0051
    .dh 0
    .dh 0
    .dh 0
    .dh 0
    .dh 0
    .db 0x03
    .db 0x5a
    .dh 0x0056
    .dh 0x0008
; Disable last entry
    .dh 0 ; Disabled
    .dh 0xff00 ; Send off to outer space
    .dh 0
    .dh 0
    .dh 0
    .dh 0
    .dh 0
    .dh 0
    .dh 0
    .dh 0
    .db 0
    .db 0
    .dh 0
    .dh 0

; Fix solo mode graphic going dim
.org 0x800900dc
    nop

; Don't show "insert more coins to select other modes" message
.org 0x8008e9e0
    nop

; Don't show secondary description text
.org 0x8008e994
    j 0x8008ea04

; Force 6 panel description when 4 panel isn't selected
.org 0x8008e944
    li v1, 0x0a
.org 0x8008e96c
    li t1, 0x02

; Load "DOUBLE" text instead of "SINGLE" for 6 panel mode
.org 0x8008e76c
    li v1, 0x0a

; Center bottom text on style select screen
.org 0x80084398
    addiu s0, s0, -0xa0

; Disable right player side text during free play mode
.org 0x80084438
    nop

; Make the character select screen show all 14 characters instead of 7 for 1P
.org 0x80091ed4
    li v0, 0x0e

; Don't show "NOT ATTEND" image on 2P side
.org 0x80091564
    b 0x80091dc0

; Change character update region width
; 2P characters leave the white glow when moving the cursor on the background because
; that region isn't being updated
.org 0x80092268
    li s7, 0x240
.org 0x80092398
    li s8, 0x240

; Don't draw 2P side character name
.org 0x80090ed8
    addiu a2, v0, 0xcb
    li t1, 0

; Disable static image when character not selected
.org 0x800910c8
    li s8, 0x180

; Remove black border triangles from character image area for 2P side
.org 0x80090fcc
    li s8, 0x180

; Use 2P select icon instead of 1P icon at top of screen (required for image edits)
.org 0x80083d04
    li v0, 0x0a
.org 0x80083d10
    addiu v1, v1, 3


; Fix I/O test menu exit key combo
.org 0x8003c314
    jal is_1p_panel_left_pressed
.org 0x8003c324
    jal is_1p_panel_right_pressed
    clear a0

.org 0x80012db8
    .asciiz " HOLD 1P LEFT +"
.org 0x80012dd0
    .asciiz "PRESS 1P RIGHT = EXIT"

; Fix start button during free player
.org 0x8001f984
    jal is_1p_start_pressed
.org 0x8001f994
    jal is_1p_start_pressed


;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
; I/O Test Menu
.org 0x8003bf08
    j InputTestMenu
InputTestMenuEnd:


; Fix centering of text
.org 0x8003bad4
    li v0, -0x60
.org 0x8003badc
    li v0, 0x30


.org 0x8003c00c
    ; Don't display 2P side buttons
    nop

.org 0x8003bf14
    ; Select L Text
    li a2, 0xfffffff2
.org 0x8003bf34
    ; Select L ON/OFF
    li a2, 0xfffffff2

.org 0x8003bf64
    ; Select R Text
    li a2, 0xfffffffa
.org 0x8003bf84
    ; Select R ON/OFF
    li a2, 0xfffffffa

.org 0x8003bfbc
    ; Start Text
    li a2, 0x02
.org 0x8003bfdc
    ; Start ON/OFF
    li a2, 0x02

.org 0x8003c140
    ; Service Switch Text
    li a2, 0x12
.org 0x8003c164
    ; Service Switch ON/OFF
    li a2, 0x12

.org 0x8003c194
    ; Coin Mech Text
    li a2, 0x1a
.org 0x8003c1b4
    ; Coin Mech ON/OFF
    li a2, 0x1a

.org 0x8003c1f4
    ; Coin Mech Text
    li a2, 0x2a
.org 0x8003c244
    ; Coin Mech ON/OFF
    li a2, 0x2a

.org 0x80012d30
    ; Don't display ULDR next to ON/OFF for IO test since Solo has no IO board.
    .asciiz "%s"


;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
; Lights Test Menu

; Fixes unable to select individual lights for test. The original "is held" function
; is nop'd out above, so we must give a negative index to this function to turn it
; into a held function.
.org 0x80039f44
    jal is_1p_start_pressed
    li a0, -0x4
