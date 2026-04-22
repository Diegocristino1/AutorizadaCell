from django.contrib import messages
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import DetailView, ListView, TemplateView

from .forms import ContactForm, ProductSearchForm
from .models import Category, Product


class HomeView(ListView):
    model = Product
    template_name = 'catalog/home.html'
    context_object_name = 'featured_products'

    def get_queryset(self):
        return (
            Product.objects.filter(featured=True, in_stock=True)
            .select_related('category')[:12]
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['categories'] = Category.objects.all()
        return ctx


class ProductListView(ListView):
    model = Product
    template_name = 'catalog/product_list.html'
    context_object_name = 'products'
    paginate_by = 12

    def get_queryset(self):
        qs = Product.objects.filter(in_stock=True).select_related('category')
        slug = self.kwargs.get('slug')
        if slug:
            self.category = get_object_or_404(Category, slug=slug)
            qs = qs.filter(category=self.category)
        else:
            self.category = None

        form = ProductSearchForm(self.request.GET)
        if form.is_valid():
            q = form.cleaned_data.get('q') or ''
            if q.strip():
                qs = qs.filter(
                    Q(name__icontains=q)
                    | Q(short_description__icontains=q)
                    | Q(description__icontains=q)
                )
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['category'] = getattr(self, 'category', None)
        ctx['search_form'] = ProductSearchForm(self.request.GET)
        ctx['categories'] = Category.objects.all()
        return ctx


class ProductDetailView(DetailView):
    model = Product
    template_name = 'catalog/product_detail.html'
    context_object_name = 'product'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_queryset(self):
        return Product.objects.select_related('category')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        product = self.object
        ctx['related'] = (
            Product.objects.filter(category=product.category, in_stock=True)
            .exclude(pk=product.pk)[:4]
        )
        return ctx


class SobreView(TemplateView):
    template_name = 'catalog/sobre.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['categories'] = Category.objects.all()
        return ctx


def contato(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(
                request,
                'Mensagem enviada com sucesso. Em breve retornaremos pelo e-mail ou WhatsApp.',
            )
            return redirect('catalog:contato')
    else:
        form = ContactForm()
    return render(
        request,
        'catalog/contato.html',
        {'form': form, 'categories': Category.objects.all()},
    )
