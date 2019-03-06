from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import render, redirect

# Create your views here.
from django.urls import reverse
from django.views import View

from homeworkapp.models import *


class HomeworkView(View):
    def get(self, request):
        try:
            page_number = request.GET.get('page', default='1')
            allhomework = Homework.objects.all()
            homework_list = []
            for h in allhomework:
                if h.questions_set.all():
                    homework_list.append(h)
            paginator = Paginator(homework_list, 10)  # 实例化分页器对象，第一个参数是数据源，第二个参数是每页显示的条数
            page = paginator.page(page_number)  # 返回page_number页的数据，以Page对象的方式封装该页数据
            return render(request, 'homework.html', locals())
        except Exception as e:
            print(e)
            return render(request, 'homework.html')


class Details(View):
    def get(self, request):
        h_id = request.GET.get('list')
        questions = Questions.objects.filter(homework_id=h_id)  # 根据作业id挑选出当前作业的所有问题
        pd_list = []
        xz_list = []
        jd_list = []
        for q in questions:
            if q.questionType == 'pd':
                pd_list.append(q)
            elif q.questionType == 'xz':
                xz_list.append(q)
            elif q.questionType == 'jd':
                jd_list.append(q)
        return render(request, 'homework_details.html', locals())


class Judge(View):
    def get(self, request):
        pass

    def post(self, request):
        try:
            h_id = request.POST.get('h')  # 获取作业id
            number = request.session['user']['number']  # 获取登录学生学号
            s = StudentScore.objects.filter(student_id=number, homework_id=h_id).first()  # 判断是否已提交作业
            if s is None:  # 未提交才可执行
                this_h = Homework.objects.filter(id=h_id).first()  # 根据作业id挑选出当前作业对象
                questions = Questions.objects.filter(homework=this_h).all()  # 根据作业对象挑选出当前作业的所有问题
                h_score = HomeworkSocre.objects.filter(homework=this_h).first()
                pd = questions.filter(questionType='pd').all()  # 挑选出所有判断题
                xz = questions.filter(questionType='xz').all()  # 挑选出所有选择题
                i = 0
                pd_score = 0
                if h_score is None:
                    h_score = HomeworkSocre.objects.create(homework=this_h)  # 没有设置作业分数时
                for p in pd:
                    pd_a = request.POST.get(str(p.id))  # 根据题目id获取学生的答案
                    pd_obj = pd[i]
                    if pd_obj.answer == pd_a:
                        pd_score += 1
                        # 添加做题日志
                        pd_log = StudentAnswerLog.objects.create(student_id=number, homework_id=h_id,
                                                                 question=pd_obj, answer=pd_a,
                                                                 score=h_score.panduan_score)
                        pd_log.save()
                    else:
                        pd_score += 0
                        pd_log1 = StudentAnswerLog.objects.create(student_id=number, homework_id=h_id,
                                                                  question=pd_obj, answer=pd_a, score=0)
                        pd_log1.save()
                    i += 1
                pd_score *= h_score.panduan_score  # 判断题总分

                j = 0
                xz_score = 0
                for x in xz:
                    xz_a = request.POST.get(str(x.id))  # 根据题目id获取学生的答案
                    xz_obj = xz[j]
                    if xz_obj.answer == xz_a:
                        xz_score += 1
                        pd_log2 = StudentAnswerLog.objects.create(student_id=number, homework_id=h_id,
                                                                  question=xz_obj, answer=xz_a,
                                                                  score=h_score.xuanze_score)
                        pd_log2.save()
                    else:
                        xz_score += 0
                        pd_log3 = StudentAnswerLog.objects.create(student_id=number, homework_id=h_id,
                                                                  question=xz_obj, answer=xz_a, score=0)
                        pd_log3.save()
                    j += 1
                xz_score *= h_score.xuanze_score  # 选择题总分
                total = pd_score + xz_score  # 判断题加选择分数
                s = StudentScore.objects.create(student_id=number, homework=this_h, pd_score=pd_score,
                                                xz_score=xz_score, total=total)
                if s:
                    s.save()
                return redirect(reverse('homework:homework'))
            else:
                return redirect(reverse('homework:homework'))

        except Exception as e:
            return redirect(reverse('homework:homework'))


class Check(View):
    def get(self, request):
        h_id = request.GET.get('h')  # 获取作业id
        number = request.session['user']['number']  # 获取已登录学生id
        s = StudentScore.objects.filter(student_id=number, homework_id=h_id)  # 判断是否已提交作业
        if s:
            return JsonResponse({'status': True})
        else:
            return JsonResponse({'status': False})


class AnswerNums(View):
    def get(self, request):
        pass

    def post(self, request):
        try:
            h_id = request.POST.get('h_id')
            h_obj = Homework.objects.filter(id=int(h_id))
            h_update_obj = h_obj.update(answer_nums=int(h_obj.first().answer_nums) + 1)
            print(h_update_obj)
            if h_update_obj:
                return JsonResponse({'status': True})
            else:
                return JsonResponse({'status': False})

        except Exception as e:
            print(e)
            return JsonResponse({'status': False})