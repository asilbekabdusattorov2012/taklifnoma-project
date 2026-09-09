import json
import re
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

from django.conf import settings
from django.shortcuts import render
from django.utils.dateparse import parse_date
from django.db import connection, OperationalError, transaction
from .models import Buyurtma


CATEGORY_FIELDS = {
    'toy': [
        ('kuyov_ismi', 'Kuyovning ismi', 'text', 'Kuyov ismini kiriting', True),
        ('kelin_ismi', 'Kelinning ismi', 'text', 'Kelin ismini kiriting', True),
        ('ota_ism', 'Ota-onalar / xonadon egasi', 'text', 'Masalan: Anvar aka va Mohira opa', False),
        ('vaqt', 'To‘y vaqti', 'time', '', True),
        ('mehmonlar', 'Mehmonlar soni', 'number', 'Masalan: 200', False),
    ],
    'yubley': [
        ('yubiley_egasi', 'Yubiley egasining ismi', 'text', 'Ismni kiriting', True),
        ('yosh', 'Yubiley yoshi', 'number', 'Masalan: 60', True),
        ('vaqt', 'Bayram vaqti', 'time', '', True),
        ('mehmonlar', 'Mehmonlar soni', 'number', 'Masalan: 100', False),
    ],
    'tugilgan_kun': [
        ('tugilgan_egasi', 'Tug‘ilgan kun egasining ismi', 'text', 'Ismni kiriting', True),
        ('yosh', 'Necha yoshga to‘ladi?', 'number', 'Masalan: 18', True),
        ('vaqt', 'Bayram vaqti', 'time', '', True),
        ('mehmonlar', 'Mehmonlar soni', 'number', 'Masalan: 50', False),
    ],
    'qiz': [
        ('qiz_ismi', 'Qizning ismi', 'text', 'Qizning ismini kiriting', True),
        ('ota_ismi', 'Otasi / xonadon egasi ismi', 'text', 'Ismni kiriting', True),
        ('vaqt', 'Marosim vaqti', 'time', '', True),
        ('mehmonlar', 'Mehmonlar soni', 'number', 'Masalan: 200', False),
    ],
    'el_oshi': [
        ('mezbon_ismi', 'Mezbonning ismi', 'text', 'Ismni kiriting', True),
        ('oila_nomi', 'Xonadon / oila nomi', 'text', 'Masalan: Abdusattorovlar xonadoni', False),
        ('vaqt', 'El oshi vaqti', 'time', '', True),
        ('mehmonlar', 'Mehmonlar soni', 'number', 'Masalan: 300', False),
    ],
}

CATEGORY_NAMES = {
    'toy': 'To‘y',
    'yubley': 'Yubiley',
    'tugilgan_kun': 'Tug‘ilgan kun',
    'qiz': 'Qiz uzatish',
    'el_oshi': 'El oshi',
}


def _catalog(request, template, css):
    return render(request, template, {'css_file': css})


def toy(request):
    return _catalog(request, 'toy.html', 'css/toy.css')


def yubley(request):
    return _catalog(request, 'yubley.html', 'css/yubley.css')


def tugulgankun(request):
    return _catalog(request, 'tugulgankun.html', 'css/tugulgankun.css')


def qiz(request):
    return _catalog(request, 'qiz.html', 'css/qiz.css')


def eloshi(request):
    return _catalog(request, 'elosh.html', 'css/eloshi.css')


def _telegram_chat_id(token):
    return str(getattr(settings, 'TELEGRAM_CHAT_ID', '') or '').strip()

def _send_telegram_order(order, extra_data):
    token = str(getattr(settings, 'TELEGRAM_BOT_TOKEN', '') or '').strip()
    if not token:
        return False, 'Telegram token sozlanmagan.'

    chat_id = _telegram_chat_id(token)
    if not chat_id:
        return False, 'Telegram botga /start yuboring, keyin qayta buyurtma bering.'

    lines = [
        '🛎 YANGI BUYURTMA',
        '━━━━━━━━━━━━━━━━━━',
        f'📌 Kategoriya: {order.get_kategoriya_display()}',
        f'🎨 Shablon: {order.shablon}',
        '',
        '👤 MIJOZ MA’LUMOTLARI',
        f'👤 Ism / F.I.Sh.: {order.ism}',
        f'📞 Telefon: {order.telefon}',
        f'📱 Telegram: {order.telegram_username}',
        f'📅 Tadbir sanasi: {order.sana:%d.%m.%Y}',
        f'📍 Manzil: {order.manzil}',
        '',
        '📋 QO‘SHIMCHA MA’LUMOTLAR',
    ]

    for label, value in extra_data:
        lines.append(f'• {label}: {value or "—"}')

    if order.izoh:
        lines.extend(['', f'📝 Izoh: {order.izoh}'])

    lines.extend([
        '',
        f'🕐 Qabul qilingan: {order.yaratilgan:%d.%m.%Y %H:%M}',
        f'🆔 Buyurtma №: {order.id}',
    ])

    payload = urlencode({'chat_id': chat_id, 'text': '\n'.join(lines)}).encode('utf-8')

    try:
        request = Request(
            f'https://api.telegram.org/bot{token}/sendMessage',
            data=payload,
            method='POST',
            headers={'Content-Type': 'application/x-www-form-urlencoded'},
        )
        with urlopen(request, timeout=10) as response:
            result = json.loads(response.read().decode('utf-8'))

        if result.get('ok'):
            return True, ''
        return False, result.get('description', 'Telegram xabari yuborilmadi.')
    except (URLError, HTTPError, TimeoutError, ValueError, OSError) as exc:
        return False, f'Telegram bilan ulanishda xatolik: {exc}'


def buyurtma(request):
    kategoriya = request.GET.get('kategoriya') or request.POST.get('kategoriya', 'toy')
    if kategoriya not in CATEGORY_NAMES:
        kategoriya = 'toy'

    shablon = (request.GET.get('shablon') or request.POST.get('shablon') or 'Tanlangan shablon').strip()
    fields = CATEGORY_FIELDS[kategoriya]

    if request.method == 'POST':
        ism = request.POST.get('ism', '').strip()
        telefon = request.POST.get('telefon', '').strip()
        telegram_username = request.POST.get('telegram_username', '').strip()
        if telegram_username and not telegram_username.startswith('@'):
            telegram_username = '@' + telegram_username
        sana_text = request.POST.get('sana', '').strip()
        sana = parse_date(sana_text)
        manzil = request.POST.get('manzil', '').strip()
        izoh = request.POST.get('izoh', '').strip()

        # HTML required maydonlari bilan birga server tomonda ham tekshiramiz.
        missing = []
        if not ism:
            missing.append('Ism / F.I.Sh.')
        if not telefon:
            missing.append('Telefon')
        if not telegram_username:
            missing.append('Telegram username')
        elif not re.fullmatch(r'@[A-Za-z0-9_]{5,32}', telegram_username):
            missing.append('Telegram username (masalan: @username)')
        if not sana_text:
            missing.append('Tadbir sanasi')
        elif sana is None:
            missing.append('Tadbir sanasi (to‘g‘ri sana tanlang)')
        if not manzil:
            missing.append('Manzil')

        for key, label, *_rest, required in fields:
            if required and not request.POST.get(key, '').strip():
                missing.append(label)

        if missing:
            return render(request, 'buyurtma.html', {
                'kategoriya': kategoriya,
                'kategoriya_nomi': CATEGORY_NAMES[kategoriya],
                'shablon': shablon,
                'fields': fields,
                'error': 'Quyidagi maydonlarni to‘ldiring: ' + ', '.join(missing),
            })

        extra = [(label, request.POST.get(key, '').strip()) for key, label, *_ in fields]
        extra_json = json.dumps(
            {key: request.POST.get(key, '').strip() for key, *_ in fields},
            ensure_ascii=False,
        )

        try:
            with transaction.atomic():
                order = Buyurtma.objects.create(
                    kategoriya=kategoriya,
                    shablon=shablon,
                    ism=ism,
                    telefon=telefon,
                    telegram_username=telegram_username,
                    sana=sana,
                    manzil=manzil,
                    qoshimcha=extra_json,
                    izoh=izoh,
                )
        except Exception as exc:
            # Do not expose a Django traceback to the customer. Keep the exact
            # exception in the terminal so the developer can diagnose it.
            print('BUYURTMA SAQLASH XATOSI:', repr(exc))
            return render(request, 'buyurtma.html', {
                'kategoriya': kategoriya,
                'kategoriya_nomi': CATEGORY_NAMES[kategoriya],
                'shablon': shablon,
                'fields': fields,
                'error': 'Buyurtma saqlanmadi. Loyiha papkasidan FIX_BUYURTMA.bat faylini ishga tushirib, sahifani qayta oching.',
            })

        telegram_sent, telegram_error = _send_telegram_order(order, extra)

        return render(request, 'buyurtma_success.html', {
            'kategoriya_nomi': CATEGORY_NAMES[kategoriya],
            'shablon': shablon,
            'telegram_sent': telegram_sent,
            'telegram_error': telegram_error,
            'order': order,
        })

    return render(request, 'buyurtma.html', {
        'kategoriya': kategoriya,
        'kategoriya_nomi': CATEGORY_NAMES[kategoriya],
        'shablon': shablon,
        'fields': fields,
    })
