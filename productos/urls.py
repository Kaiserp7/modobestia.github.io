# productos/urls.py

from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from .views import gestionar_slider, get_cart_item_count, mostrar_alerta, product_detail, productos_lista, search_products, verificar_autenticacion
from .views import ventas_diarias, ventas_semanales, ventas_mensuales,historial_y_estadisticas
urlpatterns = [
    path('', views.index, name='index'),
    path('pedido/<int:pedido_id>/', product_detail, name='product_detail'),
    path('producto/<int:producto_id>/', product_detail, name='product_detail'),
    path('categoria/<int:categoria_id>/', views.category, name='category'),
    path('crear-producto/', views.create_product, name='create_product'),
    path('crear-categoria/', views.create_category, name='create_category'),
    path('historial-ventas/', views.sales_history, name='sales_history'),
    path('registro/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('categoria/<int:categoria_id>/', views.ver_productos_categoria, name='ver_productos_categoria'),
    path('producto/editar/<int:producto_id>/', views.edit_product, name='edit_product'),
    path('producto/eliminar/<int:producto_id>/', views.delete_product, name='delete_product'),
    
    # URLs para el carrito de compras y pedidos
    path('agregar-al-carrito/<int:producto_id>/', views.agregar_al_carrito, name='agregar_al_carrito'),
    path('ver-carrito/', views.ver_carrito, name='ver_carrito'),
    path('realizar-pedido/', views.realizar_pedido, name='realizar_pedido'),
    path('estado-pedido/<int:pedido_id>/', views.estado_pedido, name='estado_pedido'),
    
   
    
    # URLs para la gestión de pedidos
    path('gestionar-pedidos/', views.gestionar_pedidos, name='gestionar_pedidos'),
    path('aprobar-pedido/<int:pedido_id>/', views.aprobar_pedido, name='aprobar_pedido'),
    path('cancelar-pedido/<int:pedido_id>/', views.cancelar_pedido, name='cancelar_pedido'),
    path('eliminar-pedido/<int:pedido_id>/', views.eliminar_pedido, name='eliminar_pedido'),
    
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('eliminar_pedido/<int:pedido_id>/', views.eliminar_pedido, name='eliminar_pedido'),
    path('some-path/', views.some_view, name='some_view'),
    path('mis-pedidos/', views.mis_pedidos, name='mis_pedidos'),
    path('actualizar-tipo-envio/<int:pedido_id>/', views.actualizar_tipo_envio, name='actualizar_tipo_envio'),
    path('carrito/modificar/<int:item_id>/', views.modificar_cantidad, name='modificar_cantidad'),
    path('carrito/eliminar/<int:item_id>/', views.eliminar_del_carrito, name='eliminar_del_carrito'),
    path('gestionar-slider/', gestionar_slider, name='gestionar_slider'),
    path('exportar_boleta/<int:pedido_id>/', views.exportar_boleta_pdf, name='exportar_boleta_pdf'),
    path('ventas-diarias/', ventas_diarias, name='ventas_diarias'),
    path('ventas-semanales/', ventas_semanales, name='ventas_semanales'),
    path('ventas-mensuales/', ventas_mensuales, name='ventas_mensuales'),
    path('historial-y-estadisticas/', historial_y_estadisticas, name='historial_y_estadisticas'),
    path('detalle_pedido/<int:id>/', views.detalle_pedido, name='detalle_pedido'),
    path('agregar_oferta/', views.agregar_oferta_carrusel, name='agregar_oferta_carrusel'),
    path('carrusel_ofertas/', views.carrusel_ofertas, name='carrusel_ofertas'),
    path('mostrar-alerta/', mostrar_alerta, name='mostrar_alerta'),
    path('verificar-autenticacion/', verificar_autenticacion, name='verificar_autenticacion'),
    path('productos/', productos_lista, name='productos_lista'),
    path('search/', search_products, name='search_products'),
    path('filter/', views.filter_products, name='filter_products'),
    path('aplicar-cupon/', views.aplicar_cupon, name='aplicar_cupon'),
    path('agregar-cupon/', views.agregar_cupon, name='agregar_cupon'),
    path('get-cart-item-count/', views.get_cart_item_count, name='get_cart_item_count'),
    

]
