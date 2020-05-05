from flask import Flask, render_template
from flask import request, session, redirect
import pymysql

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

@app.route('/')
def index():
    content=''
    if 'owner' in session:
        owner=session['owner']['name']
    else:
        owner='login please'

    return render_template('template.html',
                            owner=owner,
                            content=content)

@app.route('/login', methods=['GET','POST'])
def login():
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
                select name, password from author
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
                            content=content)

@app.route('/logout')
def logout():
    session.pop('owner',None)
    return redirect('/')

app.run(port=8000)