from app import app, db, api
from flask import render_template, redirect, url_for, flash, request, jsonify, send_file, make_response
from flask_login import current_user, login_user, logout_user
from app.forms import QAForm, LoginForm, EditForm
from app.models import Question, Answer,Admin
from flask import request, jsonify, send_file, make_response
from flask_restful import Resource, fields, marshal_with, abort,reqparse
from app.models import Question, Answer
from app import db, api
import pyttsx3

@app.route('/admin',  methods= ['GET','POST'])
def adm():
    form = QAForm()
    if  current_user.is_authenticated == False:  
        return redirect(url_for('login')) 
    if form.validate_on_submit():
        new_question = Question(text_question=form.question.data.lower().rstrip())
        db.session.add(new_question)
        db.session.commit()
        new_answer = Answer(text_answer=form.answer.data.lower(), question_id=new_question.id, count_of_answer=0)
        db.session.add(new_answer)
        db.session.commit()
        return redirect(url_for('que'))  # перенаправление на страницу с вопросами и ответами
    return render_template('admin.html', form=form)
    # return render_template('admin.html', title='admin', form=form)

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def item_edit(id):
    if not current_user.is_authenticated: 
        return redirect(url_for('login')) 
    answer = Answer.query.filter_by(question_id=id).first()
    if not answer:
        abort(404, description="Answer not found")
    question = Question.query.filter_by(id=id).first()
    form = EditForm()  
    if request.method == 'GET':
        form.question.data = question.text_question  
        form.answer.data = answer.text_answer 
    if form.validate_on_submit() and request.method == 'POST':
        question.text_question = form.question.data.lower().rstrip()
        answer.text_answer = form.answer.data
        db.session.commit()
        return redirect(url_for('que'))  
    return render_template('edit.html', form=form, question_id=id)

@app.route('/delete/<int:id>', methods=['GET', 'POST'])
def delete_item(id):
    if not current_user.is_authenticated: 
        return redirect(url_for('login')) 
    answer  = Answer.query.filter_by(question_id = id).first()
    db.session.delete(answer)
    db.session.commit()
    question = Question.query.filter_by(id = id).first()
    db.session.delete(question)
    db.session.commit()
    return redirect(url_for('que'))

@app.route('/quest', methods= ['GET'])
def que():
    print(current_user.is_authenticated)
    if  current_user.is_authenticated == False: 
        return redirect(url_for('login')) 
    results = db.session.query(Question, Answer).filter(Question.id == Answer.question_id).all()
    data = []
    for question, answer in results:
        data.append({
            'question_id': question.id,
            'question_text': question.text_question,
            'answer_text': answer.text_answer
        })
    return render_template('admin_quest.html', data=data)
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/popular')
def index():
    if current_user.is_authenticated == False: 
        return redirect(url_for('login')) 
    results = db.session.query(Question, Answer).filter((Question.id == Answer.question_id)).order_by(Answer.count_of_answer.desc()).limit(10).all()
    print(results)
    data = []
    for question, answer in results:
        data.append({
            'id' : question.id,
            'question_text': question.text_question,
            'count': answer.count_of_answer,
        })
    return render_template('stat.html', data=data)

# @app.route('/static')
# def static():
#     if not current_user.is_authenticated:
#         return redirect(url_for('login'))
    
#     results = db.session.query(Question, Answer).filter((Question.id == Answer.question_id)).order_by(Answer.count_of_answer.desc()).limit(10).all()
#     data = []
#     for question, answer in results:
#         data.append({
#             'question_id': question.id,
#             'question_text': question.text_question,
#             'answer_text': answer.text_answer
#         })
#     return render_template('statistic.html', data=data)
# @app.route('/login')
# @app.route('/', methods=['GET', 'POST'])
# def login():
#     form = LoginForm()
#     if form.validate_on_submit():
#         print(form.username.data)
#         print(form.password.data)
#         flash('Login requested for user {}, remember_me={}'.format(
#             form.username.data, form.remember_me.data))
#         return redirect(url_for('adm'))
#     return render_template('auth.html', title='Регистрация', form=form)
# @app.route('/login')
# @app.route('/', methods=['GET', 'POST'])
# def login():
#     # if current_user.is_authenticated:
#     #     return redirect(url_for('adm'))
#     form = LoginForm()
#     if form.validate_on_submit():
#         print(form.username.data)
#         user = Admin.query.filter_by(name=form.username.data).first()
#         if not user:
#             print("Not USER")
#             return redirect(url_for('login'))
#         if user.name == form.username.data and user.password == form.password.data:
#             return redirect(url_for('adm'))
#         print(user.name)
#         # print(user.password)
#         # if user.name == form.username.data and user.password == form.password.data:
#         #     return redirect(url_for('adm'))
#         # else:
#         #     flash('Invalid username or password')
#         #     return redirect(url_for('login'))
#         # if user is None or not user.check_password(form.password.data):
#         #     flash('Invalid username or password')
#         #     return redirect(url_for('login'))
#         # login_user(user, remember=form.remember_me.data)
#         # return redirect(url_for('adm'))
#     return render_template('auth.html', title='Регистрация', form=form)
@app.route('/',methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:  # Check if the user is already logged in
        return redirect(url_for('adm'))  # Redirect to a different page, for example, 'adm'
    form = LoginForm()
    if form.validate_on_submit():
        user = Admin.query.filter_by(name=form.username.data).first()
        if user and user.password == form.password.data:
            login_user(user)
            return redirect(url_for('adm'))
        flash('Invalid username or password')
    return render_template('auth.html', title='Регистрация', form=form)

from flask import request, jsonify, send_file, make_response
from flask_restful import Resource, fields, marshal_with, abort,reqparse
from app.models import Question, Answer
from app import db, api
import pyttsx3

resource_questions = {
    'id': fields.Integer,
    'text_question': fields.String,
}
resource_answers = {
    'id': fields.Integer,
    'text_answer': fields.String,
}
resource_query ={
    'text_answer': fields.String
}

task_post_args = reqparse.RequestParser()
task_post_args.add_argument("text_question",type=str,help="Task is text_question", required= True )
task_post_args.add_argument("text_answer", type = str, help="help text_answer", required = True)

response_question = reqparse.RequestParser()
response_question.add_argument("text_question",type=str,help="Task is text_question", required= True )
response_answer = reqparse.RequestParser()
response_answer.add_argument("text_answer",type=str,help="Task is text_answer", required= True )
# with app.app_context():
#     db.create_all()

class Questions(Resource):
    # поиск одного вопроса
    @marshal_with(resource_questions)
    def get(self, question_id):
        question = Question.query.filter_by(id=question_id).first()
        if not question:
            abort(404, message="Question not found")
        return question
    #изменение вопроса
    @marshal_with(resource_questions)
    def put(self, question_id):
        args = response_question.parse_args()
        question = Question.query.filter_by(id = question_id).first()
        if not question:
            abort(404, message="not question")
        if args['text_question']:
            question.text_question = args['text_question']
        db.session.commit()
        return question
    #удаление элемента по ид удаляет все т.к внешний ключ не дает возможности удалить по отдельности
    @marshal_with(resource_questions)
    def delete(self, question_id):
        print(question_id)
        answer  = Answer.query.filter_by(question_id = question_id).first()
        db.session.delete(answer)
        db.session.commit()
        question = Question.query.filter_by(id = question_id).first()
        db.session.delete(question)
        db.session.commit()
        return "Deleted", 204
class Answers(Resource):
    @marshal_with(resource_answers)
    def get(self, answer_id):
        print(answer_id)
        answer = Answer.query.filter_by(id=answer_id).first()
        if not answer:
            abort(404, message="Question not found")
        return answer
    @marshal_with(resource_answers)
    def put(self, answer_id):
        args = response_answer.parse_args()
        answer = Answer.query.filter_by(id = answer_id).first()
        print(args['text_answer'])
        if not answer:
            abort(404, message="not answer")
        if args['text_answer']:
            answer.text_answer = args['text_answer']
        db.session.commit()
        return answer
    @marshal_with(resource_answers)
    def delete(self, answer_id):
        print(answer_id)
        answer  = Answer.query.filter_by(question_id = answer_id).first()
        db.session.delete(answer)
        db.session.commit()
        question = Question.query.filter_by(id = answer_id).first()
        db.session.delete(question)
        db.session.commit()
        return "Deleted", 204




class ResponseToQuestion(Resource):
    # вывод ответа на вопрос
    # @marshal_with(resource_query)
    # def post(self):
    #     args = response_question.parse_args()
    #     question_text = args['text_question']
    #     question = Question.query.filter_by(text_question=question_text).first()
    #     if not question:
    #         abort(404, message="Question not found")
    #     answer = Answer.query.filter_by(question_id=question.id).first()
    #     count = answer.count_of_answer
    #     print(answer.count_of_answer)
    #     answer.count_of_answer = count+1
    #     db.session.commit()
    #     string = answer.text_answer
    #     engine = pyttsx3.init()
    #     engine.save_to_file(string, 'vanek.mp3')
    #     engine.runAndWait()
    #     mp3 = 'vanek.mp3'
    #     if not answer:
    #         abort(404, message="Answer not found for this question")
    #     # return {
    #     #     'text_answer': answer.text_answer
    #     # }, 201
    #     return send_file(mp3, as_attachment=True)
    def get(self):
        question_text = request.args.get('text_question').lower()
        error = '../err.wav'
        if not question_text:
            return send_file(error, as_attachment=True)
        question = Question.query.filter_by(text_question=question_text).first()
        print(question_text)
        if not question:
            return send_file(error, as_attachment=True)
        answer = Answer.query.filter_by(question_id=question.id).first()
        count = answer.count_of_answer
        answer.count_of_answer = count + 1
        db.session.commit()
        string = answer.text_answer
        engine = pyttsx3.init()
        engine.save_to_file(string, 'vanek.wav')
        engine.runAndWait()
        mp3 = '../vanek.wav'
        response = make_response(send_file(mp3))
        response.headers['Content-Type'] = 'audio/mpeg'
        response.headers['Content-Disposition'] = 'inline; filename=your_audio.mp3'
        if not answer:
            return send_file(error, as_attachment=True)
        return send_file(mp3, as_attachment=True)


class AnswerAndQuestion(Resource):
    # добавление вопроса и ответа
    @marshal_with(resource_questions)
    def post(self):
        args = task_post_args.parse_args()
        print(args['text_question'])
        print(args['text_answer'])
        new_question = Question(text_question= (args['text_question']).lower())
        db.session.add(new_question)
        db.session.commit()
        new_answer = Answer(text_answer=args['text_answer'].lower(), question_id=new_question.id, count_of_answer=0)
        db.session.add(new_answer)
        db.session.commit()
        return 201
    # вывод вопрос-ответ
    def get(self):
        results = db.session.query(Question, Answer).filter(Question.id == Answer.question_id).all()
        data = []
        for question, answer in results:
            data.append({
                'question_id': question.id,
                'question_text': question.text_question,
                'answer_text': answer.text_answer
            })
        return jsonify(data)
class Statistic(Resource):
    def get(self):
        # results = db.session.query(Question, Answer).filter((Question.id == Answer.question_id)).limit(10).all()
        results = db.session.query(Question, Answer).filter((Question.id == Answer.question_id)).order_by(Answer.count_of_answer.desc()).limit(10).all()
        print(results)
        data = []
        for question, answer in results:
            data.append({
                'question_id': question.id,
                'question_text': question.text_question,
            })
        print(data)
        return jsonify(data)
class MusicFile(Resource):
    def get(self):
        mp3_path = 'valume/speech.mp3'
        return send_file(mp3_path, as_attachment=True)

api.add_resource(Questions, '/questions/<int:question_id>')
api.add_resource(Answers, '/answers/<int:answer_id>')
api.add_resource(AnswerAndQuestion, '/all')
api.add_resource(ResponseToQuestion, '/all/question')
api.add_resource(Statistic, '/all/statistic')
api.add_resource(MusicFile, '/all/music')

