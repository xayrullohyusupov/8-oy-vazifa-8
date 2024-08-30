from django.shortcuts import render, redirect,get_object_or_404
from . import models
from random import choice, sample
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages

def index(request):
    return render(request, 'index.html')


def quizList(request):
    images = [
        'https://st2.depositphotos.com/2769299/7314/i/450/depositphotos_73146775-stock-photo-a-stack-of-books-on.jpg',
        'https://img.freepik.com/free-photo/creative-composition-world-book-day_23-2148883765.jpg',
        'https://profit.pakistantoday.com.pk/wp-content/uploads/2018/04/Stack-of-books-great-education.jpg',
        'https://live-production.wcms.abc-cdn.net.au/73419a11ea13b52c6bd9c0a69c10964e?impolicy=wcms_crop_resize&cropH=1080&cropW=1918&xPos=1&yPos=0&width=862&height=485',
        'https://live-production.wcms.abc-cdn.net.au/398836216839841241467590824c5cf1?impolicy=wcms_crop_resize&cropH=2813&cropW=5000&xPos=0&yPos=0&width=862&height=485',
        'https://images.theconversation.com/files/45159/original/rptgtpxd-1396254731.jpg?ixlib=rb-4.1.0&q=45&auto=format&w=1356&h=668&fit=crop'
    ]
    
    quizes = models.Quiz.objects.filter(author=request.user)
    # images = sample(len(quizes), images)

    quizes_list = []

    for quiz in quizes:
        quiz.img = choice(images)
        quizes_list.append(quiz)

    return render(request, 'quiz-list.html', {'quizes':quizes_list})


def quizDetail(request, id):
    quiz = models.Quiz.objects.get(id=id)
    return render(request, 'quiz-detail.html', {'quiz':quiz})

def questionDelete(request, id, pk):
    models.Question.objects.get(id=id).delete()
    return redirect('quizDetail', id=pk)


def createQuiz(request):
    if request.method == 'POST':
        quiz = models.Quiz.objects.create(
            name = request.POST['name'],
            amount = request.POST['amount'],
            author = request.user
        )
        return redirect('quizDetail', quiz.id)
    return render(request, 'quiz-create.html')


def questionCreate(request, id):
    quiz = models.Quiz.objects.get(id=id)
    if request.method == 'POST':
        question_text = request.POST['name']
        true = request.POST['true']
        false_list = request.POST.getlist('false-list')

        question = models.Question.objects.create(
            name = question_text,
            quiz = quiz,
        )
        question.save()
        models.Option.objects.create(
            question = question,
            name = true,
            correct = True,
        )

        for false in false_list:
            models.Option.objects.create(
                name = false,
                question = question,
            )
        return redirect('quizList')

    return render(request, 'question-create.html', {'quiz':quiz})


def questionDetail(request, id):
    question = models.Question.objects.get(id=id)
    return render(request, 'question-detail.html', {'question':question})


def deleteOption(request, ques, option):
    question = models.Question.objects.get(id=ques)
    models.Option.objects.get(question=question, id=option).delete()
    return redirect('questionDetail', id=ques)

@login_required
def result_list(request):
    answers = models.Answer.objects.filter(author=request.user)

    # Prepare data for results table
    result_data = []
    for answer in answers:
        correct_answers = answer.answerdetail_set.filter(user_choice__correct=True).count()
        total_questions = answer.quiz.questions_count
        incorrect_answers = answer.answerdetail_set.filter(user_choice__correct=False).count()
        
        result_data.append({
            'quiz_id': answer.quiz.id,
            'quiz_name': answer.quiz.name,
            'total_questions': total_questions,
            'correct_answers': correct_answers,
            'incorrect_answers': incorrect_answers,
            'percentage': (correct_answers / total_questions) * 100 if total_questions else 0,
        })

    # Sort results by percentage
    result_data.sort(key=lambda x: x['percentage'], reverse=True)

    # Add user name (if needed)
    for result in result_data:
        result['user_name'] = request.user.username
        
    return render(request, 'results.html', {'results': result_data})


@login_required
def result_detail(request, quiz_id):
    quiz = get_object_or_404(models.Quiz, pk=quiz_id)
    answers = models.Answer.objects.filter(quiz=quiz, author=request.user)
    
    # Correct and incorrect counts
    correct_count = answers.filter(answerdetail__user_choice__correct=True).count()
    incorrect_count = answers.filter(answerdetail__user_choice__correct=False).count()

    # Calculate correct percentage
    correct_percentage = (correct_count / quiz.questions_count) * 100 if quiz.questions_count else 0

    # AnswerDetails for the table
    details = models.AnswerDetail.objects.filter(answer__in=answers)

    context = {
        'quiz': quiz,
        'correct_count': correct_count,
        'incorrect_count': incorrect_count,
        'correct_percentage': correct_percentage,
        'details': details,
    }
    return render(request, 'result_detail.html', context)


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your account has been created successfully!')
            return redirect('login')
    else:
        form = UserCreationForm()
    
    return render(request, 'auth/register.html', {'form': form})

def export_results_to_excel(request):
    answers = models.Answer.objects.filter(author=request.user)
    details = models.AnswerDetail.objects.filter(answer__in=answers)

    df = pd.DataFrame({
        'Question': [detail.question.name for detail in details],
        'User Choice': [detail.user_choice.name for detail in details],
        'Is Correct': [detail.user_choice.correct for detail in details]
    })

    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="results.xlsx"'

    df.to_excel(response, index=False)
    return response


def participants_list(request, quiz_id):
    quiz = get_object_or_404(models.Quiz, id=quiz_id)
    answers = models.Answer.objects.filter(quiz=quiz)
    context = {
        'quiz': quiz,
        'answers': answers,
    }
    return render(request, 'participants.html', context)

def answer_detail(request, pk):
    answer = get_object_or_404(models.Answer, pk=pk)
    context = {
        'answer': answer,
    }
    return render(request, 'answer_detail.html', context)