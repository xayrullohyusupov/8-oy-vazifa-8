from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='auth/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('quiz-list', views.quizList, name='quizList'),
    path('quiz/<int:quiz_id>/participants/', views.participants_list, name='participants'),
    path('quiz-detail/<int:id>/', views.quizDetail, name='quizDetail'),
    path('questionDelete/<int:id>/<int:pk>/', views.questionDelete, name='questionDelete'),
    path('optionDelete/<int:ques>/<int:option>/', views.deleteOption, name='optionDelete'),
    path('question-detail/<int:id>/', views.questionDetail, name='questionDetail'),
    path('create-quiz', views.createQuiz, name='createQuiz'),
    path('create-question/<int:id>/', views.questionCreate, name='questionCreate'),
    path('results/', views.result_list, name='results'),
    path('results/<int:quiz_id>/', views.result_detail, name='result_detail'),
    path('export-results/', views.export_results_to_excel, name='export_results'),
    path('answer/<int:pk>/', views.answer_detail, name='answer_detail'),

]