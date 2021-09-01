# TAcademy-1

[https://www.youtube.com/watch?v=WxzWXqTNdlw](https://www.youtube.com/watch?v=WxzWXqTNdlw)

![Untitled](TAcademy-1%203ff44f3fe9c14e55ad6b5d89400a17c6/Untitled.png)

'어떻게 하면 서버의 상태를 ***쉽게***, ***안전하게*** 관리할 수 있을까?'에 대한 노력 때문에 생겨남.

### 1) 자체 서버 운영

서버 주문 → 서버 설치 → CPU, 메모리, 하드디스크 조립 → 네트워크 연결 → OS 설치 → 계정 설정 → 방화벽 설정 → ...

- 성능이 좋은 걸 미리 구매하고 효율적인 사용을 위해 여러 애플리케이션을 설치
- 서버를 설정하기 위해 많은 노력과 시간이 필요

특성 시점의 서버 상태를 누가, 언제, 어떻게 작업했는지 알 수 있을까?

똑같은 서버를 하나 더 만들 수 있을까?

서버 관리자 = GOD = 문제 생기면 다 해결함 = 휴가 못 감 = 변화를 싫어함

= 확장이 어려움 = 혁신이 어려움

### 2) 설정 관리 도구

기존에는 CLI로 명령어를 하나씩 쳤다면, 상태를 관리하는 코드(또는 설정)를 이용하여 서버 관리.

설정 파일을 실행하면 알아서 nginx를 설치하는 거임!

그런데, 그렇게 하면서 '선언적 서버 상태 정의'가 이루어짐. 이 서버에서는 ruby 1.8을 가지고 있어야 함. 새로운 서버가 생겼을 때도, 동일한 설정 파일을 이용하면 똑같은 걸 만들 수 있음. 완벽히 재현할 수는 없기에 불완전하지만 어느 정도 가능함.

서버 운영에 협업이 가능해짐. 소스를 관리하고 리뷰가 가능해졌기 때문에.

### 3) 가상 머신의 등장

하나의 서버에 여러 개의 가상 서버를 설치할 수 있음. 또한, **서버의 상태**를 **이미지**로 저장할 수 있게 됐고, 새로운 서버를 만들어서, 기존 서버의 내용을 복사할 수 있게 됐음.

- 기존 상태를 고려하지 않고, 통째로 서버를 교체 → 생각보다 어렵고 느리고 특정 회사 제품을 써야 하니 비용이 들기도...

### 4) 클라우드(AWS, GCP, Azure, ...)

하드웨어를 내가 원하는 만큼 찍어낼 수 있게 되었고, 회사에 전산실이 없어도 가상화된 환경으로 서버 운영 가능. 전기를 꽂아 쓰듯이, 돈만 내면, 서버를 가져다가 쓸 수 있게 됨.

- 이미지를 기반으로 하는 다수의 서버 상태 관리
- 상태 관리에 대한 새로운 접근 → 서버 운영의 문제는 여전함

**클라우드 이미지의 단점**

- (보통) 그 이미지가 만들어지기까지 어떻게 만들어졌는지 모름
- (보통) 그래서 처음부터 다시 만들기 어려움
- 즉, 생각보다 관리가 어려움

### 5) Platform as a service

Heroku, Netlify, AWS Elastic Beanstalk, Google Cloud App Engine, ...

'나는 이미 환경이 잘 갖춰진 서버에 내 소스만 배포하겠다!'

일반화된 [프로비저닝](https://www.redhat.com/en/topics/automation/what-is-provisioning) 방법을 제공

- 정해진 과정만 따르면, 굳이 서버를 관리할 필요가 없음

소스만 올리면, 도메인 붙여주고, 방화벽 붙여주고... 확장이 굉장히 간단함.

**PaaS 단점**

애플리케이션을 PaaS 방식에 맞게 작성해야 함

- PaaS가 지원하는 것이 자바 구버전이라면? 그걸 써야 함

서버에 대한 원격 접속 시스템을 제공하지 않음

- 서버 안에서 무슨 일이 일어나는 지 몰라서, 문제가 발생했을 때, 해결이 어려움

파일 시스템 사용 불가, 로그 수집도 제한적인 방식(stdout)으로 허용 등

![Untitled](TAcademy-1%203ff44f3fe9c14e55ad6b5d89400a17c6/Untitled%201.png)

### 5) 도커의 등장

2013년에 DotCloud(현 Docker)에서 첫 공개

컨테이너: 격리된 환경에서 작동하는 프로세스

리눅스 커널의 여러 기술을 활용

하드웨어 가상화 기술(VM)보다 훨씬 가벼움

이미지 단위로 프로세스 실행 환경 구성

![Untitled](TAcademy-1%203ff44f3fe9c14e55ad6b5d89400a17c6/Untitled%202.png)

Host OS 위의 또 다른 OS vs. Host OS 위의 격리 

**도커의 특징 - 확장성**

도커가 설치되어 있다면 어디서든 컨테이너 실행 가능.

특정 회사나 서비스에 종속적이지 않음

쉽게 개발 서버를 만들 수 있고, 테스트 서버 생성도 간편

**도커의 특징 - 표준성**

ruby, nodejs, go, php 등의 서비스 배포는 모두 제각각

컨테이너라는 표준으로 서버를 배포하므로, 모든 서비스들의 배포 과정이 동일해짐

**도커의 특징 - 이미지**

이미지에서 컨테이너를 생성하기 때문에 반드시 이미지를 만드는 과정이 필요

Dokerfile을 이용해 이미지를 만들고 처음부터 재현 가능

빌드 서버에서 이미지를 만들면 해당 이미지를 이미지 저장소에 저장하고 운영 서버에서 이미지를 불러옴

**도커의 특징 - 설정**

설정은 보통 환경 변수로 제어

MYSQL_PASS=password와 같이 컨테이너를 띄울 때, 환경 변수를 같이 지정.

하나의 이미지가 환경변수에 따라 동적으로 설정 파일을 생성하도록 만들어야 함

**도커의 특징 - 자원**

컨테이너는 삭제 후 새로 만들면 모든 데이터가 초기화됨.

업로드 파일을 외부 스토리지와 링크하여 사용하거나 S3와 같은 별도의 저장소가 필요

세션이나 캐시를 파일로 사용하고 있다면, memcached나 redis와 같이 외부로 분리

**도커가 가져온 변화**

PaaS와 같은 제한이 없고, 클라우드 이미지보다 관리하기가 쉬움.

다른 프로세스와 격리되어 가상머신처럼 활용하지만, 성능저하 (거의) 없음

복잡한 기술(namespace, cgroups, network, ...)을 몰라도 사용할 수 있음

이미지 빌드 기록이 남음

코드와 설정으로 관리 > 재현 및 수정 가능

오픈소스 > 특정 회사 기술에 종속적이지 않음

![Untitled](TAcademy-1%203ff44f3fe9c14e55ad6b5d89400a17c6/Untitled%203.png)

**서비스 디스커버리(Service Discovery)**

서버들의 정보(IP, Port 등)을 포함한 다양한 정보를 저장하고 가져오고 값의 변화가 일어날 때, 이벤트를 받아 자동으로 서비스의 설정 정보를 수정하고 재시작하는 개념

1. 새로운 서버가 추가되면 서버 정보를 key/value store에 추가함
2. key/value store는 directory 형태로 값을 저장함. /services/web 하위를 읽으면 전체 web 서버 정보를 읽을 수 있음
3. key/value store를 watch하고 있던 configuration manager가 값이 추가되었다는 이벤트를 받음
4. 이벤트를 받으면 템플릿 파일을 기반으로 새로운 설정파일을 생성
5. 새로운 설정 파일을 만들어 기존 파일을 대체하고 서비스를 재시작함

![Untitled](TAcademy-1%203ff44f3fe9c14e55ad6b5d89400a17c6/Untitled%204.png)

기존에는 nginx를 설정을 수동으로 고치고, 재시작해야 했다면 이를 자동화

**docker-gen**

docker의 기본 기능을 적극 활용한 service discovery 도구.

- 도커 데몬이 가지고 있는 컨테이너의 정보를 그대로 이용
- 컨테이너를 실행할 때, 입력한 환경 변수를 읽음
- VIRTUAL_HOST=www.example.com과 같이 환경변수를 지정하면 이를 보고 nginx의 virtual host 설정 파일들을 구성함.

당시 도커의 기능은 간단한 것이었고, 이를 확장하는 것은 서드파티(third-party)로 만들었던 거. 이런 서드파티들이 모이고 모여서 쿠버네티스라는 완성된 플랫폼이 탄생

### 컨테이너 오케스트레이션

여러 대의 서버와 여러 개의 서비스를 편리하게 관리해주는 작업

**스케줄링**

컨테이너를 적당한 서버에 배포.

여러 대의 서버 중 가장 할 일 없는 서버에 배포하거나, 차례대로 혹은 아예 랜덤하게 배포

컨테이너 개수를 여러 개로 늘리면 적당히 나눠서 배포하고, 서버가 죽으면 실행 중이던 컨테이너를 다른 서버에 띄워 줌.

**클러스터링**

여러 개의 서버를 하나의 서버처럼 사용

작게는 몇 대의 서버, 많게는 수천 대의 서버를 하나의 클러스터로

여기저기 흩어져 있는 컨테이너도 가상 네트워크를 이용해 마치 같은 서버에 있는 것처럼 쉽게 통신

**서비스 디스커버리**

서비스를 찾아주는 기능

클러스터 환경에서 컨테이너는 어느 서버에 생성될 지 알 수 없고, 다른 서버로 이동할 수도 있음

따라서, 컨테이너와 통신을 하기 위해서는 어느 서버에서 실행 중인지 알아야 하고, 컨테이너가 생성되고 중지될 때, 어딘가에 ID와 Port 같은 정보를 업데이트해 줘야 함.

key-value storage에 정보를 저장할 수도 있고 내부 DNS 서버를 이용

**로깅, 모니터링**

여러 대의 서버를 관리하는 경우, 로그와 서버 상태를 한 곳에서 관리

***대표적인 오케스트레이션 도구***

**docker swarm**

docker에서 만듦.

단순 구조에서 효과적

**kubernetes**

구글에서 개발한 컨테이너 배포, 확장, 운영 도구

사실상 표준. 대규모에 적합. 다양한 생태계 구축되어 있음.

### 서비스 매시(Service Mesh)

넷플릭스 OSS에서 지원하는 기능과 분산 모니터링과 같은 기능을 프록시 방식으로 제공.

![Untitled](TAcademy-1%203ff44f3fe9c14e55ad6b5d89400a17c6/Untitled%205.png)

어떤 언어, 어떤 프레임워크에서도 사용 가능함

![Untitled](TAcademy-1%203ff44f3fe9c14e55ad6b5d89400a17c6/Untitled%206.png)

초록색(서비스), 파란색(프록시). 프록시가 대신 요청하고 응답을 받아서 retry 이때, 이 프록시는 아주 경량화된 친구라서, 대부분의 경우에 쉽게 사용 가능

![Untitled](TAcademy-1%203ff44f3fe9c14e55ad6b5d89400a17c6/Untitled%207.png)

프록시 사이에서만 retry, 

서비스 매시 기능

- Service Discovery (서비스 발견)
- Load Balancing (부하 분산)
- Routing Management (경로 관리)
- Traffic Management (트래픽 관리)
- Resilient (운영 탄력성)
- Fault Injection (오류 주입)
- Loggin / Monitoring (로깅/모니터링)
- Distributed Tracing (분산 추적)
- Security (보안)
- Authentication, Authorization (인증, 인가)

![Untitled](TAcademy-1%203ff44f3fe9c14e55ad6b5d89400a17c6/Untitled.png)