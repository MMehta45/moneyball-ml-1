import { spawn } from 'node:child_process'
import { readFile } from 'node:fs/promises'
import path from 'node:path'
import { defineConfig, type Plugin } from 'vite'
import react from '@vitejs/plugin-react'

function deapSchedulePlugin(): Plugin {
  const rootDir = process.cwd()
  const scriptPath = path.join(rootDir, 'generate_schedule_file.py')
  const schedulePath = path.join(rootDir, 'schedule.json')

  return {
    name: 'deap-schedule-api',
    configureServer(server) {
      server.middlewares.use('/api/generate-schedule', async (req, res) => {
        if (req.method !== 'POST') {
          res.statusCode = 405
          res.end('Method Not Allowed')
          return
        }

        const child = spawn('python3', [scriptPath], {
          cwd: rootDir,
          env: { ...process.env, MPLCONFIGDIR: '/private/tmp' },
        })

        let stdout = ''
        let stderr = ''

        child.stdout.on('data', (chunk) => {
          stdout += chunk.toString()
        })
        child.stderr.on('data', (chunk) => {
          stderr += chunk.toString()
        })

        child.on('close', async (code) => {
          if (code !== 0) {
            res.statusCode = 500
            res.setHeader('Content-Type', 'application/json')
            res.end(JSON.stringify({ error: 'schedule_generation_failed', details: stderr || stdout }))
            return
          }

          const scheduleJson = await readFile(schedulePath, 'utf8')
          res.statusCode = 200
          res.setHeader('Content-Type', 'application/json')
          res.end(scheduleJson)
        })
      })
    },
  }
}

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react(), deapSchedulePlugin()],
  server: {
    port: 5173,
    open: true,
  },
  build: {
    outDir: 'dist',
    sourcemap: false,
  },
})
