from flask import Flask,request,render_template,g,redirect,url_for
import sqlite3
import os 

app=Flask(__name__)
BASE_DIR=os.path.dirname(os.path.abspath(__file__)) #finds project directory location
DATABASE=os.path.join(BASE_DIR,'blog.db')
def get_db(): #when ever this fuc calls it creates a new connection.
    if 'db' not in g:
        g.db=sqlite3.connect(DATABASE) #creates a db connection
        g.db.row_factory=sqlite3.Row #return the data in dictionary format
        return g.db

@app.teardown_appcontext
def close_db(exception=None):
    db=g.pop('db',None)#checking if db connection is open 
    if db is not None: #if db connection is open 
        db.close() #closing the db connection

#database scheme creation
def init_db():
    db=get_db()#opens a new connection
    db.executescript('''
    create table if not exists post(post_id integer primary key autoincrement,title text not null,author text not null,content longtext not null
    );
    create table if not exists comment_for_post(comment_id integer  primary key autoincrement,postid int unsigned,author text not null,comment_text longtext,foreign key(postid) references post(post_id) on delete cascade); ''')
    db.commit()

@app.route('/',methods=['GET'])
def home():
    return render_template('index.html')
@app.route('/index',methods=['GET'])
def index():
    db=get_db()
    posts=db.execute('select post.* ,(select count(*) from comment_for_post where comment_for_post.postid=post.post_id) as comment_count from post').fetchall()
    return render_template('index.html',posts=posts)
@app.route('/create_post',methods=['GET','POST'])
def create_post():
    if request.method=='POST':
        print(request.form)
        title=request.form['title']
        author=request.form['author']
        content=request.form['body']
        db=get_db()
        cursor=db.execute('insert into post(title,author,content) values(?,?,?)',(title,author,content),)
        db.commit()
        return redirect(url_for('post_details',postid=cursor.lastrowid))

    return render_template('create_post.html')
@app.route('/post_details/<int:postid>',methods=['GET','POST'])
def post_details(postid):
    db = get_db()
    if request.method == 'POST':
        author = request.form.get('author', '').strip()
        body = request.form.get('body', '').strip()

        if not author or not body:
            return redirect(url_for('post_detail', postid=postid))

        db.execute(
            'INSERT INTO comment_for_post (postid, author, comment_text) VALUES (?, ?, ?)',
            (postid, author, body),
        )
        db.commit()
        return redirect(url_for('post_details', postid=postid))

    post = db.execute('SELECT * FROM post WHERE post_id = ?', (postid,)).fetchone()
    if post is None:
        return 'Post not found', 404

    comments = db.execute(
        'SELECT * FROM comment_for_post WHERE postid = ? ', (postid,)
    ).fetchall()

    return render_template('post_details.html', post=post, comments=comments)

@app.route('/post/<int:post_id>/delete', methods=['POST'])
def delete_post(post_id):
    db = get_db()
    db.execute('DELETE FROM comment WHERE postid = ?', (post_id,))
    db.execute('DELETE FROM post WHERE post_id = ?', (post_id,))
    db.commit()
    return redirect(url_for('index'))
@app.route('/dummy')
def dummy():
    return render_template('dummy.html')
with app.app_context():
    init_db()
app.run()



































