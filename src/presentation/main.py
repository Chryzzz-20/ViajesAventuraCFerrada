from src.business.auth_service import AuthService
from src.business.destination_service import DestinationService
from src.business.reservation_service import ReservationService
from src.business.travel_package_service import TravelPackageService
from src.domain.destination import Destination
from src.domain.reservation import Reservation
from src.domain.travel_package import TravelPackage
from src.domain.user import User


def _read_int(prompt: str) -> int:
    raw = input(prompt).strip()
    try:
        return int(raw)
    except ValueError as exc:
        raise ValueError("Debes ingresar un número entero válido.") from exc


def _read_float_list(prompt: str, expected_count: int) -> list[float]:
    raw = input(prompt).strip()
    parts = [p.strip() for p in raw.split(",") if p.strip()]
    if len(parts) != expected_count:
        raise ValueError(
            f"Debes ingresar exactamente {expected_count} montos separados por coma."
        )
    values: list[float] = []
    for part in parts:
        try:
            values.append(float(part))
        except ValueError as exc:
            raise ValueError(f"Monto inválido: '{part}'.") from exc
    return values


def _read_int_list(prompt: str) -> list[int]:
    raw = input(prompt).strip()
    parts = [p.strip() for p in raw.split(",") if p.strip()]
    if not parts:
        raise ValueError("Debes ingresar al menos un ID numérico.")
    ids: list[int] = []
    for part in parts:
        try:
            ids.append(int(part))
        except ValueError as exc:
            raise ValueError(f"ID inválido: '{part}'.") from exc
    return ids


def _read_yes_no(prompt: str) -> bool:
    while True:
        answer = input(prompt).strip().lower()
        if answer in ("s", "si", "sí"):
            return True
        if answer in ("n", "no"):
            return False
        print("Respuesta no válida. Escribe 's' para sí o 'n' para no.")


def _print_destination(dest: Destination) -> None:
    state = "Activo" if dest.active else "Retirado"
    print(f"[{dest.id}] {dest.name}, {dest.country} - Estado: {state}")


def _print_package(pkg: TravelPackage) -> None:
    state = "Activo" if pkg.active else "Inactivo"
    dest_str = ", ".join(str(d_id) for d in pkg.destination_ids) or "Ninguno"
    print(
        f"[{pkg.id}] {pkg.name} | Fechas: {pkg.start_date} a {pkg.end_date} "
        f"| Total: ${pkg.total_cost:.2f} | Destinos IDs: [{dest_str}] | Estado: {state}"
    )


def _print_reservation(res: Reservation) -> None:
    print(
        f"[{res.id}] Usuario ID: {res.user_id} | Paquete ID: {res.package_id} "
        f"| Viajeros: {res.travelers_count} | Total: ${res.total_amount:.2f} "
        f"| Estado: {res.status} | Fecha: {res.created_at}"
    )


def _handle_auth_menu(
    auth_service: AuthService, current_user: User | None
) -> User | None:
    while True:
        session_label = (
            f"{current_user.full_name} ({current_user.email})"
            if current_user
            else "Sin sesión iniciada"
        )
        print(f"\n--- CUENTA Y AUTENTICACIÓN [{session_label}] ---")
        print("1. Registrarse")
        print("2. Iniciar sesión")
        if current_user:
            print("3. Cerrar sesión")
        print("0. Volver al menú principal")

        opt = input("Selecciona una opción: ").strip()
        if opt == "1":
            full_name = input("Nombre completo: ")
            email = input("Correo electrónico: ")
            password = input("Contraseña (mínimo 8 caracteres): ")
            created = auth_service.register(full_name, email, password)
            print(f"Cuenta creada para {created.full_name} (ID {created.id}).")
        elif opt == "2":
            email = input("Correo electrónico: ")
            password = input("Contraseña: ")
            logged = auth_service.login(email, password)
            current_user = logged
            print(f"Sesión iniciada como {logged.full_name}.")
        elif opt == "3" and current_user:
            current_user = None
            print("Sesión cerrada correctamente.")
        elif opt == "0":
            return current_user
        else:
            print("Opción no válida.")


def _handle_destinations_menu(dest_service: DestinationService) -> None:
    while True:
        print("\n--- GESTIÓN DE DESTINOS ---")
        print("1. Registrar destino")
        print("2. Listar todos los destinos")
        print("3. Listar solo destinos activos")
        print("4. Modificar destino")
        print("5. Eliminar o retirar destino")
        print("0. Volver al menú principal")

        opt = input("Selecciona una opción: ").strip()
        if opt == "1":
            name = input("Nombre del destino: ")
            country = input("País: ")
            created = dest_service.create_destination(name, country)
            print(
                f"Destino registrado con ID {created.id}: {created.name} ({created.country})."
            )
        elif opt == "2":
            items = dest_service.list_destinations(only_active=False)
            if not items:
                print("No hay destinos registrados.")
            for d in items:
                _print_destination(d)
        elif opt == "3":
            items = dest_service.list_destinations(only_active=True)
            if not items:
                print("No hay destinos activos.")
            for d in items:
                _print_destination(d)
        elif opt == "4":
            dest_id = _read_int("ID del destino a modificar: ")
            name = input("Nuevo nombre: ")
            country = input("Nuevo país: ")
            updated = dest_service.update_destination(dest_id, name, country)
            print(
                f"Destino [{updated.id}] actualizado: {updated.name} ({updated.country})."
            )
        elif opt == "5":
            dest_id = _read_int("ID del destino: ")
            has_trips = _read_yes_no("¿Tiene viajes o paquetes asociados? (s/n): ")
            msg = dest_service.retire_or_delete_destination(
                dest_id, has_associated_trips=has_trips
            )
            print(msg)
        elif opt == "0":
            return
        else:
            print("Opción no válida.")


def _handle_packages_menu(package_service: TravelPackageService) -> None:
    while True:
        print("\n--- GESTIÓN DE PAQUETES TURÍSTICOS ---")
        print("1. Crear paquete turístico")
        print("2. Listar todos los paquetes")
        print("3. Listar paquetes disponibles")
        print("4. Desactivar paquete")
        print("0. Volver al menú principal")

        opt = input("Selecciona una opción: ").strip()
        if opt == "1":
            name = input("Nombre del paquete: ")
            start_date = input("Fecha de inicio (AAAA-MM-DD): ")
            end_date = input("Fecha de término (AAAA-MM-DD): ")
            dest_ids = _read_int_list("IDs de destinos separados por coma (ej. 1,2): ")
            custom_costs = _read_yes_no(
                "¿Deseas ingresar costos por destino manualmente? (s/n): "
            )
            costs = (
                _read_float_list(
                    f"Ingresa {len(dest_ids)} montos separados por coma: ",
                    len(dest_ids),
                )
                if custom_costs
                else None
            )
            created = package_service.create_package(
                name=name,
                start_date_str=start_date,
                end_date_str=end_date,
                destination_ids=dest_ids,
                destination_costs=costs,
            )
            print(
                f"Paquete creado con ID {created.id}: {created.name} (Total: ${created.total_cost:.2f})."
            )
        elif opt == "2":
            pkgs = package_service.list_packages(only_available=False)
            if not pkgs:
                print("No hay paquetes registrados.")
            for p in pkgs:
                _print_package(p)
        elif opt == "3":
            pkgs = package_service.list_packages(only_available=True)
            if not pkgs:
                print("No hay paquetes disponibles actualmente.")
            for p in pkgs:
                _print_package(p)
        elif opt == "4":
            pkg_id = _read_int("ID del paquete a desactivar: ")
            deactivated = package_service.deactivate_package(pkg_id)
            print(f"Paquete [{deactivated.id}] '{deactivated.name}' desactivado.")
        elif opt == "0":
            return
        else:
            print("Opción no válida.")


def _handle_reservations_menu(
    reservation_service: ReservationService, current_user: User | None
) -> None:
    while True:
        print("\n--- GESTIÓN DE RESERVAS ---")
        print("1. Crear reserva")
        print("2. Ver mis reservas")
        print("3. Cancelar reserva")
        print("0. Volver al menú principal")

        opt = input("Selecciona una opción: ").strip()
        if opt == "1":
            if not current_user or current_user.id is None:
                raise PermissionError(
                    "Debes iniciar sesión primero para crear una reserva."
                )
            pkg_id = _read_int("ID del paquete turístico: ")
            travelers = _read_int("Cantidad de viajeros: ")
            created = reservation_service.create_reservation(
                user_id=current_user.id,
                package_id=pkg_id,
                travelers_count=travelers,
            )
            print(
                f"Reserva confirmada con ID {created.id} por ${created.total_amount:.2f}."
            )
        elif opt == "2":
            if not current_user or current_user.id is None:
                raise PermissionError(
                    "Debes iniciar sesión primero para ver tus reservas."
                )
            items = reservation_service.list_user_reservations(current_user.id)
            if not items:
                print("Aún no tienes reservas registradas.")
            for r in items:
                _print_reservation(r)
        elif opt == "3":
            if not current_user or current_user.id is None:
                raise PermissionError(
                    "Debes iniciar sesión primero para cancelar una reserva."
                )
            res_id = _read_int("ID de la reserva a cancelar: ")
            cancelled = reservation_service.cancel_reservation(
                reservation_id=res_id,
                requester_user_id=current_user.id,
            )
            print(f"Reserva [{cancelled.id}] cancelada correctamente.")
        elif opt == "0":
            return
        else:
            print("Opción no válida.")


def show_main_menu(current_user: User | None) -> None:
    user_info = (
        f"Usuario: {current_user.full_name} (ID {current_user.id})"
        if current_user
        else "Usuario: Invitado (sin sesión)"
    )
    print(f"\n=== VIAJES AVENTURA === | {user_info}")
    print("1. Cuenta y autenticación")
    print("2. Destinos")
    print("3. Paquetes turísticos")
    print("4. Reservas")
    print("0. Salir")


def main() -> None:
    auth_service = AuthService()
    dest_service = DestinationService()
    package_service = TravelPackageService()
    reservation_service = ReservationService()
    current_user: User | None = None

    while True:
        show_main_menu(current_user)
        option = input("Selecciona una opción: ").strip()

        try:
            if option == "1":
                current_user = _handle_auth_menu(auth_service, current_user)
            elif option == "2":
                _handle_destinations_menu(dest_service)
            elif option == "3":
                _handle_packages_menu(package_service)
            elif option == "4":
                _handle_reservations_menu(reservation_service, current_user)
            elif option == "0":
                print("Saliendo del sistema...")
                break
            else:
                print("Opción no válida. Intenta nuevamente.")
        except ValueError as exc:
            print(f"Error de validación: {exc}")
        except LookupError as exc:
            print(f"Aviso: {exc}")
        except PermissionError as exc:
            print(f"Acceso restringido: {exc}")
        except Exception as exc:
            print(f"Ocurrió un error inesperado: {exc}")


if __name__ == "__main__":
    main()

