# productos/forms.py

from datetime import timezone
from django import forms
from .models import Producto, Categoria

from django.contrib.auth.forms import UserCreationForm
from .models import Usuario
from .models import Producto
from .models import OfertaCarrusel, Categoria
from .models import Cupon

class CuponForm(forms.ModelForm):
    class Meta:
        model = Cupon
        fields = ['nombre', 'cantidad_usuarios', 'tipo', 'descuento', 'fecha_expiracion']
        widgets = {
            'fecha_expiracion': forms.DateInput(attrs={'type': 'date'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        descuento = cleaned_data.get('descuento')
        fecha_expiracion = cleaned_data.get('fecha_expiracion')

        # Validación del descuento
        if descuento is not None:
            if descuento < 0 or descuento > 100:
                raise forms.ValidationError('El descuento debe estar entre 0 y 100.')

        # Validación de la fecha de expiración
        if fecha_expiracion and fecha_expiracion < timezone.now().date():
            raise forms.ValidationError('La fecha de expiración no puede ser en el pasado.')

        return cleaned_data
class OfertaCarruselForm(forms.ModelForm):
    class Meta:
        model = OfertaCarrusel
        fields = ['nombre_oferta', 'categoria', 'fecha_inicio', 'fecha_fin', 'imagen_promocional']
        widgets = {
            'fecha_inicio': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'fecha_fin': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

class RegistroForm(UserCreationForm):
    nombre = forms.CharField(max_length=50)
    apellido = forms.CharField(max_length=50)
    rut = forms.CharField(max_length=12)
    telefono = forms.CharField(max_length=15)
    direccion = forms.CharField(max_length=100)
    email = forms.EmailField()

    class Meta:
        model = Usuario
        fields = ['username', 'nombre', 'apellido', 'rut', 'telefono', 'direccion', 'email', 'password1', 'password2']

class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = [
            'nombre', 'descripcion', 'sabor', 'sabor_secundario', 
            'precio', 'imagen', 'imagen_secundaria', 'categoria', 
            'stock', 'es_oferta', 'descuento', 'fecha_inicio_oferta', 
            'fecha_fin_oferta', 'imagen_oferta'
        ]
        widgets = {
            'fecha_inicio_oferta': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'fecha_fin_oferta': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }


class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ['nombre', 'descripcion', 'imagen']

from .models import Slider

class SliderForm(forms.ModelForm):
    class Meta:
        model = Slider
        fields = ['categoria', 'productos', 'imagen_slider', 'imagen_decorativa', 'url_imagen_decorativa']
        widgets = {
            'productos': forms.CheckboxSelectMultiple,  # Permite seleccionar varios productos
        }
