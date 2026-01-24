import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { render, screen, act } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { ToastProvider, useToast } from './ToastContext'

// Test component that uses the hook
function TestComponent() {
  const { toasts, addToast, removeToast, showUndoToast } = useToast()

  return (
    <div>
      <div data-testid="toast-count">{toasts.length}</div>
      <button
        data-testid="add-success"
        onClick={() => addToast({ type: 'success', message: 'Success!' })}
      >
        Add Success
      </button>
      <button
        data-testid="add-error"
        onClick={() => addToast({ type: 'error', message: 'Error!' })}
      >
        Add Error
      </button>
      <button
        data-testid="add-warning"
        onClick={() => addToast({ type: 'warning', message: 'Warning!' })}
      >
        Add Warning
      </button>
      <button
        data-testid="add-with-action"
        onClick={() =>
          addToast({
            type: 'info',
            message: 'Info with action',
            action: { label: 'Undo', onClick: vi.fn() },
          })
        }
      >
        Add With Action
      </button>
      <button
        data-testid="show-undo"
        onClick={() =>
          showUndoToast(
            'Item deleted',
            () => console.log('Undone'),
            () => console.log('Confirmed'),
            1000
          )
        }
      >
        Show Undo Toast
      </button>
      {toasts.map((toast) => (
        <div key={toast.id} data-testid={`toast-${toast.type}`}>
          {toast.message}
          <button
            data-testid={`remove-${toast.id}`}
            onClick={() => removeToast(toast.id)}
          >
            Remove
          </button>
        </div>
      ))}
    </div>
  )
}

describe('ToastContext', () => {
  beforeEach(() => {
    vi.useFakeTimers()
  })

  afterEach(() => {
    vi.useRealTimers()
  })

  it('should throw error when used outside provider', () => {
    const originalError = console.error
    console.error = vi.fn()

    expect(() => {
      render(<TestComponent />)
    }).toThrow('useToast must be used within a ToastProvider')

    console.error = originalError
  })

  it('should add toast', async () => {
    const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime })
    render(
      <ToastProvider>
        <TestComponent />
      </ToastProvider>
    )

    expect(screen.getByTestId('toast-count').textContent).toBe('0')

    await user.click(screen.getByTestId('add-success'))

    expect(screen.getByTestId('toast-count').textContent).toBe('1')
    expect(screen.getByTestId('toast-success')).toHaveTextContent('Success!')
  })

  it('should add different toast types', async () => {
    const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime })
    render(
      <ToastProvider>
        <TestComponent />
      </ToastProvider>
    )

    await user.click(screen.getByTestId('add-success'))
    await user.click(screen.getByTestId('add-error'))
    await user.click(screen.getByTestId('add-warning'))

    expect(screen.getByTestId('toast-count').textContent).toBe('3')
    expect(screen.getByTestId('toast-success')).toBeInTheDocument()
    expect(screen.getByTestId('toast-error')).toBeInTheDocument()
    expect(screen.getByTestId('toast-warning')).toBeInTheDocument()
  })

  it('should auto-remove toast after duration', async () => {
    const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime })
    render(
      <ToastProvider>
        <TestComponent />
      </ToastProvider>
    )

    await user.click(screen.getByTestId('add-success'))
    expect(screen.getByTestId('toast-count').textContent).toBe('1')

    // Fast-forward past the default 5 second duration
    act(() => {
      vi.advanceTimersByTime(6000)
    })

    expect(screen.getByTestId('toast-count').textContent).toBe('0')
  })

  it('should remove toast manually', async () => {
    const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime })
    render(
      <ToastProvider>
        <TestComponent />
      </ToastProvider>
    )

    await user.click(screen.getByTestId('add-success'))
    expect(screen.getByTestId('toast-count').textContent).toBe('1')

    const toastElement = screen.getByTestId('toast-success')
    const toastId = toastElement.querySelector('button')?.getAttribute('data-testid')?.replace('remove-', '')

    if (toastId) {
      await user.click(screen.getByTestId(`remove-${toastId}`))
    }

    expect(screen.getByTestId('toast-count').textContent).toBe('0')
  })

  it('should show undo toast with action', async () => {
    const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime })
    render(
      <ToastProvider>
        <TestComponent />
      </ToastProvider>
    )

    await user.click(screen.getByTestId('show-undo'))

    expect(screen.getByTestId('toast-count').textContent).toBe('1')
    expect(screen.getByTestId('toast-warning')).toHaveTextContent('Item deleted')
  })

  it('should execute confirm action after undo toast timeout', async () => {
    const onConfirm = vi.fn()
    const onUndo = vi.fn()

    function TestUndoComponent() {
      const { showUndoToast, toasts } = useToast()
      return (
        <div>
          <div data-testid="toast-count">{toasts.length}</div>
          <button
            data-testid="show-undo"
            onClick={() => showUndoToast('Item deleted', onUndo, onConfirm, 1000)}
          >
            Show Undo
          </button>
        </div>
      )
    }

    const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime })
    render(
      <ToastProvider>
        <TestUndoComponent />
      </ToastProvider>
    )

    await user.click(screen.getByTestId('show-undo'))

    // Wait for the undo timeout
    act(() => {
      vi.advanceTimersByTime(1100)
    })

    expect(onConfirm).toHaveBeenCalled()
    expect(onUndo).not.toHaveBeenCalled()
  })

  it('should return toast id when adding', async () => {
    let returnedId: string | undefined

    function TestIdComponent() {
      const { addToast } = useToast()
      return (
        <button
          data-testid="add"
          onClick={() => {
            returnedId = addToast({ type: 'success', message: 'Test' })
          }}
        >
          Add
        </button>
      )
    }

    const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime })
    render(
      <ToastProvider>
        <TestIdComponent />
      </ToastProvider>
    )

    await user.click(screen.getByTestId('add'))

    expect(returnedId).toBeDefined()
    expect(typeof returnedId).toBe('string')
  })
})
