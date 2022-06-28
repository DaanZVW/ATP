.section .text
.global  _start
.align   4

_start:
	MOV  fp, sp
	MOV  r4, sp
	SUB  r4, #4
	SUB  sp, #128
_input:
	MOV  r0, #5
	STR  r0, [fp, #-4]
_start_final:
	B    sommig
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
@ Start of function sommig


function_sommig:
node_2:
	LDR  r0, [fp, #-8]
	LDR  r1, [fp, #-12]
	CMP  r0, r1
	BNE  node_3
	B    node_4
node_3:
	B    node_5
node_4:
	B    node_14
node_5:
	LDR  r0, [r4]
	ADD  r0, #1
	STR  r0, [r4]
node_6:
	SUB  r4, #4
node_7:
	LDR  r0, [r4]
	SUB  r0, #1
	STR  r0, [r4]
node_8:
	ADD  r4, #4
node_9:
	BL   function_sommig
node_10:
@ End of function


sommig:
node_11:
	LDR  r0, [r4]
	STR  r0, [fp, #-8]
node_12:
	MOV  r0, #0
	STR  r0, [r4]
node_13:
	BL   function_sommig
node_14:
	MOV  r1, r4
	MOV  r2, #4
	BL   show_memory
node_15:
	B    _exit
