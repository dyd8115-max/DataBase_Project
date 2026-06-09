from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import psycopg2
import psycopg2.extras
from datetime import date
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'dev-secret-key')


def get_db():
    return psycopg2.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        port=os.getenv('DB_PORT', 5432),
        dbname=os.getenv('DB_NAME', 'library_db'),
        user=os.getenv('DB_USER', 'postgres'),
        password=os.getenv('DB_PASSWORD', ''),
    )


# ─────────────────────────────────────────
# 메인 대시보드
# ─────────────────────────────────────────
@app.route('/')
def index():
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    # 집계 통계 (GROUP BY + COUNT 쿼리)
    cur.execute("SELECT COUNT(*) FROM books")
    total_books = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM members")
    total_members = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM loans WHERE status = 'active'")
    active_loans = cur.fetchone()[0]

    cur.execute("""
        SELECT COUNT(*) FROM loans
        WHERE status = 'active' AND due_date < CURRENT_DATE
    """)
    overdue_count = cur.fetchone()[0]

    # 최근 대출 목록 (JOIN 쿼리)
    cur.execute("""
        SELECT l.loan_id, b.title, m.name, l.loan_date, l.due_date, l.status,
               CASE WHEN l.due_date < CURRENT_DATE AND l.status = 'active'
                    THEN true ELSE false END AS is_overdue
        FROM loans l
        JOIN books   b ON l.book_id   = b.book_id
        JOIN members m ON l.member_id = m.member_id
        ORDER BY l.loan_id DESC
        LIMIT 10
    """)
    recent_loans = cur.fetchall()

    cur.close()
    conn.close()

    return render_template('index.html',
                           total_books=total_books,
                           total_members=total_members,
                           active_loans=active_loans,
                           overdue_count=overdue_count,
                           recent_loans=recent_loans)


# ─────────────────────────────────────────
# 도서 관리
# ─────────────────────────────────────────
@app.route('/books')
def books():
    query = request.args.get('q', '').strip()
    category = request.args.get('category', '').strip()

    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    sql = """
        SELECT book_id, title, author, isbn, category,
               total_copies, avail_copies, published_year
        FROM books
        WHERE 1=1
    """
    params = []

    if query:
        sql += " AND (title ILIKE %s OR author ILIKE %s)"
        params += [f'%{query}%', f'%{query}%']
    if category:
        sql += " AND category = %s"
        params.append(category)

    sql += " ORDER BY book_id DESC"
    cur.execute(sql, params)
    book_list = cur.fetchall()

    cur.execute("SELECT DISTINCT category FROM books ORDER BY category")
    categories = [r[0] for r in cur.fetchall()]

    cur.close()
    conn.close()
    return render_template('books.html', books=book_list, categories=categories,
                           query=query, selected_category=category)


@app.route('/books/add', methods=['GET', 'POST'])
def add_book():
    if request.method == 'POST':
        title   = request.form['title']
        author  = request.form['author']
        isbn    = request.form.get('isbn') or None
        category = request.form.get('category')
        copies  = int(request.form.get('total_copies', 1))
        year    = request.form.get('published_year') or None

        conn = get_db()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO books (title, author, isbn, category, total_copies, avail_copies, published_year)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (title, author, isbn, category, copies, copies, year))
        conn.commit()
        cur.close()
        conn.close()
        flash('도서가 등록되었습니다.', 'success')
        return redirect(url_for('books'))

    return render_template('add_book.html')


@app.route('/books/delete/<int:book_id>', methods=['POST'])
def delete_book(book_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM loans WHERE book_id = %s AND status = 'active'", (book_id,))
    if cur.fetchone()[0] > 0:
        flash('현재 대출 중인 도서는 삭제할 수 없습니다.', 'danger')
    else:
        cur.execute("DELETE FROM books WHERE book_id = %s", (book_id,))
        conn.commit()
        flash('도서가 삭제되었습니다.', 'success')
    cur.close()
    conn.close()
    return redirect(url_for('books'))


# ─────────────────────────────────────────
# 회원 관리
# ─────────────────────────────────────────
@app.route('/members')
def members():
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    # 회원별 대출 횟수 집계 (LEFT JOIN + GROUP BY)
    cur.execute("""
        SELECT m.member_id, m.name, m.email, m.phone, m.join_date,
               COUNT(l.loan_id) AS total_loans,
               COUNT(CASE WHEN l.status = 'active' THEN 1 END) AS active_loans
        FROM members m
        LEFT JOIN loans l ON m.member_id = l.member_id
        GROUP BY m.member_id
        ORDER BY m.member_id DESC
    """)
    member_list = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('members.html', members=member_list)


@app.route('/members/add', methods=['GET', 'POST'])
def add_member():
    if request.method == 'POST':
        name  = request.form['name']
        email = request.form['email']
        phone = request.form.get('phone')

        conn = get_db()
        cur = conn.cursor()
        try:
            cur.execute("""
                INSERT INTO members (name, email, phone) VALUES (%s, %s, %s)
            """, (name, email, phone))
            conn.commit()
            flash('회원이 등록되었습니다.', 'success')
            return redirect(url_for('members'))
        except psycopg2.errors.UniqueViolation:
            conn.rollback()
            flash('이미 등록된 이메일입니다.', 'danger')
        finally:
            cur.close()
            conn.close()

    return render_template('add_member.html')


# ─────────────────────────────────────────
# 대출 처리 (트랜잭션 핵심)
# ─────────────────────────────────────────
@app.route('/loans')
def loans():
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("""
        SELECT l.loan_id, b.title, m.name, l.loan_date, l.due_date,
               l.return_date, l.status,
               CASE WHEN l.due_date < CURRENT_DATE AND l.status = 'active'
                    THEN true ELSE false END AS is_overdue
        FROM loans l
        JOIN books   b ON l.book_id   = b.book_id
        JOIN members m ON l.member_id = m.member_id
        ORDER BY l.loan_id DESC
    """)
    loan_list = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('loans.html', loans=loan_list)


@app.route('/loans/new', methods=['GET', 'POST'])
def new_loan():
    if request.method == 'POST':
        book_id   = int(request.form['book_id'])
        member_id = int(request.form['member_id'])

        conn = get_db()
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        try:
            # 트랜잭션 시작 — psycopg2는 기본적으로 autocommit=False
            cur.execute("SELECT avail_copies FROM books WHERE book_id = %s FOR UPDATE", (book_id,))
            book = cur.fetchone()
            if not book or book['avail_copies'] <= 0:
                flash('대출 가능한 재고가 없습니다.', 'danger')
                conn.rollback()
                return redirect(url_for('new_loan'))

            # 이미 같은 책을 대출 중인지 확인
            cur.execute("""
                SELECT 1 FROM loans
                WHERE book_id = %s AND member_id = %s AND status = 'active'
            """, (book_id, member_id))
            if cur.fetchone():
                flash('해당 회원이 이미 이 책을 대출 중입니다.', 'warning')
                conn.rollback()
                return redirect(url_for('new_loan'))

            # 대출 레코드 삽입
            cur.execute("""
                INSERT INTO loans (book_id, member_id) VALUES (%s, %s)
            """, (book_id, member_id))

            # 재고 감소 (원자적 갱신)
            cur.execute("""
                UPDATE books SET avail_copies = avail_copies - 1
                WHERE book_id = %s
            """, (book_id,))

            conn.commit()  # 두 작업 모두 성공해야 커밋
            flash('대출이 완료되었습니다.', 'success')
            return redirect(url_for('loans'))

        except Exception as e:
            conn.rollback()
            flash(f'오류가 발생했습니다: {str(e)}', 'danger')
        finally:
            cur.close()
            conn.close()

    # GET: 도서·회원 목록 전달
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("SELECT book_id, title, author, avail_copies FROM books WHERE avail_copies > 0 ORDER BY title")
    available_books = cur.fetchall()
    cur.execute("SELECT member_id, name, email FROM members ORDER BY name")
    member_list = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('new_loan.html', books=available_books, members=member_list)


@app.route('/loans/return/<int:loan_id>', methods=['POST'])
def return_book(loan_id):
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    try:
        cur.execute("SELECT book_id, status FROM loans WHERE loan_id = %s FOR UPDATE", (loan_id,))
        loan = cur.fetchone()
        if not loan or loan['status'] != 'active':
            flash('유효하지 않은 대출 건입니다.', 'danger')
            conn.rollback()
            return redirect(url_for('loans'))

        # 반납 처리 트랜잭션
        cur.execute("""
            UPDATE loans
            SET status = 'returned', return_date = CURRENT_DATE
            WHERE loan_id = %s
        """, (loan_id,))

        cur.execute("""
            UPDATE books SET avail_copies = avail_copies + 1
            WHERE book_id = %s
        """, (loan['book_id'],))

        conn.commit()
        flash('반납이 완료되었습니다.', 'success')

    except Exception as e:
        conn.rollback()
        flash(f'오류: {str(e)}', 'danger')
    finally:
        cur.close()
        conn.close()

    return redirect(url_for('loans'))


# ─────────────────────────────────────────
# API 엔드포인트 (JSON)
# ─────────────────────────────────────────
@app.route('/api/stats')
def api_stats():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT
            (SELECT COUNT(*) FROM books)                             AS total_books,
            (SELECT COUNT(*) FROM members)                           AS total_members,
            (SELECT COUNT(*) FROM loans WHERE status = 'active')     AS active_loans,
            (SELECT COUNT(*) FROM loans
             WHERE status = 'active' AND due_date < CURRENT_DATE)    AS overdue_loans
    """)
    row = cur.fetchone()
    cur.close()
    conn.close()
    return jsonify({
        'total_books': row[0],
        'total_members': row[1],
        'active_loans': row[2],
        'overdue_loans': row[3],
    })


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
