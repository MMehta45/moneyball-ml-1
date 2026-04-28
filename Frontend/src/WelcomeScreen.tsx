import { useState } from 'react'

interface WelcomeScreenProps {
  onStart: (hours: number) => void
}

const QUICK_HOURS = [60, 90, 120, 150, 180]

export default function WelcomeScreen({ onStart }: WelcomeScreenProps) {
  const [hours, setHours] = useState<string>('')
  const [selected, setSelected] = useState<number | null>(null)
  const [error, setError] = useState('')

  const effectiveHours = selected ?? (hours ? parseInt(hours) : null)

  const handlePillClick = (h: number) => {
    setSelected(h)
    setHours('')
    setError('')
  }

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSelected(null)
    setError('')
    const val = e.target.value.replace(/\D/g, '')
    setHours(val)
  }

  const handleStart = () => {
    if (!effectiveHours) {
      setError('Please enter or select your credit hours.')
      return
    }
    if (effectiveHours < 1 || effectiveHours > 300) {
      setError('Enter a value between 1 and 300 hours.')
      return
    }
    onStart(effectiveHours)
  }

  return (
    <div className="min-h-screen grid-bg flex items-center justify-center px-4">

      {/* Top-left Moneyball wordmark */}
      <div className="animate-fade-in opacity-0 fixed top-6 left-6 flex items-center gap-3">
        <div className="moneyball-badge">
          <span className="moneyball-word">Money</span>
          <span className="moneyball-word accent">ball</span>
        </div>
        <span className="moneyball-sub">Academics</span>
      </div>

      {/* Main card */}
      <div className="w-full max-w-md">
        {/* Header block */}
        <div className="animate-slide-up opacity-0 mb-8">
          <p
            className="text-xs tracking-widest uppercase mb-3"
            style={{ fontFamily: 'Space Mono, monospace', color: 'var(--orange)' }}
          >
            // schedule planner
          </p>
          <h1
            className="text-5xl font-bold leading-[1.1] cursor-blink"
            style={{ fontFamily: 'Space Mono, monospace', color: 'var(--dark)' }}
          >
            Plan your<br />
            <span style={{ color: 'var(--orange)' }}>degree.</span>
          </h1>
          <p className="mt-4 text-sm leading-relaxed" style={{ color: 'rgba(13,31,23,0.55)', fontFamily: 'DM Sans, sans-serif' }}>
            Enter your required credit hours at UTD and our system will generate an optimized course schedule.
          </p>
        </div>

        {/* Input card */}
        <div
          className="animate-slide-up opacity-0 delay-200 relative rounded-2xl p-8"
          style={{
            background: 'rgba(253,248,243,0.9)',
            border: '1px solid rgba(197,91,18,0.15)',
            backdropFilter: 'blur(12px)',
            boxShadow: '0 2px 40px rgba(197,91,18,0.08), 0 1px 0 rgba(255,255,255,0.8) inset'
          }}
        >
          <div className="corner-tl" />
          <div className="corner-br" />

          {/* Label */}
          <label
            className="block text-xs tracking-widest uppercase mb-6"
            style={{ fontFamily: 'Space Mono, monospace', color: 'var(--green)', opacity: 0.7 }}
          >
            Credit Hours Required
          </label>

          {/* Big number input */}
          <div className="relative mb-2">
            <input
              type="text"
              inputMode="numeric"
              className="hour-input"
              placeholder="120"
              value={selected !== null ? String(selected) : hours}
              onChange={handleInputChange}
              onFocus={() => setSelected(null)}
              maxLength={3}
            />
            <span
              className="absolute right-0 bottom-3 text-xs"
              style={{ fontFamily: 'Space Mono, monospace', color: 'rgba(197,91,18,0.4)' }}
            >
              hrs
            </span>
          </div>

          {/* Error */}
          {error && (
            <p className="text-xs mb-4" style={{ color: '#c0392b', fontFamily: 'Space Mono, monospace' }}>
              ! {error}
            </p>
          )}

          {/* Quick select pills */}
          <div className="mt-6 mb-8">
            <p
              className="text-xs mb-3"
              style={{ fontFamily: 'Space Mono, monospace', color: 'rgba(13,31,23,0.35)' }}
            >
              Quick select:
            </p>
            <div className="flex flex-wrap gap-2">
              {QUICK_HOURS.map(h => (
                <button
                  key={h}
                  onClick={() => handlePillClick(h)}
                  className={`hour-pill px-3 py-1.5 rounded-md ${selected === h ? 'selected' : ''}`}
                  style={{ color: selected === h ? 'white' : 'var(--orange)' }}
                >
                  {h}
                </button>
              ))}
            </div>
          </div>

          {/* Divider */}
          <div
            className="mb-6 h-px"
            style={{ background: 'linear-gradient(90deg, transparent, rgba(197,91,18,0.15), transparent)' }}
          />

          {/* Start button */}
          <button
            className="start-btn w-full py-4 rounded-xl text-sm font-medium"
            onClick={handleStart}
            disabled={!effectiveHours}
          >
            GENERATE SCHEDULE →
          </button>
        </div>
      </div>
    </div>
  )
}
