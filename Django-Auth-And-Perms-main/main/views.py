from django.shortcuts import render, redirect

from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth import login
from django.contrib.auth.models import User, Group

from django.http import StreamingHttpResponse

from django.views.decorators import gzip
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_cookie

from .forms import RegisterForm, InfoForm, DietForm, SearchFoodForm
from .models import DiaryDetails, Diet

from .sourceCode.camera import VideoCamera, cameraGenerator
from .sourceCode.pythonScrapper import getDataFromEDAMAM, getValuesFromEDAMAM

from django.core.cache import cache




@login_required(login_url="/login")
def home(request):
    posts = DiaryDetails.objects.all()

    if request.method == "POST":
        delete_id = request.POST.get("delete-diary")
        block_user = request.POST.get("block-user")

        if delete_id:
            diary = DiaryDetails.objects.filter(id=delete_id).first()
            if diary and (diary.user == request.user or request.user.has_perm("main.delete_post")):
                diary.delete()

        elif block_user:
            user = User.objects.filter(id=block_user).first()
            if user and request.user.is_staff:
                try:
                    group = Group.objects.get(name='default')
                    group.user_set.remove(user)
                except:
                    pass
                try:
                    group = Group.objects.get(name='mod')
                    group.user_set.remove(user)
                except:
                    pass
    return render(request, 'main/home.html', {"posts": posts})


@login_required(login_url="/login")
#@permission_required("main.add_post", login_url="/login", raise_exception=True)
def create_diary(request):
    if request.method == 'POST':
        form = InfoForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.save()
            return redirect('/home')
    else:
        form = InfoForm()
    return render(request, 'main/create_diary.html', {"form": form})


@login_required(login_url="/login")
def update_diary(request, diary_id):
    diary = DiaryDetails.objects.get(pk=diary_id)
    if diary.user == request.user or request.user.is_staff:
        form = InfoForm(request.POST or None, request.FILES or None, instance=diary)
        if form.is_valid():
            form.save()
            return redirect('/home')

        return render(request, 'main/update_diary.html',
                      {'diary': diary,
                       'form': form})

    return redirect("/home")


@login_required(login_url="/login")
def add_food_note(request, diary_id):
    exists = DiaryDetails.objects.get(pk=diary_id)
    if exists:
        if exists.user == request.user or request.user.is_staff:
            if request.method == 'POST':
                form = DietForm(request.POST or None)
                if form.is_valid():
                    post = form.save(commit=False)
                    post.user = exists
                    post.save()
                    return redirect("/home")
            else:
                form = DietForm()
            return render(request, 'main/add_food_note.html',
                          {'diary': exists,
                           'form': form})
    return redirect('/home')



@login_required(login_url="/login")
def view_diary(request, diary_id):
    diary = DiaryDetails.objects.get(pk=diary_id)
    if diary:
        if request.method == "POST":
            delete_id = request.POST.get("delete-note")
            if delete_id:
                note = Diet.objects.filter(id=delete_id).first()
                if note and (note.user.user == request.user or request.user.has_perm("main.delete_post")):
                    note.delete()
        if diary.user == request.user or request.user.is_staff:
            data = Diet.objects.filter(user=diary).all()
            return render(request, 'main/view_diary.html',
                          {'diary': diary,
                           'data': data})
    return redirect('/home')



def show_photo(request):
    return render(request, r'C:\Users\vital\Desktop\fullstack\python\new\foodProject\Django-Auth-And-Perms-main\main\templates\main\view_photo.html')



@login_required(login_url="/login")
@gzip.gzip_page
def video_feed(request):
    try:
        cam = VideoCamera()
        return StreamingHttpResponse(cameraGenerator(cam), content_type="multipart/x-mixed-replace;boundary=frame")
    except:
        pass

    return render(request, 'view_webcam.html')


def sign_up(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('/home')
    else:
        form = RegisterForm()

    return render(request, 'registration/sign_up.html', {"form": form})


def search_food_helper(request, code=10, getHtml=None, getContext=None):
    print(code)
    context = {}
    caches = ["lastFoodSearch", "lastFoodSearchLabels", "lastFoodSearchValues", "lastFoodSearchResults", "lastFoodSearchActive"]
    for k in caches:
        print(k)
        print(cache.get(k))

    if code == 10 or code == 11:
        context["form"] = SearchFoodForm()
        context["lastFoodSearch"] = cache.get(caches[0])
        response = render(request, 'main/search_food.html', context)
        cache.delete(caches[-1])
        if code == 11:
            for cacheItem in caches[0:4]:
                cache.delete(cacheItem)

    elif code == 21 or code == 22 or code == 23:
        if code == 21:
            context["searched"] = request.POST.get("search")
            cache.set(caches[0], context["searched"])
        else:
            context["searched"] = cache.get(caches[0])

        if code == 21 or code == 22:
            context["labels"] = getDataFromEDAMAM(context["searched"])
            cache.set(caches[1], context["labels"])
        else:
            context["labels"] = cache.get(caches[1])
            context["lastFoodSearchActive"] = 1

        response = render(request, 'main/active_searching_food.html', context)

        if code == 21 or code == 22:
            for cacheItem in caches[2:4]:
                cache.delete(cacheItem)
        else:
            cache.set(caches[-1], 1)

    elif code == 31 or code == 32 or code == 33:
        if code == 33:
            context["data"] = cache.get(caches[3])
        else:
            if code == 32:
                lastFoodSearchValues = eval(cache.get(caches[2]))
                relevant_id = lastFoodSearchValues[0]
                food_names = lastFoodSearchValues[1]
                quantities = lastFoodSearchValues[2]
                picks = lastFoodSearchValues[3]
            else:
                relevant_id = request.POST.getlist("choices")
                food_names = request.POST.getlist("food_name")
                quantities = request.POST.getlist("namequantity")
                picks = request.POST.getlist("GroupPicks")

            if relevant_id:
                nutrValues_list = []
                for choice in relevant_id:
                    choice_index, food_id = choice.split("_", 1)
                    choice_index = int(choice_index)
                    quantity = quantities[choice_index]
                    if quantity == "":
                        quantity = "1"
                    elif quantity[0] == "-":
                        quantity = quantity[1:]
                    measure = picks[choice_index]
                    grams = round(float(measure) * float(quantity), 3)
                    data = getValuesFromEDAMAM(food_id, grams)
                    data["food_name"] = food_names[choice_index]
                    data["Grams"] = grams
                    nutrValues_list.append(data)
                if nutrValues_list:
                    context["data"] = nutrValues_list
                else:
                    return search_food_helper(request)
            else:
                return search_food_helper(request)

        context["userDiaries"] = DiaryDetails.objects.filter(user=request.user).all()
        response = render(request, 'main/active_viewing_search_food_results.html', context)

        if code == 31:
            cache.set(caches[2], [relevant_id, food_names, quantities, picks])
        if code != 33:
            cache.set(caches[3], context["data"])

    elif code == 41:
        if request.POST.get("FoodToAdd"):
            post = request.POST.copy()
            post.update(eval(request.POST.get("FoodToAdd")))
            request.POST = post
            add_food_note(request, request.POST.get("DiaryNumber"))
            code = 33
            return search_food_helper(request, code)
        elif request.POST.get("FoodToDelete"):
            diary = DiaryDetails.objects.get(pk=request.POST.get("DiaryNumber"))
            search = eval(request.POST.get("FoodToDelete"))
            note = Diet.objects.filter(user=diary, **search).first()
            if note:
                note.delete()
                diary.update
            code = 33
            return search_food_helper(request, code)

            request.POST = post
            add_food_note(request, request.POST.get("AddToDiary"))
            code = 33
            return search_food_helper(request, code)

    return response


@login_required(login_url="/login")
def search_food(request):



    if request.method == 'POST':
        print(request.POST)
        if request.POST.get("FoodToAdd") or request.POST.get("FoodToDelete"):
            code = 41
            response = search_food_helper(request, code)

        elif request.POST.get("lastFoodSearch"):
            form = SearchFoodForm({"search": request.POST.get("lastFoodSearch")})
            if form.is_valid():
                if cache.get('lastFoodSearchLabels'):
                    code = 23
                    response = search_food_helper(request, code)
                else:
                    code = 22
                    response = search_food_helper(request, code)
            else:
                code = 11
                response = search_food_helper(request, code)

        elif request.POST.get("lastFoodSearchLabels"):
            if cache.get('lastFoodSearchValues'):
                code = 33
                response = search_food_helper(request, code)
            else:
                code = 32
                response = search_food_helper(request, code)

        elif request.POST.get("lastFoodSearchValues"):
            code = 33
            response = search_food_helper(request, code)

        elif request.POST.getlist("choices"):
            code = 31
            response = search_food_helper(request, code)

        else:
            form = SearchFoodForm(request.POST)
            if form.is_valid():
                code = 21
                response = search_food_helper(request, code)
            else:
                code = 11
                response = search_food_helper(request, code)

    else:
        lastFoodSearch = cache.get('lastFoodSearch')
        if lastFoodSearch:
            code = 10
            response = search_food_helper(request, code)
        else:
            code = 11
            response = search_food_helper(request, code)

    return response

