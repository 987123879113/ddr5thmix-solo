.psx
.open "build/GAME.DAT", 0x80010000 - 0x60000 - 0x800

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
; Force full unlocks (songs and characters)
;  0 = Off
;  1 = On
.definelabel FORCE_UNLOCK, 1

; Transforms 5th Mix into 5th Mix Solo
;  0 = Off
;  1 = On
.definelabel SOLO_MODE, 1

; Use solo cabinet I/O
; Still experimental so may not work properly on real hardware
;  0 = Off
;  1 = On
; Can be defined in the ASM directly but it's easier for the build scripts to pass "-definelabel SOLO_IO 1" to armips
;.definelabel SOLO_IO, 1

; Autoplay Enabled
; When this option is enabled, dipswitch 1 can be used to toggle autoplay
;  0 = Off
;  1 = On
.definelabel AUTOPLAY_ENABLED, 1

; Autoplay Timing Window
; Default value is 16 which results in mixture of perfect and marvelous judgement.
; Anything tigther than 2 will cause notes to be missed.
.definelabel AUTOPLAY_TIMING, 2

; Disable announcer comments during song
;  0 = Off
;  1 = On
.definelabel DISABLE_ANNOUNCER, 0

; Disable cheering during song
;  0 = Off
;  1 = On
.definelabel DISABLE_CHEERING, 0

; Swap EXTRA1/2/3/4 mapping. Some cabinets start with EXTRA1 as the front left, then
; EXTRA2 as the back left, then EXTRA3 as the front right, and finally EXTRA4 as the
; back right. If your cabinet is like this, set the below label to 1. If your cabinet
; goes top to bottom right to left, then leave this set to 0.
.definelabel SWAP_EXTRA_LIGHTS, 0
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;


.if DISABLE_ANNOUNCER == 1
.org 0x80080c50
    ; Disable random announcer comments
    nop
.org 0x80080204
    ; Disable combo is continuing
    nop
.endif


.if DISABLE_CHEERING == 1
.org 0x80080de8
    ; Disable cheering
    nop
.endif


.if FORCE_UNLOCK == 1
.org 0x8009bea0
    li v0, 0xffffffff
    jr ra
    nop
.endif


.if AUTOPLAY_ENABLED == 1
.include "src/autoplay.asm"
.endif


.if SOLO_MODE == 1
.include "src/solo.asm"
.endif


.ifdef SOLO_IO
.include "src/solo_io.asm"
.endif


.close
