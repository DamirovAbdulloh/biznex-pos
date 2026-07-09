from django.shortcuts import render, redirect, get_object_or_404
from .models import Product, Category
from biznex.utils import safe_decimal

def product_list(request):
    cat_id = request.GET.get('cat')
    q = request.GET.get('q', '')
    products = Product.objects.filter(is_active=True).select_related('category').order_by('order', 'id')
    if cat_id:
        products = products.filter(category_id=cat_id)
    if q:
        products = products.filter(name__icontains=q)
    categories = Category.objects.all()
    products_total_count = Product.objects.filter(is_active=True).count()
    return render(request, 'products/list.html', {
        'products': products, 'categories': categories,
        'selected_cat': cat_id, 'q': q, 'active_page': 'products',
        'products_total_count': products_total_count,
    })

def product_detail(request, pk):
    """Taom haqida batafsil: tan narx, sotish narxi, foyda marjasi, sotuv statistikasi"""
    from datetime import date as date_cls
    product = get_object_or_404(Product, pk=pk)

    date_str = request.GET.get('date_from')
    date_to_str = request.GET.get('date_to')
    date_from = None
    date_to = None
    if date_str:
        try:
            date_from = date_cls.fromisoformat(date_str)
        except ValueError:
            pass
    if date_to_str:
        try:
            date_to = date_cls.fromisoformat(date_to_str)
        except ValueError:
            pass

    stats = product.get_sales_stats(date_from=date_from, date_to=date_to)

    return render(request, 'products/detail.html', {
        'product': product,
        'stats': stats,
        'date_from': date_from,
        'date_to': date_to,
        'active_page': 'products',
    })

def product_create(request):
    if request.method == 'POST':
        Product.objects.create(
            name=request.POST.get('name', '').strip() or 'Nomsiz taom',
            category_id=request.POST.get('category') or None,
            price=safe_decimal(request.POST.get('price')),
            cost_price=safe_decimal(request.POST.get('cost_price')),
            quantity=safe_decimal(request.POST.get('quantity')),
            unit=request.POST.get('unit', 'dona'),
        )
        return redirect('products:list')
    categories = Category.objects.all()
    return render(request, 'products/form.html', {'categories': categories, 'active_page': 'products'})

def product_edit(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.name = request.POST.get('name', '').strip() or product.name
        product.category_id = request.POST.get('category') or None
        product.price = safe_decimal(request.POST.get('price'))
        product.cost_price = safe_decimal(request.POST.get('cost_price'))
        product.quantity = safe_decimal(request.POST.get('quantity'))
        product.unit = request.POST.get('unit', 'dona')
        product.save()
        return redirect('products:list')
    categories = Category.objects.all()
    return render(request, 'products/form.html', {'product': product, 'categories': categories, 'active_page': 'products'})

def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    product.is_active = False
    product.save()
    return redirect('products:list')


def product_reorder(request):
    """Admin/kassir Taomlar ro'yxatida kartalarni sudrab (drag & drop) tartibini o'zgartirganda
    chaqiriladi. Faqat yuborilgan (odatda joriy filtrdagi) mahsulotlarning tartib raqami yangilanadi,
    ular avvalgi eng kichik tartib qiymati atrofida joylashtiriladi — shunday qilib boshqa
    kategoriyalardagi taomlarning tartibi buzilmaydi."""
    from django.http import JsonResponse
    import json
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'POST kerak'}, status=405)
    try:
        data = json.loads(request.body)
        ordered_ids = [int(i) for i in data.get('order', [])]
    except (ValueError, TypeError, json.JSONDecodeError):
        return JsonResponse({'success': False, 'error': "Noto'g'ri so'rov"}, status=400)

    if not ordered_ids:
        return JsonResponse({'success': True})

    products = list(Product.objects.filter(pk__in=ordered_ids))
    products_by_id = {p.pk: p for p in products}
    existing_orders = [p.order for p in products]
    base = min(existing_orders) if existing_orders else 0

    for idx, pid in enumerate(ordered_ids):
        p = products_by_id.get(pid)
        if p:
            p.order = base + idx
            p.save(update_fields=['order'])

    return JsonResponse({'success': True})

def category_list(request):
    if request.method == 'POST':
        Category.objects.create(name=request.POST.get('name', '').strip() or 'Nomsiz kategoriya', code=request.POST.get('code', ''))
        return redirect('products:categories')
    categories = Category.objects.all()
    return render(request, 'products/categories.html', {'categories': categories, 'active_page': 'categories'})

def category_edit(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        category.name = request.POST.get('name', '').strip() or category.name
        category.code = request.POST.get('code', '')
        category.save()
        return redirect('products:categories')
    return redirect('products:categories')

def category_delete(request, pk):
    from django.contrib import messages
    category = get_object_or_404(Category, pk=pk)
    product_count = Product.objects.filter(category=category).count()
    if product_count > 0:
        messages.error(
            request,
            f"\"{category.name}\" kategoriyasini o'chirib bo'lmaydi — unda {product_count} ta taom bor. "
            f"Avval taomlarni boshqa kategoriyaga o'tkazing yoki o'chiring."
        )
        return redirect('products:categories')
    category.delete()
    return redirect('products:categories')
