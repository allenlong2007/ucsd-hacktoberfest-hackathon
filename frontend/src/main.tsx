import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
// Shell styles first so the theme loaded by ./components (via App) wins.
import './App.css'
import App from './App'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
