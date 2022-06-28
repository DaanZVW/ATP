.section .text
.global  _start
.align   4

_start:
	MOV  fp, sp
	MOV  r4, sp
	SUB  r4, #4
	SUB  sp, #128
	B    test_recursion
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
@ Start of function recursion


function_recursion:
node_2:
	MOV  r1, r4
	MOV  r2, #4
	BL   show_memory
node_3:
	LDR  r0, [r4]
	ADD  r0, #1
	STR  r0, [r4]
node_4:
	LDR  r0, [fp, #-4]
	LDR  r1, [fp, #-8]
	CMP  r0, r1
	BLT  node_5
	B    node_6
node_5:
	BL   function_recursion
node_6:
	B    node_12
node_7:
@ End of function


test_recursion:
node_8:
	MOV  r4, fp
	SUB  r4, #8
node_9:
	LDR  r0, [r4]
	ADD  r0, #10
	STR  r0, [r4]
node_10:
	MOV  r4, fp
	SUB  r4, #4
node_11:
	BL   function_recursion
node_12:
	MOV  r1, r4
	MOV  r2, #4
	BL   show_memory
node_13:
	B    _exit
