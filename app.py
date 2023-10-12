

import sqlite3

from flask import Flask, render_template, flash, request, redirect, url_for, send_from_directory, session, g
from flask_login import LoginManager, login_required, login_user, logout_user, current_user
import os
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from FDataBase import FDataBase
from UserLogin import UserLogin
from image_processor import IProcessor
from remove_bg_module import remove_bg
from threading import Thread
from flask_thumbnails import Thumbnail


UPLOAD_FOLDER = 'static/data/'
ALLOWED_EXTENSIONS = {"jpg", "png", "jpeg", "heic"}
DATABASE = 'db.db'
SECRET_KEY ='192b9bdd22ab9ed4d12e236c78afcb9a393ec15f71bbf5dc987d54727823bcbf'




test_img = "dog_avatar_1.jpg"

app = Flask(__name__)

thumb = Thumbnail(app)

app.config.from_object(__name__)
app.config.update(dict(DATABASE=os.path.join(app.root_path,'db.db')))
app.config['THUMBNAIL_MEDIA_ROOT'] = '/templates/'
app.config['THUMBNAIL_MEDIA_URL'] = '/data/'


login_manager = LoginManager(app)

# устанавлиаем содержимое navbar
menu = [
    {"title": "FlaskyPillow", "url": "/"},
    {"title": "Редактор", "url": "/upload"},
    {"title": "Галерея", "url": "/gallery"},
    {"title": "Инфо", "url": "/info"},

]
# иконки и ссылки для contacts(info))
cont = [{"icon": "github.png", "url": "https://github.com/dustlancer", "class":"gh"},
            {"icon": "vk.png", "url": "https://vk.com/dustlancer", "class":"vk"},
            {"icon": "instagram.png", "url": "https://instagram.com/dustlancer", "class":"ig"}
]


# выполняется перед каждым запросом
dbase = None
@app.before_request
def before_request():
    '''Установление соединения с БД перед выполнением запроса'''
    global dbase
    db = get_db()
    dbase = FDataBase(db)
    #dbase.fetchPicsFromFolder()


#
@login_manager.user_loader
def load_user(user_id):
    print("load_user")
    return UserLogin().fromDB(user_id,dbase)        




# Проверяем, имеет ли файл рпзрешённое расширение
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.',1)[1].lower() in ALLOWED_EXTENSIONS


# сохраняем картинку из запроса в папку пользователя
def get_image_from_user(request, user_name):   
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        flash('No selected file', "danger")
        return redirect(request.url)
    if not allowed_file(file.filename):
        flash("Bad format", "danger")
        return redirect(request.url)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filename = dbase.addPicture(filename, current_user.get_name(), current_user.get_id())[1]
        print(filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], f"{user_name}/", filename))
        flash("Successfuly uploaded", "success")


        session['current_image'] = filename





# отрисовка index
@app.route("/",  methods=['GET'])
def index():
    if 'counter' in session:
        session['counter'] = session.get('counter') + 1
    else: session['counter'] = 1

    users = dbase.getUsers()
    if current_user.get_id():
        print(current_user)
        cu = current_user.get_id()
        name = dbase.getUser(cu)['name']
    else: 
        cu = "-1"; name = "None"
    


    return render_template("index.html", menu=menu, f = users,user_id=cu, n = name, title="FlaskyPillow")



@app.route("/upload",  methods=['GET','POST'])
@login_required
def upload():
    if 'current_image' in session:
        if session['current_image'] != 'noCurrentImage':
            return redirect(url_for('editor'))
    if request.method =='POST':  
        get_image_from_user(request, current_user.get_name())
        #session['display_loader'] = 5000
        return redirect(url_for('editor'))
        
        
        
            
    return render_template("upload.html", menu=menu, title='Редактор')


@app.route("/abort_current_image")
def abort_current_image():
    delete_image(current_user.get_name(), session['current_image'])
    session['current_image'] = 'noCurrentImage'
    return redirect(url_for('upload'))

# Загрузка нового изображения для редактирования игнорируя текущее
@app.route("/upload_new_image")
def upload_new_image():
    if 'current_image' in session:
        session['current_image'] = 'noCurrentImage'
    return redirect(url_for('upload'))


#save to gallery
@app.route("/save_current_image")
def save_current_image():
    print('SCI route')
    if 'current_image' in session:
        session['current_image'] = 'noCurrentImage'
    return redirect(url_for('gallery'))
        

@app.route("/gallery")
@login_required
def gallery():
    dbase.fetchPicsFromFolder()
    print(dbase.getGallery(current_user.get_name()))
    gallery = dbase.getGallery(current_user.get_name())
    if not gallery:
        return render_template("empty_gallery.html", menu=menu)
    for i in dbase.getGallery(current_user.get_name()):
        print(i['file_name'] + ' ' + i['user_name']) 
    
    return render_template("gallery.html", menu=menu, gallery=gallery, title='📷Галерея🖼')


@app.route("/open_in_editor/<path:filename>")
def open_in_editor(filename):
    session['current_image'] = filename
    return redirect(url_for('editor'))



@app.route('/download/<path:filename>')
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename, as_attachment=True)


@app.route("/delete_from_gallery/<filename>")
def delete_from_gallery(filename):
    us = current_user.get_name()

    delete_image(us, filename)
    flash("Image successfuly deleted!", "success")
    return redirect(url_for('gallery'))



@app.route("/editor", methods=['GET','POST'])
@login_required
def editor():
    if 'display_loader' in session: 
        dl = session['display_loader']
    else: dl = None
    
    session['display_loader'] = None
    
    if 'current_image' not in session:
        return redirect(url_for('upload'))

    if session['current_image'] == 'noCurrentImage':
        return redirect(url_for('upload'))
    img = session['current_image']
    user = current_user.get_name()




    return render_template('editor.html', img=img, user=user, menu=menu, display_loader=dl, title='✏️Редактор✂️')









@app.route("/apply_effect/<effect_name>", methods=['POST','GET'])
def apply_effect(effect_name):
    img = session['current_image']
    user = current_user.get_name()
    editor = IProcessor(user, img)
            
    
    if effect_name=='add_text':
        editor.add_text(request.form['input_text'])

    if effect_name=='black_n_white':
        editor.black_n_white()
    
    if effect_name=="remove_bg":
        print("flag: ", editor.needsRotate())
        nr = editor.needsRotate()
        session['current_image'] = remove_bg(img,user)
        img = session['current_image']
        editor = IProcessor(user, img)
        if nr:
            editor.rotate()
  
 


    #os.chdir("../../..")
    return redirect(url_for('editor'))

    

def delete_image(user, img):
    os.chdir(f"static/data/{user}")
    if os.path.exists(img):
        os.remove(img)
    else:
        print("Image '" + img + "' not found")
    os.chdir("../../..")
    print(os.getcwd())


@app.route("/info")
def info():
    return render_template("info.html", menu=menu, contacts=cont, title='ℹ️Инфо📨')


@app.route("/login", methods=['POST','GET'])
def login():

    if request.method == 'POST':
        user = dbase.getUserByName(request.form['name'])
        if user and check_password_hash(user['password'], request.form['password']):
            userlogin = UserLogin().create(user)
            rm = True if request.form.get('remainme') else False
            login_user(userlogin, remember=rm)
            return redirect(url_for('index'))
        flash("Wrong name or password!", "danger")
    

    return render_template("login.html", menu=menu)


@app.route("/register", methods=['POST','GET'])
def register():
    if request.method == 'POST':
        if len(request.form['name']) > 4 and len(request.form['password']) > 4 \
            and request.form['password'] == request.form['repeat_password']:
            hash = generate_password_hash(request.form['password'])
            res = dbase.addUser(request.form['name'], hash)
            if res:
                create_user_folder(request.form['name'])
                flash("Successfully registered!", "success")
                return redirect(url_for('login'))
            else:
                flash('Database error!', 'error')
        else: flash("Incorrect form input!", "danger")


    return render_template("register.html", menu=menu)


@app.route("/logout")
def logout():
    logout_user()
    flash("Logged out!", "success")
    return redirect(url_for('login'))

@app.route("/create_db")
def cdb():
    create_db()
    return "ok"
    


@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html", menu=menu), 404


@app.errorhandler(401)
def no_auth(e):
    return redirect('/login')



def connect_db():  # Подключение к БД
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn


def create_db():
    """Вспомогптельная функция для создания таблиц БД"""
    db = connect_db()
    with app.open_resource('sq_db.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()
    db.close()


def get_db():
    """Соединение с БД, если оно ещё не установлено""" 
    if not hasattr(g, 'link_db'):
        g.link_db = connect_db()
    return g.link_db


def create_user_folder(name):
    try:
        os.chdir("static/data")
        os.mkdir(f"{name}")
        os.chdir("../..")
    except: print("Не удалось создать папку пользователя")





@app.teardown_appcontext
def close_db(error):
    '''Закрываем соединение с БД, если оно было установлено'''
    if hasattr(g, 'link_db'):
        g.link_db.close()




if __name__ == '__main__':
    
    
    app.run(debug=True, port=5001)

    
    #app.run(debug=True)
    
    
