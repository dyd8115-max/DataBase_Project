# 도서관 관리 시스템

PostgreSQL + Python Flask 기반의 도서관 관리 웹 서비스입니다.

## 기술 스택

- **Backend**: Python 3.10+, Flask 3.0
- **Database**: PostgreSQL
- **Frontend**: Bootstrap 5, Jinja2 템플릿

## 데이터베이스 설계

### 릴레이션 (Relation)

| 테이블 | 설명 | 주요 컬럼 |
|--------|------|-----------|
| `members` | 도서관 회원 | member_id (PK), name, email (UNIQUE), phone, join_date |
| `books` | 보유 도서 | book_id (PK), title, author, isbn (UNIQUE), category, total_copies, avail_copies |
| `loans` | 대출/반납 내역 | loan_id (PK), book_id (FK), member_id (FK), loan_date, due_date, return_date, status |

### 주요 쿼리 (Query)

- **JOIN 쿼리**: 대출 목록 조회 시 `loans ⋈ books ⋈ members`
- **집계 쿼리**: 회원별 대출 횟수 `GROUP BY + COUNT`
- **조건 검색**: 도서 제목/저자 검색 `ILIKE`
- **CASE WHEN**: 연체 여부 동적 계산

### 트랜잭션 (Transaction)

**대출 처리** (`/loans/new` POST):
1. `books.avail_copies` 잔여 확인 (`SELECT ... FOR UPDATE`)
2. `loans` 레코드 INSERT
3. `books.avail_copies -= 1` UPDATE
4. 모두 성공 시 `COMMIT`, 실패 시 `ROLLBACK`

**반납 처리** (`/loans/return/<id>` POST):
1. 대출 상태 확인 (`SELECT ... FOR UPDATE`)
2. `loans.status = 'returned'`, `return_date = CURRENT_DATE` UPDATE
3. `books.avail_copies += 1` UPDATE
4. 모두 성공 시 `COMMIT`

## 실행 방법

### 1. PostgreSQL 데이터베이스 생성

```sql
CREATE DATABASE library_db;
```

### 2. 스키마 및 샘플 데이터 적용

```bash
psql -U postgres -d library_db -f schema.sql
```

### 3. 환경 변수 설정

```bash
cp .env.example .env
# .env 파일에 DB 접속 정보 입력
```

### 4. 패키지 설치 및 서버 실행

```bash
pip install -r requirements.txt
python app.py
```

브라우저에서 `http://localhost:5000` 접속

## 주요 기능

- **대시보드**: 통계 요약 (전체 도서, 회원, 대출 중, 연체 건수)
- **도서 관리**: 도서 등록/조회/삭제, 카테고리·키워드 검색
- **회원 관리**: 회원 등록/조회, 대출 이력 집계
- **대출/반납**: 트랜잭션 기반 대출·반납 처리, 연체 표시
