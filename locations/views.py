from django.shortcuts import render, redirect, get_object_or_404
from .models import Location, Table
from biznex.utils import safe_int

def location_list(request):
    if request.method == 'POST':
        name = (request.POST.get('name') or '').strip() or 'Nomsiz joy'
        table_count = safe_int(request.POST.get('table_count'), default=10)
        table_count = max(1, min(table_count, 200))  # mantiqiy chegara
        loc = Location.objects.create(name=name)
        for i in range(1, table_count + 1):
            Table.objects.create(location=loc, name=f"{i} - Stol")
        return redirect('locations:list')
    locations = Location.objects.all()
    return render(request, 'locations/list.html', {'locations': locations, 'active_page': 'locations'})

def location_delete(request, pk):
    from django.contrib import messages
    loc = get_object_or_404(Location, pk=pk)
    busy_count = Table.objects.filter(location=loc, status='busy').count()
    if busy_count > 0:
        messages.error(
            request,
            f"\"{loc.name}\" ni o'chirib bo'lmaydi — unda {busy_count} ta band stol bor. "
            f"Avval shu stollardagi buyurtmalarni yakunlang."
        )
        return redirect('locations:list')
    loc.delete()
    return redirect('locations:list')

def table_list(request, pk):
    location = get_object_or_404(Location, pk=pk)
    tables = location.table_set.all()
    return render(request, 'locations/tables.html', {'location': location, 'tables': tables, 'active_page': 'locations'})
