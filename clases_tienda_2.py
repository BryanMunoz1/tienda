import json
import os
import sys
import shutil
import datetime
from colorama import Fore, Style
import msvcrt

# ==========================
# Clases Producto y Carrito
# ==========================
class Producto:
    _listaproductos = []  # Cambiar a un solo guion bajo

    @classmethod
    def getlistaproductos(cls):
        return cls._listaproductos

    def __init__(self, codigoproducto, nombreproducto, inventarioproducto, precioproducto):
        self.__codigoproducto = codigoproducto
        self.__nombreproducto = nombreproducto
        self.__inventarioproducto = inventarioproducto
        self.__precioproducto = precioproducto

    # Getters y setters
    def getcodigoproducto(self):
        return self.__codigoproducto

    def getnombreproducto(self):
        return self.__nombreproducto

    def getinventarioproducto(self):
        return self.__inventarioproducto

    def setinventarioproducto(self, inventario):
        self.__inventarioproducto = inventario

    def getprecioproducto(self):
        return self.__precioproducto

    @classmethod
    def cargaarchivoproductos(cls):
        try:
            with open("datos.json", "r") as file:
                data = json.load(file)
                cls._listaproductos.clear()  # Limpiamos la lista antes de cargar los productos
                for prod in data.get("datos", []):
                    producto = Producto(
                        prod.get("codigo_producto"),
                        prod.get("nombre_producto"),
                        int(prod.get("inventario_producto")),
                        float(prod.get("precio_producto"))
                    )
                    cls._listaproductos.append(producto)
            print(Fore.GREEN + "Productos cargados correctamente." + Style.RESET_ALL)
        except FileNotFoundError:
            print(Fore.RED + "Archivo 'datos.json' no encontrado." + Style.RESET_ALL)
        except json.JSONDecodeError:
            print(Fore.RED + "Error en el formato del archivo JSON." + Style.RESET_ALL)

    @classmethod
    def mostrarproductos(cls):
        if not cls._listaproductos:
            print(Fore.YELLOW + "No hay productos para mostrar." + Style.RESET_ALL)
            return

        print(Fore.GREEN + "+-----------------------------------------------------------+")
        print(Fore.WHITE + "| Código   | Nombre                      | Inventario | Precio   |")
        print(Fore.GREEN + "+-----------------------------------------------------------+")
        for producto in cls._listaproductos:
            print(Fore.WHITE + f"| {str(producto.getcodigoproducto()).zfill(3):<8} | {producto.getnombreproducto():<27} | {producto.getinventarioproducto():<10} | ${producto.getprecioproducto():<8.2f} |" + Style.RESET_ALL)
        print(Fore.GREEN + "+-----------------------------------------------------------+" + Style.RESET_ALL)

    @classmethod
    def grabaarchivoproductos(cls):
        productos_data = {"datos": []}
        for prod in cls._listaproductos:
            productos_data["datos"].append({
                'codigo_producto': prod.getcodigoproducto(),
                'nombre_producto': prod.getnombreproducto(),
                'inventario_producto': prod.getinventarioproducto(),
                'precio_producto': prod.getprecioproducto()
            })
        try:
            with open("datos.json", "w") as file:
                json.dump(productos_data, file, indent=4)
            print(Fore.GREEN + "Productos guardados exitosamente." + Style.RESET_ALL)
        except Exception as e:
            print(Fore.RED + f"Error al guardar productos: {e}" + Style.RESET_ALL)

    @classmethod
    def cargarnuevoproducto(cls):
        while True:  # Permitir al usuario volver a intentar agregar productos
            print(Fore.GREEN + "Añadiendo un nuevo producto..." + Style.RESET_ALL)
            codigo = input(Fore.WHITE + "Ingrese el código del producto: " + Style.RESET_ALL)
            nombre = input(Fore.WHITE + "Ingrese el nombre del producto: " + Style.RESET_ALL)

            # Validar que el código y nombre no existan
            if any(prod.getcodigoproducto() == codigo for prod in cls._listaproductos):
                print(Fore.RED + "Error: Ya existe un producto con ese código." + Style.RESET_ALL)
                if input(Fore.WHITE + "¿Desea intentar agregar otro producto? (s/n): " + Style.RESET_ALL).lower() == 'n':
                    return
            
            if any(prod.getnombreproducto() == nombre for prod in cls._listaproductos):
                print(Fore.RED + "Error: Ya existe un producto con ese nombre." + Style.RESET_ALL)
                if input(Fore.WHITE + "¿Desea intentar agregar otro producto? (s/n): " + Style.RESET_ALL).lower() == 'n':
                    return

            try:
                inventario = int(input(Fore.WHITE + "Ingrese la cantidad en inventario: " + Style.RESET_ALL))
                precio = float(input(Fore.WHITE + "Ingrese el precio del producto: " + Style.RESET_ALL))
            except ValueError:
                print(Fore.RED + "Error: el inventario debe ser un número entero y el precio un número decimal." + Style.RESET_ALL)
                continue  # Permitir al usuario intentar nuevamente

            nuevo_producto = Producto(codigo, nombre, inventario, precio)
            cls._listaproductos.append(nuevo_producto)
            cls.grabaarchivoproductos()
            print(Fore.GREEN + "Producto añadido correctamente." + Style.RESET_ALL)
            break  # Salir del bucle si se agrega el producto correctamente

    @classmethod
    def borrarproducto(cls):
        codigo = input(Fore.WHITE + "Ingrese el código del producto a eliminar: " + Style.RESET_ALL)
        producto_a_borrar = next((p for p in cls._listaproductos if p.getcodigoproducto() == codigo), None)
        if producto_a_borrar:
            confirmacion = input(Fore.WHITE + "¿Está seguro de que desea eliminar el producto? (s/n): " + Style.RESET_ALL).lower()
            if confirmacion == 's':
                cls._listaproductos.remove(producto_a_borrar)
                cls.grabaarchivoproductos()
                print(Fore.GREEN + "Producto eliminado correctamente." + Style.RESET_ALL)
            else:
                print(Fore.YELLOW + "Operación cancelada." + Style.RESET_ALL)
        else:
            print(Fore.RED + "Producto no encontrado." + Style.RESET_ALL)

class ProductoCarrito:
    def __init__(self, codigoproducto, nombreproducto, cantidadproducto, precioproducto):
        self.__codigoproducto = codigoproducto
        self.__nombreproducto = nombreproducto 
        self.__cantidadproducto = cantidadproducto
        self.__precioproducto = precioproducto
        self.__subtotalproducto = cantidadproducto * precioproducto

    # Getters y setters
    def getcodigoproducto(self):
        return self.__codigoproducto

    def getnombreproducto(self): 
        return self.__nombreproducto

    def getcantidadproducto(self):
        return self.__cantidadproducto

    def setcantidadproducto(self, cantidad):
        self.__cantidadproducto = cantidad
        self._subtotalproducto = cantidad * self._precioproducto

    def getprecioproducto(self):
        return self.__precioproducto

    def getsubtotalproducto(self):
        return self.__subtotalproducto


class CarritoCompra:
    def __init__(self):
        self.__productoscarrito = []

    def agregarproducto(self, producto):
        self.__productoscarrito.append(producto)

    def calcular_total(self):
        total = sum([producto.getsubtotalproducto() for producto in self.__productoscarrito])
        return total

    def comprarproductos(self, productos_disponibles):
        while True:
            try:
                codigoproducto = input(Fore.WHITE + "Ingrese el código del producto que desea comprar (o 0 para finalizar): " + Style.RESET_ALL)
                if codigoproducto == '0':
                    break

                # Verificar si el código de producto es válido
                producto = next((p for p in productos_disponibles if p.getcodigoproducto() == codigoproducto), None)
                if producto is None:
                    print(Fore.RED + "El código de producto ingresado no existe." + Style.RESET_ALL)
                    continue

                # Mostrar información del producto encontrado
                nombreproducto = producto.getnombreproducto()
                cantidadstock = producto.getinventarioproducto()
                precioproducto = producto.getprecioproducto()
                print(Fore.GREEN + f"Producto: {nombreproducto}, Stock disponible: {cantidadstock}, Precio: ${precioproducto:.2f}" + Style.RESET_ALL)

                # Solicitar cantidad a comprar
                cantidad = int(input(Fore.WHITE + "Ingrese la cantidad que desea comprar: " + Style.RESET_ALL))
                if cantidad <= 0:
                    print(Fore.RED + "La cantidad debe ser mayor a cero." + Style.RESET_ALL)
                    continue

                # Verificar si hay suficiente stock
                if cantidad > cantidadstock:
                    print(Fore.RED + "No hay suficiente stock disponible." + Style.RESET_ALL)
                    continue

                # Agregar producto al carrito
                producto_carrito = ProductoCarrito(codigoproducto, nombreproducto, cantidad, precioproducto)
                self.agregarproducto(producto_carrito)

                # Actualizar inventario del producto en la lista disponible
                producto.setinventarioproducto(cantidadstock - cantidad)

            except ValueError:
                print(Fore.RED + "Error: por favor ingrese un número válido." + Style.RESET_ALL)
                continue

    def facturar(self):
        if not self.__productoscarrito:
            print(Fore.RED + "No hay productos en el carrito para facturar." + Style.RESET_ALL)
            return

        nombre = input(Fore.WHITE + "Ingrese su nombre: " + Style.RESET_ALL)
        documento = input(Fore.WHITE + "Ingrese su documento: " + Style.RESET_ALL)

        print(Fore.GREEN + f"\nFactura para: {nombre}")
        print(Fore.GREEN + f"Documento: {documento}")
        print(Fore.GREEN + "+---------------------------------------------------+")
        print(Fore.WHITE + "| Código | Nombre Producto        | Cantidad | Subtotal |")
        print(Fore.GREEN + "+---------------------------------------------------+")

        total = 0
        for producto in self.__productoscarrito:
            codigo = producto.getcodigoproducto()
            nombre = producto.getnombreproducto()
            cantidad = producto.getcantidadproducto()
            subtotal = producto.getsubtotalproducto()
            total += subtotal

            print(Fore.WHITE + f"| {str(codigo).zfill(3):<6} | {nombre:<22} | {cantidad:<8} | ${subtotal:<8.2f} |")

        print(Fore.GREEN + "+---------------------------------------------------+")
        print(Fore.WHITE + f"Total de la compra: ${total:.2f}" + Style.RESET_ALL)

        confirmacion = input(Fore.WHITE + "¿Desea confirmar la compra? (s/n): " + Style.RESET_ALL).lower()
        if confirmacion == 's':
            print(Fore.GREEN + "Compra confirmada. ¡Gracias por su compra!" + Style.RESET_ALL)
            self.__productoscarrito.clear()  # Limpiar carrito después de la compra
            Producto.grabaarchivoproductos()  # Guardar cambios
        else:
            print(Fore.YELLOW + "Compra cancelada." + Style.RESET_ALL)

    @staticmethod
    def copia_respaldo():
        fecha = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
        nombre_respaldo = f"respaldo_{fecha}.json"
        try:
            shutil.copy("datos.json", nombre_respaldo)
            print(Fore.GREEN + f"Copia de respaldo creada: {nombre_respaldo}" + Style.RESET_ALL)
        except FileNotFoundError:
            print(Fore.RED + "Error: Archivo 'datos.json' no encontrado. No se pudo crear la copia de respaldo." + Style.RESET_ALL)
        except Exception as e:
            print(Fore.RED + f"Error al crear copia de seguridad: {e}" + Style.RESET_ALL)

    @staticmethod
    def reparar_datos():
        try:
            archivos_respaldo = sorted([f for f in os.listdir() if f.startswith("respaldo") and f.endswith(".json")], reverse=True)
            archivos_respaldo.append("datos.json")  # Incluir el archivo principal 'datos.json'

            if archivos_respaldo:
                print(Fore.GREEN + "Copias de seguridad disponibles:" + Style.RESET_ALL)
                for idx, archivo in enumerate(archivos_respaldo):
                    print(Fore.WHITE + f"{idx + 1}. {archivo}" + Style.RESET_ALL)

                while True:
                    try:
                        seleccion = int(input(Fore.WHITE + "Seleccione el número del archivo a restaurar: " + Style.RESET_ALL)) - 1
                        if 0 <= seleccion < len(archivos_respaldo):
                            archivo_seleccionado = archivos_respaldo[seleccion]
                            shutil.copy(archivo_seleccionado, "datos.json")  # Restaurar datos
                            print(Fore.GREEN + f"Datos restaurados desde '{archivo_seleccionado}'." + Style.RESET_ALL)
                            break
                        else:
                            print(Fore.RED + "Opción no válida. Inténtelo de nuevo." + Style.RESET_ALL)
                    except ValueError:
                        print(Fore.RED + "Por favor, ingrese un número válido." + Style.RESET_ALL)
            else:
                print(Fore.RED + "No se encontraron copias de seguridad disponibles." + Style.RESET_ALL)

        except Exception as e:
            print(Fore.RED + f"Error al restaurar los datos: {e}" + Style.RESET_ALL)

    def mostrar_carrito(self):
        if not self.__productoscarrito:
            print(Fore.YELLOW + "El carrito está vacío." + Style.RESET_ALL)
            return

        print(Fore.GREEN + "+-----------------------------------------------------------+")
        print(Fore.WHITE + "| Código   | Nombre                      | Cantidad | Precio   | Subtotal  |")
        print(Fore.GREEN + "+-----------------------------------------------------------+")
        for producto in self.__productoscarrito:
            print(Fore.WHITE + f"| {producto.getcodigoproducto():<8} | {producto.getnombreproducto():<27} | {producto.getcantidadproducto():<8} | ${producto.getprecioproducto():<8.2f} | ${producto.getsubtotalproducto():<8.2f} |" + Style.RESET_ALL)
        print(Fore.GREEN + "+-----------------------------------------------------------+" + Style.RESET_ALL)

# ==========================
# Funciones Auxiliares
# ==========================
def mostrar_logo():
    logo = """
    ███████╗██╗███████╗███╗   ██╗██████╗  █████╗ 
    ╚══██╔══╝██║██╔════╝████╗  ██║██╔══██╗██╔══██╗
       ██║   ██║█████╗  ██╔██╗ ██║██║  ██║███████║
       ██║   ██║██╔══╝  ██║╚██╗██║██║  ██║██╔══██║
       ██║   ██║███████╗██║ ╚████║██████╔╝██║  ██║
       ╚═╝   ╚═╝╚══════╝╚═╝  ╚═══╝╚═════╝ ╚═╝  ╚═╝
    """
    print(Fore.CYAN + logo + Style.RESET_ALL)

# ==========================
# Menú Principal
# ==========================
def mostrar_menu():
    # Cargar productos al iniciar el menú
    Producto.cargaarchivoproductos()  # Cargar productos al inicio
    carrito = CarritoCompra()

    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        mostrar_logo()
        print("\n")
        print(Fore.CYAN + "***************************************" + Style.RESET_ALL)
        print(Fore.CYAN + "* 1  " + Fore.WHITE + "Cargar Datos                     *")
        print(Fore.CYAN + "* 2  " + Fore.WHITE + "Copia de Respaldo                *")
        print(Fore.CYAN + "* 3  " + Fore.WHITE + "Reparar Datos                    *")
        print(Fore.CYAN + "* 4  " + Fore.WHITE + "Grabar Nuevos Productos          *")
        print(Fore.CYAN + "* 5  " + Fore.WHITE + "Comprar Productos                *")
        print(Fore.CYAN + "* 6  " + Fore.WHITE + "Borrar Producto                  *")
        print(Fore.CYAN + "* 7  " + Fore.WHITE + "Imprimir Factura                 *")
        print(Fore.CYAN + "* 8  " + Fore.WHITE + "Cerrar APP                       *")
        print(Fore.CYAN + "***************************************" + Style.RESET_ALL)
        
        opcion = input(Fore.WHITE + "Seleccione una opción: " + Style.RESET_ALL)
        
        if opcion == '1':
            Producto.cargaarchivoproductos()
            Producto.mostrarproductos()
            input(Fore.WHITE + "Presione Enter para continuar..." + Style.RESET_ALL)
        elif opcion == '2':
            CarritoCompra.copia_respaldo()
            input(Fore.WHITE + "Presione Enter para continuar..." + Style.RESET_ALL)
        elif opcion == '3':
            CarritoCompra.reparar_datos()
            input(Fore.WHITE + "Presione Enter para continuar..." + Style.RESET_ALL)
        elif opcion == '4':
            Producto.mostrarproductos()  # Mostrar la tabla antes de agregar un nuevo producto
            Producto.cargarnuevoproducto()
            input(Fore.WHITE + "Presione Enter para continuar..." + Style.RESET_ALL)
        elif opcion == '5':
            Producto.mostrarproductos()
            carrito.comprarproductos(Producto.getlistaproductos())
            input(Fore.WHITE + "Presione Enter para continuar..." + Style.RESET_ALL)
        elif opcion == '6':
            Producto.mostrarproductos()  # Mostrar la tabla antes de borrar
            Producto.borrarproducto()
            input(Fore.WHITE + "Presione Enter para continuar..." + Style.RESET_ALL)
        elif opcion == '7':
            carrito.facturar()
            input(Fore.WHITE + "Presione Enter para continuar..." + Style.RESET_ALL)
        elif opcion == '8':
            # Guardar todos los cambios antes de salir
            Producto.grabaarchivoproductos()  # Guardar los cambios en productos
            print(Fore.GREEN + "Saliendo de la aplicación..." + Style.RESET_ALL)
            input(Fore.WHITE + "Presione Enter para continuar..." + Style.RESET_ALL)
            sys.exit()
        else:
            print(Fore.RED + "Opción no válida." + Style.RESET_ALL)
            input(Fore.WHITE + "Presione Enter para continuar..." + Style.RESET_ALL)

# ==========================
# Ejecución Principal
# ==========================
if __name__ == "__main__":
    mostrar_menu()