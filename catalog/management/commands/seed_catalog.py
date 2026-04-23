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

# Nomes e textos alinhados às fotos em static/img/produtos/celulares/
# (name, resumo, nome do ficheiro, preço, destaque home)
ACCESSORY_PHOTOS = [
    (
        'Redmi Buds 5',
        'Fones TWS; cancelamento ativo 46dB, som claro. Cores: branco, azul e preto.',
        'Fone-de-ouvido-Xiaomi-Buds-5.webp',
        Decimal('599.00'),
        True,
    ),
    (
        'KAPBOM KA-8296 — Caixa de som Bluetooth 30W RGB',
        'Caixa 30W com luzes RGB, botão p/ trocar efeitos, design cilíndrico, portátil.',
        'caixa de som bluetooth 30 w.webp',
        Decimal('279.00'),
        True,
    ),
    (
        'Capa anti-impacto c/ anel (Redmi Note 14 / compatíveis)',
        'Capa armada, proteção deslizante câmera, anel 360° e suporte kickstand, preto fosco.',
        'capinha-anti-impacto-ring-xiaomi-redmi-note-14.webp',
        Decimal('89.00'),
        False,
    ),
    (
        'Película 3D Cerâmica Xiaomi (CERAMICS FILM)',
        'Borda preta; anti-rastro, resistente a choque, cola full cover; compat. anunciada 5,8" 2019.',
        'pelicula-3d-ceramica-xiaomi.webp',
        Decimal('49.00'),
        False,
    ),
    (
        'Power bank 20.000mAh 45W PD+ (cabos integrados)',
        '45W PD+; 20000mAh; com alça e cabo embutido. Cores: azul, prata, preto.',
        'Power Bank 2000 mAh 45 W.webp',
        Decimal('299.00'),
        True,
    ),
    (
        'Apple — Cabo USB-C para Lightning 1m',
        'Original; embalagem branca, extremidades USB-C e Lightning (1 m).',
        'Cabo USB-C Lighning 1M.webp',
        Decimal('129.00'),
        False,
    ),
    (
        'Cabo USB-C para USB-C (2m) — charge cable',
        'Cabo branco USB-C / USB-C; carga e dados.',
        'cabo-usb-tipo-c-x-tipo-c-2-metro.webp',
        Decimal('89.00'),
        False,
    ),
    (
        'Apple — Bateria portátil MagSafe (iPhone Battery Pack)',
        'Acessório Apple: bateria com alinhamento MagSafe, estojo e produto oficiais.',
        'carregador-portatil-magsafe-apple-orginal.webp',
        Decimal('899.00'),
        False,
    ),
    (
        'Carregador turbo 67W USB-C (Xiaomi) c/ cabo',
        'Fonte 67W; carregador branco, tomada redonda, cabo USB-A→USB-C com ponteiras laranja.',
        'Carregador USB-C 67 W (Xiaomi).webp',
        Decimal('199.00'),
        True,
    ),
    (
        'Baseus — Suporte magnético p/ grelha de ar',
        'Suporte veicular, cabeça magnética, clip p/ respiro, logo Baseus.',
        'suporte veicular magnetico.jpg',
        Decimal('119.00'),
        False,
    ),
    (
        'AirPods Pro (Apple)',
        'Fones in-ear, estojo e cancelamento. AirPods Pro em destaque (Apple).',
        'AirPods Pro Apple.jpg',
        Decimal('1899.00'),
        True,
    ),
    (
        'ZHIYUN — Gimbal estabilizador 3 eixos c/ tripé e cabo',
        'Estabilizador smartphone, joystick, rodinha, app; tripé e USB-A→USB-C no kit. Marca ZHIYUN.',
        'Gimbal estabilizador de celular.png',
        Decimal('449.00'),
        False,
    ),
    (
        'Ring light p/ celular c/ tripé (multiuso)',
        'Luz anel: alimentação USB, 3 tons de luz, brilho ajustável, suporte p/ smartphone ou câmera.',
        'Ring light para selfie.jpg',
        Decimal('69.00'),
        False,
    ),
    (
        'Capa de silicone iPhone 15 Pro (várias cores / MagSafe)',
        'Case soft-touch: diversas cores (terracota, azul, creme, rosa, amarelo, branco, navy…), compat. MagSafe.',
        'Capa de silicone IPHONE 15 Pro.jpeg',
        Decimal('249.00'),
        False,
    ),
    (
        'Película de vidro 3D tela inteira — iPhone 16 (série)',
        'IPHONE: 16, 16 Pro, Plus e 16 Pro Max. Película de vidro 3D, tela inteira (foto ilustrativa).',
        'Peliculas de vidro 3D IPHONES 16.jpeg',
        Decimal('79.00'),
        False,
    ),
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
        fixture_acessorios = (
            Path(settings.BASE_DIR) / 'static' / 'img' / 'produtos' / 'celulares'
        )

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

        def add_accessory_showcase():
            nonlocal created
            for name, short, image_name, price, is_featured in ACCESSORY_PHOTOS:
                slug = _unique_slug(name, slugs)
                path = fixture_acessorios / image_name
                if not path.is_file():
                    raise FileNotFoundError(
                        f'Imagem de acessório ausente: {path}'
                    )
                product = Product.objects.create(
                    category=cat_acc,
                    name=name,
                    slug=slug,
                    short_description=short,
                    description=(
                        f'{short} Consulte cores, condições e disponibilidade no WhatsApp.'
                    ),
                    price=price,
                    featured=is_featured,
                    in_stock=True,
                )
                with path.open('rb') as f:
                    product.image.save(image_name, File(f), save=True)
                created += 1

        add_xiaomi_showcase()
        add_iphone_showcase()
        add_accessory_showcase()

        self.stdout.write(self.style.SUCCESS(f'Catálogo criado: {created} produtos em 3 categorias.'))
