.section .text
.global  _start
.align   4

_start:
	MOV  fp, sp
	MOV  r4, sp
	SUB  r4, #4
	SUB  sp, #128
_input:
	MOV  r0, #4
	STR  r0, [fp, #-4]
_start_final:
	B    is_even
_exit:
	MOV  sp, fp
	MOV  r7, #0x1
	MOV  r0, #1
	SWI  0

show_memory:
	PUSH {r0, r7, lr}
	MOV  r0, #1
	MOV  r7, #0x4
	SWI  0
	POP  {r0, r7, pc}

node_1:
@ Start of function even


function_even:
node_2:
	LDR  r0, [fp, #-4]
	LDR  r1, [fp, #-8]
	CMP  r0, r1
	BEQ  node_3
	B    node_4
node_3:
	BL   function_is_even
node_4:
	LDR  r0, [r4]
	SUB  r0, #1
	STR  r0, [r4]
node_5:
	BL   function_odd
node_6:
@ End of function


node_7:
@ Start of function odd


function_odd:
node_8:
	LDR  r0, [fp, #-4]
	LDR  r1, [fp, #-8]
	CMP  r0, r1
	BEQ  node_9
	B    node_10
node_9:
	BL   function_is_odd
node_10:
	LDR  r0, [r4]
	SUB  r0, #1
	STR  r0, [r4]
node_11:
	BL   function_even
node_12:
@ End of function


node_13:
@ Start of function is_even


function_is_even:
node_14:
	MOV  r0, #1
	STR  r0, [r4]
node_15:
@ End of function


node_16:
@ Start of function is_odd


function_is_odd:
node_17:
	B    node_23
node_18:
@ End of function


is_even:
node_19:
	MOV  r4, fp
	SUB  r4, #12
node_20:
	LDR  r0, [r4]
	ADD  r0, #1
	STR  r0, [r4]
node_21:
	MOV  r4, fp
	SUB  r4, #4
node_22:
	BL   function_even
node_23:
	MOV  r1, r4
	MOV  r2, #4
	BL   show_memory
node_24:
	B    _exit
