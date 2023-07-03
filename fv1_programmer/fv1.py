EMPTY_FV1_PROGRAM = """
; Empty program

start:
    NOP
end:
    NOP
"""

ROM_REV1 = """
;reverb program
;large reverb, stereo in and out
;for mixers, uneven (for vocals)
;pot0=reverb time
;pot1=low freq response
;pot2=high freq response
;
mem	lap1	156
mem	lap2	223
mem	lap3	332
mem	lap4	548
mem	rap1	186
mem	rap2	253
mem	rap3	302
mem	rap4	498
;
mem	ap1	1251
mem	ap1b	1751
mem	ap2	1443
mem	ap2b	1343
mem	ap3	1582
mem	ap3b	1981
mem	ap4	1274
mem	ap4b	1382
;
mem	del1	5859
mem	del2	4145
mem	del3	3476
mem	del4	4568

equ 	temp	reg0
equ	lpf1	reg1
equ	lpf2	reg2
equ	lpf3	reg3
equ	lpf4	reg4
equ	hpf1	reg5
equ	hpf2	reg6
equ	hpf3	reg7
equ	hpf4	reg8
equ	rt	reg9
equ	hf	reg10
equ	lf	reg11
equ	lapout	reg12
equ	rapout	reg13

;set up lfo, 0.5Hz, +/-20 samples:
skp	run,	loop
wlds	sin0,	12,	160
loop:

;smear 2 allpass filters in reverb ring:

cho 	rda,	sin0,	0x06,	ap1+50
cho	rda,	sin0,	0,	ap1+51
wra	ap1+100,	0
cho 	rda,	sin0,	0x07,	ap3+50
cho	rda,	sin0,	1,	ap3+51	
wra	ap3+100,	0

;prepare pots for control:
rdax	POT0,	1.0
sof 	0.8, 	0.1
wrax	rt,	0		;rt ranges 0.1 to 0.9
;
;shelving controls are negative:
rdax	POT1,	1.0
sof	0.8, 	-0.8
wrax 	hf,0			;hf ranges -0.8 to 0
;
rdax	POT2,	1.0
sof 	0.8,	-0.8
wrax 	lf,0			;lf ranges -0.8 to 0
;
;get inputs and process with three APs each
;
rdax	adcl,	0.5		
rda	lap1#,	-0.5	
wrap	lap1,	0.5		
rda	lap2#,	-0.5	
wrap	lap2,	0.5		
rda	lap3#,	-0.5	
wrap	lap3,	0.5		
rda	lap4#,	-0.5	
wrap	lap4,	0.5		
wrax	lapout,	0		
;
rdax	adcr,	0.5		
rda	rap1#,	-0.5	
wrap	rap1,	0.5		
rda	rap2#,	-0.5	
wrap	rap2,	0.5		
rda	rap3#,	-0.5	
wrap	rap3,	0.5		
rda	rap4#,	-0.5	
wrap	rap4,	0.5		
wrax	rapout,	0		
;
;now do reverb ring, use temp as temp reg for filtering:
;
;delay ap into 1:
rda	del4#,	1.0	;read previous delay	
mulx	rt		;multiply by reverb time coefficient
rdax	lapout,	1.0	;read left input from input allpass filter bank
rda	ap1#,	-0.6	;do an allpass filter
wrap	ap1,	0.6
rda	ap1b#,	-0.6	;do second all pass filter
wrap	ap1b,	0.6	
wrax	temp,	1.0	;write to temp, keep in acc	
rdfx	lpf1,	0.5	
wrhx	lpf1,	-1.0	;filter done
mulx	lf		;scale by lf
rdax	temp,	1.0	;add to temp
wrax	temp,	1.0	;write to temp again
rdfx	hpf1,	0.05	
wrlx	hpf1,	-1.0	;filter done
mulx	hf		;scale by hf
rdax	temp,	1.0	;add temp
wra	del1,	0.0	;write to next delay
;
;delay ap into 2:
rda	del1#,	1.0		
mulx	rt
rda	ap2#,	-0.6	
wrap	ap2,	0.6		
rda	ap2b#,	-0.6	
wrap	ap2b,	0.6		
wrax	temp,	1.0		
rdfx	lpf2,	0.5		
wrhx	lpf2,	-1.0	
mulx	hf
rdax	temp,	1.0		
wrax	temp,	1.0		
rdfx	hpf2,	0.05	
wrlx	hpf2,	-1.0	
mulx	lf
rdax	temp,	1.0		
wra	del2,	0.0		
;
;delay ap into 3:
rda	del2#,	1.0		
mulx	rt
rdax	rapout,	1.0		
rda	ap3#,	-0.6	
wrap	ap3,	0.6		
rda	ap3b#,	-0.6	
wrap	ap3b,	0.6		
wrax	temp,	1.0		
rdfx	lpf3,	0.5		
wrhx	lpf3,	-1.0	
mulx	hf
rdax	temp,	1.0		
wrax	temp,	1.0		
rdfx	hpf3,	0.05	
wrlx	hpf3,	-1.0	
mulx	lf
rdax	temp,	1.0		
wra	del3,	0.0
;
;delay ap into 4:
rda	del3#,	1.0		
mulx	rt
rda	ap4#,	-0.6	
wrap	ap4,	0.6		
rda	ap4b#,	-0.6	
wrap	ap4b,	0.6		
wrax	temp,	1.0		
rdfx	lpf4,	0.5		
wrhx	lpf4,	-1.0	
mulx	hf
rdax	temp,	1.0		
wrax	temp,	1.0		
rdfx	hpf4,	0.05	
wrlx	hpf4,	-1.0	
mulx	lf
rdax	temp,	1.0		
wra	del4,	0.0		
;
rda	del1+2630,	1.5	;sum outputs as taps from reverb ring
rda	del2+1943,	1.2	
rda	del3+3200,	1.0	
rda	del4+4016,	0.8	
wrax	dacl,	0.0	
;		
rda	del3+1163,	1.5	
rda	del4+3330,	1.2	
rda	del1+2420,	1.0	
rda	del2+2631,	0.8	
wrax	dacr,	0.0	
;
"""