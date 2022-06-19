# (Better) Human Readable Assembly (HRA)

----
### Intro
Human Readable Assembly (HRA) is a language which uses real words to make instructions.
There are a couple of difference between actual assembly and HRA though:
* The instruction-set more resembles the esolang [brainfuck](https://esolangs.org/wiki/Brainfuck)
* HRA supports functions instead of loops which makes it easier to read.

### Instruction-set 
| Instruction                 | Parameters        | Action                                                                                                            |
|:----------------------------|-------------------|:------------------------------------------------------------------------------------------------------------------|
| plus memory pointer by      | [adres]           | Moves the memory pointer to the right [adres] amount                                                              |
| plus instruction pointer by | [adres]           | Moves the instruction pointer to the right [adres] amount                                                         |
| min memory pointer by       | [adres]           | Moves the memory pointer to the left [adres] amount                                                               |
| min instruction pointer by  | [adres]           | Moves the instruction pointer to the left [adres] amount                                                          |
| move memory pointer to      | [adres]           | Moves the pointer to [adres]                                                                                      |
| move instruction pointer to | [adres]           | Moves the pointer to [adres]                                                                                      |
| show pointer                |                   | Shows the value where the pointer is at                                                                           | 
| make function               | [function name]   | Makes a function named [function name]                                                                            |
| close                       |                   | Closes the function opened with instruction *begin function*                                                      |
| run function                | [function name]   | Runs the function named [function name]                                                                           |
| greater compare between     | [adres1] [adres2] | Checks if value of [adres1] is larger than value of [adres2], if True then *pointer + 1* otherwise *pointer + 2*  |
| less compare between        | [adres1] [adres2] | Checks if value of [adres1] is smaller than value of [adres2], if True then *pointer + 1* otherwise *pointer + 2* |
| equal compare between       | [adres1] [adres2] | Checks if value of [adres1] equals value of [adres2], if True then *pointer + 1* otherwise *pointer + 2*          |
| increment pointer by        | [value]           | Increments the value of pointer with [value]                                                                      |
| decrement pointer by        | [value]           | Decrements the value of pointer with [value]                                                                      |
| multiply pointer by         | [value]           | Multiplies the value of pointer with [value]                                                                      |
