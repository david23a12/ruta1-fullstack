// === DÍA 1: JAVASCRIPT MODERNO ===

// 1. let vs const + template literals
let nombre = "Ana";
const edad = 25;
console.log(`Hola, soy ${nombre} y tengo ${edad} años`);

// 2. Arrow function
const saludar = (nombre) => `Hola ${nombre}!`;
console.log(saludar("Carlos"));

// 3. Destructuring
const persona = { nombre: "Luis", ciudad: "Madrid", rol: "dev" };
const { nombre: nombrePersona, ciudad } = persona;
console.log(`Nombre: ${nombrePersona}, Ciudad: ${ciudad}`);

// 4. Spread operator
const numeros = [1, 2, 3];
const masNumeros = [...numeros, 4, 5];
console.log(masNumeros);

// 5. Función con template + arrow
const crearMensaje = (nombre, edad) => `
  Hola ${nombre},
  Tienes ${edad} años.
  ¡Bienvenido al bootcamp!
`;
console.log(crearMensaje("María", 30));