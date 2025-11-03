import { useState, useEffect } from 'react'
import './TodoList.css'

export default function TodoList() {
  const [tasks, setTasks] = useState([])
  const [newTask, setNewTask] = useState('')
  
  const API = 'http://localhost:8000'

  // CARGAR TAREAS AL INICIAR
  useEffect(() => {
    fetch(`${API}/tasks`)
      .then(r => r.json())
      .then(setTasks)
      .catch(err => console.error('Error cargando tareas:', err))
  }, [])

  const addTask = () => {
    if (!newTask.trim()) return
    const task = { id: Date.now(), text: newTask, completed: false }
    fetch(`${API}/tasks`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(task)
    })
    .then(r => r.json())
    .then(t => {
      setTasks(prev => [...prev, t])
      setNewTask('')
    })
    .catch(err => console.error('Error agregando:', err))
  }

  const toggleTask = (id) => {
    const task = tasks.find(t => t.id === id)
    const updated = { ...task, completed: !task.completed }
    fetch(`${API}/tasks/${id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(updated)
    })
    .then(() => {
      setTasks(prev => prev.map(t => t.id === id ? updated : t))
    })
  }

  const deleteTask = (id) => {
    fetch(`${API}/tasks/${id}`, { method: 'DELETE' })
      .then(() => {
        setTasks(prev => prev.filter(t => t.id !== id))
      })
  }

  return (
    <div className="todo-container">
      <h2>ToDo List Full Stack</h2>
      <p><strong>Backend FastAPI</strong> | Día 4</p>
      
      <div className="input-group">
        <input
          value={newTask}
          onChange={e => setNewTask(e.target.value)}
          onKeyPress={e => e.key === 'Enter' && addTask()}
          placeholder="Nueva tarea..."
        />
        <button onClick={addTask}>Agregar</button>
      </div>

      <ul className="task-list">
        {tasks.map(t => (
          <li key={t.id} className={t.completed ? 'completed' : ''}>
            <input 
              type="checkbox" 
              checked={t.completed} 
              onChange={() => toggleTask(t.id)} 
            />
            <span>{t.text}</span>
            <button className="delete" onClick={() => deleteTask(t.id)}>
              ❌
            </button>
          </li>
        ))}
      </ul>

      <footer>
        <small>Tareas guardadas en <code>backend/tasks.json</code></small>
      </footer>
    </div>
  )
}