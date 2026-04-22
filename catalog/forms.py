from django import forms

from .models import ContactMessage


class ProductSearchForm(forms.Form):
    q = forms.CharField(
        label='Buscar',
        required=False,
        max_length=200,
        widget=forms.TextInput(
            attrs={
                'placeholder': 'Modelo, acessório...',
                'class': 'search-input',
                'autocomplete': 'off',
            }
        ),
    )


class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ('name', 'email', 'phone', 'message')
        labels = {
            'name': 'Nome',
            'email': 'E-mail',
            'phone': 'Telefone / WhatsApp',
            'message': 'Mensagem',
        }
        widgets = {
            'message': forms.Textarea(attrs={'rows': 5}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if 'class' not in field.widget.attrs:
                field.widget.attrs['class'] = 'form-control'
