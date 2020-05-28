from flask import Blueprint, request, render_template, Flask, session as cookie, redirect, url_for, make_response
from . import db
from .models import Tickets, Members, Raffles
from flask_login import LoginManager, login_required
import base64
from .avatar import generate_avatar
import os
import datetime
import random
from time import gmtime, strftime
import json


app = Flask(__name__)
main = Blueprint('main', __name__)
login_manager = LoginManager()
login_manager.init_app(app)

raffle_delay = 90

@main.route('/login', methods=('GET', 'POST'))
def index2():
    return render_template('index.html')
        
        

@main.route('/activate/<member_link>', methods=['POST', 'GET'])
def activate(member_link):
    if Members.query.filter_by(member_link=member_link).scalar() is not None:
        member = Members.query.filter_by(member_link=member_link).first()
        context = {
            "member_name": member.member_name
        }
        if request.method == 'POST':
            if request.form['ticket'] is not None and request.form['ticket'] != "":
                ticket_hash = request.form['ticket']
                for ticket in member.member_tickets:
                    if ticket.ticket_hash == ticket_hash:
                        if ticket.activated != True:
                            ticket.activated = True
                            try:
                                db.session.commit()
                            except Exception as e:
                                print("Exception occured: "+str(e))
                                cookie['error'] = "Ошибка базы данных"
                                return redirect(url_for('main.activate', member_link=member_link))
                            avatar_dir = os.path.join(app.root_path, "static")
                            avatar_dir = os.path.join(avatar_dir, 'images', member_link+'.png')
                            if os.path.exists(avatar_dir) != True:
                                generate_avatar(420, 12, avatar_dir)
                            cookie['avatar'] = url_for('static', filename='images/'+member_link+'.png')
                            cookie['result'] = "Купон успешно активирован!"
                            return redirect(url_for('main.activate', member_link=member_link))
                        else:
                           
                            avatar_dir = os.path.join(app.root_path, "static")
                            avatar_dir = os.path.join(avatar_dir, 'images', member_link+'.png')
                            if os.path.exists(avatar_dir) != True:
                                generate_avatar(420, 12, avatar_dir)
                            cookie['avatar'] = url_for('static', filename='images/'+member_link+'.png')
                            cookie['error'] = "Купон уже активирован"
                            return redirect(url_for('main.activate', member_link=member_link))
                cookie['error'] = "Купон не найден"
                return redirect(url_for('main.activate', member_link=member_link))
            else:
                cookie['error'] = "Введите купон!"
                return redirect(url_for('main.activate', member_link=member_link))
        else:
            tickets = []
            for ticket in member.member_tickets:
                tickets.append(ticket.ticket_hash)
            if 'error' in cookie and cookie['error'] != "":
                context['error'] = cookie['error']
                cookie['error'] = ""
            if 'result' in cookie and cookie['result'] != "":
                context['result'] = cookie['result']
                cookie['result'] = ""
            if 'avatar' in cookie and cookie['avatar'] != "":
                context['avatar'] = cookie['avatar']
                cookie['avatar'] = ""
            #for ticket in member.member_tickets:
            #    print(ticket.ticket_hash)
            context['member_link'] = member_link

            context['tickets'] = tickets
            return render_template('activate.html', **context)
    else:
        context = {
            "big_error": "Некорректный код участника. Проверьте ссылку и попробуйте снова"
        }
        return render_template('activate.html', **context)

@main.route('/')
def roulette():
    context = {}
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
                        'image': url_for('static', filename='images/'+member.member_link+'.png'),
                        'ticket': ticket.ticket_hash
                    }
                    avatars.append(avatar)
    # Наполнение ленты
    many_avatars = avatars+avatars
    many_avatars = many_avatars+many_avatars
    many_avatars = many_avatars+avatars
    if Raffles.query.filter_by(ended=False).order_by(Raffles.date).first() is not None: # Проверка есть ли розыгрыши
        
        raffle = Raffles.query.filter_by(ended=False).order_by(Raffles.date).first()
        # Проверка розыгрыша на актуальность
        raffle = checkRaffle(raffle, avatars)

        #print(raffle.date)
        #print(datetime.datetime.now())
        if datetime.datetime.now()>raffle.date and raffle.chance != 0:
            if len(avatars) == 0:
                print("No tickets, abort")
                raffle = Raffles.query.filter_by(ended=False).order_by(Raffles.date).first()
                raffle.ended == True
                Tickets.query.delete()
                db.session.commit()
                context['raffle_date'] = "none"
                return render_template('index.html', **context)
            #print("Первый розыгрыш")
            # Выбор победителя + увеличение даты на установленное время
            index = getWinner(avatars, raffle)
            winners = json.loads(raffle.winners)
            #print(winners)
            context['winner'] = avatars[index]
            context['winner_id'] = index
            cookie['winner_id'] = index
            context['winners'] = winners
            context['avatars'] = many_avatars
            if raffle is None:
                context['raffle_date'] = "none"
            else:
                context['raffle_date'] = str(raffle.date).replace(" ", "T")
            return render_template('index.html', **context)
        elif raffle.date > datetime.datetime.now() > raffle.date-datetime.timedelta(seconds=raffle_delay) and raffle.winners is not None:
            #print("Второстепенный розыгрыш")
            winners = json.loads(raffle.winners)
            context['winner'] = winners[-1]
            context['winner_id'] = cookie['winner_id']
            context['winners'] = winners
            context['avatars'] = many_avatars
            context['raffle_date'] = str(raffle.date).replace(" ", "T")
            return render_template('index.html', **context)
        elif datetime.datetime.now() > raffle.date and raffle.chance <= 0:
            raffle.ended = True
            #print("ended")
            Tickets.query.delete()
            raffle = Raffles.query.filter_by(ended=False).order_by(Raffles.date).first()
            db.session.commit()
            if Raffles.query.filter_by(ended=False).order_by(Raffles.date).first() is not None:
                raffle = Raffles.query.filter_by(ended=False).order_by(Raffles.date).first()
            else:
                raffle = None
        #print("Простой")
        if raffle == None:
            context['raffle_date'] = "none"
        else:
            context['raffle_date'] = str(raffle.date).replace(" ", "T")
        context['avatars'] = many_avatars
        return render_template('index.html', **context)
    else:
        context['raffle_date'] = "none"
        context['avatars'] = many_avatars
        return render_template('index.html', **context)
        #return render_template('index.html')

# Добавление победителя
def getWinner(participants, raffle):
    index = random.choice(range(len(participants)))
    if raffle.winners is not None:
        winners = json.loads(raffle.winners)
        winners.append(participants[index])
        raffle.winners = json.dumps(winners, ensure_ascii=False)
    else:
        Tickets.query.filter(Tickets.activated == 0).delete()
        raffle.winners = json.dumps([participants[index]], ensure_ascii=False)
    raffle.chance = int(raffle.chance)-1
    raffle.date = raffle.date + datetime.timedelta(seconds=raffle_delay)
    #if raffle.chance == 0:
    #    raffle.ended = True
    db.session.commit()
    return index

# Проверка розыгрыша на актуальность
def checkRaffle(raffle, participants):
    while True:
        if datetime.datetime.now()>raffle.date+datetime.timedelta(seconds=raffle_delay):
            if len(participants) == 0 and Raffles.query.filter_by(ended=False).order_by(Raffles.date).first() is not None:
                print("No tickets, abort")
                #raffle = Raffles.query.filter_by(ended=False).order_by(Raffles.date).first()
                raffle.ended == True
                Tickets.query.delete()
                db.session.commit()
                break
            print(raffle.date)
            if raffle.chance != 0:
                # Пропущен один победитель, добавляем без рулетки
                index = random.choice(range(len(participants)))
                if raffle.winners is not None:
                    winners = json.loads(raffle.winners)
                    winners.append(participants[index])
                    raffle.winners = json.dumps(winners, ensure_ascii=False)
                else:
                    Tickets.query.filter(Tickets.activated == 0).delete()
                    raffle.winners = json.dumps([participants[index]], ensure_ascii=False)
                raffle.chance = int(raffle.chance)-1
                raffle.date = raffle.date + datetime.timedelta(seconds=raffle_delay)
                if raffle.chance == 0:
                    raffle.ended = True
                db.session.commit()
                #print("raffle chance = {}".format(str(raffle.chance)))
                #print("raffle.date = {}".format(raffle.date))
            else:
                #print("Raffle expired, get another one")
                Tickets.query.delete()  
                raffle = Raffles.query.filter_by(ended=False).order_by(Raffles.date).first()
        else:
            break
    #print("Raffle check succeed")
    return raffle

