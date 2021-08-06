# from datetime import date, datetime


# class UserModel(db.Model):
#     __tablename__ = "users"
#     id = db.Column(db.Integer(), primary_key = True)
#     nick = db.Column(db.String(15), nullable = False, unique = True)
#     password = db.Column(db.String(50), nullable = False)
#     created_on = db.Column(db.DateTime(), default = datetime.utcnow)


#     def __repr__(self) -> str:
#         return f"<id:{self.id}>, <nick:{self.nick}>"

