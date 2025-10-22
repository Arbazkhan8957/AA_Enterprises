# main_app/views.py

from django.shortcuts import render, get_object_or_404
from .models import Product, Category, Brand
from django.shortcuts import render, redirect
from .forms import ContactForm
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from .forms import RegisterForm, LoginForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.views import PasswordChangeView
from django.urls import reverse
from django.core.mail import send_mail  # if you want email back-end
from django.conf import settings

from .models import Enquiry

from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from .forms import UserUpdateForm, ProfileUpdateForm
from .models import Profile
from django.contrib.auth.hashers import check_password


def home_view(request):
    # Get top 6 brands (adjust filter/order as needed)
    brands_top = Brand.objects.all()[:6]

    # Get featured products (you can adjust filter here too)
    products = Product.objects.all()[:6]

    context = {
        'brands_top': brands_top,
        'products': products
    }
    return render(request, 'index.html', context)

def register_view(request):
    if request.user.is_authenticated:
        return redirect("login")
    form = RegisterForm(request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect(request.GET.get("next") or "login")
        else:
            messages.error(request, "Please correct the errors below.")
    return render(request, "auth/register.html", {"form": form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect("index")
    form = LoginForm(request, data=request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect(request.GET.get("next") or "index")
        else:
            messages.error(request, "Invalid username or password.")
    return render(request, "auth/login.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect("login")


@login_required
def dashboard_view(request):
    return render(request, "auth/dashboard.html")


def index(request):
    return render(request, 'index.html', {
        'products': Product.objects.all()[:6],
        'brands_top': Brand.objects.all(),
    })

def about(request):
    return render(request, 'about.html')

@login_required
def product_list(request):
    products = Product.objects.all()
    categories = Category.objects.all()
    return render(request, 'products/products.html', {'products': products, 'categories': categories})

@login_required
def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'products/product_detail.html', {'product': product})

def contact_view(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            # Save to database
            Enquiry.objects.create(
                name=form.cleaned_data['name'],
                email=form.cleaned_data['email'],
                phone=form.cleaned_data['phone'],
                message=form.cleaned_data['message']
            )

            # Optional: send email
            try:
                send_mail(
                    subject=f"New enquiry from {form.cleaned_data['name']}",
                    message=f"Name: {form.cleaned_data['name']}\nEmail: {form.cleaned_data['email']}\nPhone: {form.cleaned_data['phone']}\n\nMessage:\n{form.cleaned_data['message']}",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[settings.DEFAULT_FROM_EMAIL],
                    fail_silently=True,
                )
            except Exception:
                pass

            # Add Django message
            messages.success(request, "Your enquiry has been sent successfully!")

            # Redirect to same page (so page refresh won't resubmit the form)
            return redirect('contact')
    else:
        form = ContactForm()

    return render(request, "contact.html", {"form": form})

@login_required
def brands(request):
    brands = Brand.objects.all()
    return render(request, 'brands.html', {'brands': brands})

@login_required
def product_list(request):
    category_id = request.GET.get('category')
    if category_id:
        products = Product.objects.filter(category_id=category_id)
    else:
        products = Product.objects.all()
    categories = Category.objects.all()
    return render(request, 'products/products.html', {'products': products, 'categories': categories})

@login_required
def profile_view(request):
    user = request.user
    profile, _ = Profile.objects.get_or_create(user=user)

    if request.method == 'POST':
        action = request.POST.get('action')

        # Profile Update
        if action == 'update_profile':
            user.first_name = request.POST.get('first_name')
            user.last_name = request.POST.get('last_name')
            user.email = request.POST.get('email')
            user.save()

            if 'image' in request.FILES:
                profile.image = request.FILES['image']
                profile.save()

            messages.success(request, 'Profile updated successfully.')

        # Password Change
        elif action == 'update_password':
            current = request.POST.get('current_password')
            new = request.POST.get('new_password')
            confirm = request.POST.get('confirm_new_password')

            if not user.check_password(current):
                messages.error(request, 'Current password is incorrect.')
            elif new != confirm:
                messages.error(request, 'New passwords do not match.')
            else:
                user.set_password(new)
                user.save()
                update_session_auth_hash(request, user)
                messages.success(request, 'Password changed successfully.')

        return redirect('profile')  # Redirect ensures flash messages are shown once

    return render(request, 'profile.html', {'user': user, 'profile': profile})

@login_required
def update_profile_view(request):
    user = request.user
    profile = user.profile  # assumes a OneToOne field

    if request.method == 'POST':
        if 'update_profile' in request.POST:
            user.username = request.POST['username']
            user.first_name = request.POST['first_name']
            user.last_name = request.POST['last_name']
            user.email = request.POST['email']

            if 'profile_image' in request.FILES:
                profile.image = request.FILES['profile_image']

            user.save()
            profile.save()
            return render(request, 'profile.html', {'updated_profile_successfully': True})

        elif 'change_password' in request.POST:
            current = request.POST['current_password']
            new = request.POST['new_password']
            confirm = request.POST['confirm_password']

            if not user.check_password(current):
                return render(request, 'profile.html', {'password_error': "Current password incorrect"})
            if new != confirm:
                return render(request, 'profile.html', {'password_error': "Passwords do not match"})

            user.set_password(new)
            user.save()
            update_session_auth_hash(request, user)
            return render(request, 'profile.html', {'updated_password_successfully': True})

    return render(request, 'profile.html')

class CustomPasswordChangeView(PasswordChangeView):
    template_name = 'change_password.html'
    success_url = reverse_lazy('password_change_done')

