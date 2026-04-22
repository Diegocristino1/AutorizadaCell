from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from .models import Category, ContactMessage, Product


class CatalogViewsTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.cat_xiaomi = Category.objects.create(
            name='Celulares Xiaomi',
            slug='celulares-xiaomi',
            kind=Category.Kind.XIAOMI,
            description='Teste',
        )
        cls.product = Product.objects.create(
            category=cls.cat_xiaomi,
            name='Aparelho Teste',
            slug='aparelho-teste',
            short_description='Resumo',
            description='Descrição completa.',
            price=Decimal('1999.99'),
            in_stock=True,
            featured=True,
        )

    def test_home_ok(self):
        r = self.client.get(reverse('catalog:home'))
        self.assertEqual(r.status_code, 200)

    def test_product_list_ok(self):
        r = self.client.get(reverse('catalog:product_list'))
        self.assertEqual(r.status_code, 200)

    def test_category_ok(self):
        r = self.client.get(
            reverse('catalog:category', kwargs={'slug': self.cat_xiaomi.slug})
        )
        self.assertEqual(r.status_code, 200)

    def test_product_detail_ok(self):
        r = self.client.get(
            reverse('catalog:product_detail', kwargs={'slug': self.product.slug})
        )
        self.assertEqual(r.status_code, 200)

    def test_product_detail_404(self):
        r = self.client.get(
            reverse('catalog:product_detail', kwargs={'slug': 'nao-existe'})
        )
        self.assertEqual(r.status_code, 404)

    def test_category_404(self):
        r = self.client.get(
            reverse('catalog:category', kwargs={'slug': 'categoria-inexistente'})
        )
        self.assertEqual(r.status_code, 404)

    def test_sobre_contato_ok(self):
        self.assertEqual(self.client.get(reverse('catalog:sobre')).status_code, 200)
        self.assertEqual(self.client.get(reverse('catalog:contato')).status_code, 200)

    def test_contact_post_creates_message(self):
        r = self.client.post(
            reverse('catalog:contato'),
            {
                'name': 'Cliente',
                'email': 'cliente@example.com',
                'phone': '61999999999',
                'message': 'Olá, gostaria de um orçamento.',
            },
        )
        self.assertRedirects(r, reverse('catalog:contato'), fetch_redirect_response=False)
        self.assertEqual(ContactMessage.objects.filter(email='cliente@example.com').count(), 1)

        r_invalid = self.client.post(reverse('catalog:contato'), {})
        self.assertEqual(r_invalid.status_code, 200)

    def test_search_querystring(self):
        url = reverse('catalog:product_list')
        r = self.client.get(url, {'q': 'Aparelho'})
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'Aparelho Teste')


class SearchFormValidationTests(TestCase):
    def test_search_rejects_overlong_q(self):
        from catalog.forms import ProductSearchForm

        long_q = 'x' * 201
        f = ProductSearchForm({'q': long_q})
        self.assertFalse(f.is_valid())
