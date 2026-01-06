from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Product, Order, OrderItem
from .forms import UserRegisterForm, UserLoginForm, OrderForm, ProductForm
from django.contrib.auth.decorators import login_required, user_passes_test

# --- Auth Views ---
def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Welcome {user.username}! Your account is created.')
            return redirect('shop')
    else:
        form = UserRegisterForm()
    return render(request, 'register.html', {'form': form})

def custom_logout(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('login')

# --- Shop Views ---
def shop(request):
    products = Product.objects.all().order_by('-created_at')
    return render(request, 'shop.html', {'products': products})

def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'product_detail.html', {'product': product})

# --- Cart Logic (Session Based) ---
def add_to_cart(request, pk):
    cart = request.session.get('cart', {})
    cart[str(pk)] = cart.get(str(pk), 0) + 1
    request.session['cart'] = cart
    messages.success(request, "Item added to cart!")
    return redirect('shop')

def remove_from_cart(request, pk):
    cart = request.session.get('cart', {})
    if str(pk) in cart:
        del cart[str(pk)]
        request.session['cart'] = cart
    return redirect('cart_detail')

def cart_detail(request):
    cart = request.session.get('cart', {})
    cart_items = []
    total_price = 0
    
    products = Product.objects.filter(id__in=cart.keys())
    
    for product in products:
        quantity = cart[str(product.id)]
        subtotal = product.price * quantity
        total_price += subtotal
        cart_items.append({
            'product': product,
            'quantity': quantity,
            'subtotal': subtotal
        })
    
    return render(request, 'cart_detail.html', {'cart_items': cart_items, 'total_price': total_price})

@login_required
def checkout(request):
    cart = request.session.get('cart', {})
    if not cart:
        messages.warning(request, "Your cart is empty.")
        return redirect('shop')
        
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            # Calculate total again for security
            total = 0
            products = Product.objects.filter(id__in=cart.keys())
            for p in products:
                total += p.price * cart[str(p.id)]
            
            # Create Order
            order = form.save(commit=False)
            order.user = request.user
            order.total_amount = total
            order.save()
            
            # Create Order Items
            for p in products:
                OrderItem.objects.create(
                    order=order,
                    product=p,
                    quantity=cart[str(p.id)],
                    price=p.price
                )
            
            # Clear Cart
            request.session['cart'] = {}
            messages.success(request, "Your order has been placed successfully!")
            return redirect('my_orders')
    else:
        form = OrderForm()
        
    # Calculate total for display
    total_price = 0
    products = Product.objects.filter(id__in=cart.keys())
    for p in products:
        total_price += p.price * cart[str(p.id)]
        
    return render(request, 'checkout.html', {'form': form, 'total_price': total_price})

@login_required
def my_orders(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'my_orders.html', {'orders': orders})

# --- Admin Views ---
@user_passes_test(lambda u: u.is_superuser)
def admin_dashboard(request):
    products = Product.objects.all().order_by('-created_at')
    orders = Order.objects.all().order_by('-created_at')[:5] # Show recent 5 orders
    return render(request, 'admin_dashboard.html', {'products': products, 'orders': orders})

@user_passes_test(lambda u: u.is_superuser)
def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product added successfully!')
            return redirect('admin_dashboard')
    else:
        form = ProductForm()
    return render(request, 'admin_product_form.html', {'form': form, 'title': 'Add Product'})

@user_passes_test(lambda u: u.is_superuser)
def edit_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product updated successfully!')
            return redirect('admin_dashboard')
    else:
        form = ProductForm(instance=product)
    return render(request, 'admin_product_form.html', {'form': form, 'title': 'Edit Product'})

@user_passes_test(lambda u: u.is_superuser)
def delete_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.delete()
        messages.success(request, 'Product deleted successfully!')
        return redirect('admin_dashboard')
    return render(request, 'admin_product_confirm_delete.html', {'product': product})
