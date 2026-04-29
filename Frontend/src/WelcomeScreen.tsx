import { useState } from 'react'

interface WelcomeScreenProps {
  onStart: (minHoursPerSem: number) => void
}

const QUICK_MIN = [3, 6, 9, 12, 15]

type Step = 'landing' | 'modal'

export default function WelcomeScreen({ onStart }: WelcomeScreenProps) {
  const [step, setStep] = useState<Step>('landing')
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

  const handleGenerate = () => {
    if (!effectiveHours) {
      setError('Please enter or select a minimum.')
      return
    }
    if (effectiveHours < 1 || effectiveHours > 21) {
      setError('Enter a value between 1 and 21 hrs/sem.')
      return
    }
    onStart(effectiveHours)
  }

  const closeModal = () => {
    setStep('landing')
    setError('')
  }

  return (
    <>
      {/* ── Landing ── */}
      <div className="min-h-screen grid-bg flex items-center justify-center px-4">

        {/* Moneyball wordmark */}
        <div className="animate-fade-in opacity-0 fixed top-6 left-6 flex items-center gap-3">
          <div className="moneyball-badge">
            <span className="moneyball-word">Money</span>
            <span className="moneyball-word accent">ball</span>
          </div>
          <span className="moneyball-sub">Academics</span>
        </div>

        {/* Hero */}
        <div className="w-full max-w-md text-center">
          <div className="animate-slide-up opacity-0">
            <p
              className="text-xs tracking-widest uppercase mb-4"
              style={{ fontFamily: 'Space Mono, monospace', color: 'var(--orange)' }}
            >
              // schedule planner
            </p>
            <h1
              className="text-6xl font-bold leading-[1.05] cursor-blink mb-6"
              style={{ fontFamily: 'Space Mono, monospace', color: 'var(--dark)' }}
            >
              Plan your<br />
              <span style={{ color: 'var(--orange)' }}>degree.</span>
            </h1>
            <p
              className="text-sm leading-relaxed mb-10 mx-auto max-w-xs"
              style={{ color: 'rgba(13,31,23,0.5)', fontFamily: 'DM Sans, sans-serif' }}
            >
              We'll build your full UTD course schedule from start to finish.
            </p>
          </div>

          <div className="animate-slide-up opacity-0 delay-200">
            <button
              className="start-btn px-10 py-4 rounded-xl text-sm"
              onClick={() => setStep('modal')}
            >
              GET STARTED →
            </button>
          </div>
        </div>
      </div>

      {/* ── Modal overlay ── */}
      {step === 'modal' && (
        <div
          className="fixed inset-0 flex items-center justify-center px-4 z-50"
          style={{ background: 'rgba(13,31,23,0.45)', backdropFilter: 'blur(6px)' }}
          onClick={(e) => { if (e.target === e.currentTarget) closeModal() }}
        >
          <div
            className="modal-card w-full max-w-sm relative rounded-2xl p-8"
            style={{
              background: 'var(--cream)',
              border: '1px solid rgba(197,91,18,0.18)',
              boxShadow: '0 24px 60px rgba(13,31,23,0.25), 0 1px 0 rgba(255,255,255,0.9) inset',
            }}
          >
            <div className="corner-tl" />
            <div className="corner-br" />

            {/* Close */}
            <button
              onClick={closeModal}
              className="absolute top-4 right-4 text-xs"
              style={{ fontFamily: 'Space Mono, monospace', color: 'rgba(13,31,23,0.3)', background: 'none', border: 'none', cursor: 'pointer' }}
            >
              ✕
            </button>

            {/* Step indicator */}
            <p
              className="text-xs tracking-widest uppercase mb-5"
              style={{ fontFamily: 'Space Mono, monospace', color: 'var(--orange)' }}
            >
              // one quick question
            </p>

            {/* Question */}
            <h2
              className="text-xl font-bold leading-snug mb-2"
              style={{ fontFamily: 'Space Mono, monospace', color: 'var(--dark)' }}
            >
              Minimum hours<br />per semester?
            </h2>
            <p
              className="text-xs leading-relaxed mb-7"
              style={{ color: 'rgba(13,31,23,0.45)', fontFamily: 'DM Sans, sans-serif' }}
            >
              We'll make sure every semester meets this floor when building your plan.
            </p>

            {/* Label */}
            <label
              className="block text-xs tracking-widest uppercase mb-4"
              style={{ fontFamily: 'Space Mono, monospace', color: 'var(--green)', opacity: 0.65 }}
            >
              Min hrs / semester
            </label>

            {/* Number input */}
            <div className="relative mb-2">
              <input
                type="text"
                inputMode="numeric"
                className="hour-input"
                placeholder="12"
                value={selected !== null ? String(selected) : hours}
                onChange={handleInputChange}
                onFocus={() => setSelected(null)}
                maxLength={2}
                autoFocus
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
              <p className="text-xs mb-3" style={{ color: '#c0392b', fontFamily: 'Space Mono, monospace' }}>
                ! {error}
              </p>
            )}

            {/* Quick pills */}
            <div className="mt-5 mb-7">
              <p
                className="text-xs mb-3"
                style={{ fontFamily: 'Space Mono, monospace', color: 'rgba(13,31,23,0.3)' }}
              >
                Quick select:
              </p>
              <div className="flex flex-wrap gap-2">
                {QUICK_MIN.map(h => (
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

            {/* Generate */}
            <button
              className="start-btn w-full py-4 rounded-xl text-sm font-medium"
              onClick={handleGenerate}
              disabled={!effectiveHours}
            >
              GENERATE SCHEDULE →
            </button>
          </div>
        </div>
      )}
    </>
  )
}
