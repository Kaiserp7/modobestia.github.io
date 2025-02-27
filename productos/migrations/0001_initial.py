# Generated by Django 4.2.4 on 2024-07-27 04:06

from decimal import Decimal
from django.conf import settings
import django.contrib.auth.models
import django.contrib.auth.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Usuario',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('es_administrador', models.BooleanField(default=False)),
                ('nombre', models.CharField(default='Nombre', max_length=50)),
                ('apellido', models.CharField(default='Apellido', max_length=50)),
                ('rut', models.CharField(default='12345678-9', max_length=12)),
                ('telefono', models.CharField(default='123456789', max_length=15)),
                ('direccion', models.CharField(default='Dirección', max_length=100)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Categoria',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100)),
                ('descripcion', models.TextField()),
                ('imagen', models.ImageField(upload_to='categorias/')),
            ],
        ),
        migrations.CreateModel(
            name='Cupon',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100, unique=True)),
                ('cantidad_usuarios', models.PositiveIntegerField()),
                ('tipo', models.CharField(choices=[('permanente', 'Permanente'), ('unico', 'Único')], max_length=50)),
                ('descuento', models.DecimalField(decimal_places=2, max_digits=5)),
                ('fecha_creacion', models.DateTimeField(auto_now_add=True)),
                ('fecha_expiracion', models.DateTimeField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Pedido',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('estado', models.CharField(choices=[('aceptado', 'Compra Aceptada'), ('rechazado', 'Compra Rechazada'), ('preparacion', 'Pedido en Preparación'), ('enviado', 'Pedido Enviado'), ('recibido', 'Compra Recibida por el Cliente'), ('local', 'Pedido Tomado para Retiro Local')], max_length=20)),
                ('fecha', models.DateTimeField(auto_now_add=True)),
                ('total_compras', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=10)),
                ('tipo_envio', models.CharField(choices=[('domicilio_registro', 'A domicilio (Usar dirección de registro)'), ('retiro_sucursal', 'Retiro en sucursal (Modo bestia Los Ángeles CHILE Galeria Colon Calle Valdivia Frente al Mall)')], default='domicilio_registro', max_length=50)),
                ('direccion_envio', models.CharField(blank=True, max_length=255, null=True)),
                ('descuento', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=5)),
                ('descuento_aplicado', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Producto',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=200)),
                ('descripcion', models.TextField()),
                ('sabor', models.CharField(max_length=100)),
                ('sabor_secundario', models.CharField(blank=True, max_length=100, null=True)),
                ('precio', models.DecimalField(decimal_places=2, max_digits=10)),
                ('imagen', models.ImageField(upload_to='productos/')),
                ('imagen_secundaria', models.ImageField(blank=True, null=True, upload_to='productos/')),
                ('stock', models.PositiveIntegerField()),
                ('es_oferta', models.BooleanField(default=False)),
                ('descuento', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ('fecha_inicio_oferta', models.DateTimeField(blank=True, null=True)),
                ('fecha_fin_oferta', models.DateTimeField(blank=True, null=True)),
                ('imagen_oferta', models.ImageField(blank=True, null=True, upload_to='ofertas/')),
                ('categoria', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='productos.categoria')),
            ],
        ),
        migrations.CreateModel(
            name='Venta',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cantidad', models.PositiveIntegerField()),
                ('fecha', models.DateTimeField(auto_now_add=True)),
                ('producto', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='productos.producto')),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Slider',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('imagen_slider', models.ImageField(upload_to='sliders/')),
                ('imagen_decorativa', models.ImageField(blank=True, null=True, upload_to='decorativas/')),
                ('url_imagen_decorativa', models.URLField(blank=True, null=True)),
                ('categoria', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sliders', to='productos.categoria')),
                ('productos', models.ManyToManyField(to='productos.producto')),
            ],
        ),
        migrations.CreateModel(
            name='PedidoProducto',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cantidad', models.PositiveIntegerField()),
                ('precio_unitario', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=10)),
                ('pedido', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='productos', to='productos.pedido')),
                ('producto', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='productos.producto')),
            ],
        ),
        migrations.CreateModel(
            name='OfertaCarrusel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre_oferta', models.CharField(max_length=200)),
                ('fecha_inicio', models.DateTimeField()),
                ('fecha_fin', models.DateTimeField()),
                ('imagen_promocional', models.ImageField(upload_to='ofertas_carrusel/')),
                ('categoria', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='productos.categoria')),
            ],
        ),
        migrations.CreateModel(
            name='Oferta',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('descuento', models.DecimalField(decimal_places=2, max_digits=5)),
                ('fecha_inicio', models.DateTimeField()),
                ('fecha_fin', models.DateTimeField()),
                ('producto', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='productos.producto')),
            ],
        ),
        migrations.CreateModel(
            name='HistorialVentas',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha', models.DateField()),
                ('total_ventas', models.DecimalField(decimal_places=2, max_digits=10)),
                ('ganancia_total', models.DecimalField(decimal_places=2, max_digits=10)),
                ('perdida_total', models.DecimalField(decimal_places=2, max_digits=10)),
                ('detalle_ventas', models.TextField(default='Detalles de la venta')),
                ('pedido', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='productos.pedido')),
            ],
        ),
        migrations.CreateModel(
            name='EstadisticasVentas',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cantidad_vendida', models.PositiveIntegerField(default=0)),
                ('total_ventas_diarias', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('total_ventas_semanales', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('total_ventas_mensuales', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('producto', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='productos.producto')),
            ],
        ),
        migrations.CreateModel(
            name='Carrito',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cantidad', models.PositiveIntegerField(default=1)),
                ('producto', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='productos.producto')),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
