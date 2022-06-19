# (Better) Human Readable Assembly (HRA)

----
## Intro
Human Readable Assembly (HRA) is a language which uses real words to make instructions.
There are a couple of difference between actual assembly and HRA though:
* The instruction-set more resembles the esolang [brainfuck](https://esolangs.org/wiki/Brainfuck)
* HRA supports functions instead of loops which makes it easier to read.

## Instruction-set 
| Instruction                 | Parameters        | Action                                                                                                                    |
|:----------------------------|-------------------|:--------------------------------------------------------------------------------------------------------------------------|
| plus memory pointer by      | [adres]           | Moves the memory pointer to the right [adres] amount                                                                      |
| plus instruction pointer by | [adres]           | Moves the instruction pointer to the right [adres] amount                                                                 |
| min memory pointer by       | [adres]           | Moves the memory pointer to the left [adres] amount                                                                       |
| min instruction pointer by  | [adres]           | Moves the instruction pointer to the left [adres] amount                                                                  |
| move memory pointer to      | [adres]           | Moves the pointer to [adres]                                                                                              |
| move instruction pointer to | [adres]           | Moves the pointer to [adres]                                                                                              |
| move memory to              | [adres]           | Moves the value of pointer to [adres]                                                                                     |
| show memory                 |                   | Shows the value where the memory pointer is at                                                                            | 
| make function               | [function name]   | Makes a function named [function name]                                                                                    |
| close function              |                   | Closes the function opened with instruction *begin function*                                                              |
| run function                | [function name]   | Runs the function named [function name]                                                                                   |
| exit                        |                   | Stops executing the code, must be placed anywhere in the file                                                             |
| ~                           |                   | This defines a comment, for example: "~ this is a comment" there must be a space between the ~ character and the comment! |
| greater compare between     | [adres1] [adres2] | Checks if value of [adres1] is larger than value of [adres2], if True then *pointer + 1* otherwise *pointer + 2*          |
| less compare between        | [adres1] [adres2] | Checks if value of [adres1] is smaller than value of [adres2], if True then *pointer + 1* otherwise *pointer + 2*         |
| equal compare between       | [adres1] [adres2] | Checks if value of [adres1] equals value of [adres2], if True then *pointer + 1* otherwise *pointer + 2*                  |
| not equal compare between   | [adres1] [adres2] | Checks if value of [adres1] not equals value of [adres2], if True then *pointer + 1* otherwise *pointer + 2*              |
| set memory pointer to       | [value]           | Sets the value of the memory pointer to [value]                                                                           |
| increment memory pointer by | [value]           | Increments the value of memory pointer with [value]                                                                       |
| decrement memory pointer by | [value]           | Decrements the value of memory pointer with [value]                                                                       |
| multiply memory pointer by  | [value]           | Multiplies the value of memory pointer with [value]                                                                       |

## How to use
To use the HRA toolchain you need the 'hra-toolkit.py' file which is a CLI interface file. For information run the following command:
```
python hra-toolkit.py -h
```

### CLI arguments
| Argument                            | Action                                 |
|-------------------------------------|----------------------------------------|
| -f (--file) [path]                  | Filepath of file which will be ran     |
| -it (--interpreter)                 | Use the interpreter on the given file  |
| -m (--memsize) [int]                | Size of the memory                     |
| -s (--state) ([final],[all],[none]) | Return which state you want to see     |
| -i (--input) [inputs]               | Inputs for the virtual system memory   |


### Recursive test program
Run a recursive program
```
python hra-toolkit.py -f programs/test_recursion.hra -it -s all
```
This file is equivalent to this python code:
```python
def recursion():
    global check_value
    if check_value < value:
        check_value += 1
        recursion()

check_value = 0
value = 20
recursion()
```
HRA equivalent
```
make function recursion
    increment memory pointer by 1
    greater compare between 0 1
    exit
    run function recursion
close function

move memory pointer to 1
increment memory pointer by 20
move memory pointer to 0
run function recursion
```
Summary of the code above:

First it declares a function recursion that checks if check_value is greater than value
If false it will higher check_value by 1 and calls the recursion function again
Lastly it sets a value of 20 to check against and calls the function

### Even or Odd

Run the even or odd example
```
python hra-toolkit.py -f programs/is_even.hra -it -s final -i [value]
```
This file is equivalent to this python code:
```python
def even():
    global value
    if value == 0:
        print(1)
        exit()
    value -= 1
    odd()

def odd():
    global value
    if value == 0:
        print(0)
        exit()
    value -= 1
    even()

value = 10
even()
```
C(++) equivalent
```c
bool even(unsigned int n);
bool odd(unsigned int n);
bool odd(unsigned int n){
    if(n==0){return false;}
    return even(n-1);
}
bool even(unsigned int n) {
    if(n==0){return true;}
    return odd(n-1);
}
```
HRA equivalent
```
make function even
    equal compare between 0 1
    run function is_even
    decrement memory pointer by 1
    run function odd
close function

make function odd
    equal compare between 0 1
    run function is_odd
    decrement memory pointer by 1
    run function even
close function

make function is_even
    move memory pointer to 2
    show memory
    exit
close function

make function is_odd
    move memory pointer to 1
    show memory
    exit
close function

move memory pointer to 2
increment memory pointer by 1
move memory pointer to 0
run function even
```
Summary of the code above:

First it will define 4 different functions
* even - check if index 0 of memory is 0 then run function is_even otherwise lower index 0 by 1 and run function odd
* odd - check if index 0 of memory is 0 then run function is_odd otherwise lower index 0 by 1 and run function even
* is_even - print index 2 where a 1 has been stored and exit program
* is_odd - print index 1 where a 0 has been stored and exit program

The interpreter already has set the input into the virtual memory.
Then when all functions have been defined, it will put a 1 at index 2 for comparing purposes.
Then it will run function even and lower index 0 till it hits 0.

When index 0 is even it will return 1 otherwise 0.

NOTE: This can be rewritten to only use 2 functions but for showcasing the function branching I did it this way

### Sommig
Run the sommig example
```
python hra-toolkit.py -f programs/sommig.hra -it -s final -i [value]
```
This file is equivalent to this python code:
```python
def sommig():
    global value
    result = 0
    if value != 0:
        value -= 1
        result += 1
        sommig()
        
value = 4
```
C(++) equivalent
```c
unsigned int sommig(unsigned int n){
    unsigned int result = 0;
    while(n>=1){
        result += n;
        n--;
    }
    return result;
}
```
HRA equivalent
```
make function sommig
    not equal compare between 1 2
    plus instruction pointer by 2
    exit

    increment memory pointer by 1
    plus memory pointer by 1
    decrement memory pointer by 1
    min memory pointer by 1
    run function sommig
close function

move memory to 1
set memory pointer to 0
run function sommig
```
Summary of the code above:

The interpreter already has set the input into the virtual memory.
It will move the input one index to the right because we will return result which will be build at index 0.
Essentially its easier programming.

In function sommig it will check if it not equals 0, then it will move the instruction pointer by 2.
Which skips the exit. Then it will increment the memory at index 0 en decrement the memory at index 1.
Then it reruns the sommig function till index 1 equals 0.
That means that the conversion is done and that means: result == n.
