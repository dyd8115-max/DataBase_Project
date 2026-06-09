-- 도서관 관리 시스템 데이터베이스 스키마

CREATE TABLE IF NOT EXISTS members (
    member_id   SERIAL PRIMARY KEY,
    name        VARCHAR(100) NOT NULL,
    email       VARCHAR(150) UNIQUE NOT NULL,
    phone       VARCHAR(20),
    join_date   DATE NOT NULL DEFAULT CURRENT_DATE,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS books (
    book_id         SERIAL PRIMARY KEY,
    title           VARCHAR(300) NOT NULL,
    author          VARCHAR(150) NOT NULL,
    isbn            VARCHAR(20) UNIQUE,
    category        VARCHAR(50),
    total_copies    INT NOT NULL DEFAULT 1 CHECK (total_copies >= 0),
    avail_copies    INT NOT NULL DEFAULT 1 CHECK (avail_copies >= 0),
    published_year  INT,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS loans (
    loan_id     SERIAL PRIMARY KEY,
    book_id     INT NOT NULL REFERENCES books(book_id),
    member_id   INT NOT NULL REFERENCES members(member_id),
    loan_date   DATE NOT NULL DEFAULT CURRENT_DATE,
    due_date    DATE NOT NULL DEFAULT (CURRENT_DATE + INTERVAL '14 days'),
    return_date DATE,
    status      VARCHAR(20) NOT NULL DEFAULT 'active'
                    CHECK (status IN ('active', 'returned', 'overdue'))
);

CREATE INDEX IF NOT EXISTS idx_loans_status ON loans(status);
CREATE INDEX IF NOT EXISTS idx_loans_member ON loans(member_id);
CREATE INDEX IF NOT EXISTS idx_loans_book   ON loans(book_id);

-- 샘플 데이터
INSERT INTO members (name, email, phone) VALUES
    ('김민준', 'minjun@example.com', '010-1234-5678'),
    ('이서연', 'seoyeon@example.com', '010-2345-6789'),
    ('박지호', 'jiho@example.com', '010-3456-7890')
ON CONFLICT (email) DO NOTHING;

INSERT INTO books (title, author, isbn, category, total_copies, avail_copies, published_year) VALUES
    ('데이터베이스 시스템', '램 나라야난', '978-89-7050-000-1', '컴퓨터/IT', 3, 3, 2020),
    ('클린 코드', '로버트 마틴', '978-89-7050-001-8', '컴퓨터/IT', 2, 2, 2019),
    ('파이썬 완전정복', '홍길동', '978-89-7050-002-5', '컴퓨터/IT', 2, 2, 2022),
    ('운영체제 개론', '에이브러햄 실버샤츠', '978-89-7050-003-2', '컴퓨터/IT', 1, 1, 2021),
    ('알고리즘 문제해결 전략', '구종만', '978-89-7050-004-9', '컴퓨터/IT', 2, 2, 2018)
ON CONFLICT (isbn) DO NOTHING;
