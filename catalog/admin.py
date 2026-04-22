from django.contrib import admin

from .models import Category, ContactMessage, Product


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'kind', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'in_stock', 'featured', 'updated_at')
    list_filter = ('category', 'in_stock', 'featured')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name', 'short_description', 'description')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'created_at', 'read')
    list_filter = ('read',)
    search_fields = ('name', 'email', 'message')
    readonly_fields = ('name', 'email', 'phone', 'message', 'created_at')

    def has_add_permission(self, request):
        """Mensagens vêm apenas do site; evita formulário de inclusão quebrado (tudo readonly)."""
        return False
