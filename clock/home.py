from flask import Blueprint, render_template, request, url_for, redirect, flash, session, g, send_file
from datetime import datetime, timedelta
from gtts import gTTS
from clock.auth import login_required

from werkzeug.security import generate_password_hash, check_password_hash

from .models import User, Employee, RegisterDetail
from clock import db

import base64, os, pygame, time, shutil

bp = Blueprint('home', __name__)

directory_fotos = 'capturas'

os.makedirs(directory_fotos, exist_ok=True)

# ------------------------------------------------------------------------------
error_password = 'La contraseña es incorrecta.'
empresas = ["VW Partes", "Repasa", "Autoluz"]
departamentos = ["Administración", "Sistemas", "Contabilidad", "Recepción", 
                 "Marketing", "Bodega", "Mantenimiento", "Mensajeros", "Pilostos",
                 "Gerencia", "Ventas", "Taller"]

# función para actualizar registros
def updateregister(registerexist, time, fieldname):
    registerexist = registerexist
    db.session.query(RegisterDetail).filter_by(id=registerexist).update({fieldname:str(time)})
    db.session.commit()
    
    return True

# función para enviar aletas de texto a mensaje con voz

def texttospeech(employee, message_type):
    language = 'es'  # Cambia esto según el idioma de tu texto
    
    if employee == None:
        message = f"El usuario no existe."
    else:
        if message_type == 'success':
            message = f'Asistencia Registrada {employee.name}.'
        elif message_type == 'mensaje_error_contrasena':
            message = f"{employee.name} Tu contraseña es incorrecta."
    
    # Crear el archivo de audio con gTTS y guardarlo temporalmente
    tts = gTTS(message, lang=language)
    
    # Ruta de la carpta a eliminar
    audio_folder = 'clock/static/audio'

    # Eliminación de la carpeta y su contenido
    shutil.rmtree(audio_folder)

    # Creación de una nueva carpeta vacía en su lugar
    os.makedirs(audio_folder)
    
    timestamp = str(int(time.time()))
    file = 'clock/static/audio/temp_audio' + timestamp + '.mp3'
    tts.save(file)

    # Inicializar pygame y reproducir el audio desde el archivo temporal
    pygame.mixer.init()
    pygame.mixer.music.load(file)
    # pygame.mixer.music.play()

    # # Esperar hasta que se complete la reproducción del audio
    # while pygame.mixer.music.get_busy():
    #     continue

    # # Eliminar el archivo temporal después de reproducirlo
    # os.remove('clock/static/audio/temp_audio.mp3')
    
    return file

# función para verificar el tipo de registro
def registertype(employee_id, register_date):
    employee_id = employee_id
    register_date = register_date
    registerexist = RegisterDetail.query.filter_by(employee_id=employee_id, register_date=register_date).all()
    print(len(registerexist))
    if len(registerexist) == 0:
        print('Hora Entrada')
        register_type=1
        registerexist = None
        return register_type, registerexist
    else:
        for register in registerexist:
            if register.lunch_start == None:
                print('Inicio Almuerzo')
                register_type = 2
                return register_type, register.id
            elif register.lunch_end == None:
                print('Fin Almuerzo')
                register_type = 3
                return register_type, register.id
            elif register.out_hour == None:
                print('Hora Salida')
                register_type = 4
                return register_type, register.id                
        register_type = None
        register_id = None
        return register_type, register_id 

# función para obtener todos los datos de fecha del registro    
def dataofdate():
    datetime_now = datetime.today()
    date_now = datetime_now.date()
    time = datetime_now.time()
    weekday = datetime_now.weekday()
    days = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
    name_day = days[weekday]
    
    return datetime_now, date_now, time, weekday, name_day

# función para enviar mensaje de registro exitoso.
def sendsuccess(employee):
    employee = employee             
    message_type = 'success'
    ruta_audio = texttospeech(employee, message_type)
    success = f'Asistencia Registrada {employee.name}.'
    flash(success)  # Especifica la ruta del archivo de audio
    return ruta_audio

# función para enviar mensaje de error.
def senderror(employee):
    message_type = 'mensaje_error_contrasena'
    ruta_audio = texttospeech(employee, message_type)
    flash(error_password)
    return ruta_audio
    
# ------------------------------------------------------------------------------

@bp.route('/', methods=('GET', 'POST'))
@bp.route('/home', methods=('GET', 'POST'))
def home():
    message_type = ''
    error = 'El usuario no existe.'
    file = None
    ruta_audio = None
    if request.method == 'POST':
        code = request.form['code']
        password = request.form['password']
        
        employee = Employee.query.filter_by(code=code).first()

        #Validar datos de empleado
        if employee == None:
            message_type = 'None'
            file = texttospeech(employee, message_type)
            ruta_audio = file.replace('clock/', '')
            flash(error)
        else:
            if employee.password == password:
                datetime_now, date_now, time, weekday, name_day = dataofdate()                
                typeregister, registerexist = registertype(employee.id, date_now)
                if typeregister == 1:
                    register = RegisterDetail(employee.id, datetime_now, date_now, str(time), None, None, None, weekday, name_day)
                    db.session.add(register)
                    db.session.commit()                    
                    file = sendsuccess(employee)
                    ruta_audio = file.replace('clock/', '')
                    return render_template('/home.html', ruta_audio=ruta_audio)                    
                elif typeregister == 2:
                    updateregister(registerexist, time, 'lunch_start')
                    file = sendsuccess(employee)
                    ruta_audio = file.replace('clock/', '')
                    return render_template('/home.html', ruta_audio=ruta_audio)                
                elif typeregister == 3:
                    updateregister(registerexist, time, 'lunch_end')
                    file = sendsuccess(employee)
                    ruta_audio = file.replace('clock/', '')
                    return render_template('/home.html', ruta_audio=ruta_audio)                   
                elif typeregister == 4:
                    updateregister(registerexist, time, 'out_hour')                    
                    file = sendsuccess(employee)
                    ruta_audio = file.replace('clock/', '')
                    return render_template('/home.html', ruta_audio=ruta_audio)            
                else:
                    print('registros completas')
            else:
                print('contrasena incorrecta')
                file = senderror(employee)
                ruta_audio = file.replace('clock/', '')
                return render_template('/home.html', ruta_audio=ruta_audio) 
                
        print(ruta_audio)
        
        
    return render_template('/home.html', ruta_audio=ruta_audio)

@bp.route('/capture', methods=('GET', 'POST'))
def capture():
    image_data = request.json['image_data']
    # Decodificar la imagen desde base64 a bytes
    image_bytes = base64.b64decode(image_data.split(',')[1])
    # Guardar la imagen en el servidor
    image_path = os.path.join(directory_fotos, 'captured_image.png')
    with open(image_path, 'wb') as f:
        f.write(image_bytes)
    return 'Image received'

@bp.route('/employees')
@login_required
def employees():
    employees = Employee.query.all()
    return render_template('employees.html', employees =  employees)

@bp.route('/addemployee', methods=('GET', 'POST'))
@login_required
def addemployee():
    if request.method == 'POST':  
        code = request.form['code']
        name = request.form['name']
        password = request.form['password']
        departament = request.form['departament']
        company = request.form['company']

        error = None
        success = None

        employee = Employee(name, code, password, departament, company, 1)
        
        code = Employee.query.filter_by(code=code).first()
        if code == None:
            db.session.add(employee)
            db.session.commit()
            return redirect('/employees')
            # flash(success)
        else:
            print('error')

    return render_template('addemployee.html', empresas=empresas, departamentos=departamentos)

def get_employee(id):
    employee = Employee.query.get_or_404(id)
    return employee

@bp.route('/employee_update/<int:id>', methods=('GET', 'POST'))
@login_required
def employee_update(id):
    
    employee = get_employee(id)

    if request.method == 'POST':  
        employee.name = request.form['name']
        employee.code = request.form['code']
        employee.password = request.form['password']
        employee.departament = request.form['departament']
        employee.company = request.form['company']
        # user.state = True if request.form.get('state') == 'on' else False

        db.session.commit()
        return redirect('/employees')

    return render_template('employee_update.html', employee = employee, empresas=empresas, departamentos=departamentos)


@bp.route('/delete_employee/<int:id>', methods=('GET', 'POST'))
@login_required
def delete_employee(id):
    employee = get_employee(id)
    db.session.delete(employee)
    db.session.commit()
    return redirect('/employees')