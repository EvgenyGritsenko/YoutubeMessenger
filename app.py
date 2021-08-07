from flask import Flask, render_template, url_for, redirect, flash, request
from flask_sqlalchemy import SQLAlchemy
from flask_script import Manager
from forms import UserForm, LoginForm, UpdateForm, ChatForm
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_migrate import Migrate #, MigrateCommand
from flask_login import LoginManager, UserMixin, current_user, login_manager, login_user, logout_user, login_required
from threading import *

app = Flask(__name__)
app.debug = True
app.config['SECRET_KEY'] = "e0ra5894rhbeivki8r"
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///site.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
manager = Manager(app)
migrate = Migrate(app, db)
#manager.add_command("db", MigrateCommand)
login_manager = LoginManager(app)

@login_manager.user_loader
def load_user(id):
	return db.session.query(UserModel).get(id)

@app.route("/")
def MainForAnon():
	if current_user.is_authenticated:
		return redirect(url_for("MainPage"))
	return render_template("main_anon.html")


@app.route("/info_user/<int:id>")
@login_required
def infoUserId(id):
	user = db.session.query(UserModel).get(id)
	ConvStr = str(user.created_on)

	ConvSplitDate = ConvStr.split()[0]
	ConvSplitDate2 = ConvSplitDate.split("-")
	year,month,day = ConvSplitDate2[0], ConvSplitDate2[1], ConvSplitDate2[2]

	ConvSplitTime = ConvStr.split()[1]
	ConvSplitTime2 = ConvSplitTime.split(":")

	date = {'year': year, 'month': month, 'day': day}
	hour,minute,second = ConvSplitTime2[0] , ConvSplitTime2[1] , ConvSplitTime2[2].split(".")[0]
	time = {'hour': hour, 'minute': minute, 'second': second}

	return render_template("info_user_id.html", user=user, date=date, time=time)


@app.route("/info_users/")
def infoUser():
	All = db.session.query(UserModel).all()
	return render_template("info_user.html", all=All)


@app.route("/main/", methods=['get','post'])
@login_required
def MainPage():

	AllUsers = db.session.query(UserModel).all()
	return render_template("main_page.html", all = AllUsers)

@app.route("/update_acc/<int:id>/", methods=["POST", "GET"])
@login_required
def UpdateAcc(id):
	form = UpdateForm()
	All = db.session.query(UserModel.nick).all()
	this_user = db.session.query(UserModel).get(id)

	if form.validate_on_submit():
		if current_user.id == id:
			all_nicks = []
			for i in All:
				for j in i:
					if current_user.nick != j:
						all_nicks.append(j)
			print(all_nicks)

			new_nick = form.upd_nick.data
			new_pass = form.upd_password.data

			if new_nick:
				if current_user.nick not in all_nicks:
					
					if len(new_nick) >= 4:
						if len(new_nick) <= 16:
							this_user.nick = new_nick
							db.session.commit()
							flash("Ник обновлен")
						else:
							flash("Слишком длинный ник - (максимум 16 символов)")
					else:
						flash("Слишком маленький ник - (минимум 4 символа)")
					
					
				else:
					flash("Пользователь с таким ником уже существует либо это твой нынешний!")

			if new_pass:
				if len(form.upd_password.data) >= 5:
					if len(form.upd_password.data) <= 50:
						this_user.set_password(form.upd_password.data)
						db.session.commit()
						flash("Пароль обновлен")
					else:
						flash("Слишком длинный пароль - (максимум 50 символов)")
				else:
					flash("Слишком короткий пароль - (минимум 5 символов)")



		else:
			flash("Ты чо самый умный? зачем ты хочешь изменить данные другого аккаунта?")

	return render_template("upd_acc.html", form = form)


@app.route("/delete_acc/<int:id>/")
@login_required
def DeleteAcc(id):
	this_user = db.session.query(UserModel).get(id)

	if current_user.id == id:
		try:
			db.session.delete(this_user)
			db.session.commit()
			flash("Аккаунт успешно удален")
		except:
			flash("Произошла ошибка удаления аккаунта!")
	else:
		flash("Посмотрите-ка на этого хакера. Ты пытаешься удалить не свой аккаунт!")

	return render_template("del_acc.html")			


@app.route("/chat/", methods=["GET", "POST"])
@login_required
def Chat():
	TimeData = []
	data = db.session.query(MessagesModel).order_by(-MessagesModel.id_message)
	for i in data:
		ID = i.id_message
		if i.send_to_str:
			Time = str(i.send_to_str)
			TimeConv1 = Time.split()[1] # часы
			TimeConv2 = Time.split()[0] # дата
			TimeHour = TimeConv1.split(".")[0]
			TimeData.append({'id': ID ,'timeHour': TimeHour, 'timeDay': TimeConv2[:10]})

	print(TimeData)

	form = ChatForm()


	if form.validate_on_submit():
		nick = current_user.nick
		message = form.message.data
		#t = Thread(target=MessagesModel, message=message, user_nick=nick)
		add_message = MessagesModel(message=message, user_nick=nick)
		db.session.add(add_message)
		db.session.commit()
		return redirect(url_for("Chat"))

	
	return render_template("chat.html", form=form, data=data, TimeData = TimeData)


@app.route("/registration/", methods=['POST','GET'])
def Reg():
	if current_user.is_authenticated:
		return redirect(url_for("MainPage"))

	form = UserForm()
	All = db.session.query(UserModel.nick).all()
	all_users = []

	for i in All:
		for j in i:
			all_users.append(j.lower())

	if form.validate_on_submit():
		nick = form.nick.data
		password = form.password.data

		if nick.lower() not in all_users:
			add_user_db = UserModel(nick = nick, password = password)
			db.session.add(add_user_db)
			add_user_db.set_password(password)
			db.session.commit()
			return redirect(url_for('Login'))
		else:
			flash("Такой аккаунт уже существует, авторизируйся")
			return redirect(url_for('Login'))
	



	return render_template("registration.html", form=form)

@app.route("/login/", methods=["POST", "GET"])
def Login():
	form = LoginForm()

	if current_user.is_authenticated:
		return redirect(url_for("MainPage"))

	All = db.session.query(UserModel.nick).all()
	all_nicks = []

	for i in All:
		for j in i:
			all_nicks.append(j.lower())


	if form.validate_on_submit():
		if form.check_nick.data.lower() in all_nicks:
			user = db.session.query(UserModel).filter(UserModel.nick == form.check_nick.data).first()
			if user and user.check_password(form.check_pass.data):
				login_user(user)
				return redirect(url_for("MainPage"))
		else:
			flash("Такой пользователь не зарегистрирован!")
		


	return render_template("login.html", form=form)

@app.route("/logout_user/")
def LogOut():
	logout_user()
	return redirect("/login")

@app.errorhandler(401)
def NotAuthorised(error):
	return render_template("NotAuthorised.html")


@app.errorhandler(404)
def NotFound(error):
	return render_template("error404.html")



class UserModel(db.Model, UserMixin):
	__tablename__ = "users"
	id = db.Column(db.Integer(), primary_key = True)
	nick = db.Column(db.String(100), nullable = False, unique = True)
	password = db.Column(db.String(200), nullable = False)
	created_on = db.Column(db.DateTime(), default = datetime.now)
	# будет использовано в следующих обновлениях
	admin = db.Column(db.Boolean(), default=False) 
	admin_level = db.Column(db.Integer(), default = 0)

	def set_password(self, password):
		self.password = generate_password_hash(password)

	def check_password(self, password):
		return check_password_hash(self.password, password)

	def __repr__(self) -> str:
		return f"<id:{self.id}>, <nick:{self.nick}>"

class MessagesModel(db.Model):
	__tablename__ = 'messages'
	id_message = db.Column(db.Integer(), primary_key=True)
	message = db.Column(db.Text())
	user_nick = db.Column(db.String(100))
	send_to = db.Column(db.DateTime(), default=datetime.utcnow)
	send_to_str = db.Column(db.String(100), default=datetime.utcnow)
	

	def __repr__(self) -> str:
		return f'{self.id_message}, {self.message}'







if __name__ == "__main__":
	manager.run()