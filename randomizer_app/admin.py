from flask import Blueprint, request, render_template, Flask, session as cookie, redirect, url_for, make_response, send_from_directory, send_file
from .models import User, Tickets, Raffles, Members
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
import shortuuid
import uuid
import random
import datetime
import os
import json
import requests
import shutil
from .avatar import generate_avatar
from sqlalchemy import desc
from time import gmtime, strftime
from .main import raffle_delay, checkRaffle
import atexit
from apscheduler.schedulers.background import BackgroundScheduler
import string


app = Flask(__name__)
admin = Blueprint('admin', __name__)
login_manager = LoginManager()
login_manager.init_app(app)

@admin.route('/admin', methods=('GET', 'POST'))
def admin_main():
    if request.method == 'POST':
        if request.form['username'] is None or request.form['password'] is None:
            return redirect(url_for('admin.add_tickets'))
        else:
            username = request.form['username']
            password = request.form['password']
            #remember = True if request.form.get('remember') else False
            remember = False
            user = User.query.filter_by(username=username).first()
            if not user or user.password != password:
                error = "Ошибка авторизации, попробуйте снова"
                return render_template('login.html', error=error)
            login_user(user, remember=remember)
            return redirect(url_for('admin.add_tickets'))
    else:
        if db.session.query(User.id).filter_by(username='admin').scalar() is None:
            print("No users. Creating new")
            admin = User(username="admin", password="admin")
            db.session.add(admin)
            db.session.commit()
        if current_user.is_authenticated:
            return redirect(url_for('admin.add_tickets'))
        else:
            return render_template('login.html')
        
        

@admin.route('/admin/add_tickets/', methods=['GET', 'POST'])
@login_required
def add_tickets():  # Добавление купонов
    # добавить проверку имен на уникальность, и анимацию загрузки
    context = {
    "page": "Настройки - добавление купонов"
    }
    if request.method == "POST":
        if request.form['ticket_number'] != "" and request.form['ticket_owner2'] != "":
            cookie['active_2'] = 'active'
            #print("ticket_number is set!")
            if request.form['ticket_number'].isdigit() and request.form['raffle_id2'].isdigit():
                #print("ticket_number is digit!")
                
                if Raffles.query.filter_by(ended=False).filter_by(id=int(request.form['raffle_id2'])).first() is not None:
                    raffle_id = int(request.form['raffle_id2'])
                    raffle = Raffles.query.filter_by(id=raffle_id).first()
                    raffle_link = raffle.link
                    ticket_owner = request.form['ticket_owner2']
                    if Members.query.filter_by(member_name=ticket_owner).first() is None:
                        try:
                            member_link = shortuuid.uuid()
                            #print("ticket_link = {}".format(member_link))
                            member_obj = Members(member_name=ticket_owner, member_link=member_link)
                            db.session.add(member_obj)
                            db.session.commit()
                            #ticket_link = request.host + "/activate/" + member_link
                        except Exception as e:
                            print("Exception occured:\n"+str(e))
                            cookie['error'] = "Ошибка добавления пользователя в базу данных"
                            return redirect(url_for('admin.add_tickets'))
                    else:
                        member_obj = Members.query.filter_by(member_name=ticket_owner).first()
                        member_link = member_obj.member_link
                        #ticket_link = request.host + "/activate/" + member_link
                    ticket_link = raffle_link
                    date = datetime.datetime.now().strftime("%Y-%m-%d")
                    invalid_chars = string.punctuation
                    ticket_owner = ''.join(c for c in ticket_owner if c not in invalid_chars)
                    filename = ticket_owner.replace(" ", "_")+"_"+date+".txt"
                    files_folder = os.path.join(app.root_path, "tmp")
                    filedir = os.path.join(files_folder, filename)
                    f = open(filedir, "w+")

                    for index in range(int(request.form['ticket_number'])):
                        ticket_hash = uuid.uuid4().hex
                        #print("ticket_hash = {}".format(str(ticket_hash)))
                        owner_id = member_obj.id
                        ticket_obj = Tickets(
                            ticket_hash=ticket_hash, 
                            owner_id=owner_id, 
                            raffle_id=raffle_id, 
                            activated=True #Не забыть выставить в False
                        ) 
                        db.session.add(ticket_obj)
                        f.write(ticket_hash+"\n")

                    f.close()
                    try:
                        db.session.commit()
                    except Exception as e:
                        print("Exception occured:\n"+str(e))
                        cookie['error'] = "Ошибка добавления купона в базу данных"
                        return redirect(url_for('admin.add_tickets'))
                    avatar_dir = os.path.join(app.root_path, "static")
                    avatar_dir = os.path.join(avatar_dir, 'images', member_link+'.png')
                    if os.path.exists(avatar_dir) != True:
                        generate_avatar(420, 12, avatar_dir)
                    cookie['raffle_link'] = "%sraffle/%s" % (request.host_url, raffle_link)
                    cookie['ticket_link'] = "%sactivate/%s" % (request.host_url, ticket_link)
                    cookie['filename'] = filename
                    cookie['result'] = "Купоны добавлены успешно!"
                    cookie['avatar'] = url_for('static', filename='images/'+member_link+'.png')
                    return redirect(url_for('admin.add_tickets'))
                else:
                    cookie["error"] = "Розыгрыш с таким идентификатором не найден"
                    return redirect(url_for('admin.add_tickets'))
            else:
                cookie["error"] = "Количество купонов и идентификатор розыгрыша должны быть числом"
                return redirect(url_for('admin.add_tickets'))
        elif request.form['ticket_owner1'] != "":
            cookie['active_1'] = 'active'
            if request.form['raffle_id1'].isdigit():
                if Raffles.query.filter_by(ended=False).filter_by(id=int(request.form['raffle_id1'])).first() is not None:
                    raffle_id = int(request.form['raffle_id1'])
                    raffle = Raffles.query.filter_by(id=raffle_id).first()
                    raffle_link = raffle.link
                    ticket_owner = request.form['ticket_owner1']
                    if Members.query.filter_by(member_name=ticket_owner).first() is None:
                        try:
                            member_link = shortuuid.uuid()
                            member_obj = Members(member_name=ticket_owner, member_link=member_link)
                            db.session.add(member_obj)
                            db.session.commit()
                            #ticket_link = request.host + "/activate/" + member_link
                        except Exception as e:
                            print("Exception occured:\n"+str(e))
                            cookie['error'] = "Ошибка добавления пользователя в базу данных"
                            return redirect(url_for('admin.add_tickets'))
                    else:
                        member_obj = Members.query.filter_by(member_name=ticket_owner).first()
                        member_link = member_obj.member_link
                        #ticket_link = request.host + "/activate/" + member_link
                    ticket_link = "/activate/%s" % (raffle_link)
                    try:
                        ticket_hash = uuid.uuid4().hex
                        owner_id = member_obj.id
                        ticket_obj = Tickets(ticket_hash=ticket_hash, owner_id=owner_id, raffle_id=raffle_id, activated=False)
                        db.session.add(ticket_obj)
                        db.session.commit()
                    except Exception as e:
                        print("Exception occured:\n"+str(e))
                        cookie['error'] = "Ошибка добавления в базу данных"
                        return redirect(url_for('admin.add_tickets'))
                    avatar_dir = os.path.join(app.root_path, "static")
                    avatar_dir = os.path.join(avatar_dir, 'images', member_link+'.png')
                    if os.path.exists(avatar_dir) != True:
                        generate_avatar(420, 12, avatar_dir)
                    cookie['raffle_link'] = raffle.link
                    cookie['ticket_link'] = ticket_link
                    cookie['ticket_hash'] = ticket_hash
                    cookie['result'] = "Купон добавлен успешно!"
                    cookie['avatar'] = url_for('static', filename='images/'+member_link+'.png')
                    return redirect(url_for('admin.add_tickets'))
                else:
                    cookie["error"] = "Розыгрыш с таким идентификатором не найден"
                    return redirect(url_for('admin.add_tickets'))
            else:
                cookie["error"] = "Идентификатор розыгрыша должен быть числом"
                return redirect(url_for('admin.add_tickets'))
    else:
        if 'active_3' in cookie and cookie['active_3'] != "":
            context['active_3'] = cookie['active_3']
            cookie['active_3'] = ""
        else:
            if 'active_2' in cookie and cookie['active_2'] != "":
                context['active_2'] = cookie['active_2']
                cookie['active_2'] = ""
            else:
                context['active_1'] = 'active'
                cookie['active_1'] = ""
        if 'error' in cookie and cookie['error'] != "":
            context['error'] = cookie['error']
            cookie['error'] = ""
            #resp.set_cookie('error', '', expires=0)
        if 'result' in cookie and cookie['result'] != "":
            context['result'] = cookie['result']
            cookie['result'] = ""
            #resp.set_cookie('result', '', expires=0)
        if 'ticket_hash' in cookie and cookie['ticket_hash'] != "":
            context['ticket_hash'] = cookie['ticket_hash']
            cookie['ticket_hash'] = ""
            #resp.set_cookie('ticket_hash', '', expires=0)
        if 'ticket_link' in cookie and cookie['ticket_link'] != "":
            context['ticket_link'] = cookie['ticket_link']
            cookie['ticket_link'] = ""
            #resp.set_cookie('ticket_link', '', expires=0)
        if 'avatar' in cookie and cookie['avatar'] != "":
            context['avatar'] = cookie['avatar']
            cookie['avatar'] = ""
        if 'filename' in cookie and cookie['filename'] != "":
            context['filename'] = cookie['filename']
            cookie['filename'] = ""
        if 'raffle_link' in cookie and cookie['raffle_link'] != "":
            context['raffle_link'] = cookie['raffle_link']
            cookie['raffle_link'] = ""
        context['tickets'] = getTickets()
        context['nearest_raffle'] = getNearestRaffle()
        resp = make_response(render_template('tickets.html', **context))
        return resp


@admin.route('/admin/add_raffle', methods=['GET', 'POST'])
@login_required
def add_raffle():   # Добавление розыгрышей
    context = {
    "page": "Настройки - добавление розыгрышей"
    }

    def getRaffles():
        raffles = Raffles.query.order_by(Raffles.date).all()
        result = []
        for raffle in raffles:
            value = {}
            value['id'] = raffle.id
            value['date'] = str(raffle.date)[:-3]
            value['created'] = str(raffle.created_on)[:-3]
            value['members'] = Tickets.query.filter(Tickets.raffle_id == raffle.id).filter(Tickets.activated == True).count()
            value['link'] = raffle.link
            if raffle.winners is not None:
                value['chance'] = len(json.loads(raffle.winners))
            else:
                value['chance'] = raffle.chance
            value['ended'] = raffle.ended
            result.append(value)
        return result

    if request.method == "POST":
        if request.form['raffle_chance'] != "" and request.form['raffle_date'] != "":
            cookie['active_1'] = 'active'
            #print("raffle_chance is set")
            if request.form['raffle_chance'].isdigit():
                raffle_chance = int(request.form['raffle_chance'])
                #print("raffle_chance is valid")
                raffle_date = request.form['raffle_date']
                raffle_desc = request.form['raffle_desc']
                #print(raffle_date)
                date_processing = raffle_date.replace('T', '-').replace(':', '-').split('-')
                date_processing = [int(v) for v in date_processing]
                date_out = datetime.datetime(*date_processing)
                if datetime.datetime.now() > date_out:
                    print("raffle_date is invalid")
                    cookie['error'] = "Дата розыгрыша не должна быть прошедшей"
                    return redirect(url_for('admin.add_raffle'))

                # Проверка, если розыгрыш пересекается с другими во времени
                new_start = date_out
                new_end = date_out + datetime.timedelta(seconds=raffle_chance * raffle_delay)
                for comp_raffle in Raffles.query.all():
                    start = comp_raffle.date
                    end = comp_raffle.date + datetime.timedelta(seconds=comp_raffle.chance * raffle_delay)
                    if (new_end > start > new_start):
                        cookie['error'] = "Даты розыгрышей пересекаются"
                        return redirect(url_for('admin.add_raffle'))
                    if (new_end > end > new_start):
                        cookie['error'] = "Даты розыгрышей пересекаются"
                        return redirect(url_for('admin.add_raffle'))

                try:
                    raffle_link = shortuuid.uuid()
                    raffle_obj = Raffles(chance=raffle_chance, date=date_out, description=raffle_desc, link=raffle_link, ended=0)
                    db.session.add(raffle_obj)
                    db.session.commit()
                except Exception as e:
                    print("Exception occured:\n"+str(e))
                    cookie['error'] = "Ошибка добавления в базу данных"
                    return redirect(url_for('admin.add_raffle')) 
                sched = BackgroundScheduler()
                sched.add_job(checkRafflesPast, 'date', run_date=date_out+datetime.timedelta(seconds=raffle_chance*raffle_delay+raffle_delay+1))  
                #sched.start()    
                cookie['result'] = "Розыгрыш добавлен успешно!"       
                return redirect(url_for('admin.add_raffle'))
            else:
                cookie["error"] = "Введен некорректный шанс, попробуйте снова"
                return redirect(url_for('admin.add_raffle'))
            
        else:
            return redirect(url_for('admin.add_raffle'))
    else:
        if 'active_3' in cookie and cookie['active_3'] != "":
            context['active_3'] = cookie['active_3']
            cookie['active_3'] = ""
        else:
            if 'active_2' in cookie and cookie['active_2'] != "":
                context['active_2'] = cookie['active_2']
                cookie['active_2'] = ""
            else:
                context['active_1'] = 'active'
                cookie['active_1'] = ""
        if 'error' in cookie and cookie['error'] != "":
            context['error'] = cookie['error']
            cookie['error'] = ""
        if 'result' in cookie and cookie['result'] != "":
            context['result'] = cookie['result']
            cookie['result'] = ""
        context['raffles'] = getRaffles()
        context['nearest_raffle'] = getNearestRaffle()
        return render_template('raffles.html', **context)

@admin.route('/admin/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    context = {
        "page": "Настройки - смена пароля"
    }
    if request.method == 'POST':
        if request.form['old_password'] != "" and request.form['new_password'] != "":
            if request.form['old_password'] == current_user.password:
                if request.form['new_password'] == request.form['check_password']:
                    user = User.query.filter_by(username=current_user.username).first()
                    user.password = request.form['new_password']
                    try:
                        db.session.commit()
                    except Exception as e:
                        print("Exception occured:\n"+str(e))
                        cookie['error'] = "Ошибка базы данных"
                        return redirect(url_for('admin.change_password'))
                    cookie['result'] = "Пароль успешно сменен!"
                    return redirect(url_for('admin.change_password'))
                else:
                    cookie['error'] = "Пароли не совпадают"
                    return redirect(url_for('admin.change_password'))
            else:
                cookie['error'] = "Неверный старый пароль"
                return redirect(url_for('admin.change_password'))
        else:
            return redirect(url_for('admin.change_password'))
    else:
        if 'error' in cookie and cookie['error'] != "":
            context['error'] = cookie['error']
            cookie['error'] = ""
        if 'result' in cookie and cookie['result'] != "":
            context['result'] = cookie['result']
            cookie['result'] = ""
        context['nearest_raffle'] = getNearestRaffle()
        return render_template('change_password.html', **context)

@admin.route('/raffle_edit/<raffle_id>', methods=['GET', 'POST'])
@login_required
def raffle_edit(raffle_id):
    context = {
        "page": "Настройки - настройка розыгрышей"
    }
    cookie['active_2'] = 'active'
    if Raffles.query.filter_by(id=raffle_id).first() is None:
        cookie['error'] = 'Несуществующий розыгрыш'
        return redirect(url_for('admin.add_raffle'))
    if request.method == "POST":
        if request.form['raffle_chance'] != "" and request.form['raffle_date'] != "":
            #cookie['active_1'] = 'active'
            if request.form['raffle_chance'].isdigit():
                raffle_chance = int(request.form['raffle_chance'])
                raffle_date = request.form['raffle_date']
                raffle_desc = request.form['raffle_desc']
                #print(raffle_date)
                date_processing = raffle_date.replace('T', '-').replace(':', '-').split('-')
                date_processing = [int(v) for v in date_processing]
                date_out = datetime.datetime(*date_processing)
                try:
                    raffle_obj = Raffles.query.filter_by(id=raffle_id).first()
                    raffle_obj.chance = raffle_chance
                    raffle_obj.date = date_out
                    raffle_obj.description = raffle_desc
                    db.session.commit()
                except Exception as e:
                    print("Exception occured:\n"+str(e))
                    cookie['error'] = "Ошибка базы данных"
                    return redirect(url_for('admin.raffle_edit', raffle_id=raffle_id))
                cookie['result'] = "Розыгрыш добавлен успешно!"       
                return redirect(url_for('admin.add_raffle'))
            else:
                cookie["error"] = "Введен некорректный шанс, попробуйте снова"
                return redirect(url_for('admin.raffle_edit', raffle_id=raffle_id))
        else:
            return redirect(url_for('admin.raffle_edit', raffle_id=raffle_id))
    else:
        raffle = Raffles.query.filter_by(id=raffle_id).first()
        context['raffle_id'] = raffle_id
        context['raffle_chance'] = str(raffle.chance)
        context['raffle_desc'] = raffle.description
        context['raffle_date'] = str(raffle.date).replace(" ", "T")[:-3]
        context['tickets'] = getTickets(raffle_id)
        context['nearest_raffle'] = getNearestRaffle()
        return render_template('raffle_edit.html', **context)

@admin.route('/raffle_results/<raffle_id>', methods=['GET'])
@login_required
def raffle_results(raffle_id):
    context = {
        "page": "Настройки - просмотр результатов"
    }
    cookie['active_3'] = 'active'
    if Raffles.query.filter_by(id=raffle_id).first() is None:
        cookie['error'] = 'Несуществующий розыгрыш'
        return redirect(url_for('admin.add_raffle'))
    raffle = Raffles.query.filter_by(id=raffle_id).first()
    context['raffle_id'] = raffle_id
    context['raffle_desc'] = raffle.description
    context['raffle_date'] = str(raffle.date).replace(" ", "T")[:-3]
    if raffle.winners is not None:
        context['results'] = json.loads(raffle.winners)
        context['raffle_chance'] = len(json.loads(raffle.winners))
    else:
        context['raffle_chance'] = raffle.chance
    context['nearest_raffle'] = getNearestRaffle()
    return render_template('raffle_results.html', **context)

@admin.route('/delete_raffle/<raffle_id>')
@login_required
def delete_raffle(raffle_id):
    Raffles.query.filter_by(id=int(raffle_id)).delete()
    try:
        db.session.commit()
        cookie['result'] = "Розыгрыш успешно изменен"
        #cookie['active_3'] = 'active'
        return redirect(url_for('admin.add_raffle'))
        #return json.dumps({'success':True}), 200, {'ContentType':'application/json'} 
    except:
        cookie['error'] = "Ошибка базы данных"
        #cookie['active_3'] = 'active'
        return redirect(url_for('admin.add_raffle'))
        #return json.dumps({'success':False}), 500, {'ContentType':'application/json'} 

@admin.route('/delete_ticket/<ticket_id>')
@login_required
def delete_ticket(ticket_id):
    Tickets.query.filter_by(id=int(ticket_id)).delete()
    try:
        db.session.commit()
        return json.dumps({'success':True}), 200, {'ContentType':'application/json'} 
    except:
        return json.dumps({'success':False}), 500, {'ContentType':'application/json'} 

@admin.route('/download_file/<filename>')
@login_required
def download_file(filename):
    files_folder = os.path.join(app.root_path, "tmp")
    return send_file(os.path.join(files_folder, filename), as_attachment=True)
    #return send_from_directory(directory=files_folder, filename=filename)

@admin.route('/logout')
@login_required
def logout():
    logout_user()
    cookie.clear()
    return redirect(url_for('admin.admin_main'))    

def getTickets(raffle_id=None):
    if raffle_id is None:
        tickets = Tickets.query.all()
    else:
        tickets = Tickets.query.filter(Tickets.raffle_id == raffle_id).all()
        #raffle = Raffles.query.filter_by(raffle_id=raffle_id).first()
    result = []
    for ticket in tickets:
        value = {}
        value['id'] = ticket.id
        value['hash'] = ticket.ticket_hash
        if ticket.activated:
            value['activated'] = "Да"
        else:
            value['activated'] = "Нет"
        owner = Members.query.filter_by(id=ticket.owner_id).first()
        value['owner'] = owner.member_name
        value['created'] = ticket.created_on
        value['url'] = url_for('admin.delete_ticket', ticket_id=ticket.id)
        #if raffle_id is not None:
        #    value['raffle_link'] = raffle.link
        value['raffle_id'] = ticket.raffle_id
        raffle = Raffles.query.filter(Raffles.id == ticket.raffle_id).first()
        if raffle is not None:
            value['raffle_link'] = "/raffle/%s" % (raffle.link)
        else:
            value['raffle_link'] = ""
        result.append(value)
    return result

def getNearestRaffle():
    if Raffles.query.filter_by(ended=False).order_by(Raffles.date).first() is not None:
        return str(Raffles.query.filter_by(ended=False).order_by(Raffles.date).first().date).replace(" ", "T")[:-3]
    else:
        return "none"

# Проверка, есть ли пропущенные розыгрыши
# Если есть, симулируется выбор победителя
def checkRafflesPast():
    print("Происходит проверка розыгрыша")
    if Raffles.query.filter_by(ended=False).order_by(Raffles.date).first() is not None: # Проверка есть ли розыгрыши
        raffles = Raffles.query.filter_by(ended=False).order_by(Raffles.date).all()
        for raffle in raffles:
            if datetime.datetime.now() > raffle.date+datetime.timedelta(seconds=raffle.chance*raffle_delay+raffle_delay):
                # Розыгрыш пропущен, выбор победителей
                members = Members.query.all()
                avatars = []

                for member in members:
                    avatar_dir = os.path.join(app.root_path, "static")
                    avatar_dir = os.path.join(avatar_dir, 'images', member.member_link+'.png')
                    if os.path.exists(avatar_dir) != True:
                        generate_avatar(420, 12, avatar_dir)
                    if member.member_tickets is not None:
                        for ticket in member.member_tickets:
                            if ticket.activated:
                                avatar = {
                                    'id': member.id,
                                    'name': member.member_name,
                                    'image': 'static/images/'+member.member_link+'.png',
                                    'ticket': ticket.ticket_hash
                                }
                                avatars.append(avatar)
                
                # Симуляция розыгрыша
                checkRaffle(raffle, avatars)
                
