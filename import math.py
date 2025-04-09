import math

# --- Funciones Auxiliares para Aritmética Modular ---
# (Son las mismas que en el ejemplo anterior, necesarias para la reconstrucción)

def extended_gcd(a, b):
    """Calcula el máximo común divisor extendido (gcd, x, y) tal que ax + by = gcd."""
    if a == 0:
        return b, 0, 1
    d, x1, y1 = extended_gcd(b % a, a)
    x = y1 - (b // a) * x1
    y = x1
    return d, x, y

def modInverse(a, m):
    """Calcula el inverso modular de a módulo m usando el algoritmo extendido de Euclides."""
    # Asegura que 'a' esté en el rango [0, m-1]
    a = a % m
    if a < 0:
        a += m

    gcd, x, y = extended_gcd(a, m)
    if gcd != 1:
        # Si a=0, el inverso no existe. O si gcd > 1 tampoco.
        raise ValueError(f"El inverso modular de {a} mod {m} no existe (gcd={gcd})")
    else:
        # Asegura que el resultado sea positivo
        return (x % m + m) % m

# --- Función Principal de Reconstrucción ---

def reconstruct_secret(shares, prime):
    """
    Reconstruye el secreto a partir de una lista de partes (shares) usando Interpolación de Lagrange.
    Cada 'share' en la lista debe ser una tupla o lista (x, y).
    Se necesita el número primo 'prime' correcto usado al crear las partes.
    """
    if not shares:
        raise ValueError("Se necesitan partes para reconstruir el secreto.")
    if len(shares) < 2:
         # Con una sola parte (k=1), el secreto es simplemente el valor y.
         # La interpolación de Lagrange como está implementada abajo requiere al menos 2 puntos
         # para calcular diferencias (xm - xj).
         # Si k=1 originalmente, la 'parte' (x,y) ya contiene el secreto como y (P(x)=S).
         # Pero S = P(0), así que necesitaríamos saber si P(x) era constante.
         # Shamir usualmente asume k>=2. Si k=1 fuera el caso, el secreto sería shares[0][1].
         # Lo más seguro es pedir al menos 2 partes si se usa Lagrange.
         # Si sólo tienes UNA parte y sospechas que k=1, el secreto *podría* ser shares[0][1].
         print("ADVERTENCIA: Solo se proporcionó una parte. Si el umbral k original era 1,")
         print(f"el secreto podría ser el valor 'y' de esa parte: {shares[0][1]}.")
         print("La interpolación estándar requiere al menos k=2 partes.")
         # Podríamos devolver shares[0][1] aquí si asumimos k=1, pero es más seguro fallar
         # o requerir que el usuario confirme si k=1.
         raise ValueError("Se requieren al menos 2 partes para la interpolación de Lagrange tal como está implementada.")


    k = len(shares) # El número de partes que PROPORCIONAS determina el grado del polinomio que se intenta ajustar.
                    # DEBE ser >= al 'k' original para obtener el secreto correcto.
    print(f"\nIntentando reconstruir con {k} partes...")

    # Verifica que las coordenadas x sean distintas
    x_coords = [s[0] for s in shares]
    if len(x_coords) != len(set(x_coords)):
        raise ValueError("Se encontraron coordenadas 'x' duplicadas en las partes proporcionadas.")

    # Usamos la Interpolación de Lagrange para encontrar P(0) directamente
    # P(0) = Sum( y_j * L_j(0) ) mod prime
    # donde L_j(0) = Product( x_m / (x_m - x_j) ) for m != j

    secret = 0
    # Usaremos los puntos directamente de la lista de 'shares'
    x_values = [s[0] for s in shares]
    y_values = {s[0]: s[1] for s in shares} # Diccionario para buscar y por x

    for j_idx, xj in enumerate(x_values): # Para cada punto (xj, yj) en las partes proporcionadas
        yj = y_values[xj]
        lagrange_basis_at_zero = 1 # L_j(0)

        for m_idx, xm in enumerate(x_values): # Calcular el producto para L_j(0)
            if j_idx != m_idx: # m != j
                # Numerador es x_m
                numerator = xm
                # Denominador es (x_m - x_j)
                denominator = (xm - xj)

                # Asegurarse de que el denominador no sea 0 antes de la inversión modular
                if denominator == 0:
                   raise ValueError(f"Error: intento de calcular L_j(0) con xm == xj ({xm} == {xj}), indica puntos duplicados?")

                try:
                    # Necesitamos el inverso modular del denominador
                    inv_denominator = modInverse(denominator, prime)
                except ValueError as e:
                     print(f"Error calculando el inverso modular para el denominador {(xm - xj)} mod {prime}.")
                     print(f"Esto puede ocurrir si (xm - xj) es múltiplo del primo {prime} o cero.")
                     raise e # Re-lanzar para indicar fallo

                # L_j(0) = Producto( num * inv_den ) mod prime
                term = (numerator * inv_denominator) % prime
                lagrange_basis_at_zero = (lagrange_basis_at_zero * term) % prime

        # Sumar el término y_j * L_j(0)
        term_j = (yj * lagrange_basis_at_zero) % prime
        secret = (secret + term_j) % prime

    return secret

# --- Cómo Usar ---

# 1. Pídele a tu amigo el número primo 'p' que usó.
#    ¡DEBE SER EXACTAMENTE EL MISMO!
try:
    prime_str = input("Introduce el número primo (p) que usó tu amigo: ")
    prime = int(prime_str)
    if prime <= 1:
        raise ValueError("El primo debe ser un entero mayor que 1.")
    # Podríamos añadir una prueba de primalidad básica si quisiéramos ser más robustos
except ValueError:
    print("Error: Ingresa un número entero válido para el primo.")
    exit() # Salir si el primo no es válido

# 2. Reúne las partes (shares) que te dio.
#    Necesitas al menos el número mínimo 'k' que él estableció.
shares_list = []
print("\nIntroduce las partes (shares) una por una.")
print("Escribe 'fin' cuando hayas terminado.")
print("Formato por línea: x,y (ejemplo: 1,12345)")

while True:
    share_input = input(f"Parte {len(shares_list) + 1} (o escribe 'fin'): ")
    if share_input.lower() == 'fin':
        if not shares_list:
            print("No se introdujeron partes. Saliendo.")
            exit()
        break # Salir del bucle si el usuario escribe 'fin'

    try:
        # Intenta dividir la entrada por la coma y convertir a enteros
        parts = share_input.split(',')
        if len(parts) != 2:
            raise ValueError("Formato incorrecto. Debe ser x,y")
        x = int(parts[0].strip())
        y = int(parts[1].strip())
        shares_list.append((x, y))
        print(f" -> Parte ({x},{y}) agregada.")
    except ValueError as e:
        print(f"Entrada inválida: '{share_input}'. Error: {e}. Intenta de nuevo con el formato x,y (ej: 3,9876).")
    except Exception as e:
        print(f"Ocurrió un error inesperado: {e}")


# 3. Llama a la función para reconstruir
if shares_list:
    try:
        print(f"\nUsando las siguientes {len(shares_list)} partes:")
        for s in shares_list:
            print(f"  ({s[0]}, {s[1]})")
        print(f"Y el primo p = {prime}")

        reconstructed = reconstruct_secret(shares_list, prime)
        print("\n--- Resultado ---")
        print(f"El secreto reconstruido es: {reconstructed}")
        print("-----------------")
        print("\nIMPORTANTE: Si el número de partes que proporcionaste es menor que el 'k' original,")
        print("o si el número primo es incorrecto, este resultado NO será el secreto real.")

    except ValueError as e:
        print(f"\nError durante la reconstrucción: {e}")
        print("Verifica que el número primo sea correcto, que las partes tengan el formato x,y,")
        print("que no haya coordenadas 'x' duplicadas y que tengas suficientes partes.")
    except Exception as e:
        print(f"\nOcurrió un error inesperado durante la reconstrucción: {e}")