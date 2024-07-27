from decimal import Decimal, InvalidOperation
import os
from tkinter import Image
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from wtforms import ValidationError
from .models import EstadisticasVentas, HistorialVentas, Oferta, OfertaCarrusel, PedidoProducto, Producto, Categoria, Venta, Carrito, Pedido 
from .forms import  ProductoForm, CategoriaForm, RegistroForm, SliderForm
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from django.urls import reverse
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO
from django.contrib.auth.decorators import login_required
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Image, Spacer
from .models import Pedido
from django.conf import settings
from django.shortcuts import render
from django.utils import timezone
from django.db.models import Sum
from datetime import timedelta
from .forms import OfertaCarruselForm
from .forms import CuponForm
from .models import Cupon
@login_required
def agregar_cupon(request):
    if request.method == 'POST':
        form = CuponForm(request.POST)
        if form.is_valid():
            cupon = form.save()
            messages.success(request, 'Cupón creado exitosamente.')
            return redirect('agregar_cupon')
        else:
            messages.error(request, 'Error al crear el cupón.')
    else:
        form = CuponForm()
    return render(request, 'productos/crear_cupon.html', {'form': form})
@login_required(login_url='/mostrar-alerta/')
def agregar_al_carrito(request, producto_id):
    if request.method == 'POST':
        producto = get_object_or_404(Producto, id=producto_id)
        usuario = request.user
        cantidad = request.POST.get('cantidad', 1)

        response_data = {
            'success': False,
            'messages': []
        }

        if not request.user.is_authenticated:
            response_data['messages'].append({
                'icon': 'error',
                'title': 'No Autenticado',
                'text': 'Debes iniciar sesión para agregar productos al carrito.'
            })
            return JsonResponse(response_data)

        if not cantidad:
            response_data['messages'].append({
                'icon': 'error',
                'title': 'Error',
                'text': 'Debe especificar una cantidad.'
            })
            return JsonResponse(response_data)

        try:
            cantidad = int(cantidad)
            if cantidad < 1:
                response_data['messages'].append({
                    'icon': 'error',
                    'title': 'Error',
                    'text': 'La cantidad debe ser al menos 1.'
                })
                return JsonResponse(response_data)
        except ValueError:
            response_data['messages'].append({
                'icon': 'error',
                'title': 'Error',
                'text': 'La cantidad debe ser un número entero.'
            })
            return JsonResponse(response_data)

        if producto.stock < cantidad:
            response_data['messages'].append({
                'icon': 'error',
                'title': 'Error',
                'text': 'No hay stock disponible.'
            })
            return JsonResponse(response_data)

        carrito_item, created = Carrito.objects.get_or_create(usuario=usuario, producto=producto, defaults={'cantidad': cantidad})

        if not created:
            if carrito_item.cantidad + cantidad > producto.stock:
                response_data['messages'].append({
                    'icon': 'error',
                    'title': 'Error',
                    'text': 'La cantidad solicitada supera el stock disponible.'
                })
                return JsonResponse(response_data)
            carrito_item.cantidad += cantidad
            carrito_item.save()
        else:
            carrito_item.cantidad = cantidad
            carrito_item.save()

        response_data['success'] = True
        response_data['messages'].append({
            'icon': 'success',
            'title': 'Éxito',
            'text': 'Producto agregado al carrito exitosamente.'
        })

        # Agregar el total del carrito considerando el precio con descuento
        carrito_items = Carrito.objects.filter(usuario=usuario)
        carrito_total = sum(item.producto.precio_con_descuento() * item.cantidad for item in carrito_items)
        response_data['carrito_total'] = carrito_total

        return JsonResponse(response_data)

def index(request):
    ahora = timezone.now()
    # Obtener solo las ofertas que están actualmente activas
    ofertas_activas = OfertaCarrusel.objects.filter(fecha_inicio__lte=ahora, fecha_fin__gte=ahora)

    categorias = Categoria.objects.all()

    return render(request, 'productos/index.html', {
        'ofertas': ofertas_activas,
        'categorias': categorias
    })
 

def logout_view(request):
    logout(request)
    return redirect('index')

# Vista de detalle del producto
def product_detail(request, producto_id):
    producto = get_object_or_404(Producto, pk=producto_id)
    now = timezone.now()
    context = {
        'producto': producto,
        'now': now,
    }
    return render(request, 'productos/product_detail.html', context)


# Vista de productos por categoría
def category(request, categoria_id):
    categoria = get_object_or_404(Categoria, id=categoria_id)
    productos = Producto.objects.filter(categoria=categoria)
    return render(request, 'productos/category.html', {'categoria': categoria, 'productos': productos})

# Vista de creación de productos (solo para administradores)
@login_required
def create_product(request):
    if not request.user.is_superuser:
        return redirect('index')

    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('index')
    else:
        form = ProductoForm()
    return render(request, 'productos/create_product.html', {'form': form})

# Vista de creación de categorías (solo para administradores)
@login_required
def create_category(request):
    if not request.user.is_superuser:
        return redirect('index')

    if request.method == 'POST':
        form = CategoriaForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('index')
    else:
        form = CategoriaForm()
    return render(request, 'productos/create_category.html', {'form': form})

# Vista de historial de ventas (solo para administradores)
@login_required
@user_passes_test(lambda u: u.is_superuser)
def sales_history(request):
    ventas = Venta.objects.all().order_by('-fecha')
    return render(request, 'productos/sales_history.html', {'ventas': ventas})

# Registro de usuarios
def register(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('index')
    else:
        form = RegistroForm()
    return render(request, 'registration/register.html', {'form': form})

# Inicio de sesión de usuarios
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('index')
    else:
        form = AuthenticationForm()
    return render(request, 'productos/login.html', {'form': form})

# Cierre de sesión de usuarios
def logout_view(request):
    logout(request)
    return redirect('index')

# Vista de productos por categoría
def ver_productos_categoria(request, categoria_id):
    categoria = get_object_or_404(Categoria, pk=categoria_id)
    productos = Producto.objects.filter(categoria=categoria)
    return render(request, 'productos/ver_productos_categoria.html', {'categoria': categoria, 'productos': productos})

# Edición de productos (solo para administradores)
@login_required
def edit_product(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES, instance=producto)
        if form.is_valid():
            form.save()
            return redirect('product_detail', producto_id=producto.id)
    else:
        form = ProductoForm(instance=producto)
    return render(request, 'productos/edit_product.html', {'form': form, 'producto': producto})

# Eliminación de productos (solo para administradores)
@login_required
def delete_product(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    if request.method == 'POST':
        producto.delete()
        return redirect('index')
    return render(request, 'productos/delete_product.html', {'producto': producto})

# Carrito de compras
@login_required
def ver_carrito(request):
    # Obtener todos los elementos del carrito para el usuario
    carrito_items = Carrito.objects.filter(usuario=request.user)
    
    # Calcular el total del carrito usando el precio con descuento si aplica
    total_carrito = sum(item.producto.precio_con_descuento() * item.cantidad for item in carrito_items)

    # Procesar cualquier cupón aplicado
    cupon = request.POST.get('cupon', None)
    if cupon:
        try:
            cupon_obj = Cupon.objects.get(nombre=cupon)
            total_carrito = cupon_obj.aplicar_cupon(total_carrito)
            cupon_obj.usar_cupon()
            messages.success(request, 'Cupón aplicado correctamente.')
        except Cupon.DoesNotExist:
            messages.error(request, 'Cupón no válido.')

    # Obtener o crear el pedido actual del usuario
    pedido, created = Pedido.objects.get_or_create(
        usuario=request.user,
        estado='carrito',
        defaults={'tipo_envio': 'domicilio_registro'}
    )

    # Manejar cambios en el tipo de envío
    if request.method == 'POST':
        tipo_envio = request.POST.get('tipo_envio')
        if tipo_envio in dict(Pedido.TIPO_ENVIO_CHOICES).keys():
            if pedido:
                pedido.tipo_envio = tipo_envio
                if tipo_envio == 'retiro_sucursal':
                    pedido.direccion_envio = ''
                else:
                    pedido.direccion_envio = request.user.direccion
                pedido.save()
                messages.success(request, 'Tipo de envío actualizado correctamente.')
            return redirect('ver_carrito')
        else:
            messages.error(request, 'Opción de tipo de envío no válida.')

    # Preparar las opciones de tipo de envío para el template
    tipo_envio_choices = Pedido.TIPO_ENVIO_CHOICES if pedido else []

    # Preparar el contexto para el template
    context = {
        'carrito_items': carrito_items,
        'total_carrito': total_carrito,
        'total_carrito_con_descuento': total_carrito - pedido.descuento,  # Ajuste para mostrar el total con descuento aplicado
        'pedido': pedido,
        'tipo_envio_choices': tipo_envio_choices,
    }

    return render(request, 'productos/carrito.html', context)

def realizar_pedido(request):
    carrito_items = Carrito.objects.filter(usuario=request.user)
    
    if carrito_items:
        tipo_envio = request.POST.get('tipo_envio', 'domicilio_registro')
        direccion_envio = request.user.direccion if tipo_envio == 'domicilio_registro' else ''
        
        pedido = Pedido.objects.create(
            usuario=request.user,
            estado='preparacion',
            tipo_envio=tipo_envio,
            direccion_envio=direccion_envio
        )

        total_compras = 0
        descuento_aplicado = 0
        for item in carrito_items:
            precio_con_descuento = item.producto.precio_con_descuento()
            subtotal_item = precio_con_descuento * item.cantidad
            total_compras += subtotal_item

            # Calcular descuento aplicado
            if item.producto.descuento:
                descuento_item = item.producto.precio * (item.producto.descuento / 100) * item.cantidad
                descuento_aplicado += descuento_item

            PedidoProducto.objects.create(pedido=pedido, producto=item.producto, cantidad=item.cantidad)
            item.producto.stock -= item.cantidad
            item.producto.save()

            # Crear entradas en HistorialVentas
            venta = Venta.objects.create(
                usuario=request.user,
                producto=item.producto,
                cantidad=item.cantidad
            )
            
            # Actualizar estadísticas de ventas
            estadisticas, created = EstadisticasVentas.objects.get_or_create(producto=item.producto)
            estadisticas.cantidad_vendida += item.cantidad
            estadisticas.total_ventas_diarias += subtotal_item
            estadisticas.total_ventas_semanales += subtotal_item
            estadisticas.total_ventas_mensuales += subtotal_item
            estadisticas.save()
        
        # Aplicar el descuento total al total del pedido
        total_con_descuento = total_compras - descuento_aplicado

        pedido.total_compras = total_con_descuento
        pedido.descuento_aplicado = descuento_aplicado
        pedido.save()
        
        carrito_items.delete()

        response_data = {
            'success': True,
            'messages': [{
                'icon': 'success',
                'title': 'Éxito',
                'text': 'Pedido realizado correctamente. Te notificaremos como va la preparación de tu pedido.'
            }],
            'redirect': reverse('estado_pedido', args=[pedido.id])
        }
        return JsonResponse(response_data)
    else:
        response_data = {
            'success': False,
            'messages': [{
                'icon': 'error',
                'title': 'Error',
                'text': 'No hay productos en el carrito.'
            }]
        }
        return JsonResponse(response_data)
def estado_pedido(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id)
    subtotales = []
    total_sin_descuento = 0

    for item in pedido.productos.all():
        subtotal = item.cantidad * item.producto.precio_con_descuento()  # Llama al método con paréntesis
        subtotales.append({
            'producto': item.producto,
            'cantidad': item.cantidad,
            'subtotal': subtotal
        })
        total_sin_descuento += subtotal

    # Aplica descuento si hay
    descuento_aplicado = pedido.descuento_aplicado if pedido.descuento_aplicado else 0
    total_con_descuento = total_sin_descuento - descuento_aplicado

    return render(request, 'productos/estado_pedido.html', {
        'pedido': pedido,
        'subtotales': subtotales,
        'total_pedido': total_con_descuento,
        'descuento_aplicado': descuento_aplicado
    })

@login_required
def eliminar_del_carrito(request, item_id):
    if request.method == 'POST':
        try:
            item = Carrito.objects.get(id=item_id, usuario=request.user)
            item.delete()
            carrito_items = Carrito.objects.filter(usuario=request.user)
            total_carrito = sum(item.producto.precio * item.cantidad for item in carrito_items)
            return JsonResponse({
                'success': True,
                'message': 'Producto eliminado del carrito correctamente.',
                'carrito_total': total_carrito
            })
        except Carrito.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'El producto no existe en el carrito.'})
    return JsonResponse({'success': False, 'message': 'Método no permitido.'})

# Sistema de gestión de pedidos
@login_required
@user_passes_test(lambda u: u.is_superuser)
def gestionar_pedidos(request):
    pedidos = Pedido.objects.all()

    for pedido in pedidos:
        total_pedido = sum(item.producto.precio * item.cantidad for item in pedido.productos.all())
        pedido.valor_total = total_pedido  # Añadimos un atributo dinámico al objeto pedido
    
    context = {
        'pedidos': pedidos,
    }
    return render(request, 'productos/gestionar_pedidos.html', context)

@login_required
@user_passes_test(lambda u: u.is_superuser)
def aprobar_pedido(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id)
    
    try:
        # Cambiar el estado del pedido a 'aceptado'
        pedido.estado = 'aceptado'
        pedido.save()

        # Guardar en el historial de ventas
        historial_venta = HistorialVentas(pedido=pedido, usuario=pedido.usuario, valor_total=pedido.total_compras)
        historial_venta.save()

        # Actualizar las estadísticas de ventas
        for item in pedido.productos.all():
            producto = item.producto
            estadisticas, created = EstadisticasVentas.objects.get_or_create(producto=producto)
            estadisticas.cantidad_vendida += item.cantidad
            estadisticas.total_ventas_diarias = 0
            estadisticas.total_ventas_semanales = 0
            estadisticas.total_ventas_mensuales = 0
            estadisticas.actualizar_estadisticas()

        # Enviar un correo al usuario notificando la aprobación
        subject = 'Pedido Aprobado'
        message = f'Estimado {pedido.usuario.username},\n\nTu pedido ha sido aprobado y está en proceso de preparación.'
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [pedido.usuario.email]
        
        send_mail(subject, message, from_email, recipient_list)

        # Redirigir a la página de gestión de pedidos
        return redirect('gestionar_pedidos')

    except Exception as e:
        # Manejo de errores si algo sale mal
        print(f"Error al aprobar pedido: {e}")
        return redirect('gestionar_pedidos')
@login_required
@user_passes_test(lambda u: u.is_superuser)
def cancelar_pedido(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id)

    try:
        # Actualiza el stock de los productos asociados al pedido
        for item in pedido.productos.all():
            item.producto.stock += item.cantidad
            item.producto.save()

        # Cambiar el estado del pedido a 'cancelado'
        pedido.estado = 'cancelado'
        pedido.save()

        # Enviar un correo al usuario notificando la cancelación
        subject = 'Pedido Cancelado'
        message = f'Estimado {pedido.usuario.username},\n\nTu pedido ha sido cancelado. Para más información, por favor contacta con soporte.'
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [pedido.usuario.email]

        send_mail(subject, message, from_email, recipient_list)

        # Redirigir a la página de gestión de pedidos
        return redirect('gestionar_pedidos')

    except Exception as e:
        # Manejo de errores si algo sale mal
        print(f"Error al cancelar pedido: {e}")
        return redirect('gestionar_pedidos')

@login_required
@user_passes_test(lambda u: u.is_superuser)
def eliminar_pedido(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id)
    pedido.delete()
    return redirect('gestionar_pedidos')
@login_required
def some_view(request):
    # Obtener el pedido activo del usuario actual si está autenticado
    pedido_activo = Pedido.objects.filter(usuario=request.user, estado='activo').first()

    return render(request, 'base.html', {'pedido_activo': pedido_activo})

@login_required
def mis_pedidos(request):
    pedidos = Pedido.objects.filter(usuario=request.user).order_by('-fecha')

    context = {
        'pedidos': pedidos,
    }
    return render(request, 'productos/mis_pedidos.html', context)

@login_required
def actualizar_tipo_envio(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id)

    if request.method == 'POST':
        tipo_envio = request.POST.get('tipo_envio')

        response_data = {
            'success': False,
            'messages': []
        }

        if tipo_envio in dict(Pedido.TIPO_ENVIO_CHOICES).keys():
            pedido.tipo_envio = tipo_envio
            pedido.save()

            if tipo_envio == 'retiro_sucursal':
                pedido.direccion_envio = None
                pedido.save()

            response_data['success'] = True
            response_data['messages'].append({
                'icon': 'success',
                'title': 'Éxito',
                'text': 'Tipo de envío actualizado correctamente.'
            })
            response_data['redirect'] = reverse('ver_carrito')

        else:
            response_data['messages'].append({
                'icon': 'error',
                'title': 'Error',
                'text': 'Opción de tipo de envío no válida.'
            })

        return JsonResponse(response_data)

    return JsonResponse({
        'success': False,
        'messages': [{
            'icon': 'error',
            'title': 'Error',
            'text': 'Método no permitido.'
        }]
    })


def eliminar_pedido(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id)
    
    if request.method == 'POST':
        # Actualiza el stock de los productos antes de eliminar el pedido
        for item in pedido.productos.all():
            item.producto.stock += item.cantidad
            item.producto.save()

        # Elimina el pedido
        pedido.delete()
        messages.success(request, 'El pedido ha sido eliminado exitosamente.')
        return redirect('gestionar_pedidos')
    
    return render(request, 'productos/eliminar_pedido_confirmacion.html', {'pedido': pedido})

# views.py
def actualizar_pedido(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id)
    
    if request.method == 'POST':
        tipo_envio = request.POST.get('tipo_envio')
        
        if tipo_envio == 'retiro_sucursal':
            pedido.tipo_envio = 'retiro_sucursal'
        elif tipo_envio == 'domicilio_registro':
            pedido.tipo_envio = 'domicilio_registro'
        
        pedido.save()
        return redirect('estado_pedido', pedido_id=pedido.id)
    
    return render(request, 'actualizar_pedido.html', {'pedido': pedido})


@login_required
def eliminar_del_carrito(request, item_id):
    item = get_object_or_404(Carrito, id=item_id, usuario=request.user)
    item.delete()
    
    response_data = {
        'success': True,
        'message': {
            'icon': 'success',
            'title': 'Éxito',
            'text': 'Producto eliminado del carrito.'
        },
        'carrito_total': calcular_total_carrito(request.user)
    }
    return JsonResponse(response_data)

@login_required
def modificar_cantidad(request, item_id):
    item = get_object_or_404(Carrito, id=item_id, usuario=request.user)
    response_data = {'success': False, 'messages': []}
    
    if request.method == 'POST':
        nueva_cantidad = request.POST.get('cantidad')
        
        try:
            nueva_cantidad = int(nueva_cantidad)
            if nueva_cantidad < 1:
                response_data['messages'].append({
                    'icon': 'error',
                    'title': 'Error',
                    'text': 'La cantidad debe ser al menos 1.'
                })
            elif nueva_cantidad > item.producto.stock:
                response_data['messages'].append({
                    'icon': 'error',
                    'title': 'Error',
                    'text': 'La cantidad solicitada supera el stock disponible.'
                })
            else:
                item.cantidad = nueva_cantidad
                item.save()
                response_data['success'] = True
                response_data['messages'].append({
                    'icon': 'success',
                    'title': 'Éxito',
                    'text': 'Cantidad actualizada correctamente.'
                })
                response_data['carrito_total'] = calcular_total_carrito(request.user)
        except ValueError:
            response_data['messages'].append({
                'icon': 'error',
                'title': 'Error',
                'text': 'La cantidad debe ser un número entero.'
            })

        return JsonResponse(response_data)

    return redirect('ver_carrito')

def calcular_total_carrito(usuario):
    carrito_items = Carrito.objects.filter(usuario=usuario)
    total = sum(item.producto.precio_con_descuento() * item.cantidad for item in carrito_items)
    return total

def calcular_total_pedido(pedido):
    total = sum(item.producto.precio_con_descuento() * item.cantidad for item in pedido.productos.all())
    if pedido.descuento:
        total -= total * (pedido.descuento / 100)
    return total



def gestionar_slider(request):
    if request.method == 'POST':
        form = SliderForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('gestionar_slider')  # Redirige a la misma página o a otra que desees
    else:
        form = SliderForm()
    
    categorias = Categoria.objects.all()
    return render(request, 'productos/gestionar_slider.html', {'form': form, 'categorias': categorias})

@login_required
def exportar_boleta_pdf(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id)
    
    # Crear un buffer para almacenar el PDF
    buffer = BytesIO()
    
    # Crear un objeto SimpleDocTemplate de ReportLab
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    story = []
    
    styles = getSampleStyleSheet()
    
    # Encabezado
    logo_path = os.path.join(settings.BASE_DIR, 'static', 'img', 'modobestia.jpeg')
    if os.path.exists(logo_path):
        logo_image = Image(logo_path, width=150, height=50)
        story.append(logo_image)
    
    header = [
        Paragraph("<b>Modo Bestia Chile - Los Ángeles</b>", styles['Title']),
        Paragraph(f"Fecha de la compra: {pedido.fecha.strftime('%d/%m/%Y')}", styles['Normal'])
    ]
    story.extend(header)
    
    story.append(Spacer(1, 12))
    
    # Detalle de Boleta
    story.append(Paragraph("<b>Detalle de Boleta</b>", styles['Heading2']))
    data = [['Producto', 'Cantidad', 'Precio Unitario', 'Subtotal']]
    
    for item in pedido.productos.all():
        subtotal = item.cantidad * item.producto.precio
        data.append([
            item.producto.nombre,
            str(item.cantidad),
            f"${item.producto.precio:,.2f}",
            f"${subtotal:,.2f}"
        ])
    
    table = Table(data, colWidths=[200, 60, 80, 80])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), '#f4f4f4'),
        ('GRID', (0, 0), (-1, -1), 1, '#ddd'),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('BACKGROUND', (0, 0), (-1, 0), '#f4f4f4')
    ]))
    
    story.append(table)
    
    # Total
    story.append(Spacer(1, 12))
    total_paragraph = Paragraph(f"<b>Total: ${pedido.valor_total():,.2f}</b>", styles['Heading3'])
    story.append(total_paragraph)
    
    # Finalizar el PDF
    doc.build(story)
    
    # Obtener el valor del buffer y prepararlo para la respuesta
    pdf = buffer.getvalue()
    buffer.close()
    
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="boleta_{pedido.id}.pdf"'
    
    return response
@login_required
@user_passes_test(lambda u: u.is_superuser)
def estadisticas_productos(request):
    estadisticas = EstadisticasVentas.objects.all().order_by('-cantidad_vendida')
    return render(request, 'productos/estadisticas_productos.html', {'estadisticas': estadisticas})
@login_required
@user_passes_test(lambda u: u.is_superuser)
def ventas_diarias(request):
    hoy = timezone.now().date()
    ventas = Pedido.objects.filter(fecha__date=hoy).aggregate(total_ventas=Sum('total_compras'))
    return render(request, 'ventas_diarias.html', {'total_ventas': ventas['total_ventas']})
@login_required
@user_passes_test(lambda u: u.is_superuser)
def ventas_semanales(request):
    hoy = timezone.now().date()
    inicio_semana = hoy - timedelta(days=hoy.weekday())
    fin_semana = inicio_semana + timedelta(days=6)
    ventas = Pedido.objects.filter(fecha__date__range=[inicio_semana, fin_semana]).aggregate(total_ventas=Sum('total_compras'))
    return render(request, 'ventas_semanales.html', {'total_ventas': ventas['total_ventas']})
@login_required
@user_passes_test(lambda u: u.is_superuser)
def ventas_mensuales(request):
    hoy = timezone.now().date()
    inicio_mes = hoy.replace(day=1)
    fin_mes = (inicio_mes + timedelta(days=31)).replace(day=1) - timedelta(days=1)
    ventas = Pedido.objects.filter(fecha__date__range=[inicio_mes, fin_mes]).aggregate(total_ventas=Sum('total_compras'))
    return render(request, 'ventas_mensuales.html', {'total_ventas': ventas['total_ventas']})
@login_required
@user_passes_test(lambda u: u.is_superuser)
def historial_y_estadisticas(request):
    hoy = timezone.now().date()
    inicio_semana = hoy - timedelta(days=hoy.weekday())
    fin_semana = inicio_semana + timedelta(days=6)
    inicio_mes = hoy.replace(day=1)
    fin_mes = (inicio_mes + timedelta(days=31)).replace(day=1) - timedelta(days=1)
    
    ventas_diarias = Pedido.objects.filter(fecha__date=hoy).aggregate(total_ventas=Sum('total_compras'))
    ventas_semanales = Pedido.objects.filter(fecha__date__range=[inicio_semana, fin_semana]).aggregate(total_ventas=Sum('total_compras'))
    ventas_mensuales = Pedido.objects.filter(fecha__date__range=[inicio_mes, fin_mes]).aggregate(total_ventas=Sum('total_compras'))
    historial_ventas = Pedido.objects.all()

    context = {
        'ventas_diarias': ventas_diarias['total_ventas'],
        'ventas_semanales': ventas_semanales['total_ventas'],
        'ventas_mensuales': ventas_mensuales['total_ventas'],
        'historial_ventas': historial_ventas,
    }
    return render(request, 'productos/historial_y_estadisticas.html', context)
@login_required
@user_passes_test(lambda u: u.is_superuser)
def detalle_pedido(request, id):
    pedido = get_object_or_404(Pedido, id=id)
    return render(request, 'productos/detalle_pedido.html', {'pedido': pedido})
@login_required
@user_passes_test(lambda u: u.is_superuser)
def agregar_oferta_carrusel(request):
    # Recuperar todas las ofertas
    if request.method == 'POST':
        form = OfertaCarruselForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('agregar_oferta_carrusel')  # Redirige a la misma página
    else:
        form = OfertaCarruselForm()

    # Aquí se asegura de pasar las ofertas al contexto
    ofertas = OfertaCarrusel.objects.all()  # Asegúrate de que OfertaCarrusel es el nombre correcto de tu modelo
    return render(request, 'productos/agregar_oferta_carrusel.html', {
        'form': form,
        'ofertas': ofertas
    })

def carrusel_ofertas(request):
    ofertas = OfertaCarrusel.objects.filter(esta_activa=True)
    return render(request, 'productos/carrusel_ofertas.html', {'ofertas': ofertas})


@login_required(login_url='/mostrar-alerta/')
def pagina_protegida(request):
    # Lógica de la página
    return render(request, 'pagina_protegida.html')

def mostrar_alerta(request):
    return render(request, 'productos/mostrar_alerta.html')
def verificar_autenticacion(request):
    if request.user.is_authenticated:
        return JsonResponse({'autenticado': True})
    else:
        return JsonResponse({'autenticado': False})
    
def productos_lista(request):
    # Obtener el término de búsqueda
    query = request.GET.get('q', '')
    min_precio = request.GET.get('min_precio', None)
    max_precio = request.GET.get('max_precio', None)
    orden = request.GET.get('orden', 'asc')

    # Filtrar productos por búsqueda y precio
    productos = Producto.objects.filter(nombre__icontains=query)
    if min_precio:
        productos = productos.filter(precio__gte=min_precio)
    if max_precio:
        productos = productos.filter(precio__lte=max_precio)

    # Ordenar los productos según el parámetro de orden
    if orden == 'desc':
        productos = productos.order_by('-precio')
    else:
        productos = productos.order_by('precio')

    return render(request, 'productos/productos_lista.html', {
        'productos': productos
    })
def search_products(request):
    query = request.GET.get('query', '')
    min_price = request.GET.get('min_price', '0')
    max_price = request.GET.get('max_price', '1000000')  # Valor alto para simular infinito
    order_by = request.GET.get('order_by', 'nombre')

    try:
        min_price = Decimal(min_price)
        max_price = Decimal(max_price)
    except (ValidationError, ValueError):
        min_price = Decimal('0')
        max_price = Decimal('1000000')  # Valor alto para simular infinito

    # Filtrar productos según la búsqueda
    productos = Producto.objects.filter(
        nombre__icontains=query,
        precio__gte=min_price,
        precio__lte=max_price
    ).order_by(order_by)

    return render(request, 'productos/search_results.html', {'productos': productos})
def filter_products(request):
    query = request.GET.get('query', '')
    min_price = request.GET.get('min_price', '')
    max_price = request.GET.get('max_price', '')
    order_by = request.GET.get('order_by', 'nombre')

    # Definir valores predeterminados para min_price y max_price
    default_min_price = Decimal('0')
    default_max_price = Decimal('1000000')  # Valor alto para simular infinito

    try:
        if min_price:
            min_price = Decimal(min_price)
        else:
            min_price = default_min_price
        
        if max_price:
            max_price = Decimal(max_price)
        else:
            max_price = default_max_price

    except (ValidationError, ValueError, InvalidOperation) as e:
        min_price = default_min_price
        max_price = default_max_price
        print(f"Error converting price values: {e}")

    # Construir la consulta base con el filtro de búsqueda
    productos_query = Producto.objects.all()

    if query:
        productos_query = productos_query.filter(nombre__icontains=query)

    # Aplicar filtros de precio
    productos_query = productos_query.filter(
        precio__gte=min_price,
        precio__lte=max_price
    )

    # Aplicar ordenamiento
    if order_by == 'price_asc':
        productos_query = productos_query.order_by('precio')
    elif order_by == 'price_desc':
        productos_query = productos_query.order_by('-precio')
    else:
        productos_query = productos_query.order_by(order_by)

    return render(request, 'productos/search_results.html', {'productos': productos_query})

def aplicar_cupon(request):
    if request.method == 'POST':
        codigo_cupon = request.POST.get('codigo_cupon', '').strip()  # Asegúrate de que el valor esté limpio
        try:
            cupon = Cupon.objects.get(nombre=codigo_cupon)
        except Cupon.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Cupón no válido.'})

        # Obtener el pedido en curso para el usuario
        pedido = get_object_or_404(Pedido, usuario=request.user, estado='carrito')

        if cupon.tipo == 'unico' and cupon.cantidad_usuarios <= 0:
            return JsonResponse({'success': False, 'message': 'El cupón ha sido usado por todos los usuarios permitidos.'})

        # Calcular el nuevo total con el descuento
        total_carrito = calcular_total_carrito(request.user)
        descuento = cupon.descuento
        total_con_descuento = total_carrito - (total_carrito * (descuento / 100))

        # Actualizar el pedido con el descuento aplicado
        pedido.descuento = descuento
        pedido.total_compras = total_con_descuento
        pedido.save()

        return JsonResponse({
            'success': True,
            'message': f'Cupón aplicado: {cupon.nombre}',
            'descuento': descuento,
            'total': total_con_descuento  # Devuelve el nuevo total
        })
    return JsonResponse({'success': False, 'message': 'Método no permitido.'})

@csrf_exempt
@login_required
def get_cart_item_count(request):
    try:
        carrito_items = Carrito.objects.filter(usuario=request.user)
        item_count = carrito_items.aggregate(total_count=Sum('cantidad'))['total_count'] or 0
    except Carrito.DoesNotExist:
        item_count = 0

    return JsonResponse({'count': item_count})