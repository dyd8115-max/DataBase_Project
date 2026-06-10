"""스크린샷용 독립 HTML 생성 후 wkhtmltoimage로 렌더링"""
import subprocess, os, textwrap

os.makedirs('/tmp/screenshots', exist_ok=True)

STYLE = """
* { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Segoe UI', Arial, sans-serif; }
body { background: #f1f5f9; display: flex; min-height: 100vh; }
.sidebar { width: 210px; background: #1e3a5f; color: #fff; flex-shrink: 0; padding: 0; min-height: 100vh; }
.sidebar .brand { padding: 22px 16px; font-size: 17px; font-weight: 700; border-bottom: 1px solid rgba(255,255,255,.2); }
.sidebar .nav { list-style: none; padding: 12px 8px; }
.sidebar .nav li a { display: block; padding: 10px 12px; color: rgba(255,255,255,.75); border-radius: 6px; margin: 3px 0; font-size: 14px; text-decoration: none; }
.sidebar .nav li a.active, .sidebar .nav li a:hover { background: rgba(255,255,255,.15); color: #fff; }
.main { flex: 1; padding: 28px 32px; }
h4 { font-size: 22px; font-weight: 700; color: #1e293b; margin-bottom: 20px; }
.row { display: flex; gap: 16px; margin-bottom: 24px; }
.card { background: #fff; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,.08); overflow: hidden; }
.stat-card { flex: 1; padding: 20px 24px; color: #fff; border-radius: 12px; }
.stat-card p { font-size: 13px; opacity: .75; margin-bottom: 6px; }
.stat-card h3 { font-size: 36px; font-weight: 700; }
.card-header { background: #fff; padding: 14px 20px; font-weight: 600; font-size: 15px; border-bottom: 1px solid #e2e8f0; }
table { width: 100%; border-collapse: collapse; }
thead tr { background: #f8fafc; }
th, td { padding: 11px 16px; text-align: left; font-size: 14px; border-bottom: 1px solid #f1f5f9; }
th { font-weight: 600; color: #475569; font-size: 13px; }
.badge { display: inline-block; padding: 3px 10px; border-radius: 20px; font-size: 12px; font-weight: 600; }
.badge-success { background: #dcfce7; color: #16a34a; }
.badge-danger  { background: #fee2e2; color: #dc2626; }
.badge-gray    { background: #e2e8f0; color: #64748b; }
.badge-blue    { background: #dbeafe; color: #2563eb; }
.tr-danger td  { background: #fff1f2; }
.form-card { background: #fff; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,.08); padding: 28px; max-width: 480px; }
.form-group { margin-bottom: 18px; }
label { display: block; font-weight: 600; font-size: 14px; margin-bottom: 6px; color: #1e293b; }
input, select { width: 100%; padding: 9px 12px; border: 1px solid #cbd5e1; border-radius: 6px; font-size: 14px; }
.btn { display: inline-block; padding: 10px 20px; border-radius: 6px; font-weight: 600; font-size: 14px; border: none; cursor: pointer; }
.btn-primary { background: #2563eb; color: #fff; }
.btn-top { background: #2563eb; color: #fff; padding: 8px 18px; border-radius: 6px; font-size: 14px; font-weight: 600; }
.top-bar { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.search-bar { display: flex; gap: 10px; margin-bottom: 16px; }
.search-bar input { max-width: 340px; }
.search-bar select { width: 160px; }
.avail-zero { color: #dc2626; font-weight: 700; }
.alert-info { background: #eff6ff; border: 1px solid #bfdbfe; border-radius: 8px; padding: 12px 16px; font-size: 14px; color: #1d4ed8; margin-bottom: 18px; }
"""

def sidebar(active):
    items = [('대시보드','/','dash'), ('도서 관리','/books','books'), ('회원 관리','/members','members'), ('대출/반납','/loans','loans')]
    lis = ''
    for name, href, key in items:
        cls = 'active' if key == active else ''
        lis += f'<li><a href="#" class="{cls}">{"📊" if key=="dash" else "📚" if key=="books" else "👥" if key=="members" else "↔️"} {name}</a></li>'
    return f'<div class="sidebar"><div class="brand">📖 도서관 시스템</div><ul class="nav">{lis}</ul></div>'

pages = {}

# ── 대시보드 ──────────────────────────────────────────────
pages['dashboard'] = f"""<!DOCTYPE html><html><head><meta charset="UTF-8"><style>{STYLE}</style></head><body>
{sidebar('dash')}
<div class="main">
<h4>대시보드</h4>
<div class="row">
  <div class="stat-card" style="background:#1e3a5f"><p>전체 도서</p><h3>5</h3></div>
  <div class="stat-card" style="background:#2563eb"><p>전체 회원</p><h3>3</h3></div>
  <div class="stat-card" style="background:#16a34a"><p>현재 대출 중</p><h3>3</h3></div>
  <div class="stat-card" style="background:#dc2626"><p>연체 건수</p><h3>2</h3></div>
</div>
<div class="card">
  <div class="card-header">최근 대출 현황</div>
  <table><thead><tr><th>#</th><th>도서명</th><th>회원명</th><th>대출일</th><th>반납 예정일</th><th>상태</th></tr></thead>
  <tbody>
    <tr class="tr-danger"><td>2</td><td>데이터베이스 시스템</td><td>이서연</td><td>2026-05-20</td><td>2026-06-03</td><td><span class="badge badge-danger">연체</span></td></tr>
    <tr class="tr-danger"><td>1</td><td>클린 코드</td><td>김민준</td><td>2026-05-01</td><td>2026-05-15</td><td><span class="badge badge-danger">연체</span></td></tr>
    <tr><td>3</td><td>알고리즘 문제해결 전략</td><td>이서연</td><td>2026-06-01</td><td>2026-06-15</td><td><span class="badge badge-success">대출 중</span></td></tr>
    <tr><td>4</td><td>파이썬 완전정복</td><td>김민준</td><td>2026-04-10</td><td>2026-04-24</td><td><span class="badge badge-gray">반납 완료</span></td></tr>
  </tbody></table>
</div>
</div></body></html>"""

# ── 도서 목록 ─────────────────────────────────────────────
pages['books'] = f"""<!DOCTYPE html><html><head><meta charset="UTF-8"><style>{STYLE}</style></head><body>
{sidebar('books')}
<div class="main">
<div class="top-bar"><h4 style="margin:0">도서 관리</h4><button class="btn-top">+ 도서 등록</button></div>
<div class="search-bar">
  <input type="text" placeholder="제목 또는 저자 검색" value="">
  <select><option>전체 카테고리</option><option selected>컴퓨터/IT</option></select>
  <button class="btn btn-primary" style="padding:9px 16px">🔍</button>
</div>
<div class="card">
<table><thead><tr><th>#</th><th>제목</th><th>저자</th><th>카테고리</th><th>출판연도</th><th>전체/가용</th><th></th></tr></thead>
<tbody>
  <tr><td>1</td><td>데이터베이스 시스템</td><td>램 나라야난</td><td><span class="badge badge-blue">컴퓨터/IT</span></td><td>2020</td><td>3 / 2</td><td><button style="padding:4px 10px;border:1px solid #dc2626;color:#dc2626;border-radius:4px;background:#fff;font-size:12px">🗑</button></td></tr>
  <tr><td>2</td><td>클린 코드</td><td>로버트 마틴</td><td><span class="badge badge-blue">컴퓨터/IT</span></td><td>2019</td><td class="avail-zero">2 / 0</td><td><button style="padding:4px 10px;border:1px solid #dc2626;color:#dc2626;border-radius:4px;background:#fff;font-size:12px">🗑</button></td></tr>
  <tr><td>3</td><td>파이썬 완전정복</td><td>홍길동</td><td><span class="badge badge-blue">컴퓨터/IT</span></td><td>2022</td><td>2 / 2</td><td><button style="padding:4px 10px;border:1px solid #dc2626;color:#dc2626;border-radius:4px;background:#fff;font-size:12px">🗑</button></td></tr>
  <tr><td>4</td><td>운영체제 개론</td><td>에이브러햄 실버샤츠</td><td><span class="badge badge-blue">컴퓨터/IT</span></td><td>2021</td><td>1 / 1</td><td><button style="padding:4px 10px;border:1px solid #dc2626;color:#dc2626;border-radius:4px;background:#fff;font-size:12px">🗑</button></td></tr>
  <tr><td>5</td><td>알고리즘 문제해결 전략</td><td>구종만</td><td><span class="badge badge-blue">컴퓨터/IT</span></td><td>2018</td><td>2 / 1</td><td><button style="padding:4px 10px;border:1px solid #dc2626;color:#dc2626;border-radius:4px;background:#fff;font-size:12px">🗑</button></td></tr>
</tbody></table>
</div></div></body></html>"""

# ── 회원 목록 ─────────────────────────────────────────────
pages['members'] = f"""<!DOCTYPE html><html><head><meta charset="UTF-8"><style>{STYLE}</style></head><body>
{sidebar('members')}
<div class="main">
<div class="top-bar"><h4 style="margin:0">회원 관리</h4><button class="btn-top">+ 회원 등록</button></div>
<div class="card">
<table><thead><tr><th>#</th><th>이름</th><th>이메일</th><th>전화번호</th><th>가입일</th><th>총 대출</th><th>현재 대출</th></tr></thead>
<tbody>
  <tr><td>1</td><td>김민준</td><td>minjun@example.com</td><td>010-1234-5678</td><td>2025-03-01</td><td>3</td><td><span class="badge badge-blue">1권</span></td></tr>
  <tr><td>2</td><td>이서연</td><td>seoyeon@example.com</td><td>010-2345-6789</td><td>2025-04-15</td><td>2</td><td><span class="badge badge-blue">2권</span></td></tr>
  <tr><td>3</td><td>박지호</td><td>jiho@example.com</td><td>010-3456-7890</td><td>2025-05-20</td><td>1</td><td><span style="color:#94a3b8">0</span></td></tr>
</tbody></table>
</div></div></body></html>"""

# ── 대출/반납 목록 ────────────────────────────────────────
pages['loans'] = f"""<!DOCTYPE html><html><head><meta charset="UTF-8"><style>{STYLE}</style></head><body>
{sidebar('loans')}
<div class="main">
<div class="top-bar"><h4 style="margin:0">대출/반납 관리</h4><button class="btn-top">+ 신규 대출</button></div>
<div class="card">
<table><thead><tr><th>#</th><th>도서명</th><th>회원명</th><th>대출일</th><th>반납 예정일</th><th>반납일</th><th>상태</th><th></th></tr></thead>
<tbody>
  <tr class="tr-danger"><td>1</td><td>클린 코드</td><td>김민준</td><td>2026-05-01</td><td>2026-05-15</td><td>-</td><td><span class="badge badge-danger">연체</span></td><td><button style="padding:5px 12px;border:1px solid #2563eb;color:#2563eb;border-radius:4px;background:#fff;font-size:13px">반납</button></td></tr>
  <tr class="tr-danger"><td>2</td><td>데이터베이스 시스템</td><td>이서연</td><td>2026-05-20</td><td>2026-06-03</td><td>-</td><td><span class="badge badge-danger">연체</span></td><td><button style="padding:5px 12px;border:1px solid #2563eb;color:#2563eb;border-radius:4px;background:#fff;font-size:13px">반납</button></td></tr>
  <tr><td>3</td><td>알고리즘 문제해결 전략</td><td>이서연</td><td>2026-06-01</td><td>2026-06-15</td><td>-</td><td><span class="badge badge-success">대출 중</span></td><td><button style="padding:5px 12px;border:1px solid #2563eb;color:#2563eb;border-radius:4px;background:#fff;font-size:13px">반납</button></td></tr>
  <tr><td>4</td><td>파이썬 완전정복</td><td>김민준</td><td>2026-04-10</td><td>2026-04-24</td><td>2026-04-23</td><td><span class="badge badge-gray">반납 완료</span></td><td></td></tr>
</tbody></table>
</div></div></body></html>"""

# ── 신규 대출 ─────────────────────────────────────────────
pages['new_loan'] = f"""<!DOCTYPE html><html><head><meta charset="UTF-8"><style>{STYLE}</style></head><body>
{sidebar('loans')}
<div class="main">
<h4>신규 대출</h4>
<div class="form-card">
  <div class="form-group">
    <label>도서 선택 <span style="color:red">*</span></label>
    <select>
      <option>-- 도서를 선택하세요 --</option>
      <option>데이터베이스 시스템 — 램 나라야난 (재고: 2)</option>
      <option>파이썬 완전정복 — 홍길동 (재고: 2)</option>
      <option>운영체제 개론 — 에이브러햄 실버샤츠 (재고: 1)</option>
      <option>알고리즘 문제해결 전략 — 구종만 (재고: 1)</option>
    </select>
  </div>
  <div class="form-group">
    <label>회원 선택 <span style="color:red">*</span></label>
    <select>
      <option>-- 회원을 선택하세요 --</option>
      <option>김민준 (minjun@example.com)</option>
      <option>박지호 (jiho@example.com)</option>
      <option>이서연 (seoyeon@example.com)</option>
    </select>
  </div>
  <div class="alert-info">ℹ️ 대출 기간은 <strong>14일</strong>입니다. 대출 처리 시 재고가 자동으로 차감됩니다.</div>
  <button class="btn btn-primary" style="width:100%;padding:12px">대출 처리</button>
</div>
</div></body></html>"""

# 렌더링
for name, html in pages.items():
    path = f'/tmp/screenshots/{name}.html'
    with open(path, 'w') as f:
        f.write(html)
    result = subprocess.run(
        ['xvfb-run', '-a', 'wkhtmltoimage', '--width', '1280', '--quality', '95',
         f'file://{path}', f'/tmp/screenshots/{name}.png'],
        capture_output=True, text=True
    )
    ok = os.path.exists(f'/tmp/screenshots/{name}.png')
    print(f"  {name}: {'완료' if ok else '실패'}")
