from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView, PasswordResetView, PasswordChangeView
from django.contrib.messages.views import SuccessMessageMixin
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views import generic

from .daymodel import Post, Like
from .forms import RegisterForm, LoginForm, UpdateUserForm, UpdateProfileForm, PostForm

try:
    from django.utils import simplejson as json
except ImportError:
    import json
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required


@login_required
def home(request):
    return render(request, 'users/home.html')


class RegisterView(View):
    form_class = RegisterForm
    initial = {'key': 'value'}
    template_name = 'users/register.html'

    def dispatch(self, request, *args, **kwargs):
        # will redirect to the home page if a user tries to access the register page while logged in
        if request.user.is_authenticated:
            return redirect(to='/')

        # else process dispatch as it otherwise normally would
        return super(RegisterView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        form = self.form_class(initial=self.initial)
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)

        if form.is_valid():
            form.save()

            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}')

            return redirect(to='login')

        return render(request, self.template_name, {'form': form})


# Class based view that extends from the built in login view to add a remember me functionality
class CustomLoginView(LoginView):
    form_class = LoginForm

    def form_valid(self, form):
        remember_me = form.cleaned_data.get('remember_me')

        if not remember_me:
            # set session expiry to 0 seconds. So it will automatically close the session after the browser is closed.
            self.request.session.set_expiry(0)

            # Set session as modified to force data updates/cookie to be saved.
            self.request.session.modified = True

        # else browser session will be as long as the session cookie time "SESSION_COOKIE_AGE" defined in settings.py
        return super(CustomLoginView, self).form_valid(form)


class ResetPasswordView(SuccessMessageMixin, PasswordResetView):
    template_name = 'users/password_reset.html'
    email_template_name = 'users/password_reset_email.html'
    subject_template_name = 'users/password_reset_subject'
    success_message = "We've emailed you instructions for setting your password, " \
                      "if an account exists with the email you entered. You should receive them shortly." \
                      " If you don't receive an email, " \
                      "please make sure you've entered the address you registered with, and check your spam folder."
    success_url = reverse_lazy('users-home')


class ChangePasswordView(SuccessMessageMixin, PasswordChangeView):
    template_name = 'users/change_password.html'
    success_message = "Successfully Changed Your Password"
    success_url = reverse_lazy('users-home')


@login_required
def profile(request):
    if request.method == 'POST':
        user_form = UpdateUserForm(request.POST, instance=request.user)
        profile_form = UpdateProfileForm(request.POST, request.FILES, instance=request.user.profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile is updated successfully')
            return redirect(to='users-profile')
    else:
        user_form = UpdateUserForm(instance=request.user)
        profile_form = UpdateProfileForm(instance=request.user.profile)

    return render(request, 'users/profile.html',
                  {'user_form': user_form, 'profile_form': profile_form, })


class PostList(generic.ListView):
    queryset = Post.objects.filter(status=1).order_by('-created_on')
    template_name = 'users/postlist.html'


class PostDetail(generic.DetailView):
    model = Post
    template_name = 'users/post_detail.html'


@login_required
# create view
def post_create(request):
    form = PostForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            instance = form.save(commit=False)
            instance.created_by_user = request.user
            form.save()
            messages.success(request, 'Your Court Day post was successfully created!')
        return HttpResponseRedirect('/posts/')

    context = {'form': form,
               }

    return render(request, 'users/post_create.html', context)


# list view
def post_list(request):
    allposts = Post.objects.all()

    context = {'allposts': allposts,
               }

    return render(request, 'users/postlist.html', context)


@login_required
# detail view
def post_detail(request, url=None):
    post = get_object_or_404(Post, url=url)

    context = {'post': post, 'url': url,
               }

    if request.method == "POST":
        post_id = request.POST.get('post_id')
        # make sure user can't like the post more than once: request.user.username
        user = User.objects.get(username=request.user.username)
        # find whatever post is associated with like
        post = Post.objects.get(url=url)

        if user in post.user_likes.all():
            post.user_likes.remove(user)
        else:
            post.user_likes.add(user)

        like, created = Like.objects.get_or_create(user=user, post_id=post_id)

        if not created:
            if like.value == 'Im Coming & Playing this day (Sign Up)':
                like.value = 'You are already Signed up to join. Change your presence -> (Sign out)'
            else:
                like.value = 'Im Coming & Playing this day (Sign Up)'
        else:
            like.value = 'Im Coming & Playing this day (Sign Up)'

            post.save()
            like.save()

    return render(request, 'users/post_detail.html', context)
