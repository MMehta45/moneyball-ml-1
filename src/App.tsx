import { useState } from 'react'
import WelcomeScreen from './components/WelcomeScreen.tsx'
import GraphFrontend from './components/GraphFrontend.tsx'

export default function App() {
  const [minHours, setMinHours] = useState<number | null>(null)
  const [darkMode, setDarkMode] = useState(false)

  const handleStart = (hours: number) => {
    setMinHours(hours)
  }

  const handleReset = () => {
    setMinHours(null)
  }

  return (
    <div className={`${darkMode ? 'dark' : ''}`}>
      {minHours === null ? (
        <WelcomeScreen onStart={handleStart} />
      ) : (
        <GraphFrontend
          minHours={minHours}
          darkMode={darkMode}
          onDarkModeToggle={() => setDarkMode(!darkMode)}
          onReset={handleReset}
        />
      )}
    </div>
  )
}
