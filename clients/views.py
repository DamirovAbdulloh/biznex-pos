from django.shortcuts import render, redirect, get_object_or_404
from .models import Client

def client_list(request):
    q = request.GET.get('q', '')
    clients = Client.objects.all()
    if q:
        clients = clients.filter(name__icontains=q) | clients.filter(phone__icontains=q)
    return render(request, 'clients/list.html', {'clients': clients, 'q': q, 'active_page': 'clients'})

def client_create(request):
    if request.method == 'POST':
        Client.objects.create(
            name=request.POST.get('name', '').strip() or 'Nomsiz mijoz',
            phone=request.POST.get('phone', ''),
            address=request.POST.get('address', ''),
            note=request.POST.get('note', ''),
        )
        return redirect('clients:list')
    return render(request, 'clients/form.html', {'active_page': 'clients'})

def client_edit(request, pk):
    client = get_object_or_404(Client, pk=pk)
    if request.method == 'POST':
        client.name = request.POST.get('name', '').strip() or client.name
        client.phone = request.POST.get('phone', '')
        client.address = request.POST.get('address', '')
        client.note = request.POST.get('note', '')
        client.save()
        return redirect('clients:list')
    return render(request, 'clients/form.html', {'client': client, 'active_page': 'clients'})

def client_delete(request, pk):
    client = get_object_or_404(Client, pk=pk)
    client.delete()
    return redirect('clients:list')
