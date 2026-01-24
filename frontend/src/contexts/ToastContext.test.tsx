import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { render, screen, act } from '@testing-library/react'
import { ToastProvider, useToast } from './ToastContext'

// Test component that uses the hook
function TestComponent({ onToastAdded }: { onToastAdded?: (id: string) => void }) {
  const { toasts, addToast, removeToast, showUndoToast } = useToast()

  const handleAddSuccess = () => {
    const id = addToast({ type: 'success', message: 'Success!' })
    onToastAdded?.(id)
  }

  return (
    <div>
      <div data-testid="toast-count">{toasts.length}</div>
      <button data-testid="add-success" onClick={handleAddSuccess}>
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
          <button data-testid={`remove-${toast.id}`} onClick={() => removeToast(toast.id)}>
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

  it('should add toast', () => {
    render(
      <ToastProvider>
        <TestComponent />
      </ToastProvider>
    )

    expect(screen.getByTestId('toast-count').textContent).toBe('0')

    act(() => {
      screen.getByTestId('add-success').click()
    })

    expect(screen.getByTestId('toast-count').textContent).toBe('1')
    expect(screen.getByTestId('toast-success')).toHaveTextContent('Success!')
  })

  it('should add different toast types', () => {
    render(
      <ToastProvider>
        <TestComponent />
      </ToastProvider>
    )

    act(() => {
      screen.getByTestId('add-success').click()
      screen.getByTestId('add-error').click()
      screen.getByTestId('add-warning').click()
    })

    expect(screen.getByTestId('toast-count').textContent).toBe('3')
    expect(screen.getByTestId('toast-success')).toBeInTheDocument()
    expect(screen.getByTestId('toast-error')).toBeInTheDocument()
    expect(screen.getByTestId('toast-warning')).toBeInTheDocument()
  })

  it('should auto-remove toast after duration', () => {
    render(
      <ToastProvider>
        <TestComponent />
      </ToastProvider>
    )

    act(() => {
      screen.getByTestId('add-success').click()
    })
    expect(screen.getByTestId('toast-count').textContent).toBe('1')

    // Fast-forward past the default 5 second duration
    act(() => {
      vi.advanceTimersByTime(6000)
    })

    expect(screen.getByTestId('toast-count').textContent).toBe('0')
  })

  it('should remove toast manually', () => {
    render(
      <ToastProvider>
        <TestComponent />
      </ToastProvider>
    )

    act(() => {
      screen.getByTestId('add-success').click()
    })
    expect(screen.getByTestId('toast-count').textContent).toBe('1')

    const toastElement = screen.getByTestId('toast-success')
    const removeButton = toastElement.querySelector('button')

    act(() => {
      removeButton?.click()
    })

    expect(screen.getByTestId('toast-count').textContent).toBe('0')
  })

  it('should show undo toast with action', () => {
    render(
      <ToastProvider>
        <TestComponent />
      </ToastProvider>
    )

    act(() => {
      screen.getByTestId('show-undo').click()
    })

    expect(screen.getByTestId('toast-count').textContent).toBe('1')
    expect(screen.getByTestId('toast-warning')).toHaveTextContent('Item deleted')
  })

  it('should execute confirm action after undo toast timeout', () => {
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

    render(
      <ToastProvider>
        <TestUndoComponent />
      </ToastProvider>
    )

    act(() => {
      screen.getByTestId('show-undo').click()
    })

    // Wait for the undo timeout
    act(() => {
      vi.advanceTimersByTime(1100)
    })

    expect(onConfirm).toHaveBeenCalled()
    expect(onUndo).not.toHaveBeenCalled()
  })

  it('should return toast id when adding', () => {
    let returnedId: string | undefined

    render(
      <ToastProvider>
        <TestComponent onToastAdded={(id) => { returnedId = id }} />
      </ToastProvider>
    )

    act(() => {
      screen.getByTestId('add-success').click()
    })

    expect(returnedId).toBeDefined()
    expect(typeof returnedId).toBe('string')
  })
})
