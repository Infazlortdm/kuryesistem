from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django import forms
from django.http import HttpResponse
from django.utils import timezone
import zipfile
import os

from .models import Siparis, Kurye, Isletme


class SiparisForm(forms.ModelForm):
    class Meta:
        model = Siparis
        fields = ['teslim_bolge', 'adres', 'odeme_tipi', 'fis_foto']


@login_required
def anasayfa(request):

    if Kurye.objects.filter(user=request.user).exists():
        kurye = Kurye.objects.get(user=request.user)
        siparisler = Siparis.objects.filter(
            teslim_bolge__in=kurye.bolgeler.all()
        )
        return render(request, 'kurye.html', {'siparisler': siparisler})

    if Isletme.objects.filter(user=request.user).exists():
        isletme = Isletme.objects.get(user=request.user)
        siparisler = Siparis.objects.filter(isletme=isletme)
        return render(request, 'isletme.html', {'siparisler': siparisler})

    return redirect('/admin/')


@login_required
def siparis_ekle(request):

    if not Isletme.objects.filter(user=request.user).exists():
        return redirect('/')

    isletme = Isletme.objects.get(user=request.user)

    if request.method == 'POST':
        form = SiparisForm(request.POST, request.FILES)
        if form.is_valid():
            siparis = form.save(commit=False)
            siparis.isletme = isletme
            siparis.save()
            return redirect('/')
    else:
        form = SiparisForm()

    return render(request, 'siparis_ekle.html', {'form': form})


@login_required
def siparis_al(request, id):

    kurye = Kurye.objects.get(user=request.user)

    with transaction.atomic():
        siparis = Siparis.objects.select_for_update().get(id=id)

        if siparis.durum == "bekliyor":
            siparis.durum = "alindi"
            siparis.alan_kurye = kurye
            siparis.save()

    return redirect('/')


@login_required
def siparis_teslim(request, id):

    kurye = Kurye.objects.get(user=request.user)
    siparis = get_object_or_404(Siparis, id=id)

    if siparis.alan_kurye == kurye:
        siparis.durum = "teslim"
        siparis.save()

    return redirect('/')


@login_required
def gun_sonu(request):

    today = timezone.now().date()
    zip_filename = f"gun_sonu_{request.user.username}_{today}.zip"

    response = HttpResponse(content_type='application/zip')
    response['Content-Disposition'] = f'attachment; filename="{zip_filename}"'

    with zipfile.ZipFile(response, 'w') as zip_file:

        rapor_metni = ""

        if Kurye.objects.filter(user=request.user).exists():
            siparisler = Siparis.objects.filter(
                alan_kurye__user=request.user,
                olusturma_tarihi__date=today
            )

        elif Isletme.objects.filter(user=request.user).exists():
            siparisler = Siparis.objects.filter(
                isletme__user=request.user,
                olusturma_tarihi__date=today
            )

        else:
            return redirect('/')

        for siparis in siparisler:

            if siparis.fis_foto:
                file_path = siparis.fis_foto.path
                zip_file.write(file_path, f"{siparis.fis_no}.jpg")

            rapor_metni += (
                f"Fis No: {siparis.fis_no}\n"
                f"Isletme: {siparis.isletme}\n"
                f"Bolge: {siparis.teslim_bolge}\n"
                f"Kurye: {siparis.alan_kurye}\n"
                f"Odeme: {siparis.odeme_tipi}\n"
                f"Tarih: {siparis.olusturma_tarihi}\n"
                f"----------------------\n"
            )

        zip_file.writestr("rapor.txt", rapor_metni)

    return response