import { useState, useEffect } from 'react'
import './TodoList.css'

const API = 'https://ruta1-fullstack.onrender.com'

export default function TodoList() {
  const [tasks, setTasks] = useState([])
  const [newTask, setNewTask] = useState('')
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [user, setUser] = useState(null)
  const [error, setError] = useState('')

    // CARGAR TAREAS CON MANEJO DE ERRORES + AUTO-LOGOUT
  useEffect(() => {
    const token = localStorage.getItem('token')
    if (token) {
      fetchTasks(token)
    }
  }, [])

  const fetchTasks = async (token) => {
    try {
      const res = await fetch(`${API}/tasks`, {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      if (!res.ok) {
        if (res.status === 401) {
          // Token inválido → logout automático
          localStorage.removeItem('token')
          setUser(null)
          setTasks([])
          return
        }
        throw new Error('Error al cargar tareas')
      }
      const data = await res.json()
      setTasks(data)
    } catch (err) {
      console.error(err)
      setTasks([])
    }
  }

  const login = async () => {
    setError('')
    try {
      const res = await fetch(`${API}/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: new URLSearchParams({ username, password })
      })
      const data = await res.json()
      if (!res.ok) throw new Error(data.detail || 'Error de login')
      localStorage.setItem('token', data.access_token)
      setUser(username)
      fetchTasks(data.access_token)
    } catch (err) {
      setError(err.message)
    }
  }

  const logout = () => {
    localStorage.removeItem('token')
    setUser(null)
    setTasks([])
    setUsername('')
    setPassword('')
  }

    const addTask = async () => {
    if (!newTask.trim()) return
    const token = localStorage.getItem('token')
    try {
      const res = await fetch(`${API}/tasks`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ text: newTask, completed: false })
      })
      if (!res.ok) {
        if (res.status === 401) {
          logout()
          return
        }
        throw new Error('Error al agregar')
      }
      const t = await res.json()
      setTasks(prev => [...prev, t])
      setNewTask('')
    } catch (err) {
      setError('Error: sesión expirada')
    }
  }

    const toggleTask = async (id, currentCompleted) => {
    const token = localStorage.getItem('token')
    if (!token) {
      logout()
      return
    }

    try {
      const res = await fetch(`${API}/tasks/${id}`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          text: tasks.find(t => t.id === id).text,
          completed: !currentCompleted
        })
      })

      if (!res.ok) {
        if (res.status === 401) {
          logout()
          return
        }
        throw new Error('Error al actualizar')
      }

      setTasks(prev => prev.map(t =>
        t.id === id ? { ...t, completed: !currentCompleted } : t
      ))
    } catch (err) {
      setError('Sesión expirada. Vuelve a entrar.')
      logout()
    }
  }

  const deleteTask = async (id) => {
    const token = localStorage.getItem('token')
    if (!token) {
      logout()
      return
    }

    try {
      const res = await fetch(`${API}/tasks/${id}`, {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${token}` }
      })

      if (!res.ok) {
        if (res.status === 401) {
          logout()
          return
        }
        throw new Error('Error al eliminar')
      }

      setTasks(prev => prev.filter(t => t.id !== id))
    } catch (err) {
      setError('Sesión expirada. Vuelve a entrar.')
      logout()
    }
  }

  if (!user) {
    return (
      <div className="login-container">
        <div className="login-box">
          <h2>Login ToDo App</h2>
          {error && <p className="error">{error}</p>}
          <input
            type="text"
            placeholder="Usuario"
            value={username}
            onChange={e => setUsername(e.target.value)}
          />
          <input
            type="password"
            placeholder="Contraseña"
            value={password}
            onChange={e => setPassword(e.target.value)}
            onKeyPress={e => e.key === 'Enter' && login()}
          />
          <button onClick={login}>Entrar</button>
          <p><small>Prueba: david / 1234</small></p>
        </div>
      </div>
    )
  }

  return (
    <div className="todo-container">
      <div className="header">
        <h2>Bienvenido, {user}!</h2>
        <button onClick={logout} className="logout">Logout</button>
      </div>

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
              onChange={() => toggleTask(t.id, t.completed)}
            />
            <span>{t.text}</span>
            <button className="delete" onClick={() => deleteTask(t.id)}>
              ❌
            </button>
          </li>
        ))}
      </ul>
    </div>
  )
}