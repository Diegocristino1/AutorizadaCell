from django.core.validators import MinValueValidator
from django.db import models
from django.urls import reverse


class Category(models.Model):
    """Categorias principais: Xiaomi, iPhone e acessórios."""

    class Kind(models.TextChoices):
        XIAOMI = 'xiaomi', 'Celulares Xiaomi'
        IPHONE = 'iphone', 'Celulares iPhone'
        ACCESSORY = 'acessorio', 'Acessórios'

    name = models.CharField('nome', max_length=120)
    slug = models.SlugField('slug', unique=True, max_length=140)
    kind = models.CharField('tipo', max_length=20, choices=Kind.choices)
    description = models.TextField('descrição', blank=True)

    class Meta:
        verbose_name = 'categoria'
        verbose_name_plural = 'categorias'
        ordering = ['kind', 'name']

    def __str__(self) -> str:
        return self.name

    def get_absolute_url(self):
        return reverse('catalog:category', kwargs={'slug': self.slug})


class Product(models.Model):
    """Produto à venda: aparelhos ou acessórios."""

    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name='products',
        verbose_name='categoria',
    )
    name = models.CharField('nome', max_length=200)
    slug = models.SlugField('slug', unique=True, max_length=220)
    short_description = models.CharField('resumo', max_length=300, blank=True)
    description = models.TextField('descrição', blank=True)
    price = models.DecimalField(
        'preço',
        max_digits=12,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[MinValueValidator(0)],
    )
    image = models.ImageField('imagem', upload_to='produtos/', blank=True, null=True)
    in_stock = models.BooleanField('em estoque', default=True)
    featured = models.BooleanField('destaque na home', default=False)
    created_at = models.DateTimeField('criado em', auto_now_add=True)
    updated_at = models.DateTimeField('atualizado em', auto_now=True)

    class Meta:
        verbose_name = 'produto'
        verbose_name_plural = 'produtos'
        ordering = ['-featured', 'name']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['featured', '-created_at']),
        ]

    def __str__(self) -> str:
        return self.name

    def get_absolute_url(self):
        return reverse('catalog:product_detail', kwargs={'slug': self.slug})


class ContactMessage(models.Model):
    """Mensagens enviadas pelo formulário de contato."""

    name = models.CharField('nome', max_length=120)
    email = models.EmailField('e-mail')
    phone = models.CharField('telefone', max_length=30, blank=True)
    message = models.TextField('mensagem')
    created_at = models.DateTimeField('recebido em', auto_now_add=True)
    read = models.BooleanField('lida', default=False)

    class Meta:
        verbose_name = 'mensagem de contato'
        verbose_name_plural = 'mensagens de contato'
        ordering = ['-created_at']

    def __str__(self) -> str:
        return f'{self.name} — {self.created_at:%d/%m/%Y %H:%M}'
