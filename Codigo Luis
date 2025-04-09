import random
from typing import List, Tuple

class ComparticionSecretoShamir:
    def __init__(self, primo: int = 2**127 - 1):
        """
        Inicializa el sistema con un número primo grande por defecto (2^127 - 1)
        """
        self.primo = primo
    
    def _evaluar_polinomio(self, coeficientes: List[int], x: int) -> int:
        """
        Evalúa un polinomio en un punto x usando los coeficientes dados
        """
        resultado = 0
        for coeficiente in reversed(coeficientes):
            resultado = (resultado * x + coeficiente) % self.primo
        return resultado
    
    def generar_particiones(self, secreto: int, num_particiones: int, umbral: int) -> List[Tuple[int, int]]:
        """
        Divide el secreto en particiones usando el esquema de Shamir
        """
        if umbral > num_particiones:
            raise ValueError("El umbral no puede ser mayor que el número de particiones")
        
        coeficientes = [secreto] + [random.randint(0, self.primo - 1) for _ in range(umbral - 1)]
        
        particiones = []
        for x in range(1, num_particiones + 1):
            y = self._evaluar_polinomio(coeficientes, x)
            particiones.append((x, y))
        
        return particiones
    
    def reconstruir_secreto(self, particiones: List[Tuple[int, int]]) -> int:
        """
        Reconstruye el secreto a partir de particiones usando interpolación de Lagrange
        """
        if len(particiones) < 2:
            raise ValueError("Se necesitan al menos 2 particiones")
        
        valores_x, valores_y = zip(*particiones)
        secreto = 0
        
        for i in range(len(particiones)):
            numerador, denominador = 1, 1
            for j in range(len(particiones)):
                if i != j:
                    numerador = (numerador * (-valores_x[j])) % self.primo
                    denominador = (denominador * (valores_x[i] - valores_x[j])) % self.primo
            
            termino = (valores_y[i] * numerador * pow(denominador, -1, self.primo)) % self.primo
            secreto = (secreto + termino) % self.primo
        
        return secreto

def obtener_entero(mensaje: str, minimo: int = 1) -> int:
    """
    Solicita al usuario un número entero válido
    """
    while True:
        try:
            valor = int(input(mensaje))
            if valor >= minimo:
                return valor
            print(f"El valor debe ser mayor o igual a {minimo}")
        except ValueError:
            print("Por favor ingrese un número entero válido")

def main():
    print("\n=== Sistema de Compartición de Secretos de Shamir ===")
    
    # Configuración inicial
    css = ComparticionSecretoShamir()
    
    # Paso 1: Ingresar el secreto
    secreto = obtener_entero("\nIngrese el número secreto (entero positivo): ")
    
    # Paso 2: Configurar las particiones
    num_particiones = obtener_entero("Ingrese el número total de particiones a generar: ")
    umbral = obtener_entero("Ingrese el número mínimo de particiones necesarias para reconstruir el secreto: ")
    
    while umbral > num_particiones:
        print("¡Error! El umbral no puede ser mayor que el número total de particiones")
        umbral = obtener_entero("Ingrese nuevamente el número mínimo de particiones: ")
    
    # Generar las particiones
    particiones = css.generar_particiones(secreto, num_particiones, umbral)
    
    print("\n=== Particiones Generadas ===")
    for idx, (x, y) in enumerate(particiones, 1):
        print(f"Partición {idx}: (x={x}, y={y})")
    
    # Reconstrucción del secreto
    print("\n=== Reconstrucción del Secreto ===")
    print(f"Ingrese al menos {umbral} particiones para reconstruir el secreto")
    print("Ingrese los números de las particiones separados por comas")
    
    while True:
        entrada = input("\nParticiones a usar (o 'Salir' para terminar): ").strip()
        if entrada.lower() == 'salir':
            break
        
        try:
            indices = [int(i.strip()) for i in entrada.split(',')]
            particiones_seleccionadas = [particiones[i-1] for i in indices if 1 <= i <= num_particiones]
            
            if len(particiones_seleccionadas) < umbral:
                print(f"Se necesitan al menos {umbral} particiones. Ud. ingresó {len(particiones_seleccionadas)}")
                continue
            
            secreto_recuperado = css.reconstruir_secreto(particiones_seleccionadas)
            print(f"\n¡Secreto reconstruido con éxito!: {secreto_recuperado}")
            
            if secreto_recuperado == secreto:
                print("El secreto coincide con el original")
            else:
                print("El secreto no coincide con el original")
            
        except (ValueError, IndexError):
            print("Entrada inválida. Por favor ingrese números de partición válidos")

if __name__ == "__main__":
    main()
