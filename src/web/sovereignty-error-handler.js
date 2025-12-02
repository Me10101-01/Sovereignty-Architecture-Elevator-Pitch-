/**
 * Sovereignty Architecture - Console Error Handler
 * Standalone script for direct inclusion in HTML pages
 * 
 * Usage:
 *   <script src="sovereignty-error-handler.js"></script>
 *   <script>
 *     // Auto-initializes on load
 *     // Access via: window.SovereigntyErrorHandler
 *   </script>
 * 
 * Part of the Strategickhaos Autonomous Engineering System
 */

(function(global) {
  'use strict';

  var defaultConfig = {
    captureErrors: true,
    captureWarnings: true,
    captureUnhandledRejections: true,
    captureWindowErrors: true,
    maxErrors: 100,
    verbose: false,
    ignorePatterns: []
  };

  /**
   * Console Error Handler for Sovereignty Architecture
   * @param {Object} config Configuration options
   */
  function ConsoleErrorHandler(config) {
    this.config = Object.assign({}, defaultConfig, config || {});
    this.errors = [];
    this.originalConsoleError = null;
    this.originalConsoleWarn = null;
    this.initialized = false;
  }

  /**
   * Initialize the error handler
   */
  ConsoleErrorHandler.prototype.init = function() {
    var self = this;

    if (this.initialized) {
      if (this.config.verbose) {
        console.info('[SovereigntyErrorHandler] Already initialized');
      }
      return this;
    }

    // Override console.error
    if (this.config.captureErrors) {
      this.originalConsoleError = console.error;
      console.error = function() {
        var args = Array.prototype.slice.call(arguments);
        self.captureError('error', args);
        self.originalConsoleError.apply(console, args);
      };
    }

    // Override console.warn
    if (this.config.captureWarnings) {
      this.originalConsoleWarn = console.warn;
      console.warn = function() {
        var args = Array.prototype.slice.call(arguments);
        self.captureError('warn', args);
        self.originalConsoleWarn.apply(console, args);
      };
    }

    // Handle window.onerror
    if (this.config.captureWindowErrors && typeof window !== 'undefined') {
      var oldOnError = window.onerror;
      window.onerror = function(message, source, line, column, error) {
        self.handleWindowError(message, source, line, column, error);
        if (oldOnError) {
          return oldOnError.apply(this, arguments);
        }
        return false;
      };
    }

    // Handle unhandled promise rejections
    if (this.config.captureUnhandledRejections && typeof window !== 'undefined') {
      window.addEventListener('unhandledrejection', function(event) {
        self.handleUnhandledRejection(event.reason);
      });
    }

    this.initialized = true;
    if (this.config.verbose) {
      console.info('[SovereigntyErrorHandler] Initialized successfully');
    }

    return this;
  };

  /**
   * Capture a console error or warning
   */
  ConsoleErrorHandler.prototype.captureError = function(type, args) {
    var message = args.map(function(arg) {
      if (arg instanceof Error) {
        return arg.message;
      }
      if (typeof arg === 'object') {
        try {
          return JSON.stringify(arg);
        } catch (e) {
          return String(arg);
        }
      }
      return String(arg);
    }).join(' ');

    if (this.shouldIgnore(message)) {
      return;
    }

    var errorInfo = {
      type: type,
      message: message,
      timestamp: new Date().toISOString(),
      stack: null
    };

    // Extract stack trace if available
    for (var i = 0; i < args.length; i++) {
      if (args[i] instanceof Error && args[i].stack) {
        errorInfo.stack = args[i].stack;
        break;
      }
    }

    this.addError(errorInfo);
  };

  /**
   * Handle window.onerror events
   */
  ConsoleErrorHandler.prototype.handleWindowError = function(message, source, line, column, error) {
    var errorMessage = typeof message === 'string' ? message : 'Unknown error';

    if (this.shouldIgnore(errorMessage)) {
      return;
    }

    var errorInfo = {
      type: 'error',
      message: errorMessage,
      timestamp: new Date().toISOString(),
      source: source,
      line: line,
      column: column,
      stack: error && error.stack ? error.stack : null
    };

    this.addError(errorInfo);
  };

  /**
   * Handle unhandled promise rejections
   */
  ConsoleErrorHandler.prototype.handleUnhandledRejection = function(reason) {
    var message;
    var stack = null;

    if (reason instanceof Error) {
      message = 'Unhandled Promise Rejection: ' + reason.message;
      stack = reason.stack;
    } else {
      message = 'Unhandled Promise Rejection: ' + String(reason);
    }

    if (this.shouldIgnore(message)) {
      return;
    }

    var errorInfo = {
      type: 'error',
      message: message,
      timestamp: new Date().toISOString(),
      stack: stack
    };

    this.addError(errorInfo);
  };

  /**
   * Check if an error should be ignored
   */
  ConsoleErrorHandler.prototype.shouldIgnore = function(message) {
    for (var i = 0; i < this.config.ignorePatterns.length; i++) {
      if (this.config.ignorePatterns[i].test(message)) {
        return true;
      }
    }
    return false;
  };

  /**
   * Add an error to the collection
   */
  ConsoleErrorHandler.prototype.addError = function(error) {
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
        if (this.config.verbose && this.originalConsoleError) {
          this.originalConsoleError('[SovereigntyErrorHandler] onError callback failed:', e);
        }
      }
    }
  };

  /**
   * Get all captured errors
   */
  ConsoleErrorHandler.prototype.getErrors = function() {
    return this.errors.slice();
  };

  /**
   * Get errors filtered by type
   */
  ConsoleErrorHandler.prototype.getErrorsByType = function(type) {
    return this.errors.filter(function(e) {
      return e.type === type;
    });
  };

  /**
   * Clear all captured errors
   */
  ConsoleErrorHandler.prototype.clearErrors = function() {
    this.errors = [];
  };

  /**
   * Get error statistics
   */
  ConsoleErrorHandler.prototype.getStats = function() {
    var byType = {};
    for (var i = 0; i < this.errors.length; i++) {
      var type = this.errors[i].type;
      byType[type] = (byType[type] || 0) + 1;
    }
    return {
      total: this.errors.length,
      byType: byType
    };
  };

  /**
   * Export errors as JSON
   */
  ConsoleErrorHandler.prototype.exportErrors = function() {
    return JSON.stringify({
      exportedAt: new Date().toISOString(),
      platform: 'Sovereignty Architecture - Refinory',
      errors: this.errors
    }, null, 2);
  };

  /**
   * Generate a formatted error report
   */
  ConsoleErrorHandler.prototype.generateReport = function() {
    var stats = this.getStats();
    var lines = [
      '╔══════════════════════════════════════════════════════════════╗',
      '║       SOVEREIGNTY ARCHITECTURE - ERROR REPORT                ║',
      '║           Refinory Console Error Handler                     ║',
      '╠══════════════════════════════════════════════════════════════╣',
      '║ Generated: ' + new Date().toISOString().substring(0, 47) + '║',
      '║ Total Errors: ' + String(stats.total).padEnd ? String(stats.total).padEnd(44) : String(stats.total) + '║',
      '╠══════════════════════════════════════════════════════════════╣'
    ];

    for (var type in stats.byType) {
      if (stats.byType.hasOwnProperty(type)) {
        lines.push('║ ' + type.toUpperCase() + ': ' + stats.byType[type] + '                                                     ║');
      }
    }

    lines.push('╠══════════════════════════════════════════════════════════════╣');
    lines.push('║ RECENT ERRORS:                                              ║');
    lines.push('╠══════════════════════════════════════════════════════════════╣');

    var recentErrors = this.errors.slice(-5);
    for (var i = 0; i < recentErrors.length; i++) {
      var error = recentErrors[i];
      var truncatedMsg = error.message.length > 55
        ? error.message.substring(0, 52) + '...'
        : error.message;
      lines.push('║ [' + error.type.toUpperCase() + '] ' + truncatedMsg + '                                  ║');
    }

    lines.push('╚══════════════════════════════════════════════════════════════╝');

    return lines.join('\n');
  };

  /**
   * Restore original console methods
   */
  ConsoleErrorHandler.prototype.destroy = function() {
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
  };

  // Create default instance and auto-initialize
  var defaultHandler = new ConsoleErrorHandler();
  defaultHandler.init();

  // Export to global namespace
  global.SovereigntyErrorHandler = {
    handler: defaultHandler,
    ConsoleErrorHandler: ConsoleErrorHandler,
    init: function(config) {
      return new ConsoleErrorHandler(config).init();
    },
    getErrors: function() {
      return defaultHandler.getErrors();
    },
    clearErrors: function() {
      defaultHandler.clearErrors();
    },
    getStats: function() {
      return defaultHandler.getStats();
    },
    exportErrors: function() {
      return defaultHandler.exportErrors();
    },
    generateReport: function() {
      return defaultHandler.generateReport();
    }
  };

  // Log initialization
  if (typeof console !== 'undefined' && console.info) {
    console.info('[SovereigntyErrorHandler] 🏛️ Sovereignty Architecture - Console Error Handler loaded');
  }

})(typeof window !== 'undefined' ? window : typeof global !== 'undefined' ? global : this);
