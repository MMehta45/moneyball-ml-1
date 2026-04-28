import WelcomeScreen from './WelcomeScreen'

export default function App() {
  const handleStart = (hours: number) => {
    console.log('Starting with hours:', hours)
    // TODO: connect to DEAP on Tuesday
  }

  return <WelcomeScreen onStart={handleStart} />
}
