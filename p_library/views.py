from allauth.socialaccount.models import SocialAccount
from django.http import HttpResponse
from django.template import loader
from django.shortcuts import redirect, render
from p_library.models import Book, UserProfile
from p_library.models import Publisher
from p_library.models import Author
from p_library.models import Friend
from p_library.forms import AuthorForm, BookForm, FriendForm, ProfileCreationForm
from django.views.generic import CreateView, ListView, UpdateView, DeleteView, FormView
from django.urls import reverse_lazy
from django.forms import formset_factory
from django.http.response import HttpResponseRedirect, JsonResponse
from allauth.account.views import SignupView, LoginView, LogoutView


# Переопределение allauth.account.views
class PLibrarySignupView(SignupView):
    template_name = 'allauth/account/signup.html'


class PLibraryLoginView(LoginView):
    template_name = 'allauth/account/login.html'


class PLibraryLogoutView(LogoutView):
    template_name = 'allauth/account/logout.html'

# ---------------------------------------


def index(request):
    template = loader.get_template('index.html')
    context = {}
    if request.user.is_authenticated:
        try:
            context['username'] = request.user.username
            context['age'] = UserProfile.objects.get(user=request.user).age
            context['github_url'] = SocialAccount.objects.get(provider='github', user=request.user).extra_data['html_url']
        except:
            pass

    return HttpResponse(template.render(context, request))


def links(request):
    template = loader.get_template('links.html')
    data = {
        "title": "Все роуты проекта",
    }
    return HttpResponse(template.render(data, request))


def books_list(request):
    books = Book.objects.all()
    return HttpResponse(books)


def books_list_index(request):
    template = loader.get_template('books_list_index.html')
    books = Book.objects.all()
    biblio_data = {
        "title": "мою библиотеку",
        "books": books,
    }
    return HttpResponse(template.render(biblio_data, request))


def book_increment(request):
    if request.method == 'POST':
        book_id = request.POST['id']
        if not book_id:
            return redirect('/books_list_index/')
        else:
            book = Book.objects.filter(id=book_id).first()
            if not book:
                return redirect('/books_list_index/')
            book.copy_count += 1
            book.save()
        return redirect('/books_list_index/')
    else:
        return redirect('/books_list_index/')


def book_decrement(request):
    if request.method == 'POST':
        book_id = request.POST['id']
        if not book_id:
            return redirect('/books_list_index/')
        else:
            book = Book.objects.filter(id=book_id).first()
            if not book:
                return redirect('/books_list_index/')
            if book.copy_count < 1:
                book.copy_count = 0
            else:
                book.copy_count -= 1
            book.save()
        return redirect('/books_list_index/')
    else:
        return redirect('/books_list_index/')


def publishers(request):
    template = loader.get_template('publishers.html')
    publishers = Publisher.objects.all()
    books = Book.objects.all()
    publishers_data = {
        "title": "Издательства",
        "publishers": publishers,
        "books": books,
    }
    return HttpResponse(template.render(publishers_data, request))


def friends(request):
    template = loader.get_template('friends.html')
    friends = Friend.objects.all()
    books = Book.objects.all()
    friends_data = {
        "title": "Список друзей",
        "friends": friends,
        "books": books,
    }
    return HttpResponse(template.render(friends_data, request))


class AuthorEdit(CreateView):
    model = Author
    form_class = AuthorForm
    success_url = reverse_lazy('author_list')
    template_name = 'author_edit.html'


class AuthorList(ListView):
    model = Author
    template_name = 'authors_list.html'


class FriendEdit(CreateView):
    model = Friend
    form_class = FriendForm
    success_url = reverse_lazy('friends_list')
    template_name = 'friend_edith.html'


class FriendUpdate(UpdateView):
    model = Friend
    success_url = reverse_lazy('friends_list')
    fields = ['full_name', 'book']
    template_name = 'friend_edith.html'


class FriendDelete(DeleteView):
    model = Friend
    form_class = FriendForm
    fields = ['full_name']
    success_url = reverse_lazy('friends_list')
    template_name = 'friends_delete.html'


def author_create_many(request):
    #  Первым делом, получим класс, который будет создавать наши формы.
    #  Обратите внимание на параметр `extra`, в данном случае он равен двум, это значит,
    #  что на странице с несколькими формами изначально будет появляться 2 формы создания авторов.
    AuthorFormSet = formset_factory(AuthorForm, extra=2)

    #  Наш обработчик будет обрабатывать и GET и POST запросы.
    # POST запрос будет содержать в себе уже заполненные данные формы
    if request.method == 'POST':
        user = request.user
        if not user.is_superuser:
            return JsonResponse(data={"error": "У вас нет доступа"}, status=403)

        #  Здесь мы заполняем формы формсета теми данными, которые пришли в запросе.
        #  Обратите внимание на параметр `prefix`. Мы можем иметь на странице не только несколько форм,
        #  но и разных формсетов, этот параметр позволяет их отличать в запросе.
        author_formset = AuthorFormSet(request.POST, request.FILES, prefix='authors')

        #  Проверяем, валидны ли данные формы
        if author_formset.is_valid():
            for author_form in author_formset:
                #  Сохраним каждую форму в формсете
                author_form.save()

            #  После чего, переадресуем браузер на список всех авторов.
            return HttpResponseRedirect(reverse_lazy('"p_library:author_list'))

    #  Если обработчик получил GET запрос, значит в ответ нужно просто "нарисовать" формы.
    else:
        #  Инициализируем формсет и ниже передаём его в контекст шаблона.
        author_formset = AuthorFormSet(prefix='authors')

    return render(request, 'manage_authors.html', {'author_formset': author_formset})


def books_authors_create_many(request):
    AuthorFormSet = formset_factory(AuthorForm, extra=2)
    BookFormSet = formset_factory(BookForm, extra=2)
    if request.method == 'POST':
        user = request.user
        if not user.is_superuser:
            return JsonResponse(data={"error": "У вас нет доступа"}, status=403)

        author_formset = AuthorFormSet(request.POST, request.FILES, prefix='authors')
        book_formset = BookFormSet(request.POST, request.FILES, prefix='books')
        if author_formset.is_valid() and book_formset.is_valid():
            for author_form in author_formset:
                author_form.save()
            for book_form in book_formset:
                book_form.save()
            return HttpResponseRedirect(reverse_lazy('p_library:author_list'))
    else:
        author_formset = AuthorFormSet(prefix='authors')
        book_formset = BookFormSet(prefix='books')
    return render(
        request,
        'manage_books_authors.html',
        {
            'author_formset': author_formset,
            'book_formset': book_formset,
        }
    )


# Создание пользователского профиля, включает задание возраста пользователя.
class CreateUserProfile(FormView):
    form_class = ProfileCreationForm
    template_name = 'profile-create.html'
    success_url = reverse_lazy('p_library:links')

    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_anonymous:
            return HttpResponseRedirect(reverse_lazy('p_library:PLibraryLoginView'))
        return super(CreateUserProfile, self).dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        instance = form.save(commit=False)
        instance.user = self.request.user
        instance.save()
        return super(CreateUserProfile, self).form_valid(form)


