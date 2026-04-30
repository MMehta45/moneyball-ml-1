import { useState } from 'react'
import WelcomeScreen from './components/WelcomeScreen.tsx'
import GraphFrontend from './components/GraphFrontend.tsx'

export default function App() {
  const [hasSchedule, setHasSchedule] = useState(false)
  const [scheduleVersion, setScheduleVersion] = useState(0)
  const [isGenerating, setIsGenerating] = useState(false)
  const [darkMode, setDarkMode] = useState(false)

  const handleStart = async () => {
    setIsGenerating(true)
    try {
      const response = await fetch('/api/generate-schedule', { method: 'POST' })
      if (!response.ok) {
        throw new Error('Failed to generate schedule')
      }
      await response.json()
      setScheduleVersion(Date.now())
      setHasSchedule(true)
    } finally {
      setIsGenerating(false)
    }
  }

  const handleReset = () => {
    setHasSchedule(false)
  }

  return (
    <div className={`${darkMode ? 'dark' : ''}`}>
      {!hasSchedule ? (
        <WelcomeScreen onStart={handleStart} isGenerating={isGenerating} />
      ) : (
        <GraphFrontend
          scheduleVersion={scheduleVersion}
          darkMode={darkMode}
          onDarkModeToggle={() => setDarkMode(!darkMode)}
          onReset={handleReset}
        />
      )}
    </div>
  )
}
