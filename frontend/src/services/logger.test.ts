import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { logger, onLog } from './logger'

describe('logger', () => {
  const originalConsole = {
    debug: console.debug,
    info: console.info,
    warn: console.warn,
    error: console.error,
  }

  beforeEach(() => {
    console.debug = vi.fn()
    console.info = vi.fn()
    console.warn = vi.fn()
    console.error = vi.fn()
  })

  afterEach(() => {
    console.debug = originalConsole.debug
    console.info = originalConsole.info
    console.warn = originalConsole.warn
    console.error = originalConsole.error
  })

  describe('debug', () => {
    it('should log debug messages with [DEBUG] prefix', () => {
      logger.debug('test debug message')
      expect(console.debug).toHaveBeenCalledWith('[DEBUG] test debug message', undefined)
    })

    it('should include data in debug log', () => {
      const data = { foo: 'bar' }
      logger.debug('test message', data)
      expect(console.debug).toHaveBeenCalledWith('[DEBUG] test message', data)
    })
  })

  describe('info', () => {
    it('should log info messages with [INFO] prefix', () => {
      logger.info('test info message')
      expect(console.info).toHaveBeenCalledWith('[INFO] test info message', undefined)
    })

    it('should include data in log', () => {
      const data = { foo: 'bar' }
      logger.info('test message', data)
      expect(console.info).toHaveBeenCalledWith('[INFO] test message', data)
    })
  })

  describe('warn', () => {
    it('should log warning messages with [WARN] prefix', () => {
      logger.warn('test warning')
      expect(console.warn).toHaveBeenCalledWith('[WARN] test warning', undefined)
    })
  })

  describe('error', () => {
    it('should log error messages', () => {
      logger.error('test error')
      expect(console.error).toHaveBeenCalledWith('test error', undefined)
    })

    it('should log error with Error object', () => {
      const error = new Error('Test error')
      logger.error('Something failed', error)
      expect(console.error).toHaveBeenCalledWith('Something failed', error)
    })

    it('should include context in error message', () => {
      logger.error('test error', null, { context: 'ErrorContext' })
      expect(console.error).toHaveBeenCalledWith('[ErrorContext] test error', null)
    })
  })

  describe('getUserMessage', () => {
    // In DEV mode, getUserMessage uses formatError which converts any value to string
    it('should format null as string in dev', () => {
      const result = logger.getUserMessage(null)
      expect(result).toBe('null')
    })

    it('should extract message from Error object', () => {
      const error = new Error('Specific error message')
      const result = logger.getUserMessage(error)
      expect(result).toBe('Specific error message')
    })

    it('should handle string error', () => {
      const result = logger.getUserMessage('String error')
      expect(result).toBe('String error')
    })

    it('should convert object to string', () => {
      const obj = { foo: 'bar' }
      const result = logger.getUserMessage(obj)
      expect(result).toBe('[object Object]')
    })
  })

  describe('onLog callback', () => {
    it('should call registered callbacks on log', () => {
      const callback = vi.fn()
      const unsubscribe = onLog(callback)

      logger.info('test message')

      expect(callback).toHaveBeenCalledWith(
        expect.objectContaining({
          level: 'info',
          message: 'test message',
        })
      )

      unsubscribe()
    })

    it('should allow unsubscribing', () => {
      const callback = vi.fn()
      const unsubscribe = onLog(callback)

      unsubscribe()
      logger.info('test message')

      expect(callback).not.toHaveBeenCalled()
    })

    it('should include error in callback for error logs', () => {
      const callback = vi.fn()
      const unsubscribe = onLog(callback)
      const error = new Error('Test error')

      logger.error('Error occurred', error)

      expect(callback).toHaveBeenCalledWith(
        expect.objectContaining({
          level: 'error',
          message: 'Error occurred',
          error: error,
        })
      )

      unsubscribe()
    })

    it('should include options in callback', () => {
      const callback = vi.fn()
      const unsubscribe = onLog(callback)

      logger.info('test', null, { context: 'TestCtx', showToast: true })

      expect(callback).toHaveBeenCalledWith(
        expect.objectContaining({
          options: expect.objectContaining({
            context: 'TestCtx',
            showToast: true,
          }),
        })
      )

      unsubscribe()
    })

    it('should include timestamp in callback', () => {
      const callback = vi.fn()
      const unsubscribe = onLog(callback)

      logger.info('test')

      expect(callback).toHaveBeenCalledWith(
        expect.objectContaining({
          timestamp: expect.any(String),
        })
      )

      unsubscribe()
    })

    it('should handle multiple callbacks', () => {
      const callback1 = vi.fn()
      const callback2 = vi.fn()
      const unsubscribe1 = onLog(callback1)
      const unsubscribe2 = onLog(callback2)

      logger.info('test')

      expect(callback1).toHaveBeenCalled()
      expect(callback2).toHaveBeenCalled()

      unsubscribe1()
      unsubscribe2()
    })
  })
})
