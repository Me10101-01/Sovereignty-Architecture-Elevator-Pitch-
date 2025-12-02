/**
 * Sovereignty Architecture - Console Error Handler
 * 
 * This module provides a comprehensive error handling solution for web pages
 * in the Refinory platform. It captures, logs, and processes console errors
 * to enable autonomous debugging and self-healing capabilities.
 * 
 * Part of the Strategickhaos Autonomous Engineering System
 */

export interface ConsoleError {
  type: 'error' | 'warn' | 'info' | 'debug';
  message: string;
  timestamp: string;
  stack?: string;
  source?: string;
  line?: number;
  column?: number;
  context?: Record<string, unknown>;
}

export interface ErrorHandlerConfig {
  /** Enable capture of console.error */
  captureErrors: boolean;
  /** Enable capture of console.warn */
  captureWarnings: boolean;
  /** Enable capture of unhandled promise rejections */
  captureUnhandledRejections: boolean;
  /** Enable capture of window.onerror events */
  captureWindowErrors: boolean;
  /** Maximum number of errors to store in memory */
  maxErrors: number;
  /** Callback to send errors to external logging service */
  onError?: (error: ConsoleError) => void;
  /** Enable verbose logging */
  verbose: boolean;
  /** Ignore patterns - errors matching these patterns will not be captured */
  ignorePatterns: RegExp[];
}

const defaultConfig: ErrorHandlerConfig = {
  captureErrors: true,
  captureWarnings: true,
  captureUnhandledRejections: true,
  captureWindowErrors: true,
  maxErrors: 100,
  verbose: false,
  ignorePatterns: []
};

class ConsoleErrorHandler {
  private config: ErrorHandlerConfig;
  private errors: ConsoleError[] = [];
  private originalConsoleError?: typeof console.error;
  private originalConsoleWarn?: typeof console.warn;
  private initialized = false;

  constructor(config: Partial<ErrorHandlerConfig> = {}) {
    this.config = { ...defaultConfig, ...config };
  }

  /**
   * Initialize the error handler and start capturing console errors
   */
  public init(): void {
    if (this.initialized) {
      if (this.config.verbose) {
        console.info('[SovereigntyErrorHandler] Already initialized');
      }
      return;
    }

    if (typeof window === 'undefined') {
      // Server-side - skip DOM error handlers
      this.initServerSide();
    } else {
      // Client-side - full initialization
      this.initClientSide();
    }

    this.initialized = true;
    if (this.config.verbose) {
      console.info('[SovereigntyErrorHandler] Initialized successfully');
    }
  }

  private initServerSide(): void {
    // Override console methods
    if (this.config.captureErrors) {
      this.originalConsoleError = console.error;
      console.error = (...args: unknown[]) => {
        this.captureError('error', args);
        this.originalConsoleError?.apply(console, args);
      };
    }

    if (this.config.captureWarnings) {
      this.originalConsoleWarn = console.warn;
      console.warn = (...args: unknown[]) => {
        this.captureError('warn', args);
        this.originalConsoleWarn?.apply(console, args);
      };
    }

    // Handle unhandled promise rejections in Node.js
    if (this.config.captureUnhandledRejections) {
      process.on('unhandledRejection', (reason: unknown) => {
        this.handleUnhandledRejection(reason);
      });
    }
  }

  private initClientSide(): void {
    // Override console methods
    if (this.config.captureErrors) {
      this.originalConsoleError = console.error;
      console.error = (...args: unknown[]) => {
        this.captureError('error', args);
        this.originalConsoleError?.apply(console, args);
      };
    }

    if (this.config.captureWarnings) {
      this.originalConsoleWarn = console.warn;
      console.warn = (...args: unknown[]) => {
        this.captureError('warn', args);
        this.originalConsoleWarn?.apply(console, args);
      };
    }

    // Handle window.onerror
    if (this.config.captureWindowErrors) {
      window.onerror = (
        message: string | Event,
        source?: string,
        line?: number,
        column?: number,
        error?: Error
      ): boolean => {
        this.handleWindowError(message, source, line, column, error);
        return false; // Don't suppress the error
      };
    }

    // Handle unhandled promise rejections
    if (this.config.captureUnhandledRejections) {
      window.addEventListener('unhandledrejection', (event: PromiseRejectionEvent) => {
        this.handleUnhandledRejection(event.reason);
      });
    }
  }

  private captureError(type: 'error' | 'warn', args: unknown[]): void {
    const message = args
      .map(arg => {
        if (arg instanceof Error) {
          return arg.message;
        }
        if (typeof arg === 'object') {
          try {
            return JSON.stringify(arg);
          } catch {
            return String(arg);
          }
        }
        return String(arg);
      })
      .join(' ');

    // Check ignore patterns
    if (this.shouldIgnore(message)) {
      return;
    }

    const errorInfo: ConsoleError = {
      type,
      message,
      timestamp: new Date().toISOString(),
      stack: args.find(arg => arg instanceof Error)
        ? (args.find(arg => arg instanceof Error) as Error).stack
        : undefined
    };

    this.addError(errorInfo);
  }

  private handleWindowError(
    message: string | Event,
    source?: string,
    line?: number,
    column?: number,
    error?: Error
  ): void {
    const errorMessage = typeof message === 'string' ? message : 'Unknown error';

    if (this.shouldIgnore(errorMessage)) {
      return;
    }

    const errorInfo: ConsoleError = {
      type: 'error',
      message: errorMessage,
      timestamp: new Date().toISOString(),
      source,
      line,
      column,
      stack: error?.stack
    };

    this.addError(errorInfo);
  }

  private handleUnhandledRejection(reason: unknown): void {
    let message: string;
    let stack: string | undefined;

    if (reason instanceof Error) {
      message = `Unhandled Promise Rejection: ${reason.message}`;
      stack = reason.stack;
    } else {
      message = `Unhandled Promise Rejection: ${String(reason)}`;
    }

    if (this.shouldIgnore(message)) {
      return;
    }

    const errorInfo: ConsoleError = {
      type: 'error',
      message,
      timestamp: new Date().toISOString(),
      stack
    };

    this.addError(errorInfo);
  }

  private shouldIgnore(message: string): boolean {
    return this.config.ignorePatterns.some(pattern => pattern.test(message));
  }

  private addError(error: ConsoleError): void {
    this.errors.push(error);

    // Trim to max size
    while (this.errors.length > this.config.maxErrors) {
      this.errors.shift();
    }

    // Call external handler if configured
    if (this.config.onError) {
      try {
        this.config.onError(error);
      } catch (e) {
        // Don't let the error handler cause more errors
        if (this.config.verbose && this.originalConsoleError) {
          this.originalConsoleError('[SovereigntyErrorHandler] onError callback failed:', e);
        }
      }
    }
  }

  /**
   * Get all captured errors
   */
  public getErrors(): ConsoleError[] {
    return [...this.errors];
  }

  /**
   * Get errors filtered by type
   */
  public getErrorsByType(type: ConsoleError['type']): ConsoleError[] {
    return this.errors.filter(e => e.type === type);
  }

  /**
   * Clear all captured errors
   */
  public clearErrors(): void {
    this.errors = [];
  }

  /**
   * Get error statistics
   */
  public getStats(): { total: number; byType: Record<string, number> } {
    const byType: Record<string, number> = {};
    for (const error of this.errors) {
      byType[error.type] = (byType[error.type] || 0) + 1;
    }
    return {
      total: this.errors.length,
      byType
    };
  }

  /**
   * Export errors as JSON
   */
  public exportErrors(): string {
    return JSON.stringify({
      exportedAt: new Date().toISOString(),
      platform: 'Sovereignty Architecture - Refinory',
      errors: this.errors
    }, null, 2);
  }

  /**
   * Restore original console methods and stop capturing
   */
  public destroy(): void {
    if (this.originalConsoleError) {
      console.error = this.originalConsoleError;
    }
    if (this.originalConsoleWarn) {
      console.warn = this.originalConsoleWarn;
    }
    this.initialized = false;
    if (this.config.verbose) {
      console.info('[SovereigntyErrorHandler] Destroyed');
    }
  }

  /**
   * Create a formatted report of all errors
   */
  public generateReport(): string {
    const stats = this.getStats();
    const lines: string[] = [
      '╔══════════════════════════════════════════════════════════════╗',
      '║       SOVEREIGNTY ARCHITECTURE - ERROR REPORT                ║',
      '║           Refinory Console Error Handler                     ║',
      '╠══════════════════════════════════════════════════════════════╣',
      `║ Generated: ${new Date().toISOString().padEnd(47)}║`,
      `║ Total Errors: ${String(stats.total).padEnd(44)}║`,
      '╠══════════════════════════════════════════════════════════════╣'
    ];

    for (const [type, count] of Object.entries(stats.byType)) {
      lines.push(`║ ${type.toUpperCase()}: ${String(count).padEnd(53)}║`);
    }

    lines.push('╠══════════════════════════════════════════════════════════════╣');
    lines.push('║ RECENT ERRORS:                                              ║');
    lines.push('╠══════════════════════════════════════════════════════════════╣');

    const recentErrors = this.errors.slice(-5);
    for (const error of recentErrors) {
      const truncatedMsg = error.message.length > 55
        ? error.message.substring(0, 52) + '...'
        : error.message;
      lines.push(`║ [${error.type.toUpperCase()}] ${truncatedMsg.padEnd(51)}║`);
    }

    lines.push('╚══════════════════════════════════════════════════════════════╝');

    return lines.join('\n');
  }
}

// Export singleton instance for easy use
export const errorHandler = new ConsoleErrorHandler();

// Export class for custom instances
export { ConsoleErrorHandler };

// Auto-initialization for browser environments
export function autoInit(config?: Partial<ErrorHandlerConfig>): ConsoleErrorHandler {
  const handler = new ConsoleErrorHandler(config);
  handler.init();
  return handler;
}
