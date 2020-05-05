from flask import Flask, render_template

app = Flask(__name__,
            static_folder='static',
            template_folder='template')

app.config['ENV']='development'
app.config['DEBUG']=True

@app.route('/')
def index():
    content='login 해주세요.'

    return render_template('template.html',
                            content=content)

app.run(port=8000)