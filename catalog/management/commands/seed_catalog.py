from decimal import Decimal
from pathlib import Path

from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand
from django.utils.text import slugify

from catalog.models import Category, Product

# Fotos reais em catalog/fixtures/xiaomi/ — nomes alinhados aos arquivos enviados; sem preço no site.
XIAOMI_SHOWCASE = [
    (
        'Xiaomi 12 Pro',
        'Linha Pro com acabamento premium e câmeras de destaque.',
        'xiaomi-12-pro.png',
        False,
    ),
    (
        'POCO F6',
        'Desempenho focado em jogos e multitarefa.',
        'poco-f6.png',
        False,
    ),
    (
        'Xiaomi 13T Pro',
        'Câmeras co-engenharia Leica; versão global 5G (ex.: 1 TB / 16 GB).',
        'xiaomi-13t-pro.png',
        False,
    ),
    (
        'POCO M6 Pro',
        'Câmera 64 MP com OIS, design POCO em duas texturas.',
        'poco-m6-pro.png',
        False,
    ),
    (
        'Xiaomi 14 Ultra',
        'Top de linha Leica, módulo circular quádruplo, acabamentos premium.',
        'xiaomi-14-ultra.png',
        False,
    ),
    (
        'Black Shark 5 Pro',
        'Smartphone gamer Black Shark, estética técnica e refrigeração.',
        'black-shark-5-pro.png',
        False,
    ),
    (
        'POCO C65',
        'Entrada POCO, câmera 50 MP AI; cores de fone de brinde conforme disponibilidade.',
        'poco-c65.png',
        False,
    ),
    (
        'Xiaomi 15 Pro',
        'Série 15 Pro, parceria Leica e design atual.',
        'xiaomi-15-pro.png',
        True,
    ),
    (
        'Xiaomi 15 Ultra',
        'Ultra com sistema fotográfico Leica e teleobjetivas avançadas.',
        'xiaomi-15-ultra.png',
        True,
    ),
    (
        'Xiaomi 15',
        'Flagship série 15, HyperOS e conjunto de câmeras Leica.',
        'xiaomi-15.png',
        True,
    ),
    (
        'Xiaomi 14 Pro',
        'Módulo quadrado Leica Vario-Summilux, acabamento escuro premium.',
        'xiaomi-14-pro.png',
        False,
    ),
]

# Fotos reais em catalog/fixtures/iphone/ — preço None (não exibido no site).
IPHONE_SHOWCASE = [
    (
        'iPhone 17 Pro 256 GB',
        'Acabamento laranja/cobre, Dynamic Island, câmeras Pro em ilha retangular.',
        'iphone-17-pro-256gb.png',
        True,
    ),
    (
        'iPhone 16 128 GB',
        'Branco, câmera dupla vertical, tela com Dynamic Island.',
        'iphone-16-128gb-branco.png',
        True,
    ),
    (
        'iPhone 15 Pro Max 256 GB',
        'Titânio natural, tela grande, Dynamic Island, USB-C.',
        'iphone-15-pro-max-256gb-titanio-natural.png',
        True,
    ),
    (
        'iPhone 14 Pro Max 128 GB',
        'Acabamento escuro (Space Black), Dynamic Island, sistema Pro com LiDAR.',
        'iphone-14-pro-max-128gb.png',
        False,
    ),
    (
        'iPhone 13 Pro (Sierra Blue)',
        'Cor Sierra Blue, vidro fosco, conjunto triplo de câmeras; linha 13 Pro e 13 Pro Max.',
        'iphone-13-pro-sierra-blue.png',
        False,
    ),
    (
        'iPhone 12 Pro Max 256 GB',
        'Dourado, 5G, tela Super Retina, sistema triplo com LiDAR.',
        'iphone-12-pro-max-256gb-dourado.png',
        False,
    ),
    (
        'iPhone 11 Pro Max 256 GB',
        'Várias cores: dourado, verde meia-noite, prata e cinza espacial. Tripla câmera.',
        'iphone-11-pro-max-256gb.png',
        False,
    ),
    (
        'iPhone 7 Plus 32 GB',
        'Câmera dupla; cores: rose gold, dourado, prata, preto fosco e jet black.',
        'iphone-7-plus-32gb.png',
        False,
    ),
]

ACCESSORIES = [
    ('Carregador USB-C 67 W (Xiaomi)', 'Compatível com vários modelos.', Decimal('199.00')),
    ('Carregador MagSafe Apple 15 W', 'Carregamento magnético original.', Decimal('449.00')),
    ('Capa silicone iPhone 15 Pro', 'Várias cores, proteção Apple.', Decimal('249.00')),
    ('Capa anti-impacto Xiaomi 14', 'TPU reforçado, transparente.', Decimal('89.00')),
    ('Película de vidro 3D iPhone 16', 'Proteção bordas curvas.', Decimal('79.00')),
    ('Película cerâmica Redmi Note 13', 'Anti-risco, sensível ao toque.', Decimal('49.00')),
    ('Fone Bluetooth Xiaomi Buds 5', 'ANC, som Hi-Res.', Decimal('599.00')),
    ('AirPods Pro (2ª geração)', 'USB-C, cancelamento ativo.', Decimal('1899.00')),
    ('Cabo USB-C para Lightning 1 m', 'Certificado, carregamento rápido.', Decimal('129.00')),
    ('Cabo USB-C para USB-C 2 m', '100 W, nylon trançado.', Decimal('89.00')),
    ('Suporte veicular magnético MagSafe', 'Ventosa + ímã forte.', Decimal('119.00')),
    ('Power bank 20000 mAh 45 W', 'Carrega notebook e celular.', Decimal('299.00')),
    ('Ring light clip para selfie', 'LED regulável, USB-C.', Decimal('69.00')),
    ('Gimbal estabilizador smartphone', '3 eixos, app dedicado.', Decimal('449.00')),
    ('Caixa de som Bluetooth 30 W', 'À prova d’água IPX7.', Decimal('279.00')),
]


def _unique_slug(base: str, existing: set) -> str:
    s = slugify(base)[:200] or 'item'
    candidate = s
    n = 2
    while candidate in existing:
        candidate = f'{s}-{n}'
        n += 1
    existing.add(candidate)
    return candidate


class Command(BaseCommand):
    help = 'Cria categorias e produtos de exemplo (Xiaomi, iPhone e acessórios).'

    def handle(self, *args, **options):
        Product.objects.all().delete()
        Category.objects.all().delete()

        cat_xiaomi = Category.objects.create(
            name='Celulares Xiaomi',
            slug='celulares-xiaomi',
            kind=Category.Kind.XIAOMI,
            description='Linha completa Xiaomi, Redmi e POCO.',
        )
        cat_iphone = Category.objects.create(
            name='Celulares iPhone',
            slug='celulares-iphone',
            kind=Category.Kind.IPHONE,
            description='iPhones novos e seminovos com garantia.',
        )
        cat_acc = Category.objects.create(
            name='Acessórios',
            slug='acessorios',
            kind=Category.Kind.ACCESSORY,
            description='Capas, carregadores, fones e mais.',
        )

        slugs: set[str] = set()
        created = 0
        fixture_xiaomi = Path(settings.BASE_DIR) / 'catalog' / 'fixtures' / 'xiaomi'
        fixture_iphone = Path(settings.BASE_DIR) / 'catalog' / 'fixtures' / 'iphone'

        def add_products(items, category, featured_first=3):
            nonlocal created
            for i, (name, short, price) in enumerate(items):
                slug = _unique_slug(name, slugs)
                Product.objects.create(
                    category=category,
                    name=name,
                    slug=slug,
                    short_description=short,
                    description=f'{short} Consulte cores e disponibilidade no WhatsApp.',
                    price=price,
                    featured=i < featured_first,
                    in_stock=True,
                )
                created += 1

        def add_xiaomi_showcase():
            nonlocal created
            for name, short, image_name, is_featured in XIAOMI_SHOWCASE:
                slug = _unique_slug(name, slugs)
                path = fixture_xiaomi / image_name
                if not path.is_file():
                    raise FileNotFoundError(f'Imagem de fixture ausente: {path}')
                product = Product.objects.create(
                    category=cat_xiaomi,
                    name=name,
                    slug=slug,
                    short_description=short,
                    description=(
                        f'{short} Consulte cores, condições e disponibilidade no WhatsApp.'
                    ),
                    price=None,
                    featured=is_featured,
                    in_stock=True,
                )
                with path.open('rb') as f:
                    product.image.save(image_name, File(f), save=True)
                created += 1

        def add_iphone_showcase():
            nonlocal created
            for name, short, image_name, is_featured in IPHONE_SHOWCASE:
                slug = _unique_slug(name, slugs)
                path = fixture_iphone / image_name
                if not path.is_file():
                    raise FileNotFoundError(f'Imagem de fixture ausente: {path}')
                product = Product.objects.create(
                    category=cat_iphone,
                    name=name,
                    slug=slug,
                    short_description=short,
                    description=(
                        f'{short} Consulte cores, condições e disponibilidade no WhatsApp.'
                    ),
                    price=None,
                    featured=is_featured,
                    in_stock=True,
                )
                with path.open('rb') as f:
                    product.image.save(image_name, File(f), save=True)
                created += 1

        add_xiaomi_showcase()
        add_iphone_showcase()
        add_products(ACCESSORIES, cat_acc, featured_first=2)

        self.stdout.write(self.style.SUCCESS(f'Catálogo criado: {created} produtos em 3 categorias.'))
