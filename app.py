from flask import Flask, render_template
from flask import request, session, redirect
import pymysql
from datetime import datetime

app = Flask(__name__,
            static_folder='static',
            template_folder='template')

db = pymysql.connect(
    user='root',
    passwd='avante',
    host='localhost',
    db='web',
    charset='utf8',
    cursorclass=pymysql.cursors.DictCursor
)

app.config['ENV']='development'
app.config['DEBUG']=True
app.secret_key='who are you?'

def get_menu():
    cur=db.cursor()
    cur.execute(f"""
        select id, title from topic
    """)
    menu_all=cur.fetchall()
    menu=[]
    for row in menu_all:
       menu.append(f"""
        <li><a href='/{row['id']}'>{row['title']}</a></li>
       """)
    return "\n".join(menu)

@app.route('/')
def index():
    content='Python study을 위한 menu 관리'
    if 'owner' in session:
        owner=session['owner']['name']
    else:
        owner='login please'

    return render_template('template.html',
                            owner=owner,
                            menu=get_menu(),
                            content=content)

@app.route('/<id>')
def html(id):
    if 'owner' in session:
        owner=session['owner']['name']
    else:
        owner='login please'
        return redirect('/')
    cur=db.cursor()
    cur.execute(f"""
        select id, title, description from topic 
            where id='{id}'
    """)
    topic=cur.fetchone()

    return render_template('template.html',
                        owner = owner,
                        title= topic['title'] ,
                        menu=get_menu(),
                        content=topic['description']
                        )

@app.route('/create', methods=['GET','POST'])
def create():
    if 'owner' in session:
        owner=session['owner']['name']
    else:
        owner='login please'
        return redirect('/')

    if request.method == 'POST':
        if 'owner' in session:
            owner=session['owner']['name']
        
        cur=db.cursor()
        cur.execute(f"""
            insert into topic (title, description, created, author_id)
            values ('{request.form['title']}','{request.form['desc']}',
            '{datetime.now()}','{session['owner']['id']}')
        """)
        db.commit()
        return redirect('/')

    
    return render_template('create.html',
                            owner=owner,
                            menu=get_menu())

@app.route('/login', methods=['GET','POST'])
def login():
    if 'owner' in session:
        content='login 상태 입니다.'
        return render_template('template.html',
                            menu=get_menu(),
                            owner=session['owner']['name'],
                            content=content)
    else:
        content='login 해주세요.'
    if request.method == 'POST':
        cur=db.cursor()
        cur.execute(f"""
            select name from author where name='{request.form['id']}'
        """)
        user=cur.fetchone()
        if user is None:
            content='로그인 id 가 없읍니다. 확인해 주세요.'
        else:
            cur=db.cursor()
            cur.execute(f"""
                select id, name, password from author
                where password=SHA2('{request.form['pw']}',256) 
                    and name='{request.form['id']}'
            """)
            passwd=cur.fetchone()
            if passwd is None:
                content='입력하신 password 가 틀립니다.'
            else:
                session['owner']=passwd
                return redirect('/')

    return render_template('login.html',
                            menu=get_menu(),
                            content=content)

@app.route('/logout')
def logout():
    session.pop('owner',None)
    return redirect('/')

@app.route('/join', methods=['GET', 'POST'])
def join():
    content=''
    if request.method == 'POST':
        cur=db.cursor()
        cur.execute(f"""
            select name from author where name='{request.form['id']}'
        """)
        user=cur.fetchone()
        if user is None:
            if request.form['id'] == '':
                content='회원 가입시 id 을 입력해 주세요'
                return render_template('join.html',
                                        menu=get_menu(),
                                        content=content) 
            elif request.form['pw'] == '':
                content='회원가입시 password 을 입력해 주세요'
                return render_template('join.html',
                                    menu=get_menu(),
                                    content=content)           
            else:
                cur=db.cursor()
                sql=f"""
                    insert into author (name, profile, password)
                    values('{request.form['id']}','{request.form['pf']}',
                        SHA2('{request.form['pw']}',256))
                    """
                cur.execute(sql)
                db.commit()
                return redirect('/')
        else:
            content='이미 회원가입한 ID 입니다.'
    return render_template('join.html',
                            menu=get_menu(),
                            content=content
    )

@app.route('/withdraw', methods=['GET','POST'])
def withdraw():
    content=''
    if request.method == "POST":
        cur=db.cursor()
        cur.execute(f"""
            select name from author where name='{request.form['id']}'
        """)
        user=cur.fetchone()
        if user is None:
            content='가입한 id 가 아닙니다.'
        else:
            cur=db.cursor()
            cur.execute(f"""
                delete from author where name='{request.form['id']}'
            """)
            db.commit()
            return redirect('/')

    return render_template('withdraw.html',
                        menu=get_menu(),
                        content=content)

app.run(port=8000)