import locale
from datetime import datetime

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User

from django.shortcuts import render, redirect

from django.views import View

from WCScores.forms import AddTeamForm, AddMatchForm, RegisterForm, LoginForm, InputScoresForm, UserScoresForm
from WCScores.models import Team, Match, UserScore, Scoreboard

"""
Env: worldcupEnv,
requirements = requirements.txt

Po wejsciu na strone mają się wyświetlic ostatnie wyniki meczow i terminy najblizszych.
ponizej lub w nowym widoku ma byc ranking wszystkich graczy wedlug zdobytych pkt.
strona logowania.
kazdy uzytkownik moze typowac wynik do momentu rozpoczecia meczu.
punktacja za wytypowanie wyniku i zwyciezcy
profil uzytkownika, zdjecie, komentarze do meczu
"""
"""
aplikacja musi porownywac wynik meczu i wynik podany przez uzytkownika i w zaleznosci od tego przyznawac pkt.
Kazdy uzytkownik moze obstawic tylko jeden typ na jeden mecz.
ustawic odpowiednia strefe czasową
"""


# Create your views here.


def logout_view(request):
    logout(request)
    return redirect('/')

# Add teams form
class FormsView(View):
    def get(self, request):
        form = AddTeamForm()
        return render(request, 'formsy.html', {'form': form})


    def post(self, request):
        form = AddTeamForm(request.POST)
        if form.is_valid():
            country = form.cleaned_data['country']
            group = form.cleaned_data['group']
            fifa = form.cleaned_data['FIFA']
            Team.objects.create(country=country, group=group, FIFA=fifa)

            return render(request, 'formsy.html', {'form': form, 'mess': 'Dodane'})


# Add matches form
class MatchFormView(View):
    def get(self, request):
        form = AddMatchForm()
        return render(request, 'matches.html', {'form': form})

    def post(self, request):
        form = AddMatchForm(request.POST)
        if form.is_valid():
            locale.setlocale(locale.LC_TIME, 'pl_PL.utf8')
            date_time = form.cleaned_data['datetime']
            day = date_time.strftime("%A")
            team_1 = form.cleaned_data['team_1']
            team_2 = form.cleaned_data['team_2']
            Match.objects.create(datetime=date_time, day=day, team_1=team_1, team_2=team_2)
            d = Match.objects.all()
            mess = 'dodane: ' + str(len(d))
            return render(request, 'matches.html', {'form': form, 'mess': mess})


class IndexView(View):
    def get(self, request):
        group_a = Team.objects.filter(group='A').order_by('-pkt')
        group_b = Team.objects.filter(group='B').order_by('-pkt')
        group_c = Team.objects.filter(group='C').order_by('-pkt')
        group_d = Team.objects.filter(group='D').order_by('-pkt')
        group_e = Team.objects.filter(group='E').order_by('-pkt')
        group_f = Team.objects.filter(group='F').order_by('-pkt')
        group_g = Team.objects.filter(group='G').order_by('-pkt')
        group_h = Team.objects.filter(group='H').order_by('-pkt')
        return render(request, 'index.html', {'group_a': group_a, 'group_b': group_b, 'group_c': group_c,
                                              'group_d': group_d, 'group_e': group_e, 'group_f': group_f,
                                              'group_g': group_g, 'group_h': group_h})
    def post(self, request):
        group_a = Team.objects.filter(group='A').order_by('-pkt')
        group_b = Team.objects.filter(group='B').order_by('-pkt')
        group_c = Team.objects.filter(group='C').order_by('-pkt')
        group_d = Team.objects.filter(group='D').order_by('-pkt')
        group_e = Team.objects.filter(group='E').order_by('-pkt')
        group_f = Team.objects.filter(group='F').order_by('-pkt')
        group_g = Team.objects.filter(group='G').order_by('-pkt')
        group_h = Team.objects.filter(group='H').order_by('-pkt')
        return render(request, 'index.html', {'group_a': group_a, 'group_b': group_b, 'group_c': group_c,
                                              'group_d': group_d, 'group_e': group_e, 'group_f': group_f,
                                              'group_g': group_g, 'group_h': group_h})

class ScoresView(View):
    def get(self, request):

        matches = Match.objects.all().order_by('datetime')
        scores = UserScore.objects.all()
        users = User.objects.all()
        return render(request, 'scores.html', {'matches': matches, 'scores': scores, 'users': users})


class AddScoreView(View):
    def get(self, request, id):
        match = Match.objects.get(pk=id)
        team_2 = Team.objects.get(pk=match.team_2_id)
        group = Team.objects.filter(group=team_2.group).order_by('-pkt')
        match = Match.objects.get(pk=id)
        form = InputScoresForm()
        return render(request, 'addscores.html', {'form': form, 'match': match, 'group': group})

    def post(self, request, id):
        match = Match.objects.get(pk=id)
        users_scores = UserScore.objects.filter(match_id=id)
        team_1 = Team.objects.get(pk= match.team_1_id)
        team_2 = Team.objects.get(pk= match.team_2_id)
        group = Team.objects.filter(group= team_2.group).order_by('-pkt')
        form = InputScoresForm(request.POST)
        if form.is_valid():
            team_1_score = form.cleaned_data['team_1_score']
            team_2_score = form.cleaned_data['team_2_score']
            match.team_1_score = team_1_score
            match.team_2_score = team_2_score
            if team_1_score > team_2_score:
                match.winner_id = team_1.id
                match.draw = False
            elif team_1_score < team_2_score:
                match.winner_id = team_2.id
                match.draw = False
            else:
                match.draw = True
                match.winner_id = ""
            match.save()
            team_1.matches = Match.objects.filter(team_1=team_1).filter(team_1_score__isnull=False).count() \
                             + Match.objects.filter(team_2=team_1).filter(team_1_score__isnull=False).count()
            team_2.matches = Match.objects.filter(team_1=team_2).filter(team_1_score__isnull=False).count() \
                             + Match.objects.filter(team_2=team_2).filter(team_1_score__isnull=False).count()
            team_1.win = Match.objects.filter(winner=team_1).count()
            team_2.win = Match.objects.filter(winner=team_2).count()
            team_1.draw = Match.objects.filter(team_1=team_1).filter(draw=True).count()\
                          + Match.objects.filter(team_2=team_1).filter(draw=True).count()
            team_2.draw = Match.objects.filter(team_1=team_2).filter(draw=True).count()\
                          + Match.objects.filter(team_2=team_2).filter(draw=True).count()
            team_1.loose = team_1.matches - team_1.win - team_1.draw
            team_2.loose = team_2.matches - team_2.win - team_2.draw
            team_1.pkt = team_1.win * 3 + team_1.draw
            team_2.pkt = team_2.win * 3 + team_2.draw
            team_1.save()
            team_2.save()

            #add scores to scoreboard
            for score in users_scores:
                if team_1_score == score.team_1_score and team_2_score == score.team_2_score:
                    score.perfect = True
                    score.scored = False
                elif team_1_score > team_2_score and score.team_1_score > score.team_2_score:
                    score.scored = True
                    score.perfect = False
                elif team_1_score < team_2_score and score.team_1_score < score.team_2_score:
                    score.scored = True
                    score.perfect = False
                elif team_1_score == team_2_score and score.team_1_score == score.team_2_score:
                    score.scored = True
                    score.perfect = False
                else:
                    score.perfect = False
                    score.scored = False
                score.save()



            return render(request, 'addscores.html', {'form': form, 'match': match, 'message': 'Wynik dodany', 'group': group})


class UserScoresView(LoginRequiredMixin, View):
    def get(self, request, id):
        score = UserScore.objects.filter(match_id=id)
        user_match = Match.objects.get(id=id)
        FMT = '%d.%m.%Y %H:%M:%S'
        s1 = datetime.now().strftime(FMT)
        s2 = user_match.datetime.strftime(FMT)
        tdelta = datetime.strptime(s2, FMT) - datetime.strptime(s1, FMT)

        if tdelta.seconds <= 0 or tdelta.days < 0:
            message = 'Mecz już się zaczął, nie można obstawiać'
            return render(request, 'userscores.html',
                          {'match': user_match, 'score': score, 'message': message})
        form = UserScoresForm()
        try:
            score.get(name=request.user)
            message = 'Juz obstawiłeś wynik, możesz aktualizować swój typ do momentu rozpoczęcia meczu'
            return render(request, 'userscores.html', {'form': form, 'match': user_match, 'score': score,
                                                       'message': message, 'message2': 'Do meczu zostało: ' + str(tdelta)})
        except:
            return render(request, 'userscores.html', {'form': form, 'match': user_match, 'score': score,
                                                       'message2': 'Do meczu zostało' + str(tdelta)})

    def post(self, request, id):
        user_match = Match.objects.get(id=id)
        form = UserScoresForm(request.POST)
        score = UserScore.objects.filter(match_id=id)
        FMT = '%d.%m.%Y %H:%M:%S'
        s1 = datetime.now().strftime(FMT)
        s2 = user_match.datetime.strftime(FMT)
        tdelta = datetime.strptime(s2, FMT) - datetime.strptime(s1, FMT)
        try:
            user_score = score.get(name=request.user)
            if form.is_valid():
                user_score.user = User.objects.get(id=request.user.pk)
                user_score.team_1_score = form.cleaned_data['team_1_score']
                user_score.team_2_score = form.cleaned_data['team_2_score']
                user_score.save()
                message = 'zaktualizowano Twoj typ'
                return render(request, 'userscores.html',
                              {'form': form, 'match': user_match, 'score': score, 'message': message,
                               'message2': 'Do meczu zostało: ' + str(tdelta)})


            return render(request, 'userscores.html', {'form': form, 'match': user_match, 'score': score})
        except:
            if form.is_valid():
                user = User.objects.get(id=request.user.pk)
                team_1_score = form.cleaned_data['team_1_score']
                team_2_score = form.cleaned_data['team_2_score']
                UserScore.objects.create(name=user, team_1_score=team_1_score, team_2_score=team_2_score, match=user_match)

                score = UserScore.objects.filter(match_id=id)
                return render(request, 'userscores.html', {'form': form, 'match': user_match, 'score': score,
                                                           'message2': 'Do meczu zostało: ' + str(tdelta)})


class ScoreboardView(View):
    def get(self, request):
        users = User.objects.all()
        for usr in users:
            user_scores = UserScore.objects.filter(name=usr)

            user_board = Scoreboard.objects.get(user=usr)
            user_board.matches_number = user_scores.count()
            user_board.scored = user_scores.filter(scored=True).count()
            user_board.perfect = user_scores.filter(perfect=True).count()
            user_board.points = user_board.scored + user_board.perfect * 3
            user_board.save()
        scoreboard = Scoreboard.objects.all()
        return render(request, 'scoreboard.html', {'scoreboard': scoreboard})


class LoginView(View):
    def get(self, request):
        form = LoginForm()
        return render(request, 'login.html', {'form': form})

    def post(self, request):
        form = LoginForm(request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('/')

            else:
                return render(request, 'login.html', {'form': form, 'message': 'Wrong login or password'})


class RegisterView(View):
    def get(self, request):
        form = RegisterForm()
        return render(request, 'register.html', {'form': form})

    def post(self, request):
        form = RegisterForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            password2 = form.cleaned_data['password2']
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            email = form.cleaned_data['email']

            if password != password2:
                return render(request, 'register.html', {'form': form, 'message': 'The password does not match'})
            else:
                try:
                    user = User.objects.create_user(username=username, email=email, password=password, first_name=first_name,
                                             last_name=last_name)
                    Scoreboard.objects.create(user=user)
                    return render(request, 'register.html', {'form': form, 'message': 'User created'})
                except:
                    return render(request, 'register.html', {'form': form, 'message': 'Username already exist'})
        else:
            form = RegisterForm()
            return render(request, 'register.html', {'form': form, 'message': 'Invalid data'})
