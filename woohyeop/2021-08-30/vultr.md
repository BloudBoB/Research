# vultr

Virtual Private Server(VPS)

vultr 2014년 출범

# Billing

1. Credit Card
2. Paypal
3. **Crypto(암호화폐)**
4. Alipay

---

## Instances

1. Cloud Compute
- Compute: 가장 기본 인스턴스
- High Frequency Compute: 더 좋은 CPU와 SSD를 제공하는 인스턴스

![Untitled](vultr%20df6a61ee2a8642a8933244a0454f01a3/Untitled.png)

클라우드 기초 - 정승기

![Untitled](vultr%20df6a61ee2a8642a8933244a0454f01a3/Untitled%201.png)

[https://www.ciokorea.com/news/35402](https://www.ciokorea.com/news/35402)

1. Dedicated Cloud

'헌신적인', 즉, 한 사용자에게 헌신적인 인스턴스이다. 누구와도 자원(CPU, SSD, RAM)을 공유하지 않으며, 따라서, 성능 면에서 기존의 것(Compute)보다 훨씬 더 빠른 서버이다. 그러나, 호스트 운영체제에 하이퍼바이저를 올려서 가상화를 수행한다. 때문에, 소프트웨어 계층에서, 즉, 여타 다른 프로그램처럼 호스트 운영체제에서 돌아간다.

1. Bare Metal

호스트 운영체제 없이 하드웨어에 바로 하이퍼바이저가 설치되고 그 위에 가상머신을 구현하는 것이다. 이러한 방식은 Dedicated Cloud의 이점을 그대로 가져온다. 그와 동시에, 운영체제가 아닌, 호스트 하드웨어 상에 하이퍼바이저가 설치되기 때문에, VM에서 하드웨어에 대한 직접 제어 및 설정이 가능하다. 또한, 다른 작업들을 수행할 때도, 호스트 OS를 거쳐가지 않기 때문에, 더 나은 성능을 제공할 것으로 보인다.

ㅇ 하이퍼바이저
가상 머신의 생성/삭제를 관할하고, 가상 머신에서 동작할 게스트(Guest) 운영체제를 활성화시켜주는 역할을 합니다.

[https://www.redhat.com/ko/topics/virtualization/what-is-a-hypervisor](https://www.redhat.com/ko/topics/virtualization/what-is-a-hypervisor)

[https://searchservervirtualization.techtarget.com/definition/bare-metal-hypervisor](https://searchservervirtualization.techtarget.com/definition/bare-metal-hypervisor)

## Block Storage

Block Storage는 인스턴스에 직접 연결 가능한 추가 NVMe SSD 스토리지라고 보면 된다.
NY(New York)와 NJ(New Jersey)에서만 제공되기 때문에 사용하기가 한정적이다. Block Storage와 같은 지역만 공유가 가능하다. 사용할 때마다 마운트, 해제할 때는 언마운트해야 Storage 내부에 자료가 손상되지 않는다. 아래는 새 Storage에 파티션을 나누는 명령인데, 기존에 했으면, 하면 안 된다. 데이터 날라간다.

```html
Create new empty partitions:
# parted -s /dev/vdb mklabel gpt
# parted -s /dev/vdb unit mib mkpart primary 0% 100%

Create new empty filesystem:
# mkfs.ext4 /dev/vdb1
```

## Object Storage

Object Storage는 필요에 따라 확장 가능한 스토리지를 추가하고 S3 API를 통해 관리할 수 있는 스토리지 서비스이다.

![Untitled](vultr%20df6a61ee2a8642a8933244a0454f01a3/Untitled%202.png)

이처럼, 한 개의 Object Storage 안에 여러 개의 버킷을 둘 수 있으며, 해당 버킷에 파일/폴더 업로드가 가능하다. API로도 당연히 접근 가능하지만, **s3cmd CLI tool**로도 접근이 가능하다. 

![Untitled](vultr%20df6a61ee2a8642a8933244a0454f01a3/Untitled%203.png)

s3cmd를 통해서, 버킷에 public하게 사진을 올림

버킷, 파일, 디렉토리 모두 public/private을 택할 수 있는데, 아래는 public한 brwook1 버킷에 웹 사이트로 접근한 상황이다. 참고로, private이 default이다.

https://ewr1.vultrobjects.com/brwook1

https://brwook1.ewr1.vultrobjects.com

![Untitled](vultr%20df6a61ee2a8642a8933244a0454f01a3/Untitled%204.png)

![Untitled](vultr%20df6a61ee2a8642a8933244a0454f01a3/Untitled%205.png)

그 외에는 Cyberduck GUI tool로도 가능하다고 하고, 언어 중에서는 Python, Go, php가 가능하다는데, php 시도하다가 도메인이 없어서 삽질 조금 하다가 못했다.

참고로, Object Storage는 아래에서 설명할 API Token에서와는 다른 S3 Credential이 따로 존재한다. 이는 특정 Object Storage 내에 파일/폴더를 관리하는 데 필요한 Credential이고, (권한만 존재한다면), API를 통해서 S3 Credential을 얻을 수 있다.

## Firewall

Group Rules로 인바운드 규칙을 설정할 수 있다. 아래는 IPv4에서 SSH와 HTTP를 허용한 상태이다.

![Untitled](vultr%20df6a61ee2a8642a8933244a0454f01a3/Untitled%206.png)

Network

Load Balancers

Kubernetes

---

# API

![Untitled](vultr%20df6a61ee2a8642a8933244a0454f01a3/Untitled%207.png)

[https://www.vultr.com/resources/developers/](https://www.vultr.com/resources/developers/)

1. **[Vultr API v2](https://www.vultr.com/api/)**

특정 Account의 Vultr Token을 가지고 있을 때, HTTP 접근을 통해서, Vultr의 기능을 통제할 수 있도록 만들어 놓은 API이다. 그런데, 보기 불편하다.

![Untitled](vultr%20df6a61ee2a8642a8933244a0454f01a3/Untitled%208.png)

위는 인스턴스들을 리스팅한 모습이다. aws cli처럼, 권한만 있다면, [모든 서비스](https://www.vultr.com/api/)에 대해 접근하여 수정할 수 있다. 그러나, API access는 불가능한 것이 default이고, 이를 허용해도 아래처럼 API Token을 이용 가능한 사용자의 IP를 등록해줄 수 있다.

![Untitled](vultr%20df6a61ee2a8642a8933244a0454f01a3/Untitled%209.png)

1. **Metadata API**

AWS의 instance metadata service처럼, Vultr도 같은 주소에 metadata API를 만들어 놓았다. 이는 해당 인스턴스에 대한 정보를 쿼리할 수 있는 API이고, 그 응답으로 정보를 제공한다.

![Untitled](vultr%20df6a61ee2a8642a8933244a0454f01a3/Untitled%2010.png)

[http://158.247.205.131/woo.php](http://158.247.205.131/woo.php)

## Open Source Projects

1. **CLI**

Vultr API v2보다 훨씬 쓰기 편하다. 가독성도 좋고, AWS CLI에 가장 가까우면서도, vultr 특유의 구성때문인지 더 보기 편한 거 같기도

![Untitled](vultr%20df6a61ee2a8642a8933244a0454f01a3/Untitled%2011.png)

1. Terraform
2. Packer

---

# Account

![Untitled](vultr%20df6a61ee2a8642a8933244a0454f01a3/Untitled%2012.png)

1. Profile: 프로필 정보 바꾸는 곳
2. Preference: Light/Dark 모드 지정하는 곳
3. Authentication: 계정 로그인할 떄, 2차 인증 설정, 신뢰하는 디바이스 설정
4. SSH Keys: 공개키를 계정에 저장해두고 있다. 이때문에, 인스턴스를 만들기 편하다.
5. **API**: Vultr API v2에서 봤던 것과 같다. API 토큰을 만들고, 접근 가능한 아이피 지정이 가능하다.
6. **Users**

![Untitled](vultr%20df6a61ee2a8642a8933244a0454f01a3/Untitled%2013.png)

AWS에서는 User, Group, Role 그리고 그에 붙은 Policy까지. 권한을 설정해주는 벡터가 다양했지만, 여기서는 한 User에다가 어떤 권한들을 설정해줄지 지정하고 이를 만들어 준다.

1. Notifacation: 알림 관련 설정