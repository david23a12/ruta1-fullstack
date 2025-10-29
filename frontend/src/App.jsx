import TodoList from './components/TodoList'
import './App.css'

function App() {
  return (
    <div className="app">
      <header>
        <h1>Bootcamp Full Stack</h1>
        <p>Día 3: ToDo List con React</p>
      </header>
      <TodoList />
    </div>
  )
}

export default App