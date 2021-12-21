from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import Group
from django.http import HttpResponse
from django.shortcuts import render, redirect

from .decorators import unauthenticated_user, admin_only, allowed_users, superuser_only
from .models import *
from .forms import OrderForm, CreateUserForm, UpdateOrderForm, UpdateCustomerForm
from .filters import OrderFilter


# Create your views here.

@login_required(login_url='login')
@admin_only
@superuser_only
def home(request):
    customers = Customer.objects.all()
    orders = Order.objects.all()

    total_orders = orders.count()

    delivered = orders.filter(status='Delivered').count()
    pending = orders.filter(status='Pending').count()

    context = {'customers': customers, 'orders': orders,
               'total_orders': total_orders,
               'pending_count': pending, 'delivered_count': delivered}
    return render(request, 'accounts/dashboard.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def products(request):
    products = Product.objects.all()
    return render(request, 'accounts/products.html', {'products': products})


@login_required(login_url='login')
@superuser_only
def customer(request, pk_customer):
    cr = Customer.objects.get(id=pk_customer)
    orders = cr.order_set.all()

    myFilter = OrderFilter(request.GET, queryset=orders)
    orders = myFilter.qs

    orders_count = orders.count()
    context = {'customer': cr, 'myFilter': myFilter, 'orders': orders,
               'orders_count': orders_count}
    return render(request, 'accounts/customer.html', context)


@login_required(login_url='login')
def userPage(request):
    orders = request.user.customer.order_set.all()
    print('Orders:', orders)

    total_orders = orders.count()
    delivered = orders.filter(status='Delivered').count()
    pending = orders.filter(status='Pending').count()

    context = {'orders': orders, 'total_orders': total_orders, 'delivered_count': delivered, 'pending_count': pending}
    return render(request, 'accounts/user.html', context)


@login_required(login_url='login')
def update_customer(request, pk_customer):
    customer = Customer.objects.get(id=pk_customer)
    form = UpdateCustomerForm(instance=customer)
    if request.method == 'POST':
        form = UpdateCustomerForm(request.POST, instance=customer)
        if form.is_valid():
            form.save()
            return redirect('/')

    context = {'form': form}
    return render(request, 'accounts/update_customer.html', context)


@login_required(login_url='login')
@superuser_only
def createOrder(request):
    form = OrderForm()
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/')
    context = {'form': form}

    return render(request, 'accounts/order_form.html', context)


@login_required(login_url='login')
@superuser_only
def updateOrder(request, pk):
    order = Order.objects.get(id=pk)
    form = UpdateOrderForm(instance=order)
    if request.method == 'POST':
        form = UpdateOrderForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            return redirect('/')

    context = {'form': form}

    return render(request, 'accounts/update_order_form.html', context)


@login_required(login_url='login')
@superuser_only
def deleteOrder(request, pk):
    order = Order.objects.get(id=pk)
    if request.method == 'POST':
        order.delete()
        return redirect('/')
    context = {'item': order}
    return render(request, 'accounts/delete.html', context)


@unauthenticated_user
def registerPage(request):
    form = CreateUserForm()
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')

            group = Group.objects.get(name="customer")
            user.groups.add(group)

            Customer.objects.create(user=user, name=user.username)

            messages.success(request, 'Account was created for ' + username)
    context = {'form': form}
    return render(request, 'accounts/register.html', context)


@unauthenticated_user
def loginPage(request):
    if request.user.is_authenticated:
        return redirect('home')
    else:
        if request.method == 'POST':
            username = request.POST.get('username')
            password = request.POST.get('password')
            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                return redirect('home')
            else:
                messages.info(request, 'Username OR password is incorrect')

        return render(request, 'accounts/login.html')


def logoutUser(request):
    logout(request)
    return redirect('login')


@login_required(login_url='login')
@superuser_only
def deleteCustomer(request, pk_customer):
    customer = Customer.objects.get(id=pk_customer)
    if request.method == 'POST':
        customer.delete()
        return redirect('/')
    context = {'customer': customer}
    return render(request, 'accounts/delete_customer.html', context)
