import { useState } from 'react'
import './App.css'

function App() {
  const [count, setCount] = useState(0)

  return (
    <div className="container">
      <h1>Mi Contador React</h1>
      <button onClick={() => setCount(count + 1)}>
        Clicks: {count}
      </button>
      <p>¡Funciona 100% con useState!</p>
      <p className="author">Por: David (Bootcamp Día 2)</p>
    </div>
  )
}

export default App