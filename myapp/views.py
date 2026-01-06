from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import Product, Order, OrderItem, Wishlist
from .forms import UserRegisterForm, UserLoginForm, OrderForm, ProductForm

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

# --- User Views ---
@login_required
def user_dashboard(request):
    user_orders = Order.objects.filter(user=request.user).order_by('-created_at')
    wishlist_items = Wishlist.objects.filter(user=request.user).select_related('product')
    
    context = {
        'orders': user_orders,
        'wishlist_items': wishlist_items
    }
    return render(request, 'user_dashboard.html', context)

@login_required
def toggle_wishlist(request, pk):
    product = get_object_or_404(Product, pk=pk)
    wishlist_item, created = Wishlist.objects.get_or_create(user=request.user, product=product)
    
    if created:
        messages.success(request, f"Added {product.name} to wishlist.")
    else:
        wishlist_item.delete()
        messages.info(request, f"Removed {product.name} from wishlist.")
        
    return redirect('request.META.get("HTTP_REFERER", "shop")')    # Redirect back to same page

# --- Shop Views ---
def shop(request):
    products = Product.objects.all().order_by('-created_at')
    return render(request, 'shop.html', {'products': products})

def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    in_wishlist = False
    if request.user.is_authenticated:
        in_wishlist = Wishlist.objects.filter(user=request.user, product=product).exists()
    return render(request, 'product_detail.html', {'product': product, 'in_wishlist': in_wishlist})

# --- Cart Logic ---
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
            total = 0
            products = Product.objects.filter(id__in=cart.keys())
            for p in products:
                total += p.price * cart[str(p.id)]
            
            order = form.save(commit=False)
            order.user = request.user
            order.total_amount = total
            order.save()
            
            for p in products:
                OrderItem.objects.create(
                    order=order, product=p, quantity=cart[str(p.id)], price=p.price
                )
            
            request.session['cart'] = {}
            messages.success(request, "Your order has been placed successfully!")
            return redirect('user_dashboard')
    else:
        form = OrderForm()
        
    total_price = 0
    products = Product.objects.filter(id__in=cart.keys())
    for p in products:
        total_price += p.price * cart[str(p.id)]
        
    return render(request, 'checkout.html', {'form': form, 'total_price': total_price})

# --- Admin Views ---
@user_passes_test(lambda u: u.is_superuser)
def admin_dashboard(request):
    products = Product.objects.all().order_by('-created_at')
    orders = Order.objects.all().order_by('-created_at') # All orders
    return render(request, 'admin_dashboard.html', {'products': products, 'orders': orders})

@user_passes_test(lambda u: u.is_superuser)
def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST) # Removing files argument for now as ImageField is gone
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
        form = ProductForm(request.POST, instance=product)
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
