from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = 'demo-key'

# ── 더미 데이터 ──────────────────────────────────────────
books = [
    {'book_id':1,'title':'데이터베이스 시스템','author':'램 나라야난','isbn':'978-89-7050-000-1','category':'컴퓨터/IT','total_copies':3,'avail_copies':2,'published_year':2020},
    {'book_id':2,'title':'클린 코드','author':'로버트 마틴','isbn':'978-89-7050-001-8','category':'컴퓨터/IT','total_copies':2,'avail_copies':0,'published_year':2019},
    {'book_id':3,'title':'파이썬 완전정복','author':'홍길동','isbn':'978-89-7050-002-5','category':'컴퓨터/IT','total_copies':2,'avail_copies':2,'published_year':2022},
    {'book_id':4,'title':'운영체제 개론','author':'에이브러햄 실버샤츠','isbn':'978-89-7050-003-2','category':'컴퓨터/IT','total_copies':1,'avail_copies':1,'published_year':2021},
    {'book_id':5,'title':'알고리즘 문제해결 전략','author':'구종만','isbn':'978-89-7050-004-9','category':'컴퓨터/IT','total_copies':2,'avail_copies':1,'published_year':2018},
]
members = [
    {'member_id':1,'name':'김민준','email':'minjun@example.com','phone':'010-1234-5678','join_date':'2025-03-01','total_loans':3,'active_loans':1},
    {'member_id':2,'name':'이서연','email':'seoyeon@example.com','phone':'010-2345-6789','join_date':'2025-04-15','total_loans':2,'active_loans':2},
    {'member_id':3,'name':'박지호','email':'jiho@example.com','phone':'010-3456-7890','join_date':'2025-05-20','total_loans':1,'active_loans':0},
]
loans = [
    {'loan_id':1,'title':'클린 코드','name':'김민준','loan_date':'2026-05-01','due_date':'2026-05-15','return_date':None,'status':'active','is_overdue':True},
    {'loan_id':2,'title':'데이터베이스 시스템','name':'이서연','loan_date':'2026-05-20','due_date':'2026-06-03','return_date':None,'status':'active','is_overdue':True},
    {'loan_id':3,'title':'알고리즘 문제해결 전략','name':'이서연','loan_date':'2026-06-01','due_date':'2026-06-15','return_date':None,'status':'active','is_overdue':False},
    {'loan_id':4,'title':'파이썬 완전정복','name':'김민준','loan_date':'2026-04-10','due_date':'2026-04-24','return_date':'2026-04-23','status':'returned','is_overdue':False},
]

@app.route('/')
def index():
    return render_template('index.html',
        total_books=len(books), total_members=len(members),
        active_loans=sum(1 for l in loans if l['status']=='active'),
        overdue_count=sum(1 for l in loans if l['is_overdue']),
        recent_loans=loans[:5])

@app.route('/books')
def books_page():
    q = request.args.get('q','').strip()
    cat = request.args.get('category','').strip()
    result = books
    if q:
        result = [b for b in result if q.lower() in b['title'].lower() or q.lower() in b['author'].lower()]
    if cat:
        result = [b for b in result if b['category']==cat]
    cats = list(set(b['category'] for b in books))
    return render_template('books.html', books=result, categories=cats, query=q, selected_category=cat)

@app.route('/books/add', methods=['GET','POST'])
def add_book():
    if request.method == 'POST':
        flash('도서가 등록되었습니다. (데모 — 실제 저장 안 됨)', 'success')
        return redirect(url_for('books_page'))
    return render_template('add_book.html')

@app.route('/books/delete/<int:book_id>', methods=['POST'])
def delete_book(book_id):
    flash('도서가 삭제되었습니다. (데모)', 'success')
    return redirect(url_for('books_page'))

@app.route('/members')
def members_page():
    return render_template('members.html', members=members)

@app.route('/members/add', methods=['GET','POST'])
def add_member():
    if request.method == 'POST':
        flash('회원이 등록되었습니다. (데모 — 실제 저장 안 됨)', 'success')
        return redirect(url_for('members_page'))
    return render_template('add_member.html')

@app.route('/loans')
def loans_page():
    return render_template('loans.html', loans=loans)

@app.route('/loans/new', methods=['GET','POST'])
def new_loan():
    if request.method == 'POST':
        flash('대출이 완료되었습니다. (데모 — 실제 저장 안 됨)', 'success')
        return redirect(url_for('loans_page'))
    avail = [b for b in books if b['avail_copies'] > 0]
    return render_template('new_loan.html', books=avail, members=members)

@app.route('/loans/return/<int:loan_id>', methods=['POST'])
def return_book(loan_id):
    flash('반납이 완료되었습니다. (데모)', 'success')
    return redirect(url_for('loans_page'))

# URL 이름 호환
app.add_url_rule('/books', endpoint='books', view_func=books_page)
app.add_url_rule('/members', endpoint='members', view_func=members_page)
app.add_url_rule('/loans', endpoint='loans', view_func=loans_page)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
