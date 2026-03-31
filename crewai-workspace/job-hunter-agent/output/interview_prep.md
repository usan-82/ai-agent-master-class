# Interview Prep: 미리디 – [미리캔버스] 시니어 백엔드 개발자

---

## Job Overview
- **포지션**: 시니어 백엔드 개발자 (경력 7~12년)  
- **팀/제품**: 전 세계 1,600만+ 사용자의 글로벌 디자인 플랫폼 “미리캔버스” 백엔드  
- **주요 업무**  
  - Java/Spring Boot 기반 MSA 아키텍처 설계·고도화  
  - 실시간 동시 편집, AI 검색·추천, 결제·회원·검색 핵심 도메인 운영  
  - PostgreSQL, MongoDB, DynamoDB, Redis, Vector DB 성능 최적화  
  - AWS(Opensearch, ECS, Lambda, Datadog, CloudWatch 등) 환경 구축·모니터링  
  - 기술 로드맵 주도, 코드 리뷰·세미나·스터디 문화 활성화  

## Why This Job Is a Fit
- **Java & Spring Boot Expertise**  
  5년 이상 Java 8→11→17, Spring Boot 2→3 마이그레이션 및 운영 경험  
- **MSA & 대규모 트래픽**  
  LG Uplus에서 하루 100만+ 트랜잭션 처리하는 Kafka 기반 이벤트 드리븐 시스템 구축  
- **데이터베이스 최적화**  
  PostgreSQL 인덱싱·파티셔닝, Redis 캐싱 전략으로 응답 지연 40% 절감  
- **AWS 및 클라우드 운용**  
  EC2, ECS, S3, Lambda, Datadog/CloudWatch 셋업 및 장애 대응 경험  
- **점진적 리팩토링 & 협업**  
  레거시→마이크로서비스 전환, OpenRewrite 자동화, 테크 부채 관리 방식이 ‘작은 최적화 반복’ 문화와 부합  

## Resume Highlights for This Role
- **마이크로서비스 설계·운영**:  
  - C/Java8 모놀리식 → Java17/Spring Boot3 MSA 전환 프로젝트 리드  
  - Eventuate CDC → Kafka → Billing 서비스로 실시간 데이터 통합  
- **결제·빌링 도메인 전문성**:  
  - 로밍 자동가입, 선불·후불·B2B 총량상품 과금 API 설계 및 구현  
- **성능 최적화**:  
  - PostgreSQL 스키마·쿼리 튜닝, Redis 캐시 적용으로 피크 타임 레이턴시 40% 단축  
- **클라우드 & DevOps**:  
  - Docker 기반 CI/CD 파이프라인(GitHub Actions) 구축  
  - Datadog, CloudWatch 알람 및 대시보드 설정  
- **테크 리더십**:  
  - 내부 프레임워크 버전 업그레이드(OpenRewrite 레시피 개발)  
  - 코드 리뷰, 페어 프로그래밍, 사내 스터디·세미나 진행  

## Company Summary
- **회사명**: ㈜미리디 (Miridi)  
- **주력 서비스**:  
  - **미리캔버스**: 글로벌 올인원 디자인 플랫폼 (가입자 1,600만+, MAU 140만+)  
  - **비즈하우스**: PoD 커머스 솔루션 (15만+ 샘플 디자인, 3D/AR 뷰어)  
- **미션**: “모두가 쉽게 디자인을 통해 세상과 소통하게 하자”  
- **핵심 가치**:  
  - Integrity & Thinking for the Whole  
  - Customer Focus & Impact-Driven Goals  
  - Data-Driven & High Standards  
- **최근 동향**: 시리즈 B 투자(200억), 연평균 60% 매출 성장, 글로벌 진출 가속화  

## Predicted Interview Questions
1. MSA 아키텍처 전환 경험을 설명하고, 성공 요인과 도전 과제를 말씀해 주세요.  
2. 대규모 동시 편집 기능(Conflict resolution)을 어떻게 설계하셨나요? OT/CRDT 기반 접근을 비교 설명해 주세요.  
3. AI 검색/추천 파이프라인(임베딩 생성→검색→랭킹) 설계를 보여주세요.  
4. PostgreSQL 성능 이슈를 발견했고, 이를 개선한 사례를 구체적으로 알려주세요.  
5. Redis 캐싱 전략과 장애 시나리오(데이터 일관성, 캐시 무효화)를 어떻게 처리하셨나요?  
6. RESTful API 설계 시 버전 관리, 인증(OAuth2/JWT), 오류 처리 정책을 어떻게 적용하나요?  
7. AWS Opensearch를 도입해야 할 때 고려 사항과 운영 중 모니터링 지표는 무엇인가요?  
8. 기술 부채가 쌓였을 때 ‘점진적 개선’ 전략을 어떻게 세우고 우선순위를 정하나요?  
9. CI/CD 파이프라인을 설계·운영하며 겪은 가장 큰 장애와 복구 과정을 설명해 주세요.  
10. 팀 내 코드 리뷰 및 지식 공유 문화를 활성화하기 위해 어떤 활동을 주도하셨나요?  

## Questions to Ask Them
1. **팀 구조 & 역할 분담**: 결제, 회원, 검색 등 각 도메인 팀 규모와 책임은 어떻게 나뉘어 있나요?  
2. **기술 로드맵**: 향후 6~12개월 내 핵심 시스템(실시간 편집, AI 추천 등)의 우선 순위 프로젝트는 무엇인가요?  
3. **MSA 전환 과제**: 현재 MSA 아키텍처 도입에서 가장 큰 기술적/조직적 도전은 무엇이며, 어떻게 해결 중이신가요?  
4. **성능 & 안정성 목표**: 주요 SLA/SLI 지표와 장애 대응 프로세스를 구체적으로 알고 싶습니다.  
5. **데이터베이스 전략**: Vector DB 활용 사례와 인덱싱·파티셔닝 정책을 듣고 싶습니다.  
6. **협업 문화**: 코드 리뷰, 페어 프로그래밍, 세미나 운영 방식을 자세히 설명해 주세요.  
7. **기술 리더십 기회**: 시니어로서 로드맵 설계, 멘토링, 아키텍처 결정 참여 기회는 어떻게 제공되나요?  
8. **글로벌 확장 전략**: 해외 시장 대응을 위해 준비 중인 신규 기능이나 인프라 변화가 있나요?  

## Concepts To Know/Review
- MSA vs. Monolith Migration Patterns  
- OT/CRDT 기반 동시 편집 알고리즘  
- AI 검색/추천: Embedding, Retrieval, Ranking  
- Database Tuning: 인덱스 전략, 파티셔닝, 커넥션 풀링  
- Caching Patterns: Cache-Aside, Write-Through, Invalidation  
- REST API Best Practices: HATEOAS, Versioning, Idempotency  
- AWS 핵심 서비스: ECS/EKS, Lambda, Opensearch, S3, IAM, CloudWatch/Datadog  
- CI/CD & Git Flow (GitHub Actions, Docker)  
- 핵심 CS: 자료구조, 알고리즘(동기/비동기, 큐, 그래프), 디자인 패턴  

## Strategic Advice
- **Tone & Focus**  
  - “완벽한 답”보다 “함께 질문하며 해답 찾는 과정” 강조: 솔루션보다 토론·검증 프로세스에 집중  
  - 본인의 경험을 ‘문제→분석→시도→결과’ 구조로 명확히 설명  
- **Culture Fit**  
  - 점진적 개선, 테크 부채 관리 철학에 공감하고 구체적 사례 제시  
  - 코드 리뷰·스터디·세미나 활동을 수행한 경험 어필  
- **Highlight Leadership**  
  - 프레임워크 업그레이드, 마이그레이션 레시피 작성 등 기술 리더십 경험 부각  
  - 후배 멘토링, 사내 지식 공유 사례 강조  
- **Watch Out for Red Flags**  
  - 대규모 리팩토링만을 주장하지 않기: “작은 최적화 반복” 문화에 부합  
  - 기술 중심의 대화만 고집하지 말고, 비즈니스 임팩트(사용자 가치·매출 기여)도 언급  

---

이 자료를 바탕으로 자신감 있게 면접 준비하시고, 미리디 백엔드 팀과 멋진 협업을 이끌어 가시길 바랍니다. Good luck!