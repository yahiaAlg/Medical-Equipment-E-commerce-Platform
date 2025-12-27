from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q, Avg
import json

from .models import Product, Category, Brand, ProductReview, ProductQuestion, Wishlist
from .forms import ProductReviewForm, ProductQuestionForm

def product_list(request):
    products = Product.objects.all().select_related('brand', 'category').prefetch_related('images')
    categories = Category.objects.all()
    brands = Brand.objects.all()
    
    # Filtering
    category_filter = request.GET.get('category')
    brand_filter = request.GET.get('brand')
    specialty_filter = request.GET.get('specialty')
    price_min = request.GET.get('price_min')
    price_max = request.GET.get('price_max')
    availability = request.GET.get('availability')
    sort_by = request.GET.get('sort', 'name')
    
    if category_filter:
        products = products.filter(category__slug=category_filter)
    
    if brand_filter:
        products = products.filter(brand_id=brand_filter)
    
    if specialty_filter:
        products = products.filter(specialty=specialty_filter)
    
    if price_min:
        products = products.filter(price__gte=price_min)
    
    if price_max:
        products = products.filter(price__lte=price_max)
    
    if availability:
        products = products.filter(availability_status=availability)
    
    # Sorting
    if sort_by == 'price_low':
        products = products.order_by('price')
    elif sort_by == 'price_high':
        products = products.order_by('-price')
    elif sort_by == 'newest':
        products = products.order_by('-created_at')
    elif sort_by == 'rating':
        products = products.annotate(avg_rating=Avg('reviews__rating')).order_by('-avg_rating')
    else:
        products = products.order_by('name')
    
    # Pagination
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'categories': categories,
        'brands': brands,
        'current_filters': {
            'category': category_filter,
            'brand': brand_filter,
            'specialty': specialty_filter,
            'price_min': price_min,
            'price_max': price_max,
            'availability': availability,
            'sort': sort_by,
        },
        'specialties': Product.SPECIALTIES,
        'availability_choices': Product.AVAILABILITY_STATUS,
    }
    
    return render(request, 'products/list.html', context)

def search(request):
    query = request.GET.get('q', '')
    products = Product.objects.none()
    
    if query:
        products = Product.objects.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(short_description__icontains=query) |
            Q(brand__name__icontains=query) |
            Q(category__name__icontains=query)
        ).select_related('brand', 'category').prefetch_related('images')
    
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'query': query,
        'total_results': products.count(),
    }
    
    return render(request, 'products/search_results.html', context)

def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug)
    products = Product.objects.filter(category=category).select_related('brand').prefetch_related('images')
    
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'category': category,
        'page_obj': page_obj,
    }
    
    return render(request, 'products/category_detail.html', context)

def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    reviews = ProductReview.objects.filter(product=product).select_related('user')
    questions = ProductQuestion.objects.filter(product=product).select_related('user', 'answered_by')
    related_products = Product.objects.filter(category=product.category).exclude(id=product.id)[:4]
    
    # Check if user has this product in wishlist
    in_wishlist = False
    if request.user.is_authenticated:
        wishlist, created = Wishlist.objects.get_or_create(user=request.user)
        in_wishlist = wishlist.products.filter(id=product.id).exists()
    
    context = {
        'product': product,
        'reviews': reviews,
        'questions': questions,
        'related_products': related_products,
        'in_wishlist': in_wishlist,
        'review_form': ProductReviewForm(),
        'question_form': ProductQuestionForm(),
    }
    
    return render(request, 'products/detail.html', context)

@login_required
def toggle_wishlist(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        product_id = data.get('product_id')
        
        try:
            product = Product.objects.get(id=product_id)
            wishlist, created = Wishlist.objects.get_or_create(user=request.user)
            
            if wishlist.products.filter(id=product_id).exists():
                wishlist.products.remove(product)
                added = False
            else:
                wishlist.products.add(product)
                added = True
            
            return JsonResponse({
                'success': True,
                'added': added,
                'message': 'Added to wishlist' if added else 'Removed from wishlist'
            })
        except Product.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Product not found'})
    
    return JsonResponse({'success': False, 'message': 'Invalid request'})

@login_required
def add_review(request):
    if request.method == 'POST':
        form = ProductReviewForm(request.POST)
        if form.is_valid():
            product_id = request.POST.get('product_id')
            try:
                product = Product.objects.get(id=product_id)
                
                # Check if user already reviewed this product
                existing_review = ProductReview.objects.filter(
                    product=product, 
                    user=request.user
                ).first()
                
                if existing_review:
                    messages.error(request, 'You have already reviewed this product.')
                else:
                    review = form.save(commit=False)
                    review.product = product
                    review.user = request.user
                    review.save()
                    messages.success(request, 'Your review has been added successfully!')
                
            except Product.DoesNotExist:
                messages.error(request, 'Product not found.')
        
        return redirect('products:detail', slug=request.POST.get('product_slug'))
    
    return redirect('products:list')

@login_required
def ask_question(request):
    if request.method == 'POST':
        form = ProductQuestionForm(request.POST)
        if form.is_valid():
            product_id = request.POST.get('product_id')
            try:
                product = Product.objects.get(id=product_id)
                question = form.save(commit=False)
                question.product = product
                question.user = request.user
                question.save()
                messages.success(request, 'Your question has been submitted successfully!')
                
            except Product.DoesNotExist:
                messages.error(request, 'Product not found.')
        
        return redirect('products:detail', slug=request.POST.get('product_slug'))
    
    return redirect('products:list')