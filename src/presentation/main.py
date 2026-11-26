from src.business.destination_service import DestinationService


def show_menu() -> None:
    print("\n=== VIAJES AVENTURA - GESTIÓN DE DESTINOS ===")
    print("1. Registrar destino")
    print("2. Listar todos los destinos")
    print("3. Listar solo destinos activos")
    print("4. Modificar destino")
    print("5. Eliminar o retirar destino")
    print("0. Salir")


def main() -> None:
    service = DestinationService()

    while True:
        show_menu()
        option = input("Selecciona una opción: ").strip()

        try:
            if option == "1":
                name = input("Nombre del destino: ")
                country = input("País: ")
                created = service.create_destination(name, country)
                print(
                    f"Destino registrado con ID {created.id}: {created.name} ({created.country})."
                )

            elif option == "2":
                destinations = service.list_destinations(only_active=False)
                if not destinations:
                    print("No hay destinos registrados.")
                for d in destinations:
                    state = "Activo" if d.active else "Retirado"
                    print(f"[{d.id}] {d.name}, {d.country} - Estado: {state}")

            elif option == "3":
                destinations = service.list_destinations(only_active=True)
                if not destinations:
                    print("No hay destinos activos.")
                for d in destinations:
                    print(f"[{d.id}] {d.name}, {d.country} - Estado: Activo")

            elif option == "4":
                dest_id = int(input("ID del destino a modificar: "))
                name = input("Nuevo nombre: ")
                country = input("Nuevo país: ")
                updated = service.update_destination(dest_id, name, country)
                print(
                    f"Destino [{updated.id}] actualizado: {updated.name} ({updated.country})."
                )

            elif option == "5":
                dest_id = int(input("ID del destino: "))
                has_trips_input = (
                    input("¿Tiene viajes o paquetes asociados? (s/n): ").strip().lower()
                )
                has_trips = has_trips_input == "s"
                message = service.retire_or_delete_destination(
                    dest_id, has_associated_trips=has_trips
                )
                print(message)

            elif option == "0":
                print("Saliendo del sistema...")
                break

            else:
                print("Opción no válida. Intenta nuevamente.")

        except ValueError as exc:
            print(f"Error de validación: {exc}")
        except LookupError as exc:
            print(f"Aviso: {exc}")
        except Exception as exc:
            print(f"Ocurrió un error inesperado: {exc}")


if __name__ == "__main__":
    main()

    